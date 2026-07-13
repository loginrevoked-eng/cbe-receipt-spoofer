import pytest
from unittest.mock import Mock, patch, MagicMock
from receipt import Receipt
from config import Config


class TestReceipt:
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Config)
        config.pdf_baseurl = "http://localhost:8000/receipts/pdf"
        config.qrcode_baseurl = "https://api.qrserver.com/v1/create-qr-code"
        config.qr_code_size = "150x150"
        config.html2pdf_api_url = "https://html2pdfrocket.com/api"
        
        config.credentials = Mock()
        config.credentials.receipt_id_generation_secret = "test_secret"
        config.credentials.html2pdf_api_key = "test_api_key"
        
        return config
    
    def test_receipt_initialization(self, mock_config):
        receipt = Receipt(
            mock_config,
            sender_name="Alice",
            receiver_name="Bob",
            amount=100.0,
            epoch_time=1234567890
        )
        
        assert receipt.sender_name == "Alice"
        assert receipt.receiver_name == "Bob"
        assert receipt.amount == 100.0
        assert receipt.epoch_time == 1234567890
    
    def test_receipt_post_init_urls(self, mock_config):
        receipt = Receipt(
            mock_config,
            receipt_id="TEST123",
            sender_name="Alice",
            receiver_name="Bob",
            amount=100.0
        )
        
        assert "TEST123.pdf" in receipt.txn_pdf_url
        assert "150x150" in receipt.txn_qrcode_url
        assert receipt.txn_pdf_url in receipt.txn_qrcode_url
    
    def test_generate_receipt_id(self, mock_config):
        receipt = Receipt(mock_config, sender_name="Alice", receiver_name="Bob")
        receipt_id = receipt.generate_receipt_id()
        
        assert len(receipt_id) == 16
        assert receipt_id.isupper()
        assert receipt_id.isalnum()
    
    def test_to_dict(self, mock_config):
        receipt = Receipt(
            mock_config,
            receipt_id="TEST123",
            sender_name="Alice",
            receiver_name="Bob",
            sender_account="123456",
            receiver_account="789012",
            amount=100.0,
            vat=15.0,
            commission=5.0,
            total_amount=105.0,
            epoch_time=1234567890
        )
        
        data = receipt.to_dict()
        
        assert data["receipt_id"] == "TEST123"
        assert data["sender_name"] == "Alice"
        assert data["receiver_name"] == "Bob"
        assert data["amount"] == 100.0
        assert data["vat"] == 15.0
        assert data["commission"] == 5.0
        assert data["total_amount"] == 105.0
    
    @patch('receipt.requests.post')
    @patch('builtins.open', new_callable=MagicMock)
    def test_to_pdf_success(self, mock_open, mock_post, mock_config):
        mock_response = Mock()
        mock_response.content = b"PDF_CONTENT"
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        receipt = Receipt(mock_config, receipt_id="TEST123", sender_name="Alice", receiver_name="Bob")
        result = receipt.to_pdf(html_template="<html>test</html>")
        
        assert result == "TEST123.pdf"
        mock_post.assert_called_once()
    
    @patch('receipt.requests.post')
    def test_to_pdf_failure(self, mock_post, mock_config):
        mock_post.side_effect = Exception("API Error")
        
        receipt = Receipt(mock_config, receipt_id="TEST123", sender_name="Alice", receiver_name="Bob")
        result = receipt.to_pdf(html_template="<html>test</html>")
        
        assert result is None
