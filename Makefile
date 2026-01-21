

.PHONY: help build run down destroy stop run_all test build

help:
	@echo "Available commands:"
	@echo "  build             - Build the Docker images"
	@echo "  up                - Start all containers in detached mode"
	@echo "  down              - Stop and remove containers"
	@echo "  destroy           - Stop and remove containers, networks, volumes"
	@echo "  stop              - Stop running containers"
	@echo "  run               - Run FastAPI application locally"
	@echo "  format            - Run ruff format command"
	@echo "  check             - Run ruff check command"

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

check:
	ruff check --fix .
