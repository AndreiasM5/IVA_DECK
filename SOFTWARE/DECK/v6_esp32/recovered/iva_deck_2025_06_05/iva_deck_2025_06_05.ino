// ESP32 - Test hardware complet: LCD ST7789, SD card, matrix keyboard (manual scan), microfon (I2S), VL53L0X, buzzer, potențiometre

#include <SPI.h>
#include <SD.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <Adafruit_VL53L0X.h>
#include <driver/i2s.h>
#include <driver/ledc.h>
#include <ArduinoJson.h>

#include "BluetoothSerial.h"
BluetoothSerial SerialBT;

// === PINOUT CONFIG ===
#define TFT_CS     13
#define TFT_DC     17
#define TFT_RST    16
#define TFT_BL     12

#define SD_CS      15
#define SD_PWR     0
#define SD_CLK_MOSI 23
#define SD_MISO    19
#define SD_SCK     18

#define BUZZER_PIN 5

// I2S Microfon
#define I2S_WS     25
#define I2S_SCK    26
#define I2S_SD     27

// VL53L0X
#define PROXY_SCL  22
#define PROXY_SDA  21
#define PROXY_XSHUT 4

// Matrix Keyboard manuală
const int numRows = 3;
const int numCols = 3;
const int rowPins[numRows] = {1, 3, 2};
const int colPins[numCols] = {14, 33, 32};
bool keyStates[numRows][numCols] = {false};
const char keymap[3][3] = {
  {'1','2','3'},
  {'4','5','6'},
  {'7','8','9'}
};

// Volume potențiometre
const int Volume0 = 36;
const int Volume1 = 39;
const int Volume2 = 34;
int previousVolume = 0;
int previousGameControl = 0;
int previousSpotifyControl = 0;

SPIClass spi = SPIClass(VSPI);
Adafruit_ST7789 tft = Adafruit_ST7789(&spi, TFT_CS, TFT_DC, TFT_RST);
Adafruit_VL53L0X lox = Adafruit_VL53L0X();

void resetSDPower() {
  pinMode(SD_PWR, OUTPUT);
  digitalWrite(SD_PWR, LOW);
  delay(500);
  digitalWrite(SD_PWR, HIGH);
  delay(300);
}

bool initSD() {
  SD.end();
  delay(100);
  for (int i = 0; i < 5; i++) {
    pinMode(SD_CS, OUTPUT);
    digitalWrite(SD_CS, HIGH); delay(5);
    digitalWrite(SD_CS, LOW);  delay(5);
    digitalWrite(SD_CS, HIGH); delay(5);
    if (SD.begin(SD_CS, spi)) return true;
    delay(300);
  }
  return false;
}

void initLCD() {
  tft.init(240, 240);
  tft.setRotation(0);
  ledcSetup(0, 5000, 8);
  ledcAttachPin(TFT_BL, 0);
  ledcWrite(0, 255);
  tft.fillScreen(ST77XX_BLACK);
  tft.setCursor(10, 10);
  tft.setTextSize(2);
  tft.setTextColor(ST77XX_GREEN);
  tft.println("LCD OK");
}

void testBuzzer() {
  tone(BUZZER_PIN, 1000, 200);
  delay(300);
  tone(BUZZER_PIN, 1500, 200);
  delay(300);
}

void scanKeypadManual() {
  for (int row = 0; row < numRows; row++) {
    digitalWrite(rowPins[row], LOW);
    for (int col = 0; col < numCols; col++) {
      if (digitalRead(colPins[col]) == LOW) {
        if (!keyStates[row][col]) {
          char key = keymap[row][col];
//          SerialBT.print("Tasta: "); SerialBT.println(key);
          sendEvent("key", "pressed", key);
          keyStates[row][col] = true;
        }
      } else {
        keyStates[row][col] = false;
      }
    }
    digitalWrite(rowPins[row], HIGH);
  }
}

void testVL53L0X() {
  digitalWrite(PROXY_XSHUT, HIGH);
  delay(10);
  if (!lox.begin()) {
    tft.setTextColor(ST77XX_RED);
    tft.println("VL53 FAIL");
    return;
  }
  VL53L0X_RangingMeasurementData_t measure;
  lox.rangingTest(&measure, false);
  sendEvent("proxy", "distance", measure.RangeMilliMeter);
}

