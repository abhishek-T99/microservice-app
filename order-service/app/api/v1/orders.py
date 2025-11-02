from fastapi import APIRouter, Depends, status, Query
from typing import List
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from app.models.order import OrderStatus
from app.services.order_service import OrderService
from app.dependencies import get_order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    service: OrderService = Depends(get_order_service)
):
    return await service.create_order(order_data)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service)
):
    return service.get_order(order_id)


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: OrderStatus = Query(None, alias="status"),
    service: OrderService = Depends(get_order_service)
):
    if status_filter:
        return service.get_orders_by_status(status_filter, skip, limit)
    return service.get_orders(skip, limit)


@router.get("/user/{user_id}", response_model=List[OrderResponse])
async def get_user_orders(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    service: OrderService = Depends(get_order_service)
):
    return service.get_user_orders(user_id, skip, limit)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    service: OrderService = Depends(get_order_service)
):
    return service.update_order(order_id, order_data)


@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    service: OrderService = Depends(get_order_service)
):
    return service.delete_order(order_id)
