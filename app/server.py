import os
import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from s3 import S3Client
from db import DBManager
from config import Config
from receipt import Receipt

config = Config().from_json("../configuration/config.json")
s3_client = S3Client(config=config)
db_manager = DBManager(config=config)
db_manager.create_receipts_table()

app = FastAPI()



@app.get("/")
def get_receipt_form():
    return FileResponse(config.receipt_form_html_filename)

from fastapi import Query

@app.get(config.mobile_receipt_gen_endpoint)
async def generate_mobile_receipt(
    sender_name: str = Query("NULL"),
    receiver_name: str = Query("NULL"),
    sender_account: str = Query(""),
    receiver_account: str = Query(""),
    amount: float = Query(0.0),
    vat: float = Query(0.0),
    commission: float = Query(0.0),
):
    receipt_obj = Receipt(config,
        sender_name=sender_name,
        receiver_name=receiver_name,
        sender_account=sender_account,
        receiver_account=receiver_account,
        amount=amount,
        epoch_time=int(datetime.datetime.now().timestamp()),
        total_amount=amount,
        vat=vat,
        commission=commission,
    )
    receipt_obj.generate_receipt_id()
    pdf_txn, mobile_txn = receipt_obj.pdf_html_template(), receipt_obj.mobile_html_template()
    pdf_filename = receipt_obj.to_pdf(html_template=pdf_txn)
    if pdf_filename is None:
        raise HTTPException(status_code=500, detail="Failed to generate PDF")
    if pdf_filename != "config-disallowed-it":
        s3_client.upload_file(pdf_filename)
        os.remove(pdf_filename)
    db_manager.save_receipt(receipt_obj)
    return HTMLResponse(content=mobile_txn, status_code=200)









@app.get("/receipts/pdf/{receipt_id}")
def get_pdf_receipt(receipt_id: str):
    direct_s3_pdf_url = s3_client.get_direct_url(f"{receipt_id}.pdf")
    
    if not direct_s3_pdf_url:
        raise HTTPException(status_code=404, detail="Receipt PDF not found")
        
    return RedirectResponse(url=direct_s3_pdf_url, status_code=307)


@app.get("/receipts/mobile/{receipt_id}", response_class=HTMLResponse)
def get_mobile_receipt(receipt_id: str):
    receipt_obj = db_manager.fetch_receipt(receipt_id, as_receipt=True)
    if not receipt_obj:
        raise HTTPException(status_code=404, detail="Receipt data not found")
    return receipt_obj.mobile_html_template()
