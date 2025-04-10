#!/bin/bash

# Configuration
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DJANGO_APP_DIR="${BASE_DIR}/sports_news"
LOG_DIR="${BASE_DIR}/logs"
VENV_DIR="${BASE_DIR}/.venv"  # Assuming virtualenv is used
CELERY_WORKERS=1  # Hardcoded to 1 to avoid unnecessary memory usage

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

# Function to kill process by port for Django (more reliable than just pkill)
kill_process_by_port() {
    local PORT=$1
    local PID=$(lsof -ti:$PORT)
    
    if [ -n "$PID" ]; then
        log_message "Found process using port $PORT, PID: $PID. Killing..."
        kill $PID
        sleep 2
        
        # Check if still running and force kill if necessary
        if kill -0 $PID 2>/dev/null; then
            log_message "Process still running. Force killing PID: $PID"
            kill -9 $PID
            sleep 1
        fi
        
        # Verify port is now free
        if lsof -ti:$PORT >/dev/null; then
            log_message "ERROR: Port $PORT is still in use after kill attempts!"
            return 1
        else
            log_message "Port $PORT successfully freed"
        fi
    else
        log_message "No process found using port $PORT"
    fi
    
    return 0
}

# Function to stop all Django processes more thoroughly
stop_django_processes() {
    log_message "Stopping all Django processes..."
    
    # First, free up the port 8000
    kill_process_by_port 8000
    
    # Then also use pkill to catch any remaining Django processes
    if pgrep -f "python.*manage.py runserver" > /dev/null; then
        log_message "Killing Django server processes with pkill..."
        pkill -f "python.*manage.py runserver"
        sleep 2
        
        # Use more aggressive killing if needed
        if pgrep -f "python.*manage.py runserver" > /dev/null; then
            log_message "Some Django processes still running. Force killing..."
            pkill -9 -f "python.*manage.py runserver"
            sleep 1
            
            # Final check
            if pgrep -f "python.*manage.py runserver" > /dev/null; then
                log_message "ERROR: Failed to kill all Django processes despite multiple attempts."
                ps aux | grep "python.*manage.py runserver" | grep -v grep
                return 1
            fi
        fi
    fi
    
    # Final verification that port is free
    if lsof -ti:8000 >/dev/null; then
        log_message "ERROR: Port 8000 is still in use after all kill attempts!"
        lsof -i:8000
        return 1
    fi
    
    log_message "All Django server processes stopped successfully."
    return 0
}

# Function to check if Redis is running
check_redis_running() {
    if ! pgrep -x "redis-server" > /dev/null; then
        log_message "WARNING: Redis is not running. Some features may not work properly."
        return 1
    else
        log_message "Redis is running properly."
    fi
    return 0
}

# Function to stop and restart Celery worker with better control
restart_celery_worker() {
    # First, ensure we're in the Django app directory
    cd "$DJANGO_APP_DIR" || { 
        log_message "ERROR: Could not change to $DJANGO_APP_DIR directory"
        return 1
    }
    
    log_message "Stopping ALL Celery worker processes..."
    
    # Kill all celery workers, regardless of how they were started
    if pgrep -f "celery.*worker" > /dev/null; then
        # Show current celery processes before killing
        log_message "Current Celery worker processes:"
        ps aux | grep "celery.*worker" | grep -v grep
        
        # Kill all celery worker processes
        pkill -f "celery.*worker"
        sleep 3
        
        # Force kill any remaining celery processes
        if pgrep -f "celery.*worker" > /dev/null; then
            log_message "Some Celery workers still running. Force killing..."
            pkill -9 -f "celery.*worker"
            sleep 2
            
            # Final check
            if pgrep -f "celery.*worker" > /dev/null; then
                log_message "WARNING: Some Celery worker processes couldn't be killed"
                ps aux | grep "celery.*worker" | grep -v grep
            fi
        fi
    else
        log_message "No Celery worker processes found running."
    fi
    
    # Clear any leftover pid files that might cause issues
    rm -f "${DJANGO_APP_DIR}/celery.pid" 2>/dev/null
    
    # Wait to ensure sockets and resources are freed
    sleep 2
    
    log_message "Starting new Celery worker (single process)..."
    
    # Start with explicit options to prevent multiple workers
    celery -A "$(basename "$DJANGO_APP_DIR").celery" worker \
        --concurrency=1 \
        --max-tasks-per-child=100 \
        --loglevel=info \
        --without-gossip \
        --without-mingle \
        --pidfile="${DJANGO_APP_DIR}/celery.pid" \
        > "$LOG_DIR/celery_worker.log" 2>&1 &
    
    WORKER_PID=$!
    sleep 5
    
    # Verify worker started successfully
    if ps -p $WORKER_PID > /dev/null && pgrep -f "celery.*worker" > /dev/null; then
        log_message "Celery worker started successfully with PID: $WORKER_PID"
        log_message "Verifying worker count..."
        WORKER_COUNT=$(pgrep -f "celery.*worker" | wc -l)
        log_message "Total worker processes: $WORKER_COUNT"
        
        if [ "$WORKER_COUNT" -gt 2 ]; then
            log_message "WARNING: More worker processes than expected. This might use unnecessary memory."
        fi
    else
        log_message "ERROR: Celery worker failed to start."
        return 1
    fi
    return 0
}

