from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    DateTime,
    ForeignKey,
    Text,
)

from sqlalchemy.orm import relationship

from database import Base


# =========================================================
# USER MODEL
# =========================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    telegram_id = Column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True
    )

    telegram_username = Column(
        String(255),
        nullable=True
    )

    language = Column(
        String(10),
        nullable=False,
        default="am"
    )

    participant_name = Column(
        String(100),
        nullable=False
    )

    phone = Column(
        String(30),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship with payments
    payments = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# =========================================================
# PAYMENT MODEL
# =========================================================

class Payment(Base):

    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    payment_method = Column(
        String(50),
        nullable=False
    )

    receipt_path = Column(
        Text,
        nullable=False
    )

    transaction_reference = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    participant_name = Column(
        String(100),
        nullable=True
    )

    participant_phone = Column(
        String(30),
        nullable=True
    )

    payment_for = Column(
        String(20),
        nullable=True
    )

    participant_number = Column(
        Integer,
        nullable=True,
        index=True
    )

    status = Column(
        String(30),
        nullable=False,
        default="PENDING",
        index=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    verified_at = Column(
        DateTime,
        nullable=True
    )

    rejection_reason = Column(
        Text,
        nullable=True
    )

    # Relationship with user
    user = relationship(
        "User",
        back_populates="payments"
    )