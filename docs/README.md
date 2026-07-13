# Receipt Generator Web Service

A FastAPI-based web service for generating digital receipts with PDF generation and S3 storage.

## Project Structure

```
reccbe/
├── app/                    # Application code
│   ├── config.py          # Configuration management
│   ├── db.py              # Database manager
│   ├── receipt.py         # Receipt model and logic
│   ├── s3.py              # S3 storage client
│   ├── server.py          # FastAPI application
│   ├── templates.py       # HTML template rendering
│   └── utils.py           # Utility functions
├── configuration/         # Configuration files
│   ├── .env              # Environment variables (secrets)
│   └── config.json       # Application configuration
├── templates/            # HTML templates
│   ├── card.html         # Mobile receipt template
│   ├── receipt.pdf.html  # PDF receipt template
│   └── receipt_form.html # Receipt form page
├── docs/                 # Documentation
├── requirements.txt      # Python dependencies
└── run.py               # Server launcher script
```

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables** in `configuration/.env`:
   - `RECEIPT_ID_GENERATION_SECRET` - Secret key for generating receipt IDs
   - `HTML2PDF_API_KEY` - API key for HTML to PDF conversion service
   - `SUPABASE_S3_ACCESS_KEY_ID` - Supabase S3 access key
   - `SUPABASE_S3_SECRET_ACCESS_KEY` - Supabase S3 secret key
   - `NEON_DATABASE_URL` - PostgreSQL database connection string

3. **Configure application settings** in `configuration/config.json`:
   - Adjust URLs, endpoints, and bucket names as needed

4. **Initialize the database:**
```python
# Run Python shell from project root
python
>>> from sys import path
>>> path.insert(0, 'app')
>>> from db import DBManager
>>> from config import Config
>>> config = Config()
>>> db = DBManager(config)
>>> db.create_receipts_table()
>>> exit()
```

## Running the Server

**Method 1: Using the run script (recommended)**
```bash
python run.py
```

**Method 2: Using uvicorn directly**
```bash
cd app
uvicorn server:app --reload --port 8000
```

The server will start at http://localhost:8000

## API Endpoints

- `GET /` - Receipt form page
- `POST /generate-mobile-receipt` - Generate a new receipt
  - Request body: `{ "sender_name", "receiver_name", "sender_account", "receiver_account", "amount", "vat", "commission" }`
  - Returns: HTML mobile receipt view
- `GET /receipts/pdf/{receipt_id}` - Get receipt PDF (redirects to S3 URL)
- `GET /receipts/mobile/{receipt_id}` - Get mobile receipt view

## Features

- ✅ FastAPI-based REST API
- ✅ PostgreSQL database with Neon
- ✅ S3-compatible storage with Supabase
- ✅ HTML to PDF conversion
- ✅ SHA256-based receipt ID generation
- ✅ Mobile and PDF receipt templates
- ✅ QR code integration
- ✅ VAT and commission calculation

## Configuration

### Environment Variables (.env)
Sensitive credentials that should never be committed to version control.

### Configuration JSON (config.json)
Non-sensitive application settings that can be version controlled.

## Development

The application uses:
- **FastAPI** - Modern web framework
- **psycopg2** - PostgreSQL adapter
- **boto3** - AWS S3 SDK (compatible with Supabase)
- **requests** - HTTP library for PDF API calls
- **python-dotenv** - Environment variable management
