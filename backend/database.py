import os
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./salon_bookings.db")

# Neon/Postgres URLs often start with postgres://, which SQLAlchemy requires as postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure engine parameters depending on SQLite vs PostgreSQL (Neon)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_phone = Column(String, index=True)
    customer_name = Column(String, nullable=True)
    service_name = Column(String)
    appointment_time = Column(String)
    total_price = Column(Float)
    deposit_amount = Column(Float, default=20.0)
    deposit_paid = Column(Boolean, default=False)
    stripe_session_id = Column(String, nullable=True)
    status = Column(String, default="pending_deposit") # pending_deposit, confirmed, cancelled
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def create_booking_record(phone: str, service: str, appt_time: str, total_price: float, deposit: float = 20.0, name: str = None) -> Booking:
    session = SessionLocal()
    try:
        booking = Booking(
            customer_phone=phone,
            customer_name=name,
            service_name=service,
            appointment_time=appt_time,
            total_price=total_price,
            deposit_amount=deposit,
            status="pending_deposit"
        )
        session.add(booking)
        session.commit()
        session.refresh(booking)
        return booking
    finally:
        session.close()

def mark_deposit_paid(booking_id: int, stripe_session_id: str = None):
    session = SessionLocal()
    try:
        booking = session.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            booking.deposit_paid = True
            booking.status = "confirmed"
            if stripe_session_id:
                booking.stripe_session_id = stripe_session_id
            session.commit()
            return booking
        return None
    finally:
        session.close()
