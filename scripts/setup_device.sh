#!/usr/bin/env bash
# Script to verify ADB connection to iQOO / Android device and configure permissions.

set -e

echo "=== NEXUS iQOO Device Setup & Diagnostic ==="

if ! command -v adb &> /dev/null; then
    echo "[-] Error: 'adb' command not found in PATH."
    echo "    Please install Android Platform Tools: sudo apt install adb (or download platform-tools)"
    exit 1
fi

echo "[+] Checking connected devices..."
adb devices -l

DEVICES=$(adb devices | grep -v "List of devices" | grep "device" | awk '{print $1}')

if [ -z "$DEVICES" ]; then
    echo "[!] No device authorized or detected."
    echo "    1. Connect iQOO phone via USB."
    echo "    2. Enable Developer Options -> USB Debugging."
    echo "    3. Authorize the computer on the phone screen."
    exit 1
fi

echo "[+] Found device: $DEVICES"
echo "[+] Checking UIAutomator support..."
adb shell uiautomator dump /data/local/tmp/test_dump.xml
echo "[+] UIAutomator dump test succeeded!"

echo "[+] Device is fully prepared for NEXUS runtime!"
