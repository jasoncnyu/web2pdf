#!/bin/bash

restart_service() {
    local service=$1
    local description=$2

    if systemctl is-active --quiet "$service"; then
        echo "🔁 Restarting $description ($service)..."
    else
        echo "⚠️ $description is not currently running. Attempting to start..."
    fi

    sudo systemctl restart "$service"

    if systemctl is-active --quiet "$service"; then
        echo "✅ $description is now running."
    else
        echo "❌ Failed to start $description."
        echo "🔍 Use: journalctl -u $service -e"
        exit 1
    fi
}

restart_service "redis6" "Redis"
restart_service "celery" "Celery Worker"
restart_service "gunicorn_flask" "Flask (Gunicorn)"

echo "🔄 All services processed."
