#!/bin/bash
# Sekar Wangi Tally Pro Control - macOS Installation Script

echo "Sekar Wangi Tally Pro Control v4.1 - macOS Installer"
echo "==================================================="

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "This script is for macOS only."
    exit 1
fi

# Check for Homebrew (optional but recommended)
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Installing Python 3 via Homebrew..."
    brew install python3
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION or higher is required."
    echo "Installing latest Python via Homebrew..."
    brew install python3
fi

echo "Python $PYTHON_VERSION found ✓"

# Install Python dependencies
echo "Installing Python dependencies..."
python3 -m pip install --user -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Failed to install Python dependencies."
    exit 1
fi

echo "Dependencies installed ✓"

# Copy app to Applications folder
echo "Installing application to Applications folder..."
if [ -d "/Applications/SekarWangiTally.app" ]; then
    echo "Removing existing installation..."
    rm -rf "/Applications/SekarWangiTally.app"
fi

cp -r "SekarWangiTally.app" "/Applications/"

if [ $? -ne 0 ]; then
    echo "Failed to copy app to Applications folder."
    exit 1
fi

echo "Application installed ✓"

# Make the launcher executable
chmod +x "/Applications/SekarWangiTally.app/Contents/MacOS/SekarWangiTally"

echo ""
echo "Installation completed successfully!"
echo ""
echo "To run the application:"
echo "1. Open Finder → Applications"
echo "2. Find 'SekarWangiTally' and double-click"
echo "3. First time: Right-click → Open (to bypass Gatekeeper)"
echo ""
echo "Configuration file: /Applications/SekarWangiTally.app/Contents/Resources/.env"
echo "Edit this file to configure OBS WebSocket and MIDI settings."
echo ""
echo "For uninstallation, drag the app from Applications to Trash."