#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_TEMPLATE="$SCRIPT_DIR/glow-controller.service"
export GLOW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
export GLOW_USER="$(whoami)"

if [[ ! -f "$SERVICE_TEMPLATE" ]]; then
    echo "Error: $SERVICE_TEMPLATE not found"
    exit 1
fi

echo "Installing glow-controller.service (GLOW_DIR=$GLOW_DIR)..."
envsubst '${GLOW_DIR} ${GLOW_USER}' < "$SERVICE_TEMPLATE" | sudo tee /etc/systemd/system/glow-controller.service > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable --now glow-controller

echo "Done. Check status with: sudo systemctl status glow-controller"
