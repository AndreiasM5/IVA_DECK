import serial
import serial.tools.list_ports
import win32com.client

class SerialManager:
    def __init__(self):
        self.serial_conn = None
        self.serial_running = False

    def connect(self, port, baudrate=9600):
        try:
            self.serial_conn = serial.Serial(port, baudrate, timeout=1)
            self.serial_running = True
            print(f"Connected to {port} at {baudrate} baud.")
        except Exception as e:
            print(f"Error connecting to serial port: {e}")

    def disconnect(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_running = False
            self.serial_conn.close()
            print("Disconnected from serial port.")

    def listen(self):
        while self.serial_running and self.serial_conn and self.serial_conn.is_open:
            try:
                line = self.serial_conn.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    self.handle_message(line)
            except Exception as e:
                print(f"Error reading from serial port: {e}")

    def handle_message(self, message):
        print(f"Received message: {message}")

def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    port_list = []
    wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    service = wmi.ConnectServer(".", "root\\cimv2")
    query = "SELECT * FROM Win32_PnPEntity WHERE Name LIKE '%(COM%'"
    devices = {d.DeviceID: d.Name for d in service.ExecQuery(query)}

    for port in ports:
        label = port.device
        desc = port.description
        hwid = port.hwid
        friendly_name = None
        for dev_id, name in devices.items():
            if port.device in name:
                friendly_name = name
                break
        if friendly_name:
            label = f"{port.device} ({friendly_name})"
        elif desc and desc != port.device:
            label = f"{port.device} ({desc})"
        port_list.append({"label": label, "device": port.device})
    return port_list