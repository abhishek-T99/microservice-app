from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate, OrderUpdate


class OrderRepository:
    """Repository pattern for Order data access - Single Responsibility Principle"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, order_id: int) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).first()
    
    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        return self.db.query(Order).filter(Order.user_id == user_id).offset(skip).limit(limit).all()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        return self.db.query(Order).offset(skip).limit(limit).all()
    
    def create(self, order_data: OrderCreate) -> Order:
        db_order = Order(**order_data.model_dump())
        self.db.add(db_order)
        self.db.commit()
        self.db.refresh(db_order)
        return db_order
    
    def update(self, order: Order, order_data: OrderUpdate) -> Order:
        update_data = order_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def delete(self, order: Order) -> bool:
        self.db.delete(order)
        self.db.commit()
        return True
    
    def get_by_status(self, status: OrderStatus, skip: int = 0, limit: int = 100) -> List[Order]:
        return self.db.query(Order).filter(Order.status == status).offset(skip).limit(limit).all()