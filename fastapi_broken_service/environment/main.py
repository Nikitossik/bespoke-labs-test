from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Payment
from schemas import PaymentRequest, PaymentResponse


DATABASE_URL = "sqlite:////app/data.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Broken Idempotent Payments")


@app.post("/payments")
def create_payment(
	payload: PaymentRequest,
	idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
	if not idempotency_key:
		raise HTTPException(status_code=400, detail="Idempotency-Key header is required")

	db = SessionLocal()
	try:
		lookup_key = getattr(payload, "idempotency_key", None)
		existing_payment = (
			db.query(Payment)
			.filter(Payment.idempotency_key == lookup_key)
			.first()
		)

		if existing_payment:
			response_body = PaymentResponse.model_validate(existing_payment).model_dump(by_alias=True)
			return JSONResponse(status_code=200, content=response_body)

		payment = Payment(
			idempotency_key=idempotency_key,
			amount=payload.amount,
			status="succeeded",
		)
		db.add(payment)
		db.commit()
		db.refresh(payment)

		response_body = PaymentResponse.model_validate(payment).model_dump(by_alias=True)
		return JSONResponse(status_code=201, content=response_body)
	finally:
		db.close()
