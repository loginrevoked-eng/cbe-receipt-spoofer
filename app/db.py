import psycopg2
from .config import Config
from .receipt import Receipt


class DBManager:
    RECEIPT_COLUMNS = {
        "receipt_id": "TEXT PRIMARY KEY",
        "sender_name": "TEXT",
        "receiver_name": "TEXT",
        "sender_account": "TEXT",
        "receiver_account": "TEXT",
        "txn_qrcode_url": "TEXT",
        "txn_pdf_url": "TEXT",
        "amount": "NUMERIC",
        "epoch_time": "BIGINT",
        "vat": "NUMERIC",
        "commission": "NUMERIC",
        "total_amount": "NUMERIC",
    }

    def __init__(self, config: Config, **kwargs):
        self.config = config
        self.db_conn = psycopg2.connect(
            kwargs.get("connection_string") or config.credentials.neon_database_url,
            connect_timeout=10)
        self.receipts_table = kwargs.get("receipts_table") or config.receipts_db_table

    def create_table(self, table_name=None, **kwargs):
        table_name = table_name or self.receipts_table
        columns = kwargs or self.RECEIPT_COLUMNS
        cols_sql = ", ".join(f"{col} {col_type}" for col, col_type in columns.items())
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({cols_sql})"

        with self.db_conn.cursor() as cur:
            cur.execute(query)
            self.db_conn.commit()

    def create_receipts_table(self):
        """Convenience wrapper that builds the table matching Receipt.to_dict()."""
        self.create_table(self.receipts_table, **self.RECEIPT_COLUMNS)

    def save_receipt(self, receipt: Receipt):
        data = receipt.to_dict()
        columns = list(data.keys())
        values = list(data.values())

        cols_sql = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))

        query = f"INSERT INTO {self.receipts_table} ({cols_sql}) VALUES ({placeholders})"

        with self.db_conn.cursor() as cur:
            cur.execute(query, values)
            self.db_conn.commit()

    def fetch_receipt(self, receipt_id, as_receipt=False):
        query = f"SELECT * FROM {self.receipts_table} WHERE receipt_id = %s"

        with self.db_conn.cursor() as cur:
            cur.execute(query, (receipt_id,))
            row = cur.fetchone()
            if row is None:
                return None
            columns = [desc[0] for desc in cur.description]

        data = dict(zip(columns, row))
        return Receipt(self.config, **data) if as_receipt else data