void testI2SMicrophone() {
  const i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 16000,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 64
  };
  const i2s_pin_config_t pin_config = {
    I2S_SCK,
    I2S_WS,
    I2S_PIN_NO_CHANGE,
    I2S_SD
  };
  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_config);
  int16_t buffer[64];
  size_t bytes_read;
  i2s_read(I2S_NUM_0, &buffer, sizeof(buffer), &bytes_read, portMAX_DELAY);;
  i2s_driver_uninstall(I2S_NUM_0);
}

void sendEvent(const char* type, const char* key, int value) {
  StaticJsonDocument<128> doc;
  doc["type"] = type;
  doc["key"] = key;
  doc["value"] = value;
  serializeJson(doc, SerialBT);
  SerialBT.println(); // trimitem și newline ca delimitator
}

void listSD(File dir, int numTabs = 0) {
  while (true) {
    File entry = dir.openNextFile();
    if (!entry) break;
    for (int i = 0; i < numTabs; i++) SerialBT.print('\t');
    SerialBT.print(entry.name());
    if (entry.isDirectory()) {
      SerialBT.println("/");
      listSD(entry, numTabs + 1);
    } else {
      SerialBT.print("\t\t");
      SerialBT.println(entry.size());
    }
    entry.close();
  }
}

void setup() {
  SerialBT.begin("IVA_Deck_FINAL"); // nume Bluetooth vizibil
  SerialBT.println("Bluetooth Serial pornit");
  delay(300);

  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(PROXY_XSHUT, OUTPUT);
  digitalWrite(PROXY_XSHUT, LOW);
  delay(10);

  spi.begin(SD_SCK, SD_MISO, SD_CLK_MOSI, SD_CS);

  Wire.begin(PROXY_SDA, PROXY_SCL);
  resetSDPower();
  bool sdOK = initSD();

  // Setup tastatură
  for (int col = 0; col < numCols; col++) {
    pinMode(colPins[col], INPUT_PULLUP);
  }
  for (int row = 0; row < numRows; row++) {
    pinMode(rowPins[row], OUTPUT);
    digitalWrite(rowPins[row], HIGH);
  }

  testBuzzer();
  initLCD();
  tft.setTextColor(ST77XX_WHITE);
  tft.setCursor(0, 60);
  tft.print("SD card: ");
  tft.println(sdOK ? "OK" : "FAIL");
//  testVL53L0X();
//  testI2SMicrophone();
}

unsigned long lastVL53Read = 0;
const unsigned long vl53Interval = 200;

File uploadFile;
bool receivingUpload = false;
size_t remainingBytes = 0;

