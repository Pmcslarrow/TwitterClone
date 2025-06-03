#!/bin/bash

set -e  # Exit immediately on error

echo "Tearing down any existing containers and volumes..."
docker-compose down -v || true
docker rm -f test_mysql 2>/dev/null || true

echo "Starting MySQL container..."
docker-compose up -d

echo "Waiting for MySQL to be ready..."
until docker exec test_mysql mysqladmin ping -h "localhost" --silent; do
  sleep 1
done

echo "Initializing database from init.sql..."
docker exec test_mysql mysql -h 127.0.0.1 -u test_user -ptest_pass TwitterClone

echo "Database container rebuilt and initialized."