#!/bin/bash

DJANGO_PID_FILE="/var/run/django.pid"
CELERY_PID_FILE="/var/run/celery.pid"
LOG_DIR="/var/log"
DJANGO_LOG_FILE="$LOG_DIR/django.log"
CELERY_LOG_FILE="$LOG_DIR/celery.log"
VENV_PATH="/opt/pd-enem/venv"  # Caminho do ambiente virtual
APP_DIR="/opt/pd-enem"  # Caminho da aplicação Django

# Função para registrar logs no formato correto
log_message() {
    local log_type=$1
    local log_title=$2
    local log_message=$3
    echo "$(date '+%Y-%m-%d %H:%M:%S')-$log_type-$log_title-$log_message" >> $DJANGO_LOG_FILE
}

start() {
    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR"
        log_message "INFO" "System" "Log directory created: $LOG_DIR"
    fi

    if [ ! -f "$DJANGO_LOG_FILE" ]; then
        touch "$DJANGO_LOG_FILE"
        log_message "INFO" "System" "Log file created: $DJANGO_LOG_FILE"
    fi

    if [ ! -f "$CELERY_LOG_FILE" ]; then
        touch "$CELERY_LOG_FILE"
        log_message "INFO" "System" "Celery log file created: $CELERY_LOG_FILE"
    fi

    # Iniciar Django (com manage.py runserver)
    if [ -f $DJANGO_PID_FILE ]; then
        DJANGO_PID=$(cat $DJANGO_PID_FILE)
        if ps -p $DJANGO_PID > /dev/null; then
            log_message "ERROR" "Django" "Django is already running (PID: $DJANGO_PID)."
            return 1
        else
            log_message "WARNING" "Django" "PID file exists but Django is not running. Removing stale PID file."
            rm -f $DJANGO_PID_FILE
        fi
    fi

    log_message "INFO" "Django" "Starting Django (python manage.py runserver)..."
    nohup $VENV_PATH/bin/python3 $APP_DIR/manage.py runserver 0.0.0.0:7000 > $DJANGO_LOG_FILE 2>&1 &
    echo $! > $DJANGO_PID_FILE
    log_message "INFO" "Django" "Django started with PID $(cat $DJANGO_PID_FILE)."

    # Iniciar Celery
    if [ -f $CELERY_PID_FILE ]; then
        CELERY_PID=$(cat $CELERY_PID_FILE)
        if ps -p $CELERY_PID > /dev/null; then
            log_message "ERROR" "Celery" "Celery is already running (PID: $CELERY_PID)."
            return 1
        else
            log_message "WARNING" "Celery" "PID file exists but Celery is not running. Removing stale PID file."
            rm -f $CELERY_PID_FILE
        fi
    fi

    log_message "INFO" "Celery" "Starting Celery worker..."
    nohup $VENV_PATH/bin/celery -A core worker --loglevel=info > $CELERY_LOG_FILE 2>&1 &
    echo $! > $CELERY_PID_FILE
    log_message "INFO" "Celery" "Celery worker started with PID $(cat $CELERY_PID_FILE)."
}

stop() {
    # Parar Django
    if [ -f $DJANGO_PID_FILE ]; then
        DJANGO_PID=$(cat $DJANGO_PID_FILE)
        if ps -p $DJANGO_PID > /dev/null; then
            log_message "INFO" "Django" "Stopping Django (PID: $DJANGO_PID)..."
            kill $DJANGO_PID
            rm -f $DJANGO_PID_FILE
            log_message "INFO" "Django" "Django stopped."
        else
            log_message "WARNING" "Django" "Django PID file exists but no such process is running. Removing stale PID file."
            rm -f $DJANGO_PID_FILE
        fi
    else
        log_message "ERROR" "Django" "Django is not running."
    fi

    # Parar Celery
    if [ -f $CELERY_PID_FILE ]; then
        CELERY_PID=$(cat $CELERY_PID_FILE)
        if ps -p $CELERY_PID > /dev/null; then
            log_message "INFO" "Celery" "Stopping Celery worker (PID: $CELERY_PID)..."
            kill $CELERY_PID
            rm -f $CELERY_PID_FILE
            log_message "INFO" "Celery" "Celery worker stopped."
        else
            log_message "WARNING" "Celery" "Celery PID file exists but no such process is running. Removing stale PID file."
            rm -f $CELERY_PID_FILE
        fi
    else
        log_message "ERROR" "Celery" "Celery worker is not running."
    fi
}

restart() {
    stop
    start
}

status() {
    if [ -f $DJANGO_PID_FILE ]; then
        DJANGO_PID=$(cat $DJANGO_PID_FILE)
        if ps -p $DJANGO_PID > /dev/null; then
            log_message "INFO" "Status" "Django is running (PID: $DJANGO_PID)."
        else
            log_message "ERROR" "Status" "Django PID file exists but the process is not running."
        fi
    else
        log_message "ERROR" "Status" "Django is not running."
    fi

    if [ -f $CELERY_PID_FILE ]; then
        CELERY_PID=$(cat $CELERY_PID_FILE)
        if ps -p $CELERY_PID > /dev/null; then
            log_message "INFO" "Status" "Celery worker is running (PID: $CELERY_PID)."
        else
            log_message "ERROR" "Status" "Celery PID file exists but the process is not running."
        fi
    else
        log_message "ERROR" "Status" "Celery worker is not running."
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
