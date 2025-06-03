#!/bin/bash

echo "Stopping and removing containers, networks, and volumes..."

# Stop and remove containers, networks, and volumes
docker-compose down --volumes --remove-orphans

# Ensure that no container is running after the above command
echo "Checking if any containers are still running..."
docker ps -a

# If there are containers still running, stop and remove them manually
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

# Remove all unused volumes (if any)
docker volume prune -f

echo "Docker Compose services and volumes have been refreshed!"

# Start the containers in detached mode
docker-compose up -d

echo "docker-compose up -d completed successfully!"

chmod +x ./run_tests.sh

echo "Permissions changed for run_tests.sh"

echo "--------------------------------"
echo "Waiting for MySQL server to be ready..."
echo "--------------------------------"

# Try to connect to MySQL server until it's available
MAX_RETRIES=30
count=0
while ! docker-compose exec -T mysql mysql -h localhost -u root -proot -e "SELECT 1" >/dev/null 2>&1; do
    count=$((count+1))
    if [ $count -ge $MAX_RETRIES ]; then
        echo "Maximum retries reached. MySQL might not be running correctly."
        exit 1
    fi
    echo "Waiting for MySQL to be ready... Attempt $count/$MAX_RETRIES"
    sleep 1
done

echo "MySQL server is ready!"

# Run the tests after MySQL is fully ready
echo 'Running tests...'
pytest --cov=lambda_functions --cov-report=term -vv --durations=0

echo "Tests completed."