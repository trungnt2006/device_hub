using System;
using System.Runtime.InteropServices;
using System.Windows.Interop;

namespace DeviceHub.Services
{
    public class HotkeyService : IDisposable
    {
        private const int MOD_ALT = 0x0001;
        private const int MOD_CONTROL = 0x0002;
        private const int MOD_NOREPEAT = 0x4000;
        private const int VK_UP = 0x26;
        private const int VK_DOWN = 0x28;
        private const int WM_HOTKEY = 0x0312;

        private const int HOTKEY_UP_ID = 9001;
        private const int HOTKEY_DOWN_ID = 9002;

        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool UnregisterHotKey(IntPtr hWnd, int id);

        private IntPtr _hWnd;
        private HwndSource? _source;
        private Action _onUp;
        private Action _onDown;

        public bool IsRegistered { get; private set; }

        public HotkeyService(IntPtr hWnd, Action onUp, Action onDown)
        {
            _hWnd = hWnd;
            _onUp = onUp;
            _onDown = onDown;

            try
            {
                bool upOk = RegisterHotKey(_hWnd, HOTKEY_UP_ID, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_UP);
                bool downOk = RegisterHotKey(_hWnd, HOTKEY_DOWN_ID, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_DOWN);
                IsRegistered = upOk && downOk;
            }
            catch
            {
                IsRegistered = false;
            }

            _source = HwndSource.FromHwnd(_hWnd);
            _source?.AddHook(HwndHook);
        }

        private IntPtr HwndHook(IntPtr hwnd, int msg, IntPtr wParam, IntPtr lParam, ref bool handled)
        {
            if (msg == WM_HOTKEY)
            {
                int id = wParam.ToInt32();
                if (id == HOTKEY_UP_ID)
                {
                    _onUp?.Invoke();
                    handled = true;
                }
                else if (id == HOTKEY_DOWN_ID)
                {
                    _onDown?.Invoke();
                    handled = true;
                }
            }
            return IntPtr.Zero;
        }

        public void Dispose()
        {
            if (_hWnd != IntPtr.Zero)
            {
                try
                {
                    UnregisterHotKey(_hWnd, HOTKEY_UP_ID);
                    UnregisterHotKey(_hWnd, HOTKEY_DOWN_ID);
                }
                catch { }
            }
            _source?.RemoveHook(HwndHook);
        }
    }
}
