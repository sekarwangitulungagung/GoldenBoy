#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <Adafruit_TinyUSB.h>
#include <MIDI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "hardware/watchdog.h"

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

Adafruit_USBD_MIDI usb_midi;
MIDI_CREATE_INSTANCE(Adafruit_USBD_MIDI, usb_midi, MIDI);

RF24 radio(17, 18); // CE, CSN

const uint64_t pipes[8] = {
  0xE8E8F0F0E1LL, 0xE8E8F0F0E2LL, 0xE8E8F0F0E3LL, 0xE8E8F0F0E4LL,
  0xE8E8F0F0E5LL, 0xE8E8F0F0E6LL, 0xE8E8F0F0E7LL, 0xE8E8F0F0E8LL
};

struct Payload { byte id; byte status; };
byte camStatus[9]; // Status: 0=IDLE, 1=LIVE(Merah), 2=PREVIEW(Hijau)
bool camOnline[9];

const int buttonPins[10] = {2, 3, 6, 7, 8, 9, 13, 14, 15, 16};
unsigned long lastPress[10];
bool lastButtonState[10]; // TAMBAHAN: Untuk melacak status terakhir tombol

const int potPin = 26;
int lastPot = -1;
int lastRawPot = -1; // TAMBAHAN: Untuk filter noise T-Bar yang lebih halus

#define LED_TX 20
#define LED_ERR 21

// --- VARIABEL STATE SWITCHER ---
int activeLive = 1;    // Default start Kamera 1 Live
int activePreview = 2; // Default start Kamera 2 Preview

void kirimKeTally(byte id, byte status) {
  Payload p; p.id = id; p.status = status;
  digitalWrite(LED_TX, HIGH);
  radio.openWritingPipe(pipes[id - 1]);
  camOnline[id] = radio.write(&p, sizeof(p));
  digitalWrite(LED_TX, LOW);
}

void updateTallyStates() {
  for (int i = 1; i <= 8; i++) {
    byte newStatus = 0; 
    
    if (i == activeLive) {
      newStatus = 1; // LIVE
    } else if (i == activePreview) {
      newStatus = 2; // PREVIEW
    }
    
    if (camStatus[i] != newStatus) {
      camStatus[i] = newStatus;
      kirimKeTally(i, newStatus);
    }
  }
  drawUI(); 
}

// TAMBAHAN: Fungsi untuk melakukan PING ke semua kamera saat alat dinyalakan
void pingAllCamerasAtStartup() {
  for (int i = 1; i <= 8; i++) {
    camStatus[i] = (i == activeLive) ? 1 : ((i == activePreview) ? 2 : 0);
    kirimKeTally(i, camStatus[i]);
    delay(5); // Jeda kecil agar radio NRF tidak "tersumbat" saat kirim data beruntun
  }
  drawUI();
}

void handleNoteOn(byte channel, byte pitch, byte velocity) { /* Dikosongkan */ }
void handleNoteOff(byte channel, byte pitch, byte velocity) { /* Dikosongkan */ }

void initRadio() {
  SPI1.setSCK(10); SPI1.setTX(11); SPI1.setRX(12); SPI1.begin();
  if(radio.begin(&SPI1)) {
    radio.setDataRate(RF24_250KBPS);
    radio.setPALevel(RF24_PA_MAX);
    radio.setRetries(3, 10);
    radio.setChannel(76);
    digitalWrite(LED_ERR, LOW);
  } else { digitalWrite(LED_ERR, HIGH); }
}

void drawUI() {
  display.clearDisplay();
  display.setCursor(0, 0); display.print("ULTRA PRO 4.1");
  for (int i = 1; i <= 8; i++) {
    int col = (i > 4) ? 64 : 0;
    int row = (i > 4) ? (i - 4) * 12 : i * 12;
    display.setCursor(col, row);
    display.print("C"); display.print(i); display.print(":");
    if (!camOnline[i]) display.print("OFF");
    else if (camStatus[i] == 1) display.print("LIV");
    else if (camStatus[i] == 2) display.print("PRV");
    else display.print("IDL");
  }
  display.display();
}

void setup() {
  watchdog_enable(4000, 1);
  MIDI.setHandleNoteOn(handleNoteOn);
  MIDI.setHandleNoteOff(handleNoteOff);
  MIDI.begin(MIDI_CHANNEL_OMNI);
  analogReadResolution(10); 

  pinMode(LED_TX, OUTPUT); pinMode(LED_ERR, OUTPUT);
  for (int i = 0; i < 10; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP); 
    lastPress[i] = 0;
    lastButtonState[i] = HIGH; // Set status awal ke HIGH (Tidak ditekan)
  }

  Wire.setSDA(4); Wire.setSCL(5); Wire.begin();
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.setTextColor(SSD1306_WHITE);

  initRadio(); 
  pingAllCamerasAtStartup(); // Panggil ping universal di awal
}

void loop() {
  watchdog_update();
  MIDI.read(); 

  for (int i = 0; i < 10; i++) {
    bool currentState = digitalRead(buttonPins[i]);
    
    // PERBAIKAN: Edge Detection + Debounce 50ms
    // Hanya dieksekusi jika tombol baru saja ditekan dari posisi terlepas
    if (currentState == LOW && lastButtonState[i] == HIGH && (millis() - lastPress[i] > 200)) { 
      
      // --- LOGIKA TOMBOL KAMERA 1-8 ---
      if (i < 8) { 
        int selectedCam = i + 1;
        
        if (activePreview == selectedCam) {
          activePreview = activeLive;
          activeLive = selectedCam;
        } else if (activeLive != selectedCam) {
          activePreview = selectedCam;
        }
        updateTallyStates(); 
      }
      
      // --- LOGIKA TOMBOL 9 (CUT) & 10 (AUTO) ---
      else if (i == 8 || i == 9) {
        int tempCam = activeLive;
        activeLive = activePreview;
        activePreview = tempCam;
        updateTallyStates();
      }
      
      MIDI.sendNoteOn(60 + i, 127, 1);
      MIDI.sendNoteOff(60 + i, 0, 1);
      
      lastPress[i] = millis(); // Catat waktu penekanan
    }
    
    lastButtonState[i] = currentState; // Simpan status tombol untuk siklus berikutnya
  }

  // --- LOGIKA POTENSIOMETER (T-BAR) DIPERBAIKI ---
  int rawPot = analogRead(potPin);
  // Toleransi perubahan raw 4 titik agar tidak loncat akibat noise analog listrik
  if (abs(rawPot - lastRawPot) > 4) { 
    int val = map(rawPot, 0, 1023, 0, 127);
    if (val != lastPot) { // Kirim MIDI hanya jika nilai map 0-127 benar-benar berubah
      MIDI.sendControlChange(1, val, 1);
      lastPot = val;
    }
    lastRawPot = rawPot;
  }
}