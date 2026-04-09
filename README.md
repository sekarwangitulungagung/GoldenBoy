# **Sekar Wangi Tally Pro Control v4.1**

**Sekar Wangi Tally Pro Control** adalah solusi perangkat lunak manajemen lampu Tally profesional yang menjembatani OBS Studio dengan perangkat keras berbasis MIDI (seperti Raspberry Pi Pico atau Arduino). Software ini dirancang dengan antarmuka modern yang terinspirasi dari standar industri penyiaran (Blackmagic Design) untuk memudahkan operator memantau status kamera secara real-time.

## **🚀 Fitur Utama**

* **Real-time Synchronization**: Sinkronisasi instan antara status *Scene* di OBS Studio (Program & Preview) dengan lampu Tally fisik.  
* **Modern Dark UI**: Antarmuka berbasis PyQt6 dengan kontras tinggi, ideal untuk lingkungan kontrol yang gelap (Control Room).  
* **8-Channel Dashboard**: Monitor visual untuk 8 kamera sekaligus langsung dari layar komputer.  
* **Smart MIDI Routing**:  
  * **Note 1 \- 8**: Mengaktifkan lampu **LIVE/PROGRAM** (Merah).  
  * **Note 11 \- 18**: Mengaktifkan lampu **PREVIEW** (Hijau).  
* **Auto-Detect Hardware**: Fitur pemindaian otomatis untuk mendeteksi perangkat MIDI (Pico/TinyUSB) yang terhubung.  
* **Multithreaded Engine**: Mesin pemrosesan terpisah dari UI, memastikan aplikasi tetap responsif tanpa *freeze/lag*.  
* **Activity Logging**: Konsol log real-time untuk memantau aktivitas koneksi dan pergantian scene.

## **🛠️ Teknologi yang Digunakan**

Aplikasi ini memanggil dan mengintegrasikan beberapa pustaka (libraries) utama:

1. **PyQt6**: Digunakan untuk membangun seluruh *User Interface* (GUI) yang responsif dan estetis.  
2. **obsws-python (v5)**: Pustaka komunikasi tingkat tinggi untuk berinteraksi dengan OBS Studio melalui protokol WebSocket.  
3. **Mido (MIDI Objects)**: Digunakan untuk mengolah pesan MIDI yang dikirim ke hardware.  
4. **python-rtmidi**: Sebagai backend MIDI yang stabil untuk sistem operasi Windows/Linux.  
5. **Re (Regular Expression)**: Digunakan untuk logika "Smart Matching", yaitu mengambil angka ID kamera secara otomatis dari nama Scene di OBS (misal: "CAM 1" atau "Kamera 2").

## **📋 Persyaratan Sistem**

* **OBS Studio v28.0** atau yang lebih baru.  
* **OBS WebSocket v5.x** (Sudah terintegrasi di OBS v28 ke atas).  
* **Hardware Tally**: Raspberry Pi Pico atau Arduino yang mendukung MIDI USB.  
* **Python 3.9+** (Jika menjalankan dari kode sumber).

## **📥 Panduan Instalasi (Development)**

Jika Anda ingin menjalankan atau mengembangkan kode ini, ikuti langkah berikut:

1. **Clone atau salin kode sumber.**  
2. **Instal dependensi melalui Terminal/CMD:**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Konfigurasi environment (opsional):**  
   Edit file `.env` untuk mengatur pengaturan OBS WebSocket, MIDI port, dll.

4. **Jalankan aplikasi:**  
   ```bash
   python main.py
   ```

## **🏗️ Struktur Proyek**

```
SekarWangi_MidiControll/
├── main.py                 # Entry point aplikasi utama
├── .env                    # Environment settings
├── requirements.txt        # Python dependencies
├── README.md              # Dokumentasi
├── styles/
│   └── ui_styles.py       # Styling antarmuka PyQt6
├── logic/
│   ├── obs_midi_handler.py # Logika OBS WebSocket & MIDI
│   └── ui_components.py   # Komponen UI (TallyBox)
└── arduino/
    └── client_tally/
        └── client_tally.ino  # Kode Arduino untuk hardware tally
```

## **📦 Cara Membuat File Executable (.EXE)**

Untuk mendistribusikan aplikasi ini sebagai software mandiri:

1. Instal auto-py-to-exe.  
2. Pilih file `main.py` sebagai script utama.
3. Konfigurasi build settings sesuai kebutuhan.  
3. Pilih opsi **"Window Based"** (untuk menyembunyikan konsol hitam).  
4. Tambahkan ikon (file .ico) untuk hasil yang lebih profesional.  
5. Klik **Convert**.

## **📖 Cara Penggunaan**

1. Pastikan OBS Studio sudah terbuka.  
2. Pergi ke menu Tools \-\> WebSocket Server Settings di OBS. Pastikan Server aktif dan catat passwordnya.  
3. Hubungkan perangkat Pico Tally Anda ke USB.  
4. Buka **Sekar Wangi Tally Pro Control**.  
5. Pilih perangkat MIDI Anda di dropdown (misal: "TinyUSB MIDI").  
6. Masukkan password OBS WebSocket.  
7. Klik **HUBUNGKAN**.  
8. Aplikasi akan mulai mengirim sinyal ke lampu setiap kali Anda mengganti scene di OBS.

**Developed with ❤️ for the Live Production Community.**

*Sekar Wangi \- Keanggunan dalam Teknologi.*