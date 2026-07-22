from io import BytesIO
import segno


class QRGen:

    def __init__(self, ecorr: str = "H", out_kind: str = "png"):
        self.ecorr = ecorr
        self.out_kind = out_kind

    def asbytes(self, data: str = "https://pornhub.com"):
        buffer = BytesIO()
        qrcode = segno.make(data, error=self.ecorr)
        qrcode.save(buffer, kind=self.out_kind, scale=10, border=4)
        return buffer.getvalue()
