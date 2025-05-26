#!/bin/bash

stop_service() {
    local service=$1
    local description=$2

    if systemctl is-active --quiet "$service"; then
        echo "⏹️ Stopping $description ($service)..."
        sudo systemctl stop "$service"

        if systemctl is-active --quiet "$service"; then
            echo "❌ Failed to stop $description."
        else
            echo "✅ $description stopped successfully."
        fi
    else
        echo "⚠️ $description is not running."
    fi
}

stop_service "gunicorn_flask" "Flask (Gunicorn)"
stop_service "celery" "Celery Worker"
stop_service "redis6" "Redis"

echo "🛑 All services processed."
