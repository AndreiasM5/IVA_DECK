# ESP32 v6 firmware status

[Overview](../../../README.md) · [Hardware](../../../docs/hardware.md) · [Protocol](../../../docs/protocol.md)

The original checkout contained peripheral tests and an empty `src/` directory. A complete historical sketch has now been recovered from the author's own message in the **“ESP32 hardware test setup”** development conversation, dated **5 June 2025**.

## Recovered source

[Open `iva_deck_2025_06_05.ino`](recovered/iva_deck_2025_06_05/iva_deck_2025_06_05.ino)

The sketch is preserved as posted, with whitespace cleanup only. A whitespace-normalized content check matched the original message. It includes matrix scanning, potentiometers, ST7789 display, SD access, Bluetooth serial, and JSON command handling. It is a recovered development snapshot, **not a verified final release or a claim of compatibility with the current desktop app**.

### Known differences and unfinished paths

- Messages and commands use `SerialBT`; USB serial transport is not implemented in this snapshot.
- Volume events use `master`, `game`, and `spotify`, whereas the current desktop GUI indexes its three sliders by `0`, `1`, and `2`.
- Proximity initialization and periodic readings are commented out; XSHUT remains LOW after setup.
- The microphone helper exists but is not called. Full audio streaming is absent.
- Binary-upload start handling is commented out.
- `display_raw`, `list_sd`, and `buzz` are present; the GUI's `display_text` command has no handler here.
- Matrix rows use GPIO 1 and 3, which are also the usual UART0 pins. Do not add UART serial use without checking the hardware and pin allocation.
- The sketch uses legacy APIs such as `ledcSetup` / `ledcAttachPin` and I2S driver structures. The original ESP32 core and library versions were not preserved, so current-toolchain compilation is not asserted.

Open the `.ino` in its same-named directory with Arduino IDE, an ESP32 target supporting Bluetooth Classic, and the required Adafruit display/VL53L0X and ArduinoJson libraries. Confirm API compatibility and the pin map before any build or flash. No firmware has been flashed in this update.

## Peripheral tests

| Sketch | Purpose |
| --- | --- |
| `tests/test_matrix_and_volume.ino` | Matrix and potentiometers, 9600 baud |
| `tests/test_lcd/test_lcd.ino` | ST7789 / SD diagnostic |
| `tests/test_proxi/test_proxi.ino` | Historical name; contents focus on LCD / SD |

Open sketches separately in Arduino IDE with matching ESP32 support and Adafruit libraries. Copy the standalone matrix test into a same-named sketch directory if required by Arduino IDE.

The tests do not collectively implement the full JSON / Bluetooth workflow. The recovered sketch above is the original historical source, not invented firmware. Compilation and physical integration have not been revalidated.
