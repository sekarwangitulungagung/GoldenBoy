# GOLDENBOY - Tally Control Suite

GOLDENBOY adalah aplikasi native PyQt6 untuk kontrol tally broadcast dengan integrasi langsung ke OBS Studio atau vMix, serta output MIDI ke hardware Arduino/Pico untuk lampu tally fisik.

## Highlight

- UI modern, responsif, dan animatif (native desktop, bukan webview)
- Theme engine: `qdarktheme` + icon pack `qtawesome`
- Integrasi switcher:
  - OBS Studio (WebSocket v5)
  - vMix (HTTP API)
- Mode runtime:
  - `APP_MODE=production`: wajib hardware MIDI (Arduino/Pico)
  - `APP_MODE=development`: tanpa hardware, tersedia shortcut test dan klik kartu
- Database SQLite (`goldenboy_config.db`) untuk menyimpan konfigurasi terakhir
- Cross-platform: macOS, Windows, Linux (dengan Python 3.10+)

## Requirement

Install semua dependency dari file `requirements.txt`:

```bash
pip install -r requirements.txt
```

Library yang digunakan:

- PyQt6
- pyqtdarktheme (Python < 3.12)
- qdarkstyle (fallback Python >= 3.12)
- qtawesome
- obsws-python
- mido
- python-rtmidi
- python-dotenv
- requests

## Konfigurasi Environment

Salin `.env.example` menjadi `.env`, lalu sesuaikan:

```dotenv
# OBS
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=

# vMix
VMIX_HOST=localhost
VMIX_PORT=8088

# Pilihan switcher: obs | vmix
SWITCHER_TYPE=obs

# MIDI
MIDI_PORT_NAME=Arduino MIDI

# App
APP_MODE=development
CHANNEL_COUNT=8
```

## Menjalankan Aplikasi

```bash
python main.py
```

## Development Test Mode

Saat `APP_MODE=development`, Anda dapat test tanpa Arduino:

- `1..8` -> set channel menjadi PROGRAM
- `Ctrl+1..8` -> set channel menjadi PREVIEW
- `Shift+1..8` -> set channel menjadi IDLE
- Klik kartu channel juga bisa untuk cycle state

## Production Mode (Hardware Arduino)

Saat `APP_MODE=production`:

- Aplikasi akan mencoba konek ke switcher (OBS/vMix)
- Aplikasi akan membuka MIDI port dari `MIDI_PORT_NAME`
- Jika MIDI tidak tersedia, koneksi dianggap gagal
- Mapping MIDI:
  - PROGRAM: Note `1..N`
  - PREVIEW: Note `11..(10+N)`
  - IDLE: kirim `note_off` untuk keduanya

## Struktur Utama Proyek

```text
main.py
logic/
  app_controller.py      # Runtime controller (mode, polling, MIDI, switcher)
  switcher_clients.py    # Klien OBS/vMix
  config_store.py        # SQLite config store
styles/
  modern_styles.py       # QSS untuk tampilan modern
```

## Build Notes

Sebelum build executable, pastikan dependency sudah terpasang dari `requirements.txt` agar proses build tidak gagal karena paket kurang.
