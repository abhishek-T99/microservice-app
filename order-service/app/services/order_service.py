from typing import List, Optional
from datetime import datetime
import httpx
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderEvent
from app.models.order import OrderStatus
from app.messaging.publisher import MessagePublisher
from fastapi import HTTPException, status
import redis
import logging
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class OrderService:
    """Business logic for Order operations - Single Responsibility Principle"""
    
    def __init__(self, repository: OrderRepository, publisher: MessagePublisher):
        self.repository = repository
        self.publisher = publisher
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        self.cache_ttl = 300  # 5 minutes
    
    async def _verify_user_exists(self, user_id: int) -> bool:
        """Verify user exists by calling User Service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.user_service_url}/api/v1/users/{user_id}",
                    timeout=5.0
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Error verifying user: {e}")
            return False
    
    def _get_cache_key(self, order_id: int) -> str:
        return f"order:{order_id}"
    
    def _cache_order(self, order: OrderResponse):
        try:
            cache_key = self._get_cache_key(order.id)
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                order.model_dump_json()
            )
            logger.debug(f"Successfully cached order {order.id}")
        except redis.RedisError as e:
            logger.error(f"Failed to cache order {order.id}: {str(e)}")
    
    def _get_cached_order(self, order_id: int) -> Optional[OrderResponse]:
        try:
            cache_key = self._get_cache_key(order_id)
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for order {order_id}")
                return OrderResponse.model_validate_json(cached)
            logger.debug(f"Cache miss for order {order_id}")
            return None
        except redis.RedisError as e:
            logger.error(f"Failed to get order {order_id} from cache: {str(e)}")
            return None
    
    def _invalidate_cache(self, order_id: int):
        try:
            cache_key = self._get_cache_key(order_id)
            self.redis_client.delete(cache_key)
            logger.debug(f"Successfully invalidated cache for order {order_id}")
        except redis.RedisError as e:
            logger.error(f"Failed to invalidate cache for order {order_id}: {str(e)}")
    
    def get_order(self, order_id: int) -> OrderResponse:
        # Try cache first
        cached_order = self._get_cached_order(order_id)
        if cached_order:
            return cached_order
        
        order = self.repository.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order_response = OrderResponse.model_validate(order)
        self._cache_order(order_response)
        return order_response
    
    def get_orders(self, skip: int = 0, limit: int = 100) -> List[OrderResponse]:
        orders = self.repository.get_all(skip, limit)
        return [OrderResponse.model_validate(order) for order in orders]
    
    def get_user_orders(self, user_id: int, skip: int = 0, limit: int = 100) -> List[OrderResponse]:
        orders = self.repository.get_by_user_id(user_id, skip, limit)
        return [OrderResponse.model_validate(order) for order in orders]
    
    async def create_order(self, order_data: OrderCreate) -> OrderResponse:
        # Verify user exists
        user_exists = await self._verify_user_exists(order_data.user_id)
        if not user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )
        
        # Create order
        order = self.repository.create(order_data)
        order_response = OrderResponse.model_validate(order)
        
        # Cache order
        self._cache_order(order_response)
        
        # Publish event
        event = OrderEvent(
            event_type="order.created",
            order_id=order.id,
            user_id=order.user_id,
            status=order.status,
            timestamp=datetime.utcnow()
        )
        self.publisher.publish_order_event(event)
        
        return order_response
    
    def update_order(self, order_id: int, order_data: OrderUpdate) -> OrderResponse:
        order = self.repository.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        updated_order = self.repository.update(order, order_data)
        order_response = OrderResponse.model_validate(updated_order)
        
        # Invalidate and update cache
        self._invalidate_cache(order_id)
        self._cache_order(order_response)
        
        # Publish event
        event = OrderEvent(
            event_type="order.updated",
            order_id=updated_order.id,
            user_id=updated_order.user_id,
            status=updated_order.status,
            timestamp=datetime.utcnow()
        )
        self.publisher.publish_order_event(event)
        
        return order_response
    
    def delete_order(self, order_id: int) -> dict:
        order = self.repository.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Publish event before deletion
        event = OrderEvent(
            event_type="order.deleted",
            order_id=order.id,
            user_id=order.user_id,
            status=order.status,
            timestamp=datetime.utcnow()
        )
        self.publisher.publish_order_event(event)
        
        self.repository.delete(order)
        self._invalidate_cache(order_id)
        
        return {"message": "Order deleted successfully"}
    
    def get_orders_by_status(self, status: OrderStatus, skip: int = 0, limit: int = 100) -> List[OrderResponse]:
        orders = self.repository.get_by_status(status, skip, limit)
        return [OrderResponse.model_validate(order) for order in orders]