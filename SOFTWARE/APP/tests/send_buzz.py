import serial
import time
import json

# 🔁 înlocuiește cu portul tău real
port = "COM18"           # ex: COM6 pe Windows sau /dev/rfcomm0 pe Linux
baudrate = 115200       # sau 9600 dacă ai setat altfel în ESP

ser = serial.Serial(port, baudrate, timeout=1)
time.sleep(2)  # dă timp să se deschidă conexiunea

# === Comandă pentru buzzer ===
cmd = {
    "cmd": "buzz",
    "freq": 1500,
    "duration": 400
}

# Trimite JSON urmat de newline (pentru ESP.readStringUntil('\n'))
ser.write((json.dumps(cmd) + "\n").encode())

print("Comandă trimisă.")

# Optionally: citește și răspunsul (dacă există)
time.sleep(0.2)
while ser.in_waiting:
    line = ser.readline().decode().strip()
    print("ESP32 spune:", line)

ser.close()
