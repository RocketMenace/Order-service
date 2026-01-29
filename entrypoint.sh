#!/bin/bash

set -e

echo "[ENTRYPOINT] Running database migrations..."
alembic upgrade head

echo "[ENTRYPOINT] Starting Order Service workers..."

# Start run_kafka_consumer
echo "[ENTRYPOINT] Starting run_kafka_consumer..."
python -m app.infrastructure.workers.run_kafka_consumer &
KAFKA_PID=$!
echo "[ENTRYPOINT] run_kafka_consumer started with PID: $KAFKA_PID"
sleep 2

# Start run_inbox_worker
echo "[ENTRYPOINT] Starting run_inbox_worker..."
python -m app.infrastructure.workers.run_inbox_worker &
INBOX_PID=$!
echo "[ENTRYPOINT] run_inbox_worker started with PID: $INBOX_PID"
sleep 2

# Start run_outbox_notifications_worker
echo "[ENTRYPOINT] Starting run_outbox_notifications_worker..."
python -m app.infrastructure.workers.run_outbox_notifications_worker &
NOTIFICATIONS_PID=$!
echo "[ENTRYPOINT] run_outbox_notifications_worker started with PID: $NOTIFICATIONS_PID"
sleep 2

# Start run_outbox_payments_worker
echo "[ENTRYPOINT] Starting run_outbox_payments_worker..."
python -m app.infrastructure.workers.run_outbox_payments_worker &
PAYMENTS_PID=$!
echo "[ENTRYPOINT] run_outbox_payments_worker started with PID: $PAYMENTS_PID"
sleep 2

# Start run_outbox_shipping_worker
echo "[ENTRYPOINT] Starting run_outbox_shipping_worker..."
python -m app.infrastructure.workers.run_outbox_shipping_worker &
SHIPPING_PID=$!
echo "[ENTRYPOINT] run_outbox_shipping_worker started with PID: $SHIPPING_PID"

echo "[ENTRYPOINT] All workers started successfully"

# Function to handle shutdown
cleanup() {
    echo "[ENTRYPOINT] Received shutdown signal, stopping all workers..."
    kill $KAFKA_PID $INBOX_PID $NOTIFICATIONS_PID $PAYMENTS_PID $SHIPPING_PID 2>/dev/null || true
    wait
    echo "[ENTRYPOINT] All workers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start uvicorn server in foreground (main process)
echo "[ENTRYPOINT] Starting uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --loop uvloop --http httptools || true

# If uvicorn exits, cleanup workers
cleanup

