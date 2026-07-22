from dataclasses import dataclass, field
from dotenv import load_dotenv
import os
import json
from typing import List

@dataclass
class Credentials:
    receipt_id_generation_secret: str = None
    html2pdf_api_key: str = None
    supabase_s3_access_key_id: str = None
    supabase_s3_secret_access_key: str = None
    neon_database_url: str = None

    def load(self, env_filepath:str):
        load_dotenv(env_filepath)
        
        self.receipt_id_generation_secret = os.getenv("RECEIPT_ID_GENERATION_SECRET", self.receipt_id_generation_secret)
        self.html2pdf_api_key = os.getenv("HTML2PDF_API_KEY", self.html2pdf_api_key)
        self.supabase_s3_access_key_id = os.getenv("SUPABASE_S3_ACCESS_KEY_ID", self.supabase_s3_access_key_id)
        self.supabase_s3_secret_access_key = os.getenv("SUPABASE_S3_SECRET_ACCESS_KEY", self.supabase_s3_secret_access_key)
        self.neon_database_url = os.getenv("NEON_DATABASE_URL", self.neon_database_url)
        self.validate()
        return self
    
    def validate(self):
        not_set : List[str] = []
        for attr in [
            "RECEIPT_ID_GENERATION_SECRET", 
            "HTML2PDF_API_KEY", 
            "SUPABASE_S3_ACCESS_KEY_ID", 
            "SUPABASE_S3_SECRET_ACCESS_KEY", 
            "NEON_DATABASE_URL"
        ]:
            if getattr(self, attr.lower(), None) is None:
                not_set.append(attr)
        if not_set:
            raise ValueError(f"The following credentials are not set: {', '.join(not_set)}")


@dataclass
class CommandConfig:
    generate_pdfs:bool=False
    outsource_pdf:bool=True
    
    def load(self, json_filepath:str):
        return self.from_json(json_filepath)
    
    def from_dict(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)   

    def from_json(self, json_filename: str):
        with open(json_filename, "r") as f:
            data = json.load(f)
            self.from_dict(**data)
        return self

@dataclass
class Config:
    self_domain: str = "localhost"
    mobile_receipt_gen_endpoint: str = "/generate-mobile-receipt"
    qr_code_size: str = "150x150"
    pdf_baseurl: str = "https://%DOMAIN%/receipts/pdf"
    qrcode_baseurl: str = "https://api.qrserver.com/v1/create-qr-code"
    mobile_receipt_html_template_filename: str = None
    receipt_pdf_html_template_filename: str = None
    html2pdf_api_url: str = "https://api.html2pdfrocket.com/pdf"
    supabase_s3_bucket_name: str = "receipt_pdfs"
    supabase_s3_endpoint_url_s3: str = "https://imjyodtjkxfeuduamnab.storage.supabase.co/storage/v1/s3"
    supabase_s3_aws_region: str = "us-east-2"
    receipts_db_table: str = "receipts"
    receipt_form_html_filename: str = None
    credentials: Credentials = field(default_factory=lambda: Credentials().load("configuration/.env"))
    commands:CommandConfig=field(default_factory=lambda: CommandConfig().load("configuration/command-config.json"))

    def __post_init__(self):
        self.pdf_baseurl = self.pdf_baseurl.replace("%DOMAIN%", self.self_domain)

    def from_dict(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def from_json(self, json_filename: str):
        with open(json_filename, "r") as f:
            data = json.load(f)
            self.from_dict(**data)
        return self
