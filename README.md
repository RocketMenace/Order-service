# Order Service

A microservice for managing orders in an e-commerce system, built with FastAPI and following Domain-Driven Design (DDD) principles. The service handles order creation, payment processing, shipping registration, and notifications through an event-driven architecture using Kafka and an outbox pattern.

## Overview

The Order Service is responsible for:
- Creating and managing orders
- Validating item availability through the Catalog Service
- Processing payment requests and callbacks
- Managing order status updates
- Sending notifications
- Registering shipping requests via Kafka
- Processing shipping responses from Kafka

## Architecture

The service follows a **Clean Architecture** pattern with clear separation of concerns:

- **Presentation Layer**: FastAPI routers and request/response schemas
- **Application Layer**: Use cases and business logic (DTOs, interfaces)
- **Core Layer**: Domain models, value objects, and exceptions
- **Infrastructure Layer**: Database, HTTP clients, message brokers, adapters, and workers

### Key Patterns

- **Outbox Pattern**: Ensures reliable event publishing by storing events in the database before publishing
- **Inbox Pattern**: Processes incoming events from Kafka to update order status
- **Unit of Work**: Manages database transactions and ensures data consistency
- **Dependency Injection**: Uses Dishka for IoC container management
- **Event-Driven Architecture**: Uses Kafka for asynchronous communication

## Features

- ✅ Order creation with idempotency support
- ✅ Stock validation via Catalog Service integration
- ✅ Payment processing integration
- ✅ Order status management
- ✅ Asynchronous event processing (Outbox pattern)
- ✅ Kafka message consumption for shipping updates
- ✅ Notification service integration
- ✅ Database migrations with Alembic
- ✅ Structured logging with structlog
- ✅ Health check endpoints
- ✅ Comprehensive error handling

## Tech Stack

- **Framework**: FastAPI 0.127+
- **Python**: 3.13+
- **Database**: PostgreSQL (asyncpg, SQLAlchemy 2.0)
- **Message Broker**: Apache Kafka (aiokafka)
- **HTTP Client**: httpx
- **Dependency Injection**: Dishka
- **Migrations**: Alembic
- **Logging**: structlog
- **Validation**: Pydantic
- **ASGI Server**: Uvicorn with uvloop and httptools

## Project Structure

```
Order-service/
├── app/
│   ├── application/          # Application layer (use cases, DTOs, interfaces)
│   │   ├── dto/              # Data Transfer Objects
│   │   ├── enums/            # Application enums
│   │   ├── interfaces/       # Protocol definitions
│   │   └── use_cases/        # Business logic use cases
│   ├── core/                 # Domain layer (models, exceptions, value objects)
│   │   ├── enums/            # Domain enums
│   │   ├── exceptions/       # Domain exceptions
│   │   ├── models/           # Domain models
│   │   └── value_objects/    # Value objects
│   ├── infrastructure/       # Infrastructure layer
│   │   ├── adapters/         # External service adapters
│   │   ├── broker/           # Kafka consumer/producer
│   │   ├── config/           # Configuration and settings
│   │   ├── ioc_container/    # Dependency injection setup
│   │   ├── models/           # Database models
│   │   ├── repositories/     # Data access layer
│   │   └── workers/          # Background workers
│   ├── presentation/         # Presentation layer
│   │   └── api/              # FastAPI routers and schemas
│   └── main.py               # Application entry point
├── migrations/               # Alembic database migrations
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile               # Docker image definition
├── entrypoint.sh            # Worker startup script
├── Makefile                 # Development commands
└── pyproject.toml           # Project dependencies

```

## Prerequisites

- Python 3.13+
- PostgreSQL 15+
- Apache Kafka (or use Docker Compose)
- uv package manager (recommended) or pip

## Installation & Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd Order-service
```

### 2. Install dependencies

Using `uv` (recommended):
```bash
uv sync
```

Or using `pip`:
```bash
pip install -e .
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
# Project
PROJECT_NAME=Order Service
VERSION=0.1.0
DEBUG=true

# Database
POSTGRES_DB=order_service
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/order_service

# Database Pool
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# Redis (optional)
REDIS_HOST=
REDIS_PORT=6379
REDIS_DB=1

# Application
APP_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# External Services
CATALOG_SERVICE_API_URL=http://localhost:8001/api
PAYMENTS_SERVICE_API_URL=http://localhost:8002/api
PAYMENTS_CALLBACK_URL=http://localhost:8000/api/v1/orders/payment-callback
NOTIFICATIONS_SERVICE_API_URL=http://localhost:8003/api

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:29092
KAFKA_TOPIC=shipping-events

# Capashino (if needed)
CAPASHINO_SERVICE_ACCESS_TOKEN=
```

### 4. Database Setup

Create the database:
```bash
createdb order_service
```

Run migrations:
```bash
alembic upgrade head
```

### 5. Start Kafka (if not using Docker)

Or use Docker Compose to start Kafka and Zookeeper:
```bash
docker-compose up -d zookeeper kafka
```

## Running the Application

### Development Mode

Run the FastAPI application:
```bash
make run
```

Or directly:
```bash
uvicorn app.main:app --reload --loop uvloop --http httptools
```

### Production Mode

The application will be available at:
- API: `http://localhost:8000/api`
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

### Running Workers

The service includes several background workers that process events asynchronously. To run all workers:

```bash
./entrypoint.sh
```

Or run individual workers:

