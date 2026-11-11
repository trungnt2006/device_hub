using System;
using System.Linq;
using HidSharp;

namespace DeviceHub.Services
{
    public class MouseStatus
    {
        public bool Connected { get; set; }
        public int Battery { get; set; }
        public bool IsCharging { get; set; }
        public int VoltageMv { get; set; }
        public string DeviceName { get; set; } = "VXE Dragonfly R1 SE+";
    }

    public class KeyboardStatus
    {
        public bool Connected { get; set; }
        public int Battery { get; set; }
        public bool IsCharging { get; set; }
        public string DeviceName { get; set; } = "AULA F75 Mechanical Keyboard";
    }

    public class PeripheralService
    {
        private const int VID_COMPX = 0x3554;
        private const int PID_VXE_MOUSE = 0xF58E;
        private const int PID_AULA_KEYBOARD = 0xFA09;

        private static byte CalculateCompxChecksum(byte[] data)
        {
            int sum = 0;
            for (int i = 0; i < data.Length - 1; i++)
            {
                sum += data[i];
            }
            return (byte)((0x55 - (sum & 0xFF)) & 0xFF);
        }

        public MouseStatus GetMouseStatus()
        {
            var status = new MouseStatus();

            try
            {
                var devices = DeviceList.Local.GetHidDevices(VID_COMPX, PID_VXE_MOUSE);
                foreach (var dev in devices)
                {
                    // Target interface with output report length 17
                    if (dev.GetMaxOutputReportLength() >= 17)
                    {
                        if (dev.TryOpen(out HidStream stream))
                        {
                            using (stream)
                            {
                                stream.ReadTimeout = 250;
                                stream.WriteTimeout = 250;

                                byte[] req = new byte[17];
                                req[0] = 0x08;
                                req[1] = 0x04;
                                req[16] = CalculateCompxChecksum(req);

                                stream.Write(req);

                                byte[] res = new byte[17];
                                int readBytes = stream.Read(res);

                                if (readBytes >= 10 && res[0] == 0x08)
                                {
                                    status.Connected = true;
                                    status.Battery = Math.Max(0, Math.Min(100, (int)res[6]));
                                    status.IsCharging = res[7] == 1;
                                    status.VoltageMv = (res[8] << 8) | res[9];
                                    return status;
                                }
                            }
                        }
                    }
                }
            }
            catch
            {
                // Ignored
            }

            return status;
        }

        public KeyboardStatus GetKeyboardStatus()
        {
            var status = new KeyboardStatus();

            try
            {
                var devices = DeviceList.Local.GetHidDevices(VID_COMPX, PID_AULA_KEYBOARD);
                foreach (var dev in devices)
                {
                    if (dev.GetMaxOutputReportLength() >= 19)
                    {
                        if (dev.TryOpen(out HidStream stream))
                        {
                            using (stream)
                            {
                                stream.ReadTimeout = 250;
                                stream.WriteTimeout = 250;

                                byte[] req = new byte[19];
                                req[0] = 0x13;
                                req[1] = 0x4A;

                                int sum = 0;
                                for (int i = 0; i < req.Length - 1; i++) sum += req[i];
                                req[req.Length - 1] = (byte)(sum & 0xFF);

                                stream.Write(req);

                                byte[] res = new byte[19];
                                int readBytes = stream.Read(res);

                                if (readBytes >= 7 && res[0] == 0x13)
                                {
                                    status.Connected = true;
                                    status.Battery = Math.Max(0, Math.Min(100, (int)res[5]));
                                    // 0x10 is charging / cable, 0x01 is battery
                                    status.IsCharging = res[6] == 0x10;
                                    return status;
                                }
                            }
                        }
                    }
                }
            }
            catch
            {
                // Ignored
            }

            return status;
        }
    }
}
