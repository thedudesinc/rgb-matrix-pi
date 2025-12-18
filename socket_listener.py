import os
import socket
import threading
import json
import time
import queue


class SocketListener:
    """Server-side UNIX domain socket listener.

    Listens on a UNIX socket for newline-delimited JSON messages of the form:
      {"key":"left","is_down":true,"ts":<float>}

    Provides same API as other listeners: start(), stop(), get_event(), is_pressed(), pressed_duration().
    """

    def __init__(self, socket_path='/tmp/rgb_input.sock'):
        self.socket_path = socket_path
        self.server = None
        self.client = None
        self.thread = None
        self.running = False
        self.event_queue = queue.Queue()
        self.key_states = {'up': False, 'down': False, 'left': False, 'right': False}
        self.key_press_time = {k: 0.0 for k in self.key_states}
        self._lock = threading.Lock()

    def start(self):
        # ensure old socket removed
        try:
            if os.path.exists(self.socket_path):
                os.remove(self.socket_path)
        except Exception:
            pass

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.socket_path)
        # allow non-root clients to connect
        try:
            os.chmod(self.socket_path, 0o666)
        except Exception:
            pass

        self.server.listen(1)
        self.running = True
        self.thread = threading.Thread(target=self._accept_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        try:
            if self.client:
                self.client.close()
        except Exception:
            pass
        try:
            if self.server:
                self.server.close()
        except Exception:
            pass
        try:
            if os.path.exists(self.socket_path):
                os.remove(self.socket_path)
        except Exception:
            pass

    def _accept_loop(self):
        while self.running:
            try:
                client, _ = self.server.accept()
                with self._lock:
                    self.client = client
                # read loop
                buf = b''
                while self.running:
                    data = client.recv(4096)
                    if not data:
                        break
                    buf += data
                    while b'\n' in buf:
                        line, buf = buf.split(b'\n', 1)
                        try:
                            msg = json.loads(line.decode('utf-8'))
                            key = msg.get('key')
                            is_down = bool(msg.get('is_down'))
                            ts = float(msg.get('ts', time.time()))
                            if key in self.key_states:
                                self.key_states[key] = is_down
                                if is_down:
                                    self.key_press_time[key] = ts
                                self.event_queue.put((key, is_down, ts))
                        except Exception:
                            # ignore malformed lines
                            continue
                # client disconnected
                try:
                    client.close()
                except Exception:
                    pass
                with self._lock:
                    self.client = None
            except Exception:
                time.sleep(0.1)

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
