from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    postgres_order_host: str
    postgres_order_port: int
    postgres_order_db: str
    postgres_order_user: str
    postgres_order_password: str
    
    # Redis
    redis_host: str
    redis_port: int
    redis_password: str
    
    # RabbitMQ
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_user: str
    rabbitmq_password: str
    
    # Service Config
    service_name: str = "order-service"
    api_v1_prefix: str = "/api/v1"
    user_service_url: str
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_order_user}:{self.postgres_order_password}@{self.postgres_order_host}:{self.postgres_order_port}/{self.postgres_order_db}"
    
    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/1"
    
    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}/"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()