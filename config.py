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

# Render supplies PORT at runtime. DASHBOARD_PORT remains supported for local use.
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
DASHBOARD_PORT = int(os.getenv("PORT", os.getenv("DASHBOARD_PORT", "8000")))
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
CBE_ACCOUNT_NAME = os.getenv("CBE_ACCOUNT_NAME")
CBE_ACCOUNT_NUMBER = os.getenv("CBE_ACCOUNT_NUMBER")

TELEBIRR_ACCOUNT_NAME = os.getenv("TELEBIRR_ACCOUNT_NAME")
TELEBIRR_PHONE = os.getenv("TELEBIRR_PHONE")
EQUB_AMOUNT = os.getenv(
    "EQUB_AMOUNT"
)
