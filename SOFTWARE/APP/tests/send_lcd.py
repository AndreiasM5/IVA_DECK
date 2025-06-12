import serial
import json
import time

# === CONFIG ===
PORT = "COM18"
BAUDRATE = 115200
FILENAME = "gradient.raw"   # fișier existent pe SD card (ex: 240x240x2 bytes)

# === Deschidere serială ===
ser = serial.Serial(PORT, BAUDRATE, timeout=2)
time.sleep(2)
print(f"[INFO] Conectat la {PORT} @ {BAUDRATE}")

# === Trimite comanda JSON ===
cmd = {
    "cmd": "display_raw",
    "filename": FILENAME
}
ser.write((json.dumps(cmd) + "\n").encode())
print(f"[TX] Trimis: {cmd}")

# === Ascultă răspuns ESP ===
try:
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if line:
            print(f"[ESP] {line}")
except KeyboardInterrupt:
    print("\n[INFO] Oprire manuală.")
finally:
    ser.close()
