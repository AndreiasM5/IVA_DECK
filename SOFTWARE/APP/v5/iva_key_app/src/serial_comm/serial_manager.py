import serial.tools.list_ports


def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [{'device': port.device,
             'label': f'{port.device} ({port.description})' if port.description != port.device else port.device}
            for port in ports]
