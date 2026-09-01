#!/usr/bin/env bash
# ==============================================================================
# CYBER_VOLT // macOS One-Click Installer & Persistent Widget Setup
# Developed for Yahia Bin Zaman
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================================="
echo "  CYBER_VOLT // PowerPulse macOS Installer"
echo "  System Architect: Yahia Bin Zaman"
echo "=========================================================="

APP_DEST="/Applications/PowerPulse.app"

# 1. Compile Native Swift Status Bar Widget
echo "[*] [1/5] Compiling Native Swift Menu Bar App..."
swiftc -O -o "$DIR/mac_widget/PowerPulseBar" "$DIR/mac_widget/PowerPulseBar.swift"

# 2. Package Self-Contained App Bundle
echo "[*] [2/5] Building Self-Contained PowerPulse.app..."
mkdir -p "$DIR/dist/PowerPulse.app/Contents/MacOS"
mkdir -p "$DIR/dist/PowerPulse.app/Contents/Resources"

cp "$DIR/mac_widget/PowerPulseBar" "$DIR/dist/PowerPulse.app/Contents/MacOS/"
cp "$DIR/app.py" "$DIR/dist/PowerPulse.app/Contents/Resources/"
cp "$DIR/power_engine.py" "$DIR/dist/PowerPulse.app/Contents/Resources/"
cp -R "$DIR/static" "$DIR/dist/PowerPulse.app/Contents/Resources/"

cat << 'EOF' > "$DIR/dist/PowerPulse.app/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>PowerPulseBar</string>
    <key>CFBundleIdentifier</key>
    <string>com.yahiabinzaman.powerpulse</string>
    <key>CFBundleName</key>
    <string>PowerPulse</string>
    <key>CFBundleDisplayName</key>
    <string>PowerPulse</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>4.2</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF
chmod +x "$DIR/dist/PowerPulse.app/Contents/MacOS/PowerPulseBar"

# 3. Create .DMG Installer Disk Image
echo "[*] [3/5] Creating PowerPulse-Installer.dmg..."
mkdir -p "$DIR/dist/dmg_root"
rm -rf "$DIR/dist/dmg_root/*"
cp -R "$DIR/dist/PowerPulse.app" "$DIR/dist/dmg_root/"
ln -sf /Applications "$DIR/dist/dmg_root/Applications"
rm -f "$DIR/PowerPulse-Installer.dmg"
hdiutil create -volname "PowerPulse" -srcfolder "$DIR/dist/dmg_root" -ov -format UDZO "$DIR/PowerPulse-Installer.dmg" > /dev/null

# 4. Install App into /Applications
echo "[*] [4/5] Installing to /Applications/PowerPulse.app..."
pkill -f PowerPulseBar || true
rm -rf "$APP_DEST"
cp -R "$DIR/dist/PowerPulse.app" /Applications/

# 5. Register macOS LaunchAgent (Persistent on Reboot / Shutdown)
echo "[*] [5/5] Configuring Persistent Auto-Start on macOS Boot..."
PLIST_PATH="$HOME/Library/LaunchAgents/com.yahiabinzaman.powerpulse.plist"
mkdir -p "$HOME/Library/LaunchAgents"

cat << EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.yahiabinzaman.powerpulse</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/PowerPulse.app/Contents/MacOS/PowerPulseBar</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOF

# Start Application Now
echo "[*] Starting PowerPulse..."
open /Applications/PowerPulse.app

echo "=========================================================="
echo " [OK] INSTALLATION COMPLETE!"
echo " - PowerPulse installed to /Applications/PowerPulse.app"
echo " - DMG Created: PowerPulse-Installer.dmg"
echo " - Persistent Auto-Start on Boot: ENABLED"
echo " - Statusbar Widget is ACTIVE in top menu bar!"
echo "=========================================================="
