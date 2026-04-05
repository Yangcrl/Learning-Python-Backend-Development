from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class OrderBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    total_amount: float


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: Optional[str] = None


class OrderResponse(OrderBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
