import pytest
from unittest.mock import Mock, patch, MagicMock
from s3 import S3Client
from config import Config
from botocore.exceptions import ClientError


class TestS3Client:
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Config)
        config.supabase_s3_endpoint_url_s3 = "https://test.supabase.co/storage/v1/s3"
        config.supabase_s3_aws_region = "us-east-2"
        config.supabase_s3_bucket_name = "test_bucket"
        config.credentials = Mock()
        config.credentials.supabase_s3_access_key_id = "test_key"
        config.credentials.supabase_s3_secret_access_key = "test_secret"
        return config
    
    @patch('s3.boto3.client')
    def test_init_s3_client(self, mock_boto, mock_config):
        s3 = S3Client(mock_config)
        
        assert s3.bucket_name == "test_bucket"
        mock_boto.assert_called_once()
        call_kwargs = mock_boto.call_args[1]
        assert call_kwargs['endpoint_url'] == mock_config.supabase_s3_endpoint_url_s3
        assert call_kwargs['region_name'] == mock_config.supabase_s3_aws_region
    
    @patch('s3.boto3.client')
    def test_upload_file_success(self, mock_boto, mock_config):
        mock_client = Mock()
        mock_boto.return_value = mock_client
        
        s3 = S3Client(mock_config)
        s3.upload_file("test.pdf")
        
        mock_client.upload_file.assert_called_once()
        call_kwargs = mock_client.upload_file.call_args[1]
        assert call_kwargs['Filename'] == "test.pdf"
        assert call_kwargs['Bucket'] == "test_bucket"
        assert call_kwargs['ExtraArgs']['ContentType'] == "application/pdf"
    
    @patch('s3.boto3.client')
    def test_upload_file_with_destination(self, mock_boto, mock_config):
        mock_client = Mock()
        mock_boto.return_value = mock_client
        
        s3 = S3Client(mock_config)
        s3.upload_file("test.pdf", "custom/path/test.pdf")
        
        mock_client.upload_file.assert_called_once()
        call_kwargs = mock_client.upload_file.call_args[1]
        assert call_kwargs['Key'] == "custom/path/test.pdf"
    
    @patch('s3.boto3.client')
    def test_upload_file_failure(self, mock_boto, mock_config):
        mock_client = Mock()
        mock_client.upload_file.side_effect = Exception("Upload failed")
        mock_boto.return_value = mock_client
        
        s3 = S3Client(mock_config)
        s3.upload_file("test.pdf")  # Should not raise, just print error
        
        mock_client.upload_file.assert_called_once()
    
    @patch('s3.boto3.client')
    def test_get_direct_url_success(self, mock_boto, mock_config):
        mock_client = Mock()
        mock_client.generate_presigned_url.return_value = "https://signed.url"
        mock_boto.return_value = mock_client
        
        s3 = S3Client(mock_config)
        url = s3.get_direct_url("test.pdf")
        
        assert url == "https://signed.url"
        mock_client.generate_presigned_url.assert_called_once()
    
    @patch('s3.boto3.client')
    def test_get_direct_url_with_custom_expiry(self, mock_boto, mock_config):
        mock_client = Mock()
        mock_client.generate_presigned_url.return_value = "https://signed.url"
        mock_boto.return_value = mock_client
        
        s3 = S3Client(mock_config)
        url = s3.get_direct_url("test.pdf", expires_in=7200)
        
        call_kwargs = mock_client.generate_presigned_url.call_args[1]
        assert call_kwargs['ExpiresIn'] == 7200
    
    @patch('s3.boto3.client')
    def test_get_direct_url_failure(self, mock_boto, mock_config):
        mock_client = Mock()
        mock_client.generate_presigned_url.side_effect = ClientError(
            {'Error': {'Code': 'NoSuchKey'}}, 'generate_presigned_url'
        )
        mock_boto.return_value = mock_client
        
        s3 = S3Client(mock_config)
        url = s3.get_direct_url("test.pdf")
        
        assert url is None
