
import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from s3 import S3Client
from db import DBManager
from config import Config
from receipt import Receipt, receipt

config = Config()
s3_client = S3Client(config=config)
db_manager = DBManager(config=config)

app = FastAPI()



@app.get("/")
def get_receipt_form():
    return FileResponse(config.receipt_form_html_filename)

@app.post(config.mobile_receipt_gen_endpoint)
async def generate_mobile_receipt(req:Request):
    body = await req.json()
    receipt = Receipt(config,
        sender_name=body.get("sender_name", "NULL"),
        receiver_name=body.get("receiver_name", "NULL"),
        sender_account=body.get("sender_account", ""),
        receiver_account=body.get("receiver_account", ""),
        amount=body.get("amount", 0.0),
        epoch_time=int(datetime.datetime.now().timestamp()),
        total_amount=body.get("amount", 0.0),
    )
    receipt.generate_receipt_id()
    pdf_txn, mobile_txn = receipt.pdf_html_template(), receipt.mobile_html_template()
    pdf_filename = receipt.to_pdf(html_template=pdf_txn)
    if pdf_filename is None:
        return HTTPException(status_code=500, detail="Failed to generate PDF")
    s3_client.upload_file(pdf_filename)
    db_manager.save_receipt(receipt_id=receipt.receipt_id, **receipt.to_dict())
    return HTMLResponse(content=mobile_txn, status_code=200)









@app.get("/receipts/pdf/{receipt_id}")
def get_pdf_receipt(receipt_id: str):
    direct_s3_pdf_url = s3_client.direct_url(f"{receipt_id}.pdf")
    
    if not direct_s3_pdf_url:
        raise HTTPException(status_code=404, detail="Receipt PDF not found")
        
    return RedirectResponse(url=direct_s3_pdf_url, status_code=307)


@app.get("/receipts/mobile/{receipt_id}", response_class=HTMLResponse)
def get_mobile_receipt(receipt_id: str):
    receipt = db_manager.fetch_receipt(receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt data not found")
    return receipt.mobile_html_template()
