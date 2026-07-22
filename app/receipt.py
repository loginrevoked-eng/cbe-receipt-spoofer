import hashlib
import time
import requests
from datetime import datetime
from .templates import HTMLMobileReceiptTemplate, HTMLPDFReceiptTemplate
from .config import Config

class Receipt:
    def __init__(self, config:Config, **kwargs):
        self.receipt_id:str = kwargs.get("receipt_id", "")
        self.sender_name:str = kwargs.get("sender_name", "")
        self.receiver_name:str = kwargs.get("receiver_name", "")
        self.sender_account:str = kwargs.get("sender_account", "")
        self.receiver_account:str = kwargs.get("receiver_account", "")
        self.txn_qrcode_url:str = kwargs.get("txn_qrcode_url", "")
        self.txn_pdf_url:str = kwargs.get("txn_pdf_url", "")
        self.amount:float = kwargs.get("amount", 0.0)
        self.epoch_time:int = kwargs.get("epoch_time", 0)
        self.vat:float = kwargs.get("vat", 0.0)
        self.commission:float = kwargs.get("commission", 0.0)
        self.total_amount:float = kwargs.get("total_amount", 0.0)
        self.config = config


        self.post_init()

    def kwargs_init(self, **kwargs):
        self.receipt_id = kwargs.get("receipt_id", "")
        self.sender_name = kwargs.get("sender_name", "")
        self.receiver_name = kwargs.get("receiver_name", "")
        self.sender_account = kwargs.get("sender_account", "")
        self.receiver_account = kwargs.get("receiver_account", "")
        self.txn_qrcode_url = kwargs.get("txn_qrcode_url", "")
        self.txn_pdf_url = kwargs.get("txn_pdf_url", "")
        self.amount = kwargs.get("amount", 0.0)
        self.epoch_time = kwargs.get("epoch_time", 0)
        self.vat = kwargs.get("vat", 0.0)
        self.commission = kwargs.get("commission", 0.0)
        self.total_amount = kwargs.get("total_amount", 0.0)

    def post_init(self):
        pdf_baseurl = self.config.pdf_baseurl
        qrcode_baseurl = self.config.qrcode_baseurl
        qrcode_size = self.config.qr_code_size
        self.txn_pdf_url = f"{pdf_baseurl}/{self.receipt_id}.pdf"
        self.txn_qrcode_url = f"{qrcode_baseurl}/?data={self.txn_pdf_url}"
    
    def to_dict(self) -> dict[str, str | float | int]:
        return {
            "receipt_id": self.receipt_id,
            "sender_name": self.sender_name,
            "receiver_name": self.receiver_name,
            "sender_account": self.sender_account,
            "receiver_account": self.receiver_account,
            "txn_qrcode_url": self.txn_qrcode_url,
            "txn_pdf_url": self.txn_pdf_url,
            "amount": self.amount,
            "epoch_time": self.epoch_time,
            "vat": self.vat,
            "commission": self.commission,
            "total_amount": self.total_amount,
        }
    
    def pdf_html_template(self) -> str:
        template = HTMLPDFReceiptTemplate(
            template_path=self.config.receipt_pdf_html_template_filename,
            sender=self.sender_name,
            receiver=self.receiver_name,
            amount=self.amount,
            date=datetime.fromtimestamp(self.epoch_time).strftime("%d-%b-%Y"),
            receipt_id=self.receipt_id,
            qr_code_img_src=self.txn_qrcode_url,
            receipt_pdf_url=self.txn_pdf_url,
            vat=self.vat,
            commission=self.commission,
            total_amount=self.total_amount,
            sender_account=self.sender_account,
            receiver_account=self.receiver_account,
        )
        return template.render()
    
    def mobile_html_template(self) -> str:
        template = HTMLMobileReceiptTemplate(   
            template_path=self.config.mobile_receipt_html_template_filename,
            sender=self.sender_name,
            receiver=self.receiver_name,
            amount=self.amount,
            date=datetime.fromtimestamp(self.epoch_time).strftime("%d-%b-%Y"),
            receipt_id=self.receipt_id,
            qr_code_img_src=self.txn_qrcode_url,
            receipt_pdf_url=self.txn_pdf_url,
            vat=self.vat,
            commission=self.commission,
            total_amount=self.total_amount,
            sender_account=self.sender_account,
            receiver_account=self.receiver_account,
        )
        return template.render()
    
    def generate_receipt_id(self, secret:str=None):
        secret = secret or self.config.credentials.receipt_id_generation_secret
        self.receipt_id = hashlib.sha256(
            f"{secret}_{int(time.time())}".encode()
        ).hexdigest()[:16].upper()
        self.post_init()
        return self.receipt_id
    
    def to_pdf(self, pdf_filepath: str=None, html_template: str = None) -> bytes:
        if not self.config.commands.generate_pdfs:
            return "config-disallowed-it"
        try:
            pdf_filepath = pdf_filepath or f"{self.receipt_id}.pdf"
            html_template = html_template or self.pdf_html_template()
            response = requests.post(
                self.config.html2pdf_api_url,
                data={"apikey": self.config.credentials.html2pdf_api_key, "value": html_template},
            )
            response.raise_for_status()
            with open(pdf_filepath, "wb") as f:
                f.write(response.content)
            print(f"PDF generated: {pdf_filepath}")
            return pdf_filepath
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None
    
    def to_mobile(self) -> str:
        return self.mobile_html_template()
    


