"""
Add new columns to existing database tables.
Run once after upgrading: python migrate_db.py
"""

from sqlalchemy import inspect, text

from database import engine


def column_exists(table: str, column: str) -> bool:
    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns(table)]
    return column in columns


def migrate():
    with engine.connect() as conn:
        if not column_exists("payments", "payment_for"):
            conn.execute(
                text("ALTER TABLE payments ADD COLUMN payment_for VARCHAR(20)")
            )
            print("Added payments.payment_for")

        if not column_exists("payments", "participant_number"):
            conn.execute(
                text(
                    "ALTER TABLE payments ADD COLUMN participant_number INTEGER"
                )
            )
            print("Added payments.participant_number")

        if not column_exists("payments", "participant_name"):
            conn.execute(
                text(
                    "ALTER TABLE payments ADD COLUMN participant_name VARCHAR(100)"
                )
            )
            print("Added payments.participant_name")

        if not column_exists("payments", "participant_phone"):
            conn.execute(
                text(
                    "ALTER TABLE payments ADD COLUMN participant_phone VARCHAR(30)"
                )
            )
            print("Added payments.participant_phone")

        conn.commit()

    print("Migration complete.")


if __name__ == "__main__":
    migrate()
