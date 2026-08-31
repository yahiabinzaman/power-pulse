#!/usr/bin/env bash
# ==============================================================================
# CYBER_VOLT // macOS Native Menu Bar Status Widget Launcher
# Developed for Yahia Bin Zaman
# ==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# 1. Start background Python telemetry engine if not already running
if ! pgrep -f "app.py" > /dev/null; then
    echo "⚡ Starting PowerPulse Telemetry Daemon..."
    nohup python3 "$DIR/app.py" > /dev/null 2>&1 &
    sleep 1
fi

# 2. Launch Native macOS Menu Bar Widget App
echo "🚀 Launching Native macOS Status Bar Widget..."
open "$DIR/mac_widget/PowerPulseBar.app"

echo "✅ CYBER_VOLT is now active in your macOS Menu Bar (Top Right)!"
