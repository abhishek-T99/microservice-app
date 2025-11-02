from typing import List, Optional
from datetime import datetime
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserEvent
from app.messaging.publisher import MessagePublisher
from fastapi import HTTPException, status
import redis
import logging
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class UserService:
    """Business logic for User operations - Single Responsibility Principle"""
    
    def __init__(self, repository: UserRepository, publisher: MessagePublisher):
        self.repository = repository
        self.publisher = publisher
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        self.cache_ttl = 300  # 5 minutes
    
    def _get_cache_key(self, user_id: int) -> str:
        return f"user:{user_id}"
    
    def _cache_user(self, user: UserResponse):
        try:
            cache_key = self._get_cache_key(user.id)
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                user.model_dump_json()
            )
            logger.debug(f"Successfully cached user {user.id}")
        except redis.RedisError as e:
            logger.error(f"Failed to cache user {user.id}: {str(e)}")
    
    def _get_cached_user(self, user_id: int) -> Optional[UserResponse]:
        try:
            cache_key = self._get_cache_key(user_id)
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for user {user_id}")
                return UserResponse.model_validate_json(cached)
            logger.debug(f"Cache miss for user {user_id}")
            return None
        except redis.RedisError as e:
            logger.error(f"Failed to get user {user_id} from cache: {str(e)}")
            return None
    
    def _invalidate_cache(self, user_id: int):
        try:
            cache_key = self._get_cache_key(user_id)
            self.redis_client.delete(cache_key)
            logger.debug(f"Successfully invalidated cache for user {user_id}")
        except redis.RedisError as e:
            logger.error(f"Failed to invalidate cache for user {user_id}: {str(e)}")
    
    def get_user(self, user_id: int) -> UserResponse:
        # Try cache first
        cached_user = self._get_cached_user(user_id)
        if cached_user:
            return cached_user
        
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_response = UserResponse.model_validate(user)
        self._cache_user(user_response)
        return user_response
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        users = self.repository.get_all(skip, limit)
        return [UserResponse.model_validate(user) for user in users]
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        # Check if user exists
        if self.repository.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if self.repository.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create user
        user = self.repository.create(user_data)
        user_response = UserResponse.model_validate(user)
        
        # Cache user
        self._cache_user(user_response)
        
        # Publish event
        event = UserEvent(
            event_type="user.created",
            user_id=user.id,
            user_email=user.email,
            username=user.username,
            timestamp=datetime.utcnow()
        )
        self.publisher.publish_user_event(event)
        
        return user_response
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check email uniqueness if updating
        if user_data.email and user_data.email != user.email:
            if self.repository.get_by_email(user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Check username uniqueness if updating
        if user_data.username and user_data.username != user.username:
            if self.repository.get_by_username(user_data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        updated_user = self.repository.update(user, user_data)
        user_response = UserResponse.model_validate(updated_user)
        
        # Invalidate and update cache
        self._invalidate_cache(user_id)
        self._cache_user(user_response)
        
        # Publish event
        event = UserEvent(
            event_type="user.updated",
            user_id=updated_user.id,
            user_email=updated_user.email,
            username=updated_user.username,
            timestamp=datetime.utcnow()
        )
        self.publisher.publish_user_event(event)
        
        return user_response
    
    def delete_user(self, user_id: int) -> dict:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Publish event before deletion
        event = UserEvent(
            event_type="user.deleted",
            user_id=user.id,
            user_email=user.email,
            username=user.username,
            timestamp=datetime.utcnow()
        )
        self.publisher.publish_user_event(event)
        
        self.repository.delete(user)
        self._invalidate_cache(user_id)
        
        return {"message": "User deleted successfully"}
