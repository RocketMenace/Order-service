# Order Service

A microservice for managing orders in an e-commerce system, built with FastAPI and following Domain-Driven Design (DDD) principles. This service handles order creation, payment processing, shipping coordination, and order status management using an event-driven architecture with Kafka.

## 🏗️ Architecture

This service implements a **Clean Architecture** pattern with the following layers:

- **Presentation Layer**: FastAPI routers, schemas, and error handlers
- **Application Layer**: Use cases, DTOs, and business logic interfaces
- **Domain Layer**: Core domain models, value objects, and exceptions
- **Infrastructure Layer**: Database repositories, external service adapters, message brokers, and workers

### Event-Driven Architecture

The service uses an **Outbox/Inbox Pattern** for reliable event processing:

- **Outbox Pattern**: Ensures reliable message publishing to Kafka
- **Inbox Pattern**: Ensures idempotent message processing from Kafka
- **Background Workers**: Process pending events asynchronously

## ✨ Features

- **Order Management**
  - Create orders with idempotency support
  - Stock validation via Catalog Service integration
  - Order status tracking (NEW → PAID → SHIPPED → CANCELLED)

- **Payment Processing**
  - Integration with external Payment Service
  - Payment callback handling
  - Automatic order status updates based on payment results

- **Shipping Coordination**
  - Kafka-based shipping request publishing
  - Shipping response consumption and processing
  - Order status updates when orders are shipped

- **Event-Driven Communication**
  - Kafka producer for publishing events
  - Kafka consumer for receiving events
  - Reliable message delivery with retry mechanisms

- **Notification System**
  - Order creation notifications
  - Payment status notifications
  - Shipping status notifications

- **Idempotency**
  - All operations support idempotency keys
  - Prevents duplicate processing of events

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.127+
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0+
- **Message Broker**: Apache Kafka (via aiokafka)
- **Async Runtime**: uvloop, httptools
- **Dependency Injection**: Dishka
- **Migrations**: Alembic
- **HTTP Client**: httpx
- **Validation**: Pydantic
- **Logging**: structlog

## 📁 Project Structure

```
Order-service/
├── app/
│   ├── application/          # Application layer (use cases, DTOs, interfaces)
│   │   ├── dto/              # Data Transfer Objects
│   │   ├── enums/            # Event and status enums
│   │   ├── interfaces/       # Protocol definitions
│   │   └── use_cases/        # Business logic use cases
│   ├── core/                 # Domain layer
│   │   ├── exceptions/       # Domain exceptions
│   │   ├── models/           # Domain models
│   │   └── value_objects/    # Value objects
│   ├── infrastructure/       # Infrastructure layer
│   │   ├── adapters/         # External service adapters
│   │   ├── broker/           # Kafka producer/consumer
│   │   ├── config/           # Configuration classes
│   │   ├── models/           # Database models
│   │   ├── repositories/     # Data access layer
│   │   ├── ioc_container/   # Dependency injection
│   │   ├── inbox_worker.py   # Inbox event processor
│   │   └── outbox_worker.py  # Outbox event processor
│   ├── presentation/         # Presentation layer
│   │   └── api/             # REST API endpoints
│   └── main.py              # Application entry point
├── migrations/               # Database migrations
├── docker-compose.yml        # Docker services configuration
├── pyproject.toml           # Project dependencies
└── README.md                # This file
```

## 📋 Prerequisites

- Python 3.13+
- PostgreSQL 15+
- Apache Kafka (or use Docker Compose)
- Docker & Docker Compose (optional, for local development)

## 🚀 Installation & Setup

The API will be available at:
- **API**: http://localhost:8000/api
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 🔄 Background Workers

The service runs several background workers for asynchronous event processing:

### Outbox Workers

- **OutboxPaymentsWorker**: Processes pending payment requests
- **OutboxNotificationsWorker**: Sends pending notifications
- **OutboxShippingWorker**: Publishes shipping requests to Kafka

### Inbox Worker

- **InboxWorker**: Processes incoming events and updates order status

Workers run continuously and poll for pending events every 5 seconds.

## 📦 Event Types

The service handles the following event types:

### Outbox Events (Published)
- `order.created` - Order creation notification
- `order.paid` - Payment success notification
- `order.cancelled` - Order cancellation notification
- `order.shipped` - Shipping confirmation notification
- `payment.requested` - Payment processing request
- `shipping.requested` - Shipping coordination request

### Inbox Events (Consumed)
- `order.paid` - Payment status update
- `order.shipped` - Shipping status update
- `order.cancelled` - Order cancellation

## 🔐 Idempotency

All operations support idempotency keys to prevent duplicate processing:

- **Order Creation**: Uses `idempotency_key` from request
- **Payment Callback**: Uses `idempotency_key` from payment
- **Shipping Response**: Generates UUID from `shipment_id` or `order_id`

## 🌐 External Service Integration

### Catalog Service
- **Endpoint**: `GET /items/{item_id}/stock`
- **Purpose**: Validates item existence and stock availability

### Payments Service
- **Endpoint**: `POST /payments`
- **Callback**: `POST /api/v1/orders/payment-callback`
- **Purpose**: Processes order payments

### Notifications Service
- **Endpoint**: `POST /notifications`
- **Purpose**: Sends order status notifications

## 🐳 Docker Configuration

### Kafka Configuration

The service supports both local and Docker deployments:

- **Local Development**: `KAFKA_BOOTSTRAP=localhost:29092`
- **Docker Deployment**: `KAFKA_BOOTSTRAP=kafka:9092`

Kafka is configured with two listeners:
- External (localhost): Port `29092`
- Internal (Docker network): Port `9092`

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_DB` | PostgreSQL database name | `order_service` |
| `POSTGRES_USER` | PostgreSQL username | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `postgres` |
| `POSTGRES_HOST` | PostgreSQL host | `postgres` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `DATABASE_URL` | Full database connection URL | - |
| `KAFKA_BOOTSTRAP` | Kafka bootstrap servers | - |
| `KAFKA_TOPIC` | Kafka topic name | `student_system_order.events` |
| `CATALOG_SERVICE_API_URL` | Catalog service base URL | - |
| `PAYMENTS_SERVICE_API_URL` | Payments service base URL | - |
| `NOTIFICATIONS_SERVICE_API_URL` | Notifications service base URL | - |
| `APP_PORT` | Application port | `8000` |
| `DEBUG` | Debug mode | `True` |
| `LOG_LEVEL` | Logging level | `INFO` |


## 🔗 Related Services

- Catalog Service - Item and inventory management
- Payments Service - Payment processing
- Notifications Service - User notifications


## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
