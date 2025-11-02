from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())