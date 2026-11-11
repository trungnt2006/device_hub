import hid
from typing import Optional, Dict, Any

class PeripheralController:
    """Điều khiển & đọc thông số chuột VXE R1 SE+ và phím AULA F75 qua giao thức HID"""

    VID_COMPX = 0x3554
    PID_VXE_MOUSE = 0xf58e
    PID_AULA_KEYBOARD = 0xfa09

    @staticmethod
    def _checksum_compx(data: list) -> int:
        """Tổng tất cả byte == 0x55 (mod 256)"""
        s = sum(data[:-1]) & 0xFF
        return (0x55 - s) & 0xFF

    def get_mouse_status(self) -> Dict[str, Any]:
        """Đọc tình trạng chuột VXE Dragonfly R1 SE+"""
        result = {
            "connected": False,
            "battery": 0,
            "is_charging": False,
            "voltage_mv": 0,
            "device_name": "VXE Dragonfly R1 SE+"
        }
        
        target_path = None
        for d in hid.enumerate(self.VID_COMPX, self.PID_VXE_MOUSE):
            if d['usage_page'] == 0xff02 and d['usage'] == 0x02:
                target_path = d['path']
                break
                
        if not target_path:
            return result

        try:
            h = hid.device()
            h.open_path(target_path)
            
            # Gói tin 17-byte, Report ID 0x08, Subcommand 0x04
            req = [0x08, 0x04] + [0x00] * 14 + [0x00]
            req[-1] = self._checksum_compx(req)
            
            h.set_nonblocking(True)
            while h.read(64): 
                pass
            
            h.set_nonblocking(False)
            h.write(bytes(req))
            res = h.read(17, timeout_ms=300)
            h.close()
            
            if res and len(res) >= 10 and res[0] == 0x08:
                result["connected"] = True
                result["battery"] = max(0, min(100, int(res[6])))
                result["is_charging"] = bool(res[7])
                result["voltage_mv"] = (res[8] << 8) | res[9]
        except Exception:
            pass

        return result

    def get_keyboard_status(self) -> Dict[str, Any]:
        """Đọc tình trạng phím AULA F75"""
        result = {
            "connected": False,
            "battery": 0,
            "is_charging": False,
            "device_name": "AULA F75 Mechanical Keyboard"
        }

        target_path = None
        for d in hid.enumerate(self.VID_COMPX, self.PID_AULA_KEYBOARD):
            if d['usage_page'] == 0xff02 and d['usage'] == 0x02:
                target_path = d['path']
                break

        if not target_path:
            return result

        try:
            h = hid.device()
            h.open_path(target_path)

            req = [0x13, 0x4A] + [0x00] * 16 + [0x00]
            req[-1] = sum(req[:-1]) & 0xFF

            h.set_nonblocking(True)
            while h.read(64):
                pass

            h.set_nonblocking(False)
            h.write(bytes(req))
            res = h.read(19, timeout_ms=300)
            h.close()

            if res and len(res) >= 7 and res[0] == 0x13:
                result["connected"] = True
                result["battery"] = max(0, min(100, int(res[5])))
                # Theo chuẩn Compx F75: byte 6 == 0x01 là Đang dùng pin (Battery), 0x10 là Đang sạc (Charging)
                result["is_charging"] = (res[6] == 0x10)
        except Exception:
            pass

        return result
