from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    postgres_user_host: str
    postgres_user_port: int
    postgres_user_db: str
    postgres_user_user: str
    postgres_user_password: str
    
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
    service_name: str = "user-service"
    api_v1_prefix: str = "/api/v1"
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user_user}:{self.postgres_user_password}@{self.postgres_user_host}:{self.postgres_user_port}/{self.postgres_user_db}"
    
    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"
    
    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}/"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()