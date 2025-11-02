from fastapi import APIRouter, Depends, status
from typing import List
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService
from app.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return service.create_user(user_data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    return service.get_user(user_id)


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(get_user_service)
):
    return service.get_users(skip, limit)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service)
):
    return service.update_user(user_id, user_data)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    return service.delete_user(user_id)
