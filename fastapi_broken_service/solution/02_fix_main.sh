#!/bin/bash

set -euo pipefail

cat > /app/main.py <<'PY'
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from models import Base, Payment
from schemas import PaymentRequest, PaymentResponse


DATABASE_URL = "sqlite:////app/data.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fixed Idempotent Payments")


@app.post("/payments")
def create_payment(
    payload: PaymentRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")

    idempotency_key = idempotency_key.strip()
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")

    db = SessionLocal()
    try:
        existing_payment = (
            db.query(Payment)
            .filter(Payment.idempotency_key == idempotency_key)
            .first()
        )
        if existing_payment:
            if existing_payment.amount != payload.amount:
                raise HTTPException(
                    status_code=409,
                    detail="idempotency_key_reused_with_different_payload",
                )
            response_body = PaymentResponse.model_validate(existing_payment).model_dump(by_alias=True)
            return JSONResponse(status_code=200, content=response_body)

        payment = Payment(
            idempotency_key=idempotency_key,
            amount=payload.amount,
            status="succeeded",
        )
        db.add(payment)
        db.flush()
        db.commit()
        db.refresh(payment)

        response_body = PaymentResponse.model_validate(payment).model_dump(by_alias=True)
        return JSONResponse(status_code=201, content=response_body)
    except IntegrityError:
        db.rollback()
        existing_payment = (
            db.query(Payment)
            .filter(Payment.idempotency_key == idempotency_key)
            .first()
        )
        if existing_payment and existing_payment.amount == payload.amount:
            response_body = PaymentResponse.model_validate(existing_payment).model_dump(by_alias=True)
            return JSONResponse(status_code=200, content=response_body)
        raise HTTPException(
            status_code=409,
            detail="idempotency_key_reused_with_different_payload",
        )
    finally:
        db.close()
PY
