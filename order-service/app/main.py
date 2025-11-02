from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.database import engine, Base
from app.api.v1 import orders
from app.messaging.consumer import MessageConsumer

settings = get_settings()

# Message consumer instance
consumer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    
    # Start message consumer
    global consumer
    consumer = MessageConsumer()
    consumer.start_in_thread()
    
    yield
    
    # Shutdown
    if consumer and consumer.connection:
        consumer.connection.close()


app = FastAPI(
    title="Order Service",
    description="Microservice for order management",
    version="1.0.0",
    lifespan=lifespan
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
app.include_router(orders.router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.service_name}