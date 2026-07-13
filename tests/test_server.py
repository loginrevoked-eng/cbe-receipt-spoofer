import pytest
import logging
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from server import app

logger = logging.getLogger(__name__)


@pytest.fixture
def client():
    logger.info("Creating TestClient for FastAPI app")
    return TestClient(app)


@pytest.fixture
def mock_dependencies():
    with patch('server.config') as mock_config, \
         patch('server.s3_client') as mock_s3, \
         patch('server.db_manager') as mock_db:
        
        mock_config.receipt_form_html_filename = "test_form.html"
        yield mock_config, mock_s3, mock_db


class TestServerEndpoints:
    
    @patch('server.FileResponse')
    def test_get_receipt_form(self, mock_file_response, client):
        response = client.get("/")
        assert response.status_code == 200
    
    @patch('server.Receipt')
    @patch('server.s3_client')
    @patch('server.db_manager')
    def test_generate_mobile_receipt_success(self, mock_db, mock_s3, mock_receipt_class, client):
        # Setup mocks
        mock_receipt = Mock()
        mock_receipt.generate_receipt_id.return_value = "TEST123"
        mock_receipt.pdf_html_template.return_value = "<html>pdf</html>"
        mock_receipt.mobile_html_template.return_value = "<html>mobile</html>"
        mock_receipt.to_pdf.return_value = "TEST123.pdf"
        mock_receipt_class.return_value = mock_receipt
        
        mock_s3.upload_file.return_value = None
        mock_db.save_receipt.return_value = None
        
        # Make request
        response = client.post(
            "/generate-mobile-receipt",
            json={
                "sender_name": "Alice",
                "receiver_name": "Bob",
                "sender_account": "123456",
                "receiver_account": "789012",
                "amount": 100.0,
                "vat": 15.0,
                "commission": 5.0
            }
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
    
    @patch('server.Receipt')
    def test_generate_mobile_receipt_pdf_failure(self, mock_receipt_class, client):
        mock_receipt = Mock()
        mock_receipt.to_pdf.return_value = None
        mock_receipt_class.return_value = mock_receipt
        
        response = client.post(
            "/generate-mobile-receipt",
            json={
                "sender_name": "Alice",
                "receiver_name": "Bob",
                "amount": 100.0
            }
        )
        
        assert response.status_code == 500
        assert "Failed to generate PDF" in response.json()["detail"]
    
    @patch('server.s3_client')
    def test_get_pdf_receipt_success(self, mock_s3, client):
        mock_s3.get_direct_url.return_value = "https://s3.example.com/TEST123.pdf"
        
        response = client.get("/receipts/pdf/TEST123")
        
        assert response.status_code == 200  # 307 redirect becomes 200 after following
    
    @patch('server.s3_client')
    def test_get_pdf_receipt_not_found(self, mock_s3, client):
        mock_s3.get_direct_url.return_value = None
        
        response = client.get("/receipts/pdf/TEST123")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @patch('server.db_manager')
    def test_get_mobile_receipt_success(self, mock_db, client):
        mock_receipt = Mock()
        mock_receipt.mobile_html_template.return_value = "<html>receipt</html>"
        mock_db.fetch_receipt.return_value = mock_receipt
        
        response = client.get("/receipts/mobile/TEST123")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
    
    @patch('server.db_manager')
    def test_get_mobile_receipt_not_found(self, mock_db, client):
        mock_db.fetch_receipt.return_value = None
        
        response = client.get("/receipts/mobile/TEST123")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
