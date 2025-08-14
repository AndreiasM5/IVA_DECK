class KeybindManager:
    def __init__(self, file_path="keybinds.json"):
        self.file_path = file_path
        self.keybinds = self.load_keybinds()

    def load_keybinds(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                return json.load(f)
        return {}

    def save_keybinds(self):
        with open(self.file_path, "w") as f:
            json.dump(self.keybinds, f, indent=4)

    def get_keybind(self, key):
        return self.keybinds.get(key, "")

    def set_keybind(self, key, value):
        self.keybinds[key] = value
        self.save_keybinds()

    def simulate_keybind(self, command_str):
        keys = command_str.split("+")
        key_map = {
            "ctrl": Key.ctrl,
            "shift": Key.shift,
            "alt": Key.alt,
            "cmd": Key.cmd,
            "win": Key.cmd,
            "enter": Key.enter,
            "esc": Key.esc,
            "space": Key.space,
            "tab": Key.tab,
            "backspace": Key.backspace,
            "up": Key.up,
            "down": Key.down,
            "left": Key.left,
            "right": Key.right
        }

        parsed_keys = []
        for k in keys:
            k = k.strip().lower()
            if k in key_map:
                parsed_keys.append(key_map[k])
            else:
                parsed_keys.append(k)

        try:
            for k in parsed_keys:
                self.keyboard.press(k)
            for k in reversed(parsed_keys):
                self.keyboard.release(k)
            print(f"[Keybind] Simulated: {command_str}")
        except Exception as e:
            print(f"[Keybind] Error simulating: {e}")