# Sekar Wangi Tally Pro Control v4.1 - macOS Installation

## 📦 Installation

### Option 1: Using .app Bundle (Recommended)
1. Download the `SekarWangiTally.app` bundle
2. Copy to your Applications folder: `cp -r SekarWangiTally.app /Applications/`
3. First run: Right-click the app → Open (to bypass Gatekeeper)

### Option 2: Manual Installation
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Run the application
python3 main.py
```

## 🚀 Quick Start

1. **Connect Hardware**: Ensure Arduino/Raspberry Pi Pico is connected via USB
2. **Configure OBS**: Set up OBS WebSocket server
3. **Edit Configuration**: Modify `.env` file in the app bundle Resources folder
4. **Run Application**: Double-click the app icon in Applications

## ⚙️ Configuration

The app bundle contains a `.env` file in:
`SekarWangiTally.app/Contents/Resources/.env`

Edit this file to configure:
- OBS WebSocket settings (host, port, password)
- vMix API settings (for future integration)
- MIDI device settings

## 🔧 System Requirements

- macOS 10.13 (High Sierra) or later
- Python 3.9+ (automatically installed by the app if needed)
- Arduino/Raspberry Pi Pico with MIDI support
- OBS Studio with WebSocket plugin

## 🆘 Troubleshooting

- **Gatekeeper Block**: Right-click app → Open, then click Open in dialog
- **ModuleNotFoundError (qtawesome, PyQt6, etc.)**:
  ```bash
  # Run the automatic fix script
  chmod +x fix_dependencies.command
  ./fix_dependencies.command

  # Or manually reinstall dependencies
  python3 -m pip install --user --force-reinstall -r requirements.txt

  # Restart Terminal after installation
  ```
- **Permission Issues**: Check System Preferences → Security & Privacy → Accessibility
- **MIDI Not Found**: Check Audio MIDI Setup in Applications/Utilities
- **OBS Connection**: Verify WebSocket server is running in OBS
- **Dependencies**: Run `python3 -m pip install --user -r requirements.txt`

## 📞 Support

- GitHub: https://github.com/sekarwangitulungagung/GoldenBoy
- Check README.md for detailed documentation

---
**Version**: 4.1 | **Platform**: macOS | **Release Date**: April 2026