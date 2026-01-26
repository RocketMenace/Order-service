

.PHONY: help build run down destroy stop run_all test build worker-payments worker-notifications worker-shipping

help:
	@echo "Available commands:"
	@echo "  build                - Build the Docker images"
	@echo "  up                   - Start all containers in detached mode"
	@echo "  down                 - Stop and remove containers"
	@echo "  destroy              - Stop and remove containers, networks, volumes"
	@echo "  stop                 - Stop running containers"
	@echo "  run                  - Run FastAPI application locally"
	@echo "  worker-payments      - Run OutboxPaymentsWorker"
	@echo "  worker-notifications - Run OutboxNotificationsWorker"
	@echo "  worker-shipping      - Run OutboxShippingWorker"
	@echo "  format               - Run ruff format command"
	@echo "  check                - Run ruff check command"

run_all:
	docker-compose up -d

build:
	docker-compose build

run:
	uvicorn app.main:app --reload --loop uvloop --http httptools

down:
	docker-compose down

destroy:
	docker-compose down -v

stop:
	docker-compose stop

test:
	pytest

format:
	ruff format .
	isort .

check:
	ruff check --fix .

worker-payments:
	python -m app.infrastructure.workers.run_outbox_payments_worker

worker-notifications:
	python -m app.infrastructure.workers.run_outbox_notifications_worker

worker-shipping:
	python -m app.infrastructure.workers.run_outbox_shipping_worker