# Function to restart Celery Beat with better control
restart_celery_beat() {
    # First, ensure we're in the Django app directory
    cd "$DJANGO_APP_DIR" || { 
        log_message "ERROR: Could not change to $DJANGO_APP_DIR directory"
        return 1
    }
    
    log_message "Stopping Celery Beat processes..."
    
    if pgrep -f "celery.*beat" > /dev/null; then
        # Show current celery beat processes
        log_message "Current Celery beat processes:"
        ps aux | grep "celery.*beat" | grep -v grep
        
        # Kill all celery beat processes
        pkill -f "celery.*beat"
        sleep 2
        
        # Force kill if necessary
        if pgrep -f "celery.*beat" > /dev/null; then
            log_message "Celery Beat still running. Force killing..."
            pkill -9 -f "celery.*beat"
            sleep 2
            
            # Final check
            if pgrep -f "celery.*beat" > /dev/null; then
                log_message "WARNING: Failed to kill all Celery Beat processes"
                ps aux | grep "celery.*beat" | grep -v grep
            fi
        fi
    else
        log_message "No Celery Beat processes found running."
    fi
    
    # Clear any leftover pid files
    rm -f "${DJANGO_APP_DIR}/celerybeat.pid" 2>/dev/null
    
    # Wait to ensure resources are freed
    sleep 2
    
    log_message "Starting Celery Beat..."
    
    # Start with explicit options to prevent issues
    celery -A "$(basename "$DJANGO_APP_DIR").celery" beat \
        --scheduler django_celery_beat.schedulers:DatabaseScheduler \
        --pidfile="${DJANGO_APP_DIR}/celerybeat.pid" \
        --max-interval=300 \
        > "$LOG_DIR/celery_beat.log" 2>&1 &
    
    BEAT_PID=$!
    sleep 3
    
    if ps -p $BEAT_PID > /dev/null && pgrep -f "celery.*beat" > /dev/null; then
        log_message "Celery Beat started successfully with PID: $BEAT_PID"
    else
        log_message "ERROR: Celery Beat failed to start."
        return 1
    fi
    return 0
}

# Function to restart Django server with better port checking
restart_django_server() {
    # First, ensure we're in the Django app directory
    cd "$DJANGO_APP_DIR" || { 
        log_message "ERROR: Could not change to $DJANGO_APP_DIR directory"
        return 1
    }
    
    # Make sure Django processes are stopped and port is free
    if ! stop_django_processes; then
        log_message "ERROR: Failed to stop existing Django processes. Please check manually."
        return 1
    fi
    
    # Double check the port is available
    if lsof -ti:8000 >/dev/null; then
        log_message "ERROR: Port 8000 is still in use. Cannot start Django server."
        lsof -i:8000
        return 1
    fi
    
    log_message "Starting Django server..."
    
    # Check Django configuration before starting
    python manage.py check > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        log_message "WARNING: Django check failed. There might be issues with your Django application."
        log_message "Running full check and showing errors:"
        python manage.py check
    fi
    
    # Start Django with explicit port and address
    python manage.py runserver 0.0.0.0:8000 > "$LOG_DIR/django.log" 2>&1 &
    DJANGO_PID=$!
    
    # Give it time to start
    sleep 5
    
    # Verify it's running and the correct process has the port
    if ps -p $DJANGO_PID > /dev/null; then
        log_message "Django server started with PID: $DJANGO_PID"
        
        # Check if our process actually has the port
        PORT_PID=$(lsof -ti:8000)
        if [ "$PORT_PID" = "$DJANGO_PID" ] || [ "$PORT_PID" = "$(pgrep -P $DJANGO_PID)" ]; then
            log_message "Confirmed Django server has port 8000"
        else
            log_message "WARNING: Django started but another process has port 8000: $PORT_PID"
        fi
        
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
        log_message "WARNING: High memory usage."
    fi

    if [ "$DISK_PCT" -gt 80 ]; then
        log_message "WARNING: High disk usage."
    fi
}

# Main function to restart Django and Celery
restart_django_and_celery() {
    log_message "========================================="
    log_message "Restarting Django and Celery services"
    log_message "========================================="

    # Check if we can activate the virtual environment
    ensure_virtualenv || {
        log_message "Failed to set up Python environment. Exiting."
        exit 1
    }
    
    # Check system resources
    check_system_resources
    
    # Check Redis is running but don't start/stop it
    check_redis_running
    
    # Restart Django server (after ensuring port is free)
    restart_django_server || {
        log_message "Django failed to restart. Exiting."
        exit 1
    }
    
    # Restart Celery components
    restart_celery_worker || {
        log_message "WARNING: Celery worker failed to restart, but continuing..."
    }
    
    restart_celery_beat || {
        log_message "WARNING: Celery beat failed to restart, but continuing..."
    }

    log_message "========================================="
    log_message "Services restarted, checking running processes:"
    log_message "Django logs: $LOG_DIR/django.log"
    log_message "Celery worker logs: $LOG_DIR/celery_worker.log"
    log_message "Celery beat logs: $LOG_DIR/celery_beat.log"
    log_message "========================================="

    ps aux | grep -E "redis-server|celery|python.*manage.py" | grep -v grep | while read -r process; do
        log_message "$process"
    done
    
    log_message "Memory usage after restart:"
    free -h | tee -a "$LOG_DIR/services.log"
}

# Run the main function
restart_django_and_celery