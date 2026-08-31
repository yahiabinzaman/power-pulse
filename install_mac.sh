#!/usr/bin/env bash
# ==============================================================================
# CYBER_VOLT // macOS One-Click Installer & Widget Setup
# Developed for Yahia Bin Zaman
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================================="
echo "⚡ CYBER_VOLT // macOS Installer & Menu Bar Widget Setup"
echo "   System Architect: Yahia Bin Zaman"
echo "=========================================================="

APP_DEST="$HOME/Applications"
mkdir -p "$APP_DEST"

# 1. Compile Latest Swift Menu Bar Widget
echo "⚙️ [1/4] Compiling Native Menu Bar Widget (Swift)..."
swiftc -O -o "$DIR/mac_widget/PowerPulseBar" "$DIR/mac_widget/PowerPulseBar.swift"
mkdir -p "$DIR/mac_widget/PowerPulseBar.app/Contents/MacOS"
cp "$DIR/mac_widget/PowerPulseBar" "$DIR/mac_widget/PowerPulseBar.app/Contents/MacOS/"

# 2. Copy App to Applications folder
echo "📦 [2/4] Installing PowerPulse to $APP_DEST..."
cp -R "$DIR/mac_widget/PowerPulseBar.app" "$APP_DEST/"

# 3. Create Desktop Launcher
echo "🖥️ [3/4] Creating Desktop Launcher..."
DESKTOP_DIR="$HOME/Desktop"
cat << 'EOF' > "$DESKTOP_DIR/Launch CYBER_VOLT.command"
#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
"$HOME/Applications/PowerPulseBar.app/Contents/MacOS/PowerPulseBar" &
open "http://127.0.0.1:8765"
EOF
chmod +x "$DESKTOP_DIR/Launch CYBER_VOLT.command"

# 4. Set up Auto-Start on Boot (Login Items)
echo "🚀 [4/4] Configuring Auto-Start in macOS Menu Bar..."
osascript -e "tell application \"System Events\" to delete (login items whose name is \"PowerPulseBar\")" 2>/dev/null || true
osascript -e "tell application \"System Events\" to make login item at end with properties {path:\"$APP_DEST/PowerPulseBar.app\", hidden:false}" 2>/dev/null || true

# 5. Launch Application Now
echo "✨ Starting PowerPulse..."
pkill -f PowerPulseBar || true
open "$APP_DEST/PowerPulseBar.app"

echo "=========================================================="
echo "✅ INSTALLATION COMPLETE!"
echo "   • Menu Bar Widget is now PINNED to your top status bar!"
echo "   • Auto-Start on Boot is ACTIVE."
echo "   • Desktop shortcut created: 'Launch CYBER_VOLT.command'"
echo "=========================================================="
