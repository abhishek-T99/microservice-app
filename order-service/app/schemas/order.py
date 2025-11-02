from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.order import OrderStatus


class OrderBase(BaseModel):
    user_id: int
    product_name: str
    quantity: int = Field(gt=0)
    total_price: float = Field(gt=0)


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    product_name: Optional[str] = None
    quantity: Optional[int] = Field(None, gt=0)
    total_price: Optional[float] = Field(None, gt=0)
    status: Optional[OrderStatus] = None


class OrderResponse(OrderBase):
    id: int
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class OrderEvent(BaseModel):
    event_type: str
    order_id: int
    user_id: int
    status: OrderStatus
    timestamp: datetime


class UserEventMessage(BaseModel):
    event_type: str
    user_id: int
    user_email: str
    username: str
    timestamp: datetime
