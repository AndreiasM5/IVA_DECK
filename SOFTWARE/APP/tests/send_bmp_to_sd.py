import serial
import time
import json
import os
import threading

# === CONFIGURARE ===
PORT = "COM18"
BAUDRATE = 115200
FILE_PATH = "nyan.bmp"        # imaginea locală
DEST_FILENAME = "nyan.bmp"    # numele pe cardul SD
CHUNK_SIZE = 128

# === DESCHIDERE SERIALĂ ===
ser = serial.Serial(PORT, BAUDRATE, timeout=1)
print(f"[INFO] Deschis portul {PORT} la {BAUDRATE} bps.")
time.sleep(2)  # așteaptă conexiunea ESP

# === TRIMITE HEADER JSON ===
file_size = os.path.getsize(FILE_PATH)
header = {
    "cmd": "upload_start",
    "filename": DEST_FILENAME,
    "size": file_size
}
ser.write((json.dumps(header) + "\n").encode())
print(f"[TX] upload_start → {DEST_FILENAME} ({file_size} bytes)")

# # === ASCULTĂ ÎN PARALEL OUTPUTUL DE LA ESP ===
# def listen_serial():
#     while True:
#         try:
#             line = ser.readline().decode(errors="ignore").strip()
#             if line:
#                 print(f"[ESP] {line}")
#         except Exception as e:
#             print(f"[ERR] {e}")
#             break

# listener_thread = threading.Thread(target=listen_serial, daemon=True)
# listener_thread.start()

# === Așteaptă răspuns de la ESP ===
start = time.time()
while time.time() - start < 3:
    if ser.in_waiting:
        line = ser.readline().decode(errors="ignore").strip()
        if line:
            print(f"[ESP] {line}")
        if "upload_ready" in line:
            break
        if "error" in line:
            print(f"[ESP ERROR] {line}")
            ser.close()
            exit(1)


# === TRIMITE FIȘIERUL PE SERIALĂ ===
with open(FILE_PATH, "rb") as f:
    sent = 0
    while True:
        chunk = f.read(CHUNK_SIZE)
        if not chunk:
            break
        ser.write(chunk)
        sent += len(chunk)
        time.sleep(0.01)
        print(f"[TX] {sent}/{file_size} bytes", end='\r')

print("\n[INFO] Fișier trimis complet. Aștept confirmare ESP...")

# === NU ÎNCHIDE SERIALA! ===
print("[INFO] Port serial rămâne deschis. Apasă Ctrl+C pentru a opri.")
try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\n[INFO] Închidere manuală.")
    ser.close()
