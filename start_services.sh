#!/bin/bash

# Configuration
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DJANGO_APP_DIR="${BASE_DIR}/sports_news"
LOG_DIR="${BASE_DIR}/logs"
VENV_DIR="${BASE_DIR}/.venv"  # Assuming virtualenv is used
CELERY_WORKERS=1  # Adjust based on your Raspberry Pi's available resources

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/services.log"
}

# Function to check if we're using the virtual environment
ensure_virtualenv() {
    if [[ -d "$VENV_DIR" ]]; then
        if [[ "$VIRTUAL_ENV" != "$VENV_DIR" ]]; then
            log_message "Activating virtual environment..."
            source "$VENV_DIR/bin/activate" || {
                log_message "ERROR: Failed to activate virtual environment."
                return 1
            }
        fi
    else
        log_message "No virtual environment found at $VENV_DIR. Using system Python."
    fi
    return 0
}

# Function to check and start Redis if not running
ensure_redis_running() {
    if ! pgrep -x "redis-server" > /dev/null; then
        log_message "Redis is not running. Starting..."
        redis-server --daemonize yes
        sleep 2
        if pgrep -x "redis-server" > /dev/null; then
            log_message "Redis started successfully."
        else
            log_message "ERROR: Failed to start Redis."
            return 1
        fi
    else
        log_message "Redis is already running."
    fi
    return 0
}

# Function to restart Celery worker only if necessary
restart_celery_worker() {
    # First, ensure we're in the Django app directory
    cd "$DJANGO_APP_DIR" || { 
        log_message "ERROR: Could not change to $DJANGO_APP_DIR directory"
        return 1
    }
    
    if pgrep -f "celery.*worker" > /dev/null; then
        log_message "Stopping Celery worker..."
        pkill -f "celery.*worker"
        sleep 3
    fi
    
    log_message "Starting Celery worker..."
    celery -A "$(basename "$DJANGO_APP_DIR").celery" worker \
        --concurrency=$CELERY_WORKERS \
        --loglevel=info > "$LOG_DIR/celery_worker.log" 2>&1 &
    
    WORKER_PID=$!
    sleep 3
    
    if ps -p $WORKER_PID > /dev/null || pgrep -f "celery.*worker" > /dev/null; then
        log_message "Celery worker started successfully."
    else
        log_message "ERROR: Celery worker failed to start."
        return 1
    fi
    return 0
}

# Function to restart Celery Beat only if necessary
restart_celery_beat() {
    # First, ensure we're in the Django app directory
    cd "$DJANGO_APP_DIR" || { 
        log_message "ERROR: Could not change to $DJANGO_APP_DIR directory"
        return 1
    }
    
    if pgrep -f "celery.*beat" > /dev/null; then
        log_message "Stopping Celery Beat..."
        pkill -f "celery.*beat"
        sleep 2
    fi
    
    log_message "Starting Celery Beat..."
    celery -A "$(basename "$DJANGO_APP_DIR").celery" beat \
        --scheduler django_celery_beat.schedulers:DatabaseScheduler \
        > "$LOG_DIR/celery_beat.log" 2>&1 &
    
    BEAT_PID=$!
    sleep 3
    
    if ps -p $BEAT_PID > /dev/null || pgrep -f "celery.*beat" > /dev/null; then
        log_message "Celery Beat started successfully."
    else
        log_message "ERROR: Celery Beat failed to start."
        return 1
    fi
    return 0
}

# Function to check Django server, with better error handling
ensure_django_running() {
    # First, ensure we're in the Django app directory
    cd "$DJANGO_APP_DIR" || { 
        log_message "ERROR: Could not change to $DJANGO_APP_DIR directory"
        return 1
    }
    
    if pgrep -f "python.*manage.py runserver" > /dev/null; then
        log_message "Django is already running."
        return 0
    fi
    
    log_message "Starting Django server..."
    
    # Before starting, check if Django can be started without errors
    python manage.py check > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        log_message "WARNING: Django check failed. There might be issues with your Django application."
        log_message "Running full check and showing errors:"
        python manage.py check
    fi
    
    # Actually start Django
    python manage.py runserver 0.0.0.0:8000 > "$LOG_DIR/django.log" 2>&1 &
    DJANGO_PID=$!
    
    # Give it time to start and check if it's still running
    sleep 5
    if ps -p $DJANGO_PID > /dev/null || pgrep -f "python.*manage.py runserver" > /dev/null; then
        log_message "Django server successfully started."
        # Test if Django is responding
        if curl -s http://localhost:8000/ > /dev/null; then
            log_message "Django server is responding to requests."
        else
            log_message "WARNING: Django started but not responding to requests."
            log_message "Check $LOG_DIR/django.log for errors."
            tail -n 20 "$LOG_DIR/django.log" | tee -a "$LOG_DIR/services.log"
        fi
    else
        log_message "ERROR: Django server failed to start."
        log_message "Last 20 lines of Django log:"
        tail -n 20 "$LOG_DIR/django.log" | tee -a "$LOG_DIR/services.log"
        return 1
    fi
    return 0
}

# Function to check system resources
check_system_resources() {
    log_message "Checking system resources..."
    
    # Check memory usage
    local MEM_TOTAL=$(free -m | awk '/^Mem:/{print $2}')
    local MEM_USED=$(free -m | awk '/^Mem:/{print $3}')
    local MEM_PCT=$((MEM_USED * 100 / MEM_TOTAL))
    
    # Check disk usage
    local DISK_PCT=$(df -h . | awk 'NR==2 {print $5}' | tr -d '%')
    
    # Check CPU load
    local CPU_LOAD=$(uptime | awk -F'[a-z]:' '{print $2}' | awk '{print $1}' | tr -d ',')

    log_message "Memory: $MEM_PCT% used ($MEM_USED MB / $MEM_TOTAL MB)"
    log_message "Disk: $DISK_PCT% used"
    log_message "CPU Load: $CPU_LOAD"

    if [ "$MEM_PCT" -gt 80 ]; then
        log_message "WARNING: High memory usage. Consider reducing Celery workers."
    fi

    if [ "$DISK_PCT" -gt 80 ]; then
        log_message "WARNING: High disk usage."
    fi
}

# Main function to start/restart necessary services
restart_services() {
    log_message "========================================="
    log_message "Starting services for Django application"
    log_message "========================================="

    # Check if we can activate the virtual environment
    ensure_virtualenv || {
        log_message "Failed to set up Python environment. Exiting."
        exit 1
    }
    
    # Check system resources
    check_system_resources
    
    # Start Redis
    ensure_redis_running || {
        log_message "Redis failed to start. Exiting."
        exit 1
    }
    
    # Start Django first (it's the main app)
    ensure_django_running || {
        log_message "Django failed to start. Exiting."
        exit 1
    }
    
    # Start Celery components
    restart_celery_worker || {
        log_message "WARNING: Celery worker failed, but continuing..."
    }
    
    restart_celery_beat || {
        log_message "WARNING: Celery beat failed, but continuing..."
    }

    log_message "========================================="
    log_message "Services status:"
    log_message "Django logs: $LOG_DIR/django.log"
    log_message "Celery worker logs: $LOG_DIR/celery_worker.log"
    log_message "Celery beat logs: $LOG_DIR/celery_beat.log"
    log_message "To stop all services: pkill -f 'celery|redis-server|python.*manage.py'"
    log_message "========================================="

    log_message "Running processes:"
    pgrep -fa "redis-server|celery|python.*manage.py" | while read -r process; do
        log_message "$process"
    done
}

# Run the main function
restart_services