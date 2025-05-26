#!/bin/bash

start_service() {
    local service=$1
    local description=$2

    if systemctl is-active --quiet "$service"; then
        echo "✅ $description ($service) is already running."
    else
        echo "🔄 Starting $description ($service)..."
        sudo systemctl enable "$service"
        sudo systemctl start "$service"

        if systemctl is-active --quiet "$service"; then
            echo "✅ $description started successfully."
        else
            echo "❌ Failed to start $description. Check: journalctl -u $service -e"
            exit 1
        fi
    fi
}

start_service "redis6" "Redis"
start_service "celery" "Celery Worker"
start_service "gunicorn_flask" "Flask (Gunicorn)"

echo "🚀 All services are active."
echo "📄 Logs: journalctl -u celery -f | gunicorn_flask -f | redis6 -f"
