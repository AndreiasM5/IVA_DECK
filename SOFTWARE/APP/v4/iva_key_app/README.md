# IVA Key App

## Overview
The IVA Key App is a desktop application designed to manage key bindings, volume control, and voice recognition functionalities. It provides a user-friendly interface for interacting with various hardware components via serial communication.

## Project Structure
```
iva_key_app
├── src
│   ├── main.py                # Entry point of the application
│   ├── ui                     # User interface components
│   │   ├── __init__.py
│   │   └── main_window.py      # Main window UI logic
│   ├── serial_comm            # Serial communication handling
│   │   ├── __init__.py
│   │   └── serial_manager.py    # Manages serial connections and data
│   ├── keybinds               # Key binding management
│   │   ├── __init__.py
│   │   └── keybind_manager.py   # Handles keybind loading and simulation
│   ├── voice                  # Voice recognition functionality
│   │   ├── __init__.py
│   │   └── voice_recognition.py  # Manages voice command recognition
│   └── utils                  # Utility functions
│       ├── __init__.py
│       └── helpers.py          # Common utility functions
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Installation
To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd iva_key_app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the application, execute the following command:
```
python src/main.py
```

## Features
- **Key Bindings**: Customize key bindings for various actions.
- **Volume Control**: Adjust volume levels for different applications.
- **Voice Recognition**: Use voice commands to control the application.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.