#!/bin/bash
# Sekar Wangi Tally Pro Control - Linux Installation Script

echo "Sekar Wangi Tally Pro Control v4.1 - Linux Installer"
echo "=================================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root. Please run as normal user."
   exit 1
fi

# Check for required dependencies
echo "Checking dependencies..."

# Check if Python 3.9+ is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.9 or higher."
    echo "On Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "On CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "On Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION or higher is required."
    exit 1
fi

echo "Python $PYTHON_VERSION found ✓"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3."
    exit 1
fi

echo "pip3 found ✓"

# Install Python dependencies
echo "Installing Python dependencies..."
echo "This may take a few minutes..."

# Try to install with --user flag first
pip3 install --user -r requirements.txt

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo "User installation failed, trying system-wide installation..."
    echo "You may be prompted for sudo password..."
    sudo pip3 install -r requirements.txt

    if [ $? -ne 0 ]; then
        echo "Failed to install Python dependencies."
        echo "Please try installing manually:"
        echo "pip3 install --user -r requirements.txt"
        echo "or"
        echo "sudo pip3 install -r requirements.txt"
        exit 1
    fi
fi

# Verify critical packages are installed
echo "Verifying installation..."
python3 -c "import PyQt6; print('PyQt6 ✓')"
python3 -c "import obsws_python; print('obsws-python ✓')"
python3 -c "import mido; print('mido ✓')"
python3 -c "import qtawesome; print('qtawesome ✓')"
python3 -c "import dotenv; print('python-dotenv ✓')"

if [ $? -ne 0 ]; then
    echo "Some packages failed to import. Please check your Python installation."
    exit 1
fi

echo "Dependencies installed ✓"

# Create desktop entry
echo "Creating desktop entry..."
mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/sekar-wangi-tally.desktop << EOF
[Desktop Entry]
Name=Sekar Wangi Tally Pro Control
Comment=Professional MIDI Tally Light Management System
Exec=$HOME/.local/bin/sekar-wangi-tally
Icon=$HOME/.local/share/sekar-wangi-tally/icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Audio;
StartupNotify=true
EOF

echo "Desktop entry created ✓"

# Copy application files
echo "Installing application files..."
mkdir -p ~/.local/share/sekar-wangi-tally
mkdir -p ~/.local/bin

cp main.py ~/.local/share/sekar-wangi-tally/
cp -r styles ~/.local/share/sekar-wangi-tally/
cp -r logic ~/.local/share/sekar-wangi-tally/
cp .env ~/.local/share/sekar-wangi-tally/
cp README.md ~/.local/share/sekar-wangi-tally/

# Create launcher script
cat > ~/.local/bin/sekar-wangi-tally << EOF
#!/bin/bash
cd ~/.local/share/sekar-wangi-tally
python3 main.py
EOF

chmod +x ~/.local/bin/sekar-wangi-tally

echo "Application installed ✓"
echo ""
echo "Installation completed successfully!"
echo ""
echo "To run the application:"
echo "1. From terminal: sekar-wangi-tally"
echo "2. From applications menu: Search for 'Sekar Wangi Tally Pro Control'"
echo ""
echo "Configuration file: ~/.local/share/sekar-wangi-tally/.env"
echo "Edit this file to configure OBS WebSocket and MIDI settings."
echo ""
echo "For uninstallation, run: rm -rf ~/.local/share/sekar-wangi-tally ~/.local/bin/sekar-wangi-tally ~/.local/share/applications/sekar-wangi-tally.desktop"