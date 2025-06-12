#include <SPI.h>
#include <SD.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>

// ==== Config pini ====
#define TFT_CS     21
#define TFT_DC     17
#define TFT_RST    16
#define SD_CS      13
#define SD_PWR     12  // GPIO12 → control GND SD prin tranzistor

#define IMG_W 240
#define IMG_H 240

SPIClass spi = SPIClass(VSPI);
Adafruit_ST7789 tft = Adafruit_ST7789(&spi, TFT_CS, TFT_DC, TFT_RST);

// ===== Reset fizic al SD prin tranzistor =====
void resetSDPower() {
  pinMode(SD_PWR, OUTPUT);
  digitalWrite(SD_PWR, LOW);   // Tranzistor oprit → SD dezalimentat
  delay(500);                  // Așteaptă „stingere completă”
  digitalWrite(SD_PWR, HIGH);  // Tranzistor conduce → SD primește GND
  delay(300);                  // Stabilizare
}

// ===== Inițializare robustă SD card =====
bool safeSDInit(int retries, int delay_ms) {
  SD.end();
  delay(100);

  for (int i = 0; i < retries; i++) {
    Serial.print("🔁 SD init încercare "); Serial.println(i + 1);

    // Pulse CS scurt
    pinMode(SD_CS, OUTPUT);
    digitalWrite(SD_CS, HIGH); delay(5);
    digitalWrite(SD_CS, LOW);  delay(5);
    digitalWrite(SD_CS, HIGH); delay(5);

    if (SD.begin(SD_CS, spi)) {
      Serial.println("✅ SD init OK");
      return true;
    }

    delay(delay_ms);
  }

  Serial.println("❌ Toate încercările SD au eșuat.");
  return false;
}

// ===== Scrie gradient.raw =====
void writeGradientToSD() {
  File file = SD.open("/gradient.raw", FILE_WRITE);
  if (!file) {
    Serial.println("❌ Eroare la scrierea gradient.raw!");
    return;
  }

  Serial.println("📝 Scriu gradient...");

  for (int y = 0; y < IMG_H; y++) {
    for (int x = 0; x < IMG_W; x++) {
      uint8_t r = map(x, 0, IMG_W - 1, 255, 0);
      uint8_t g = map(x, 0, IMG_W - 1, 0, 255);
      uint16_t color = tft.color565(r, g, 0);
      file.write(color >> 8);
      file.write(color & 0xFF);
    }
  }

  file.flush();
  file.close();
  Serial.println("✅ gradient.raw salvat.");
}

// ===== Verifică fișierul =====
bool checkGradientFileExists() {
  File test = SD.open("/gradient.raw");
  if (test) {
    Serial.println("📁 gradient.raw este disponibil!");
    test.close();
    return true;
  } else {
    Serial.println("⚠️ gradient.raw NU este accesibil.");
    return false;
  }
}

// ===== Afișează gradient.raw pe LCD =====
void displayGradientFromSD() {
  File file = SD.open("/gradient.raw");
  if (!file) {
    Serial.println("❌ Nu pot deschide gradient.raw");
    return;
  }

  Serial.println("🖥️ Afișez gradient...");

  for (int y = 0; y < IMG_H; y++) {
    for (int x = 0; x < IMG_W; x++) {
      int hi = file.read();
      int lo = file.read();
      if (hi < 0 || lo < 0) break;
      uint16_t color = (hi << 8) | lo;
      tft.drawPixel(x, y, color);
    }
  }

  file.close();
  Serial.println("✅ Gradient afișat.");
}

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  delay(300);

  // Reset fizic la SD
  resetSDPower();

  // SPI
  spi.begin(18, 19, 23, -1);

  // LCD
  tft.init(240, 240);
  tft.setRotation(0);
  tft.fillScreen(ST77XX_BLACK);
  tft.setTextColor(ST77XX_CYAN);
  tft.setTextSize(2);
  tft.setCursor(10, 10);
  tft.println("Init LCD");

  // Inițializare SD cu retry
  if (!safeSDInit(5, 300)) {
    tft.setTextColor(ST77XX_RED);
    tft.println("SD FAIL");
    return;
  }

  tft.setTextColor(ST77XX_GREEN);
  tft.println("SD OK");

  // Scrie fișier și resetează SD logic după
  writeGradientToSD();
  SD.end(); delay(300);
  SD.begin(SD_CS, spi);

  if (!checkGradientFileExists()) {
    tft.println("NO FILE");
    return;
  }

  tft.fillScreen(ST77XX_BLACK);
  displayGradientFromSD();
}

void loop() {}
