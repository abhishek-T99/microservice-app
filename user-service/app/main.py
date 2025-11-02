### `user-service/app/main.py`
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base
from app.api.v1 import users

settings = get_settings()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service",
    description="Microservice for user management",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.service_name}