```bash
# Kafka Consumer (processes shipping events)
python -m app.infrastructure.workers.run_kafka_consumer

# Inbox Worker (processes inbox events for order status updates)
python -m app.infrastructure.workers.run_inbox_worker

# Outbox Payments Worker (sends payment requests)
python -m app.infrastructure.workers.run_outbox_payments_worker

# Outbox Notifications Worker (sends notifications)
python -m app.infrastructure.workers.run_outbox_notifications_worker

# Outbox Shipping Worker (publishes shipping events to Kafka)
python -m app.infrastructure.workers.run_outbox_shipping_worker
```

## Workers

The service runs multiple background workers to handle asynchronous processing:

### 1. Kafka Consumer (`run_kafka_consumer`)
- Consumes shipping response events from Kafka
- Updates order status based on shipping information
- Runs continuously, processing messages as they arrive

### 2. Inbox Worker (`run_inbox_worker`)
- Processes inbox events from the database
- Updates order status (e.g., ORDER_PAID, ORDER_CANCELLED)
- Polls every 5 seconds for new inbox events

### 3. Outbox Payments Worker (`run_outbox_payments_worker`)
- Processes pending payment request events from the outbox
- Sends payment requests to the Payments Service
- Marks events as processed after successful delivery
- Polls every 5 seconds

### 4. Outbox Notifications Worker (`run_outbox_notifications_worker`)
- Processes pending notification events from the outbox
- Sends notifications to the Notifications Service
- Marks events as processed after successful delivery
- Polls every 5 seconds

### 5. Outbox Shipping Worker (`run_outbox_shipping_worker`)
- Processes pending shipping events from the outbox
- Publishes shipping events to Kafka
- Marks events as processed after successful publishing
- Polls every 5 seconds

All workers are started automatically by `entrypoint.sh` with 2-second delays between each startup.

## API Documentation

### Endpoints

#### Create Order
```http
POST /api/v1/orders
Content-Type: application/json

{
  "item_id": "uuid",
  "quantity": 2,
  "user_id": "user-123",
  "idempotency_key": "uuid"
}
```

**Response**: Order details with status "new"

#### Payment Callback
```http
POST /api/v1/orders/payment-callback
Content-Type: application/json

{
  "id": "payment-uuid",
  "user_id": "user-uuid",
  "order_id": "order-uuid",
  "amount": "100.00",
  "status": "succeeded",
  "idempotency_key": "uuid",
  "created_at": "2025-01-01T00:00:00Z"
}
```

**Response**: Empty data payload (processing happens asynchronously)

### Interactive Documentation

- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`
- **OpenAPI JSON**: `http://localhost:8000/api/openapi.json`

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "description"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

## Docker

### Build the image
```bash
make build
# or
docker-compose build
```

### Run with Docker Compose
```bash
make run_all
# or
docker-compose up -d
```

### Stop containers
```bash
make down
# or
docker-compose down
```

The Dockerfile uses a multi-stage build for optimized image size and runs as a non-root user for security.

## Development

### Code Formatting
```bash
make format
```

### Code Linting
```bash
make check
```

### Running Tests
```bash
make test
```

### Available Make Commands

```bash
make help              # Show all available commands
make build             # Build Docker images
make run               # Run FastAPI application locally
make run_all           # Start all containers in detached mode
make down              # Stop and remove containers
make destroy           # Stop and remove containers, networks, volumes
make stop              # Stop running containers
make test              # Run tests
make format            # Format code with ruff and isort
make check             # Run ruff check with auto-fix
make worker-payments   # Run OutboxPaymentsWorker
make worker-notifications  # Run OutboxNotificationsWorker
make worker-shipping   # Run OutboxShippingWorker
```

## Architecture Details

### Order Flow

1. **Order Creation**:
   - Client sends order request with idempotency key
   - Service validates item exists and stock is available
   - Order is created with status "NEW"
   - Payment request event is added to outbox
   - Notification event is added to outbox

2. **Payment Processing**:
   - Outbox Payments Worker sends payment request to Payments Service
   - Payments Service processes payment and calls back
   - Payment callback creates inbox event (ORDER_PAID or ORDER_CANCELLED)
   - Inbox Worker processes the event and updates order status

3. **Shipping Registration**:
   - When order is paid, shipping event is added to outbox
   - Outbox Shipping Worker publishes event to Kafka
   - Shipping service consumes event and processes shipping
   - Shipping service publishes response back to Kafka
   - Kafka Consumer processes shipping response and updates order

4. **Notifications**:
   - Outbox Notifications Worker sends notifications to Notifications Service
   - Notifications are sent for order creation, payment success/failure, etc.

### Outbox Pattern

The outbox pattern ensures reliable event publishing:
- Events are stored in the database within the same transaction as the business operation
- Background workers poll the outbox and publish events
- Events are marked as processed only after successful publishing
- Failed events can be retried

### Inbox Pattern

The inbox pattern ensures idempotent event processing:
- Incoming events are stored in the inbox table
- Events are processed based on idempotency keys
- Duplicate events are ignored
- Order status is updated based on event type

## Configuration

All configuration is managed through environment variables (see `.env` example above). The service uses `pydantic-settings` for configuration management with automatic validation.

## Logging

The service uses `structlog` for structured logging. Logs are output in JSON format by default, making them easy to parse and search in log aggregation systems.

## Error Handling

The service implements comprehensive error handling:
- Domain exceptions for business logic errors
- Infrastructure exceptions for external service failures
- HTTP exception handlers for proper API responses
- Retry logic for transient failures

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

