import ctypes
from ctypes import wintypes
import threading
from typing import Callable

user32 = ctypes.windll.user32

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_NOREPEAT = 0x4000

VK_UP = 0x26
VK_DOWN = 0x28

HOTKEY_BRIGHTNESS_UP = 1
HOTKEY_BRIGHTNESS_DOWN = 2

class GlobalHotkeyManager:
    """Quản lý phím tắt toàn hệ thống (Ctrl + Alt + Up / Down) để chỉnh sáng không cần mở app"""

    def __init__(self, on_up: Callable[[], None], on_down: Callable[[], None]):
        self.on_up = on_up
        self.on_down = on_down
        self.thread: threading.Thread = None
        self.running = False
        self.thread_id = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._hotkey_loop, daemon=True)
        self.thread.start()

    def _hotkey_loop(self):
        self.thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
        
        # Đăng ký Ctrl + Alt + Up (ID 1)
        ok1 = user32.RegisterHotKey(
            None, HOTKEY_BRIGHTNESS_UP, 
            MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_UP
        )
        # Đăng ký Ctrl + Alt + Down (ID 2)
        ok2 = user32.RegisterHotKey(
            None, HOTKEY_BRIGHTNESS_DOWN, 
            MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_DOWN
        )

        msg = wintypes.MSG()
        while self.running:
            # GetMessage chờ nhận sự kiện phím bấm
            res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if res <= 0:
                break
            if msg.message == 0x0312:  # WM_HOTKEY
                if msg.wParam == HOTKEY_BRIGHTNESS_UP and self.on_up:
                    self.on_up()
                elif msg.wParam == HOTKEY_BRIGHTNESS_DOWN and self.on_down:
                    self.on_down()
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        user32.UnregisterHotKey(None, HOTKEY_BRIGHTNESS_UP)
        user32.UnregisterHotKey(None, HOTKEY_BRIGHTNESS_DOWN)

    def stop(self):
        self.running = False
        if self.thread_id:
            user32.PostThreadMessageW(self.thread_id, 0x0012, 0, 0)  # WM_QUIT
