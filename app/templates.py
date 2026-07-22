from .utils import Utils
from .config import Config

class HTMLMobileReceiptTemplate:
    def __init__(self, config:Config, template_path:str=None, **kwargs):
        self.sender = kwargs.get('sender', 'N/A')
        self.receiver = kwargs.get('receiver', 'N/A')
        self.amount = kwargs.get('amount', '0.00')
        self.date = kwargs.get('date', '')
        self.receipt_id = kwargs.get('receipt_id', '')
        self.qr_code_img_src = kwargs.get('qr_code_img_src', '')
        self.receipt_pdf_url = kwargs.get('receipt_pdf_url', '#')
        self.vat = kwargs.get('vat', 15)
        self.commission = kwargs.get('commission', 0.0)
        self.total_amount = kwargs.get('total_amount', self.amount)
        self.config = config
        
        self.template_html = self.read_template(template_path)

    def read_template(self, template_path:str):
        with open(template_path, "r") as f:
            return f.read()
    
    def render(self):
        vat_amount = float(self.commission) * (float(self.vat) / 100) if self.commission else 0.0
        message = [
            f"ETB {self.amount} debited from {self.sender}",
            f"for {self.receiver} on {self.date}",
            f"with transaction ID: {self.receipt_id}",
            f"Total Amount Debited ETB {self.total_amount}", 
            f"with commission of ETB {self.commission} and",
            f"{self.vat}% VAT of ETB {vat_amount:.2f}"
        ]
        return (self.template_html
                .replace('%MESSAGE%', " ".join(message))
                .replace('%QR_CODE_IMG_SRC%', self.qr_code_img_src)
                .replace('%RECEIPT_PDF_URL%', self.receipt_pdf_url)
        )


class HTMLPDFReceiptTemplate:
    def __init__(self, config:Config, template_path:str=None, **kwargs):
        self.sender = kwargs.get('sender', 'N/A')
        self.receiver = kwargs.get('receiver', 'N/A')
        self.amount = kwargs.get('amount', '0.00')
        self.date = kwargs.get('date', '')
        self.receipt_id = kwargs.get('receipt_id', '')
        self.qr_code_img_src = kwargs.get('qr_code_img_src', '')
        self.vat = kwargs.get('vat', 15)
        self.commission = kwargs.get('commission', 0.0)
        self.total_amount = kwargs.get('total_amount', self.amount)
        self.sender_account = kwargs.get('sender_account', '')
        self.receiver_account = kwargs.get('receiver_account', '')
        self.config = config

        self.template_path = template_path
        self.template_html = self.read_template(template_path)

    def read_template(self, template_path:str):
        with open(template_path, "r") as f:
            return f.read()
    



    
    def render(self):
        sender_account = Utils.mask_account(self.sender_account)
        receiver_account = Utils.mask_account(self.receiver_account)
        vat_amount = float(self.commission) * (float(self.vat) / 100) if self.commission else 0.0
        amount_words = Utils.numtoword(self.total_amount)
        return (self.template_html
            .replace("%ASSETS_ENDPOINT%", f"https://{self.config.self_domain}/assets")
            .replace('%RECEIPT_ID%', self.receipt_id)
            .replace('%SENDER%', self.sender)
            .replace('%SENDER_ACCOUNT%', sender_account)
            .replace('%RECEIVER%', self.receiver)
            .replace('%RECEIVER_ACCOUNT%', receiver_account)
            .replace('%DATE%', self.date)
            .replace('%AMOUNT%', str(self.amount))
            .replace('%COMMISSION%', str(self.commission))
            .replace('%VAT%', str(self.vat))
            .replace('%VAT_AMOUNT%', f"{vat_amount:.2f}")
            .replace('%TOTAL_AMOUNT%', str(self.total_amount))
            .replace('%AMOUNT_WORDS%', amount_words)
            .replace('%QR_CODE_IMG_SRC%', self.qr_code_img_src))


