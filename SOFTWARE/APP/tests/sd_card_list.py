import serial
import time

# === Configurație ===
port = "COM18"
baudrate = 115200

# === Deschide portul serial ===
try:
    ser = serial.Serial(port, baudrate, timeout=2)
    print(f"[INFO] Port deschis: {port} @ {baudrate} bps")
    time.sleep(2)  # ESP are nevoie de timp după deschidere
except Exception as e:
    print(f"[EROARE] Nu pot deschide portul serial: {e}")
    exit(1)

# === Trimite comanda JSON pentru listare SD ===
cmd = '{"cmd":"list_sd"}\n'
ser.write(cmd.encode())
print("[TX] Trimis:", cmd.strip())

# === Ascultă răspunsurile ESP32 ===
print("[RX] Aștept fișiere...")
try:
    while True:
        line = ser.readline().decode().strip()
        if line:
            print("[ESP]", line)
except KeyboardInterrupt:
    print("\n[INFO] Ieșire manuală.")
finally:
    ser.close()
    print("[INFO] Port închis.")
