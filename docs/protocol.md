# Serial protocol

[← Overview](../README.md)

The host exchanges UTF-8 JSON messages terminated by `\n`. USB and Bluetooth are serial transports. The desktop application produces OS macros; this is not a native USB HID or BLE HID implementation.

Examples below reflect `SOFTWARE/APP/v4/iva_key_app/src/ui/main_window.py`.

## Device → host

```json
{"type":"key","key":"pressed","value":"49"}
{"type":"volume","key":"0","value":720}
{"type":"proxy","key":"distance","value":45}
```

Each line is a separate event. Key presses require `key: pressed`. Character-code values map to physical keys as follows:

| Values | UI keys |
| --- | --- |
| 49 / 50 / 51 | T3 / T2 / T1 |
| 52 / 53 / 54 | T6 / T5 / T4 |
| 55 / 56 / 57 | T9 / T8 / T7 |

The value `1` does not substitute for `49`. The three volume controls use identifiers `0`, `1`, and `2`. Volume uses an inverted ADC scale: `(4095 - value) / 4095 * 100`, clamped to 0–100. Proximity is in millimeters; the UI changes from green at ≤30 mm to red at ≥80 mm.

## Host → device

| Function | Payload |
| --- | --- |
| Buzzer | `{"cmd":"buzz","freq":1500,"duration":400}` |
| Display text | `{"cmd":"display_text","text":"IVA DECK"}` |
| List SD | `{"cmd":"list_sd"}` |
| Display image | `{"cmd":"display_raw","filename":"test.raw"}` |

The app appends a newline to each command. SD listing is processed as text with image filenames detected by extension; no complete structured response schema is defined. The LCD test uses 240×240 raw-image rendering; inspect it for byte order.

The GUI selects 115200 baud for USB and 9600 for Bluetooth serial. Old diagnostic sketches can use other rates and formats, so they are not interchangeable with the complete protocol.

## Recovered sketch compatibility

The recovered June 2025 sketch is Bluetooth-only and sends volume identifiers `master`, `game`, and `spotify`; the current GUI expects `0`, `1`, and `2`. Its proximity and microphone reads are disabled, and it has no `display_text` handler. The tables above describe the current **host expectations**, not a claim that the archived sketch implements every feature. See [firmware status](../SOFTWARE/DECK/v6_esp32/README.md).
