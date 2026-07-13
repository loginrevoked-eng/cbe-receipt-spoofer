"""
Pytest configuration and fixtures shared across all tests.
"""
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# Set environment variables before any imports
os.environ.setdefault('RECEIPT_ID_GENERATION_SECRET', 'test_secret')
os.environ.setdefault('HTML2PDF_API_KEY', 'test_api_key')
os.environ.setdefault('SUPABASE_S3_ACCESS_KEY_ID', 'test_access_key')
os.environ.setdefault('SUPABASE_S3_SECRET_ACCESS_KEY', 'test_secret_key')
os.environ.setdefault('NEON_DATABASE_URL', 'postgresql://test:test@localhost/test')

# Mock database and S3 connections at import time
mock_db_conn = MagicMock()
mock_cursor = MagicMock()
mock_db_conn.cursor.return_value.__enter__.return_value = mock_cursor

# Patch psycopg2.connect before any module imports it
sys.modules['psycopg2'] = MagicMock()
sys.modules['psycopg2'].connect = MagicMock(return_value=mock_db_conn)

# Patch boto3.client before any module imports it
mock_boto_client = MagicMock()
sys.modules['boto3'] = MagicMock()
sys.modules['boto3'].client = MagicMock(return_value=mock_boto_client)
