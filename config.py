import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv(
    "BOT_TOKEN"
)

ADMIN_ID = int(
    os.getenv("ADMIN_ID")
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/ethio_car_equb"
)

DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "127.0.0.1")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8000"))
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "")
CBE_ACCOUNT_NAME = os.getenv("CBE_ACCOUNT_NAME")
CBE_ACCOUNT_NUMBER = os.getenv("CBE_ACCOUNT_NUMBER")

TELEBIRR_ACCOUNT_NAME = os.getenv("TELEBIRR_ACCOUNT_NAME")
TELEBIRR_PHONE = os.getenv("TELEBIRR_PHONE")
EQUB_AMOUNT = os.getenv(
    "EQUB_AMOUNT"
)