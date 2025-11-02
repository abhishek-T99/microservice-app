# Microservice App

A small microservices example consisting of two services:

- user-service: manages users (HTTP API, PostgreSQL, Redis cache, RabbitMQ events)
- order-service: manages orders (HTTP API, PostgreSQL, Redis cache, RabbitMQ events)

This repo is intended as a development/demo workspace. Each service is a self-contained FastAPI application with a clear separation between API routers, service/business logic, repositories (DB interaction), schemas (Pydantic models), messaging, and migrations.

## Quick start (Docker)

1. Copy or create a `.env` file at repo root with required variables (example keys shown below).

2. Build and start all services in detached mode:

```bash
# from repo root
docker-compose up --build -d
```

3. Open the interactive API docs:

- User service: http://localhost:8001/docs
- Order service: http://localhost:8002/docs

4. Follow logs:

```bash
# follow all logs
docker-compose logs -f

# follow a single service
docker-compose logs -f order-service
```

## Architecture overview

Each service follows the same structure under `<service>/app`:

- `config.py` - pydantic-settings `Settings` and `get_settings()` helper
- `main.py` - FastAPI app and startup/shutdown wiring
- `api/v1/` - routers and HTTP endpoints
- `services/` - business logic (caching, validations, event publish)
- `repositories/` - persistence layer (SQLAlchemy/ORM calls)
- `models/` - DB models / enums
- `schemas/` - Pydantic request/response/event schemas
- `messaging/` - publisher and consumer helpers for RabbitMQ
- `alembic/` - DB migrations

Data flow (typical):

HTTP request -> API router -> Service -> Repository -> DB

Services publish domain events via `publisher.publish_*_event(...)` when records are created/updated/deleted. Consumers can be implemented in `messaging/consumer.py` when needed.

## Environment variables

Create a `.env` file at the repo root with the variables referenced in each service `app/config.py`. Example keys (names may differ slightly between services):

```
# Postgres - user service
POSTGRES_USER_HOST=postgres
POSTGRES_USER_PORT=5432
POSTGRES_USER_DB=users_db
POSTGRES_USER_USER=user
POSTGRES_USER_PASSWORD=pass

# Postgres - order service
POSTGRES_ORDER_HOST=postgres
POSTGRES_ORDER_PORT=5432
POSTGRES_ORDER_DB=orders_db
POSTGRES_ORDER_USER=order
POSTGRES_ORDER_PASSWORD=pass

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Service URLs
USER_SERVICE_URL=http://user-service:8001
```
