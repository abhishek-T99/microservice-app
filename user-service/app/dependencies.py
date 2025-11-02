from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.messaging.publisher import MessagePublisher


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_message_publisher() -> MessagePublisher:
    return MessagePublisher()


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
    publisher: MessagePublisher = Depends(get_message_publisher)
) -> UserService:
    return UserService(repository, publisher)