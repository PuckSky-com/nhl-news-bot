#!/bin/bash

# Function to restart Redis
manage_redis() {
    if pgrep -x "redis-server" > /dev/null
    then
        echo "Redis is already running. Restarting..."
        sudo service redis-server restart || { echo "Failed to restart Redis service"; return 1; }
        echo "Redis restarted successfully."
    else
        echo "Starting Redis..."
        redis-server &
        sleep 2
        if ! pgrep -x "redis-server" > /dev/null; then
            echo "ERROR: Failed to start Redis."
            return 1
        fi
        echo "Redis started successfully."
    fi
    return 0
}

# Function to restart Celery worker
manage_celery_worker() {
    if pgrep -f "celery.*worker" > /dev/null
    then
        echo "Celery worker is already running. Stopping..."
        pkill -f "celery.*worker"
        sleep 2
    fi
    
    echo "Starting Celery worker..."
    cd sports_news
    celery -A sports_news.celery worker --loglevel=info &
    cd ..
    sleep 3
    
    # Check if the worker started successfully
    if ! pgrep -f "celery.*worker" > /dev/null; then
        echo "ERROR: Failed to start Celery worker. Check your Celery configuration."
        return 1
    fi
    echo "Celery worker started successfully."
    return 0
}

# Function to restart Django server
manage_django_server() {
    if pgrep -f "python.*manage.py runserver" > /dev/null
    then
        echo "Django server is already running. Stopping..."
        pkill -f "python.*manage.py runserver"
        sleep 2
    fi
    
    echo "Starting Django development server..."
    cd sports_news
    python manage.py runserver &
    cd ..
    sleep 3
    
    # Check if the server started successfully
    if ! pgrep -f "python.*manage.py runserver" > /dev/null; then
        echo "ERROR: Failed to start Django server."
        return 1
    fi
    echo "Django server started successfully."
    return 0
}

# Function to restart Celery Beat
manage_celery_beat() {
    if pgrep -f "celery.*beat" > /dev/null
    then
        echo "Celery Beat is already running. Stopping..."
        pkill -f "celery.*beat"
        sleep 2
    fi
    
    echo "Starting Celery Beat..."
    cd sports_news
    celery -A sports_news.celery beat --scheduler django_celery_beat.schedulers:DatabaseScheduler &
    cd ..
    sleep 3
    
    # Check if the beat scheduler started successfully
    if ! pgrep -f "celery.*beat" > /dev/null; then
        echo "ERROR: Failed to start Celery Beat. Check your Celery configuration."
        return 1
    fi
    echo "Celery Beat started successfully."
    return 0
}

# Main function to restart all services
restart_services() {
    echo "========================================="
    echo "Starting/Restarting all services..."
    echo "========================================="
    
    manage_redis || { echo "Redis startup/restart failed"; exit 1; }
    manage_celery_worker || { echo "Celery worker startup/restart failed"; exit 1; }
    manage_django_server || { echo "Django server startup/restart failed"; exit 1; }
    manage_celery_beat || { echo "Celery Beat startup/restart failed"; exit 1; }

    echo "========================================="
    echo "All services have been started/restarted successfully!"
    echo "To view logs, check the terminal where processes are running."
    echo "To stop all services: pkill -f 'celery|redis-server|python.*manage.py'"
    echo "========================================="
}

# Run the main function
restart_services