void loop() {
  scanKeypadManual();

  int volumeReading = analogRead(Volume0);
  int gameControlReading = analogRead(Volume1);
  int spotifyControlReading = analogRead(Volume2);

  if (abs(previousVolume - volumeReading) > 200) {
    sendEvent("volume", "master", volumeReading);
    previousVolume = volumeReading;
  }
  if (abs(previousGameControl - gameControlReading) > 200) {
    sendEvent("volume", "game", gameControlReading);
    previousGameControl = gameControlReading;
  }
  if (abs(previousSpotifyControl - spotifyControlReading) > 200) {
    sendEvent("volume", "spotify", spotifyControlReading);
    previousSpotifyControl = spotifyControlReading;
  }

//  if (millis() - lastVL53Read >= vl53Interval) {
//  VL53L0X_RangingMeasurementData_t measure;
//  lox.rangingTest(&measure, false);
//  sendEvent("proxy", "distance", measure.RangeMilliMeter);
//  lastVL53Read = millis();
//  }

  // === Upload binar ===
  while (receivingUpload && SerialBT.available()) {
    uint8_t byte = SerialBT.read();
    uploadFile.write(byte);
    remainingBytes--;

    if (remainingBytes <= 0) {
      uploadFile.close();
      receivingUpload = false;

      tft.fillRect(0, 60, 240, 10, ST77XX_BLACK);
      tft.setCursor(0, 60);
      tft.setTextColor(ST77XX_WHITE);
      tft.print("Upload Done");

      SerialBT.println("{\"status\":\"upload_complete\"}");
    }
  }

  // === Comenzi JSON ===
  if (!receivingUpload && SerialBT.available()) {
    String msg = SerialBT.readStringUntil('\n');

    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, msg);

    if (!error) {
      String cmd = doc["cmd"].as<String>();

//      // Upload start
//      if (cmd == "upload_start") {
//        String filename = doc["filename"].as<String>();
//        filename.trim();
//        if (!filename.startsWith("/")) filename = "/" + filename;
//        remainingBytes = doc["size"];
//
//        SerialBT.print(">> Upload request pentru: ");
//        SerialBT.print(filename);
//        SerialBT.print(" (");
//        SerialBT.print(remainingBytes);
//        SerialBT.println(" bytes)");
//
//        if (SD.exists(filename)) SD.remove(filename);
//        uploadFile = SD.open(filename.c_str(), FILE_WRITE);
//
//        SerialBT.print("uploadFile is ");
//        SerialBT.println(uploadFile ? "valid" : "null");
//
//        tft.fillRect(0, 60, 240, 10, ST77XX_BLACK);
//        tft.setCursor(0, 60);
//        tft.setTextColor(ST77XX_WHITE);
//
//        if (uploadFile) {
//          receivingUpload = true;
//          tft.print("Upload Ready");
//          SerialBT.print("{\"status\":\"upload_ready\",\"filename\":\"");
//          SerialBT.print(filename);
//          SerialBT.println("\"}");
//        } else {
//          tft.print("Upload Failed");
//          SerialBT.print("{\"error\":\"file_open_failed\",\"filename\":\"");
//          SerialBT.print(filename);
//          SerialBT.println("\"}");
//        }
//      }

      // Buzz
      if (cmd == "buzz") {
        int freq = doc["freq"] | 1000;
        int dur = doc["duration"] | 300;
        tone(BUZZER_PIN, freq, dur);
        SerialBT.println("{\"status\":\"buzz_ok\"}");
      }

      // List SD
      else if (cmd == "list_sd") {
        File root = SD.open("/");
        if (root) {
          SerialBT.println("{\"status\":\"listing_sd\"}");
          listSD(root);
          root.close();
        } else {
          SerialBT.println("{\"error\":\"sd_open_failed\"}");
        }
      }

else if (cmd == "display_raw") {
  String filename = doc["filename"].as<String>();
  filename.trim();
  if (!filename.startsWith("/")) filename = "/" + filename;

  SerialBT.print("{\"info\":\"trying_to_open\",\"filename\":\"");
  SerialBT.print(filename);
  SerialBT.println("\"}");

  File f = SD.open(filename.c_str(), FILE_READ);
  if (!f) {
    SerialBT.print("{\"error\":\"file_not_found\",\"filename\":\"");
    SerialBT.print(filename);
    SerialBT.println("\"}");
    return;
  }

  const int w = 240, h = 240;
  const int linePixels = w;
  uint16_t lineBuffer[linePixels];  // 480 bytes per linie

  tft.fillRect(0, 220, 240, 20, ST77XX_BLACK);
  tft.setCursor(0, 220);
  tft.setTextColor(ST77XX_YELLOW);
  tft.print("Drawing raw...");

  SerialBT.println("{\"info\":\"start_draw_loop\"}");

  for (int y = 0; y < h; y++) {
    int bytesRead = f.read((uint8_t*)lineBuffer, w * 2);
    if (bytesRead < w * 2) {
      SerialBT.print("{\"warn\":\"short_read\",\"line\":");
      SerialBT.print(y);
      SerialBT.println("}");
      break;
    }

    tft.drawRGBBitmap(0, y, lineBuffer, w, 1);  // desenăm linie cu linie

    if (y % 60 == 0) {
      SerialBT.print("{\"progress_line\":");
      SerialBT.print(y);
      SerialBT.println("}");
    }
  }

  f.close();

  tft.fillRect(0, 220, 240, 20, ST77XX_BLACK);
  tft.setCursor(0, 220);
  tft.setTextColor(ST77XX_GREEN);
  tft.print("Draw complete");

  SerialBT.print("{\"status\":\"draw_raw_ok\",\"filename\":\"");
  SerialBT.print(filename);
  SerialBT.println("\"}");
}

    } else {
      SerialBT.print("{\"error\":\"invalid_json\",\"raw\":\"");
      SerialBT.print(msg);
      SerialBT.println("\"}");
    }
  }

  delay(100);
}
