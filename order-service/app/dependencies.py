from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.order_repository import OrderRepository
from app.services.order_service import OrderService
from app.messaging.publisher import MessagePublisher


def get_order_repository(db: Session = Depends(get_db)) -> OrderRepository:
    return OrderRepository(db)


def get_message_publisher() -> MessagePublisher:
    return MessagePublisher()


def get_order_service(
    repository: OrderRepository = Depends(get_order_repository),
    publisher: MessagePublisher = Depends(get_message_publisher)
) -> OrderService:
    return OrderService(repository, publisher)