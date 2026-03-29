from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    idempotency_key = Column(String, nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="succeeded")


class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"

    id = Column(Integer, primary_key=True)
    idempotency_key = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    error = Column(String, nullable=True)
