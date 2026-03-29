from pydantic import BaseModel, ConfigDict, Field


class PaymentRequest(BaseModel):
    amount: int = Field(gt=0)


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    payment_id: int = Field(validation_alias="id", serialization_alias="payment_id")
    idempotency_key: str
    amount: int
    status: str
