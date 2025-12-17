import threading
import queue
import time

try:
    from evdev import InputDevice, list_devices, ecodes
except Exception:
    InputDevice = None
    list_devices = None
    ecodes = None


class InputListener:
    """Listens to a Linux input device (evdev) and exposes arrow-key states and an event queue.

    Usage: run as root or set udev rules for the input device.
    """

    KEY_MAP = {
        'KEY_UP': 'up',
        'KEY_DOWN': 'down',
        'KEY_LEFT': 'left',
        'KEY_RIGHT': 'right'
    }

    def __init__(self, device_path=None):
        self.device_path = device_path
        self.device = None
        self.thread = None
        self.running = False
        self.event_queue = queue.Queue()
        # key -> bool
        self.key_states = {'up': False, 'down': False, 'left': False, 'right': False}
        # key -> last press timestamp
        self.key_press_time = {'up': 0.0, 'down': 0.0, 'left': 0.0, 'right': 0.0}

    def _find_device(self):
        if self.device_path:
            try:
                return InputDevice(self.device_path)
            except Exception:
                return None

        # try to pick first device that looks like a keyboard
        if list_devices is None:
            return None

        for dev_path in list_devices():
            try:
                dev = InputDevice(dev_path)
                caps = dev.capabilities().get(ecodes.EV_KEY, [])
                # presence of arrow keys is a good hint
                if ecodes.KEY_UP in caps and ecodes.KEY_DOWN in caps:
                    return dev
            except Exception:
                continue
        return None

    def start(self):
        if InputDevice is None:
            raise RuntimeError('evdev is not available; install python-evdev')

        self.device = self._find_device()
        if not self.device:
            raise RuntimeError(f'No input device found (tried: {self.device_path})')

        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        try:
            if self.device:
                self.device.close()
        except Exception:
            pass

    def _run(self):
        for ev in self.device.read_loop():
            if not self.running:
                break
            if ev.type == ecodes.EV_KEY:
                keyname = ecodes.KEY[ev.code]
                if keyname in self.KEY_MAP:
                    key = self.KEY_MAP[keyname]
                    # ev.value: 1=down, 0=up, 2=hold/repeat
                    is_down = ev.value == 1 or ev.value == 2
                    self.key_states[key] = is_down
                    if is_down:
                        self.key_press_time[key] = time.time()
                    # push event
                    self.event_queue.put((key, is_down, time.time()))

    def get_event(self, timeout=None):
        try:
            return self.event_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def is_pressed(self, key):
        return self.key_states.get(key, False)

    def pressed_duration(self, key):
        if not self.is_pressed(key):
            return 0.0
        return time.time() - self.key_press_time.get(key, 0.0)
