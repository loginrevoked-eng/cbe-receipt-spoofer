import pytest
from config import Config, Credentials
from unittest.mock import patch, mock_open
import os


class TestCredentials:
    
    @patch.dict(os.environ, {
        'RECEIPT_ID_GENERATION_SECRET': 'test_secret',
        'HTML2PDF_API_KEY': 'test_api_key',
        'SUPABASE_S3_ACCESS_KEY_ID': 'test_access_key',
        'SUPABASE_S3_SECRET_ACCESS_KEY': 'test_secret_key',
        'NEON_DATABASE_URL': 'postgresql://test'
    })
    def test_load_credentials_success(self):
        creds = Credentials().load()
        assert creds.receipt_id_generation_secret == 'test_secret'
        assert creds.html2pdf_api_key == 'test_api_key'
        assert creds.supabase_s3_access_key_id == 'test_access_key'
        assert creds.supabase_s3_secret_access_key == 'test_secret_key'
        assert creds.neon_database_url == 'postgresql://test'
    
    def test_validate_missing_credentials(self):
        creds = Credentials()
        with pytest.raises(ValueError, match="The following credentials are not set"):
            creds.validate()


class TestConfig:
    
    def test_default_config_values(self):
        with patch.object(Credentials, 'load', return_value=self._mock_credentials()):
            config = Config()
            assert config.self_domain == "localhost"
            assert config.mobile_receipt_gen_endpoint == "/generate-mobile-receipt"
            assert config.receipts_db_table == "receipts"
    
    def test_from_dict(self):
        with patch.object(Credentials, 'load', return_value=self._mock_credentials()):
            config = Config()
            config.from_dict(self_domain="example.com", receipts_db_table="custom_receipts")
            assert config.self_domain == "example.com"
            assert config.receipts_db_table == "custom_receipts"
    
    def test_from_dict_ignores_invalid_keys(self):
        with patch.object(Credentials, 'load', return_value=self._mock_credentials()):
            config = Config()
            config.from_dict(invalid_key="should_not_set", self_domain="example.com")
            assert not hasattr(config, 'invalid_key')
            assert config.self_domain == "example.com"
    
    @staticmethod
    def _mock_credentials():
        creds = Credentials()
        creds.receipt_id_generation_secret = 'test'
        creds.html2pdf_api_key = 'test'
        creds.supabase_s3_access_key_id = 'test'
        creds.supabase_s3_secret_access_key = 'test'
        creds.neon_database_url = 'test'
        return creds
