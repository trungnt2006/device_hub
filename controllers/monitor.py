import ctypes
from ctypes import wintypes
from typing import Optional, Tuple

class PHYSICAL_MONITOR(ctypes.Structure):
    _fields_ = [
        ('hPhysicalMonitor', wintypes.HANDLE),
        ('szPhysicalMonitorDescription', wintypes.WCHAR * 128)
    ]

user32 = ctypes.windll.user32
dxva2 = ctypes.windll.dxva2

class MonitorController:
    """Điều khiển màn hình ngoài (Xiaomi A24i) qua chuẩn DDC/CI WinAPI (dxva2.dll)"""
    
    def __init__(self):
        self.cached_handle: Optional[int] = None
        self.cached_name: str = "Xiaomi A24i"
        self._find_active_monitor()

    def _find_active_monitor(self) -> bool:
        monitors = []
        def enum_proc(hMonitor, hdcMonitor, lprcMonitor, dwData):
            monitors.append(hMonitor)
            return True

        MONITORENUMPROC = ctypes.WINFUNCTYPE(
            wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, 
            ctypes.POINTER(wintypes.RECT), wintypes.LPARAM
        )
        user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(enum_proc), 0)

        for hMon in monitors:
            num_phys = wintypes.DWORD()
            if not dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(hMon, ctypes.byref(num_phys)):
                continue
            if num_phys.value > 0:
                phys_array = (PHYSICAL_MONITOR * num_phys.value)()
                if dxva2.GetPhysicalMonitorsFromHMONITOR(hMon, num_phys.value, phys_array):
                    for p in phys_array:
                        hPhys = p.hPhysicalMonitor
                        cur_bright = wintypes.DWORD()
                        max_bright = wintypes.DWORD()
                        # Test xem có phản hồi DDC/CI VCP 0x10 không
                        if dxva2.GetVCPFeatureAndVCPFeatureReply(
                            hPhys, 0x10, None, 
                            ctypes.byref(cur_bright), 
                            ctypes.byref(max_bright)
                        ):
                            self.cached_handle = hPhys
                            desc = p.szPhysicalMonitorDescription
                            if "Generic" not in desc and desc.strip():
                                self.cached_name = desc
                            return True
        return False

    def get_brightness(self) -> Tuple[bool, int]:
        """Trả về (Thành công, Giá trị độ sáng 0-100)"""
        if not self.cached_handle:
            if not self._find_active_monitor():
                return False, 0
                
        cur_bright = wintypes.DWORD()
        max_bright = wintypes.DWORD()
        res = dxva2.GetVCPFeatureAndVCPFeatureReply(
            self.cached_handle, 0x10, None, 
            ctypes.byref(cur_bright), 
            ctypes.byref(max_bright)
        )
        if res:
            return True, int(cur_bright.value)
        else:
            # Handle có thể bị stale, thử tìm lại một lần
            if self._find_active_monitor():
                res = dxva2.GetVCPFeatureAndVCPFeatureReply(
                    self.cached_handle, 0x10, None, 
                    ctypes.byref(cur_bright), 
                    ctypes.byref(max_bright)
                )
                if res:
                    return True, int(cur_bright.value)
            return False, 0

    def set_brightness(self, value: int) -> bool:
        """Đặt độ sáng 0-100"""
        value = max(0, min(100, int(value)))
        if not self.cached_handle:
            if not self._find_active_monitor():
                return False
                
        res = dxva2.SetVCPFeature(self.cached_handle, 0x10, value)
        if not res:
            if self._find_active_monitor():
                res = dxva2.SetVCPFeature(self.cached_handle, 0x10, value)
        return bool(res)
