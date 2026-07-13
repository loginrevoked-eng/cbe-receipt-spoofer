import pytest
from unittest.mock import Mock, patch, MagicMock
from db import DBManager
from config import Config
from receipt import Receipt


class TestDBManager:
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Config)
        config.receipts_db_table = "receipts"
        config.credentials = Mock()
        config.credentials.neon_database_url = "postgresql://test"
        return config
    
    @pytest.fixture
    def mock_connection(self):
        with patch('db.psycopg2.connect') as mock_conn:
            mock_cursor = MagicMock()
            mock_conn.return_value.cursor.return_value.__enter__.return_value = mock_cursor
            yield mock_conn, mock_cursor
    
    def test_init_db_manager(self, mock_config, mock_connection):
        mock_conn, _ = mock_connection
        db = DBManager(mock_config)
        
        assert db.config == mock_config
        assert db.receipts_table == "receipts"
        mock_conn.assert_called_once()
    
    def test_create_table(self, mock_config, mock_connection):
        _, mock_cursor = mock_connection
        db = DBManager(mock_config)
        db.create_table()
        
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS" in call_args
        assert "receipts" in call_args
    
    def test_create_receipts_table(self, mock_config, mock_connection):
        _, mock_cursor = mock_connection
        db = DBManager(mock_config)
        db.create_receipts_table()
        
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args[0][0]
        assert "receipt_id" in call_args
        assert "PRIMARY KEY" in call_args
    
    def test_save_receipt(self, mock_config, mock_connection):
        _, mock_cursor = mock_connection
        db = DBManager(mock_config)
        
        mock_receipt = Mock(spec=Receipt)
        mock_receipt.to_dict.return_value = {
            "receipt_id": "TEST123",
            "sender_name": "Alice",
            "receiver_name": "Bob",
            "amount": 100.0,
            "total_amount": 100.0,
            "vat": 0.0,
            "commission": 0.0,
            "epoch_time": 1234567890,
            "sender_account": "123456",
            "receiver_account": "789012",
            "txn_qrcode_url": "http://qr.url",
            "txn_pdf_url": "http://pdf.url"
        }
        
        db.save_receipt(mock_receipt)
        
        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args[0][0]
        assert "INSERT INTO" in call_args
        assert "receipts" in call_args
    
    def test_fetch_receipt_as_dict(self, mock_config, mock_connection):
        _, mock_cursor = mock_connection
        mock_cursor.fetchone.return_value = (
            "TEST123", "Alice", "Bob", "123456", "789012",
            "http://qr.url", "http://pdf.url", 100.0, 1234567890, 0.0, 0.0, 100.0
        )
        mock_cursor.description = [
            ("receipt_id",), ("sender_name",), ("receiver_name",),
            ("sender_account",), ("receiver_account",),
            ("txn_qrcode_url",), ("txn_pdf_url",),
            ("amount",), ("epoch_time",), ("vat",), ("commission",), ("total_amount",)
        ]
        
        db = DBManager(mock_config)
        result = db.fetch_receipt("TEST123", as_receipt=False)
        
        assert isinstance(result, dict)
        assert result["receipt_id"] == "TEST123"
        assert result["sender_name"] == "Alice"
    
    def test_fetch_receipt_not_found(self, mock_config, mock_connection):
        _, mock_cursor = mock_connection
        mock_cursor.fetchone.return_value = None
        
        db = DBManager(mock_config)
        result = db.fetch_receipt("NOTFOUND")
        
        assert result is None
