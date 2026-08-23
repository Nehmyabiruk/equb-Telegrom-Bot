"""Copy the existing local SQLite data to the DATABASE_URL Postgres database.

Run this once from your computer after creating Supabase Postgres and setting
DATABASE_URL in your local .env to Supabase's Session Pooler connection URL:

    python migrate_sqlite_to_postgres.py
"""

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, func, inspect, select
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session

from config import DATABASE_URL
from database import Base
from models import Payment, User  # Registers both tables with Base.metadata.

# The real local database is two folders above this script. The `car_equb.db`
# beside this script can be an empty database created during local testing.
DEFAULT_SOURCE_PATH = Path(__file__).resolve().parents[2] / "ethio_car_equb.db"


def main() -> None:
    if not DATABASE_URL.startswith("postgresql"):
        sys.exit("DATABASE_URL must be your Supabase PostgreSQL connection URL before running this script.")

    source_path = Path(
        os.getenv("SOURCE_SQLITE_PATH", str(DEFAULT_SOURCE_PATH))
    ).expanduser().resolve()
    if not source_path.is_file():
        sys.exit(f"SQLite database not found: {source_path}")

    source_engine = create_engine(URL.create("sqlite", database=str(source_path)))
    source_tables = set(inspect(source_engine).get_table_names())
    if not {"users", "payments"}.issubset(source_tables):
        sys.exit(
            f"{source_path} does not contain the required users and payments tables. "
            "Set SOURCE_SQLITE_PATH to the database that contains your bot data."
        )

    destination_engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
    Base.metadata.create_all(destination_engine)

    with Session(source_engine) as source, Session(destination_engine) as destination:
        existing_users = destination.scalar(select(func.count()).select_from(User))
        existing_payments = destination.scalar(select(func.count()).select_from(Payment))
        if existing_users or existing_payments:
            sys.exit("Destination database is not empty. Stopping to prevent duplicate data.")

        users = source.scalars(select(User)).all()
        payments = source.scalars(select(Payment)).all()

        for user in users:
            destination.add(
                User(
                    id=user.id,
                    telegram_id=user.telegram_id,
                    telegram_username=user.telegram_username,
                    language=user.language,
                    participant_name=user.participant_name,
                    phone=user.phone,
                    created_at=user.created_at,
                )
            )
        destination.flush()

        for payment in payments:
            destination.add(
                Payment(
                    id=payment.id,
                    user_id=payment.user_id,
                    payment_method=payment.payment_method,
                    receipt_path=payment.receipt_path,
                    transaction_reference=payment.transaction_reference,
                    participant_name=payment.participant_name,
                    participant_phone=payment.participant_phone,
                    payment_for=payment.payment_for,
                    participant_number=payment.participant_number,
                    status=payment.status,
                    created_at=payment.created_at,
                    verified_at=payment.verified_at,
                    rejection_reason=payment.rejection_reason,
                )
            )
        destination.commit()

    print(f"Migration complete: {len(users)} users and {len(payments)} payments copied.")


if __name__ == "__main__":
    main()
