#!/bin/bash
# Fix script for ModuleNotFoundError issues

echo "Sekar Wangi Tally Pro Control - Dependency Fix Script"
echo "===================================================="

echo "This script will reinstall all Python dependencies to fix import errors."
echo ""

# Check if we're on Linux or macOS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PACKAGE_MANAGER="pip3"
    echo "Detected Linux system"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PACKAGE_MANAGER="python3 -m pip"
    echo "Detected macOS system"
else
    echo "Unsupported operating system"
    exit 1
fi

echo "Reinstalling Python dependencies..."
echo "This may take a few minutes..."
echo ""

# Force reinstall all packages
$PACKAGE_MANAGER install --user --force-reinstall -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Failed to reinstall dependencies."
    echo "Trying with sudo (you may be prompted for password)..."
    sudo pip3 install --force-reinstall -r requirements.txt

    if [ $? -ne 0 ]; then
        echo "Installation failed. Please check your internet connection and try again."
        exit 1
    fi
fi

echo ""
echo "Verifying installation..."

# Test each critical import
PACKAGES=("PyQt6" "obsws_python" "mido" "qtawesome" "dotenv")
FAILED_PACKAGES=()

for package in "${PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo "$package ✓"
    else
        echo "$package ✗ FAILED"
        FAILED_PACKAGES+=("$package")
    fi
done

echo ""

if [ ${#FAILED_PACKAGES[@]} -eq 0 ]; then
    echo "All dependencies installed successfully!"
    echo "Please restart your terminal and try running the application again."
else
    echo "The following packages failed to install:"
    printf '%s\n' "${FAILED_PACKAGES[@]}"
    echo ""
    echo "Please check your Python installation or try installing manually:"
    echo "python3 -m pip install --user <package_name>"
fi