#!/bin/bash
set -e

echo "========================================"
echo "URL Shortener - Starting Service"
echo "========================================"

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done
echo "✓ PostgreSQL is ready"

# Wait for Redis
echo "Waiting for Redis..."
until redis-cli -h "$REDIS_HOST" ping 2>/dev/null; do
    echo "Redis is unavailable - sleeping"
    sleep 2
done
echo "✓ Redis is ready"

echo "========================================"
echo "Starting URL Shortener Service..."
echo "========================================"

exec "$@"