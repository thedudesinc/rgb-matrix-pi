import threading
import queue
import time
import os
import traceback

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

    def __init__(self, device_path=None, grab=False):
        self.device_path = device_path
        self.device = None
        self.thread = None
        self.running = False
        self.event_queue = queue.Queue()
        # key -> bool
        self.key_states = {'up': False, 'down': False, 'left': False, 'right': False}
        # key -> last press timestamp
        self.key_press_time = {'up': 0.0, 'down': 0.0, 'left': 0.0, 'right': 0.0}
        self.grab = grab
        # prepare numeric code map for variants (keypad arrows etc.)
        self.KEY_CODE_MAP = {}
        try:
            # main arrow keys
            self.KEY_CODE_MAP[ecodes.KEY_UP] = 'up'
            self.KEY_CODE_MAP[ecodes.KEY_DOWN] = 'down'
            self.KEY_CODE_MAP[ecodes.KEY_LEFT] = 'left'
            self.KEY_CODE_MAP[ecodes.KEY_RIGHT] = 'right'
        except Exception:
            pass
        # some keyboards send keypad arrows - map common variants if present
        try:
            self.KEY_CODE_MAP[ecodes.KEY_KP8] = 'up'
            self.KEY_CODE_MAP[ecodes.KEY_KP2] = 'down'
            self.KEY_CODE_MAP[ecodes.KEY_KP4] = 'left'
            self.KEY_CODE_MAP[ecodes.KEY_KP6] = 'right'
        except Exception:
            pass

    def _find_device(self):
        if self.device_path:
            try:
                dev = InputDevice(self.device_path)
                return dev
            except Exception as e:
                # raise informative error to caller
                raise RuntimeError(f"Failed to open input device '{self.device_path}': {e}")

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
        # Attempt to find/open the device; collect diagnostics on failure
        try:
            self.device = self._find_device()
        except Exception as e:
            # gather runtime diagnostics to help debug permission / path issues
            uid = os.geteuid()
            gid = os.getegid()
            dev_stat = None
            try:
                if self.device_path:
                    dev_stat = os.stat(self.device_path)
            except Exception:
                dev_stat = None

            devs = list_devices() if list_devices is not None else []
            names = []
            for d in devs:
                try:
                    names.append((d, InputDevice(d).name))
                except Exception:
                    names.append((d, '<unreadable>'))

            tb = traceback.format_exc()
            raise RuntimeError(
                "Failed to open input device in _find_device() - diagnostics:\n"
                f"  requested: {self.device_path}\n"
                f"  euid={uid} egid={gid}\n"
                f"  device_stat={dev_stat}\n"
                f"  available_devices={names}\n"
                f"  error={e}\n"
                f"  traceback:\n{tb}")

        if not self.device:
            # list available devices for debugging
            devs = list_devices() if list_devices is not None else []
            names = []
            for d in devs:
                try:
                    names.append((d, InputDevice(d).name))
                except Exception:
                    names.append((d, '<unreadable>'))
            raise RuntimeError(f'No input device found (tried: {self.device_path}). Available: {names}')

        # optionally grab the device exclusively
        try:
            if self.grab:
                try:
                    self.device.grab()
                except Exception:
                    # non-fatal; continue without exclusive grab
                    pass
        except Exception:
            pass

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
                # prefer numeric code mapping (handles variants)
                key = None
                try:
                    key = self.KEY_CODE_MAP.get(ev.code)
                except Exception:
                    key = None

                # fallback to name-based mapping for completeness
                if key is None:
                    try:
                        keyname = ecodes.KEY[ev.code]
                        key = self.KEY_MAP.get(keyname)
                    except Exception:
                        key = None

                if key:
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
