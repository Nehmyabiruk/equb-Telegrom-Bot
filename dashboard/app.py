"""
Ethio Car Equb — Admin Dashboard API
Serves approved participants to the frontend and generates PDF exports.
"""

from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, joinedload

from config import DASHBOARD_PASSWORD
from database import get_db
from models import Payment, User
from pdf_generator import generate_approved_users_pdf

STATIC_DIR = Path(__file__).parent / "static"


def get_db_session():
    db = get_db()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title="Ethio Car Equb Dashboard",
    description="Admin dashboard for approved Equb participants",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _participant_payload(payment: Payment) -> dict:
    user = payment.user
    # Prefer participant_name stored on the payment (snapshot), fall back to user name
    participant_name = (
        payment.participant_name
        if getattr(payment, "participant_name", None)
        else (user.participant_name if user else "—")
    )
    # Prefer phone stored on the payment (snapshot) to avoid showing the
    # current user phone which may have changed since approval.
    phone = (
        payment.participant_phone
        if getattr(payment, "participant_phone", None)
        else (user.phone if user else "—")
    )

    return {
        "id": payment.id,
        "participant_number": payment.participant_number,
        "participant_name": participant_name,
        "phone": phone,
        "telegram_username": user.telegram_username if user else None,
        "language": user.language if user else "—",
        "payment_method": payment.payment_method,
        "payment_for": payment.payment_for,
        "transaction_reference": payment.transaction_reference,
        "status": payment.status,
        "verified_at": payment.verified_at.isoformat()
        if payment.verified_at
        else None,
        "created_at": payment.created_at.isoformat()
        if payment.created_at
        else None,
    }


def _get_approved_payments(db: Session) -> list[Payment]:
    return (
        db.query(Payment)
        .options(joinedload(Payment.user))
        .filter(Payment.status == "APPROVED")
        # Order by approval time ascending so the first-approved user stays at
        # the top and new approvals are appended after (first-approved first).
        .order_by(Payment.verified_at.asc())
        .all()
    )


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db_session)):
    approved = db.query(Payment).filter(Payment.status == "APPROVED").count()
    rejected = db.query(Payment).filter(Payment.status == "REJECTED").count()
    pending = db.query(Payment).filter(Payment.status == "PENDING").count()
    total_users = db.query(User).count()

    return {
        "approved": approved,
        "rejected": rejected,
        "pending": pending,
        "total_users": total_users,
        "updated_at": datetime.utcnow().isoformat(),
    }


@app.get("/api/approved-users")
def get_approved_users(db: Session = Depends(get_db_session)):
    payments = _get_approved_payments(db)
    return {
        "count": len(payments),
        "participants": [_participant_payload(payment) for payment in payments],
        "updated_at": datetime.utcnow().isoformat(),
    }


@app.get("/api/rejected-users")
def get_rejected_users(db: Session = Depends(get_db_session)):
    payments = (
        db.query(Payment)
        .options(joinedload(Payment.user))
        .filter(Payment.status == "REJECTED")
        .order_by(Payment.verified_at.desc())
        .all()
    )
    return {
        "count": len(payments),
        "participants": [_participant_payload(payment) for payment in payments],
    }


@app.get("/api/download-pdf")
def download_pdf(password: str | None = None, db: Session = Depends(get_db_session)):
    if DASHBOARD_PASSWORD and password != DASHBOARD_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid dashboard password")

    payments = _get_approved_payments(db)
    participants = [_participant_payload(payment) for payment in payments]
    pdf_buffer = generate_approved_users_pdf(participants)

    filename = (
        f"ethio-car-equb-approved-"
        f"{datetime.utcnow().strftime('%Y%m%d-%H%M')}.pdf"
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/")
def serve_dashboard():
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return FileResponse(index_path)


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
