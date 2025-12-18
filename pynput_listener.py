import queue
import time

try:
    from pynput import keyboard
    from pynput.keyboard import Key
except Exception:
    keyboard = None
    Key = None


class PynputListener:
    """Fallback input listener using pynput.

    Provides the same minimal API as `InputListener`:
    - start()
    - stop()
    - get_event(timeout=None) -> (key, is_down, ts) or None
    - is_pressed(key)
    - pressed_duration(key)

    This listener maps the four arrow keys to 'up','down','left','right'.
    """

    def __init__(self, device_path=None, grab=False):
        self.device_path = device_path
        self.grab = grab
        self.listener = None
        self.running = False
        self.event_queue = queue.Queue()
        self.key_states = {'up': False, 'down': False, 'left': False, 'right': False}
        self.key_press_time = {k: 0.0 for k in self.key_states}

    def _map_key(self, key):
        try:
            if key == Key.up:
                return 'up'
            if key == Key.down:
                return 'down'
            if key == Key.left:
                return 'left'
            if key == Key.right:
                return 'right'
        except Exception:
            pass

        # Fallback: pynput may expose a KeyCode with a name attribute
        try:
            name = getattr(key, 'name', None)
            if name in ('up', 'down', 'left', 'right'):
                return name
        except Exception:
            pass

        return None

    def start(self):
        if keyboard is None:
            raise RuntimeError('pynput is not available; install pynput')

        self.running = True

        def _on_press(key):
            k = self._map_key(key)
            if k:
                if not self.key_states.get(k):
                    self.key_states[k] = True
                    self.key_press_time[k] = time.time()
                self.event_queue.put((k, True, time.time()))

        def _on_release(key):
            k = self._map_key(key)
            if k:
                self.key_states[k] = False
                self.event_queue.put((k, False, time.time()))

        self.listener = keyboard.Listener(on_press=_on_press, on_release=_on_release)
        # pynput's Listener runs in its own thread
        self.listener.daemon = True
        self.listener.start()

    def stop(self):
        self.running = False
        try:
            if self.listener:
                self.listener.stop()
        except Exception:
            pass

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
