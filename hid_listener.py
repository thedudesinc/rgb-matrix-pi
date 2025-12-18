import threading
import time
import queue
import logging

log = logging.getLogger('hid_listener')
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(name)s %(levelname)s: %(message)s')

try:
    import hid
except Exception:
    hid = None

# HID usage codes for arrow keys (keyboard boot protocol)
USAGE_ARROW_MAP = {
    0x52: 'up',
    0x51: 'down',
    0x4F: 'right',
    0x50: 'left',
}


class HIDListener:
    """Simple HID listener reading boot-report keyboards via hidapi.

    Usage:
      l = HIDListener(vid=0x046d, pid=0xc52b)  # vendor/product
      l.start()
      ev = l.get_event(timeout=1.0)

    Notes:
    - Requires `pip install hidapi` (or system hidapi libs).
    - Device permissions must allow opening `/dev/hidraw*` or use udev rule to set GROUP/MODE.
    """

    def __init__(self, vid=None, pid=None, device_path=None):
        self.vid = vid
        self.pid = pid
        self.device_path = device_path
        self.dev = None
        self.thread = None
        self.running = False
        self.event_queue = queue.Queue()
        self.key_states = {'up': False, 'down': False, 'left': False, 'right': False}
        self.key_press_time = {k: 0.0 for k in self.key_states}

    def _open(self):
        if hid is None:
            raise RuntimeError('hidapi not available; pip install hidapi')

        # Try open by path if provided
        try:
            if self.device_path:
                # hid.Device() open_path may be available; try hid.open_path
                try:
                    h = hid.device()
                    h.open_path(self.device_path)
                    return h
                except Exception:
                    # fallback to enumerate/open by vid/pid
                    pass

            if self.vid and self.pid:
                h = hid.device()
                h.open(self.vid, self.pid)
                return h

            # enumerate and pick first keyboard-like device
            for d in hid.enumerate():
                # match usage_page/usage or interface if present
                # prefer devices with usage_page==1 (Generic Desktop) and usage==6 (Keyboard)
                # but not all enumerators expose that; fall back to first HID keyboard vendor device
                name = d.get('product_string') or d.get('manufacturer_string') or ''
                if 'keyboard' in name.lower() or 'logitech' in name.lower():
                    h = hid.device()
                    try:
                        h.open_path(d['path'])
                        return h
                    except Exception:
                        continue

            raise RuntimeError('No suitable HID device found')
        except Exception:
            raise

    def start(self):
        self.dev = self._open()
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        log.info('HID listener started')

    def stop(self):
        self.running = False
        try:
            if self.dev:
                try:
                    self.dev.close()
                except Exception:
                    pass
        except Exception:
            pass

    def _run(self):
        # hid.read returns list/bytes of report data
        prev_keys = set()
        while self.running:
            try:
                data = None
                try:
                    # Blocking read; timeout ms
                    data = self.dev.read(8, timeout_ms=500)
                except TypeError:
                    # some hid bindings use read(size) returning bytes
                    data = self.dev.read(8)

                if not data:
                    continue

                # Ensure we have a sequence of ints
                if isinstance(data, bytes):
                    buf = list(data)
                else:
                    buf = list(data)

                # debug: show raw report buffer
                log.info('HID raw report: %s', buf)

                # Boot keyboard report: [mod, reserved, k1, k2, k3, k4, k5, k6]
                keys = set()
                for usage in buf[2:]:
                    if usage == 0:
                        continue
                    name = USAGE_ARROW_MAP.get(usage)
                    if name:
                        keys.add(name)

                # compute down/up
                down = keys - prev_keys
                up = prev_keys - keys
                ts = time.time()
                for k in down:
                    self.key_states[k] = True
                    self.key_press_time[k] = ts
                    self.event_queue.put((k, True, ts))
                    log.info('HID event DOWN %s', k)
                for k in up:
                    self.key_states[k] = False
                    self.event_queue.put((k, False, ts))
                    log.info('HID event UP %s', k)

                prev_keys = keys
            except Exception as e:
                log.exception('HID read error: %s', e)
                time.sleep(0.5)

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
