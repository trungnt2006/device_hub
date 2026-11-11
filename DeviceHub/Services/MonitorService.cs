using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

namespace DeviceHub.Services
{
    public class MonitorService
    {
        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Auto)]
        public struct PHYSICAL_MONITOR
        {
            public IntPtr hPhysicalMonitor;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
            public string szPhysicalMonitorDescription;
        }

        private delegate bool MonitorEnumProc(IntPtr hMonitor, IntPtr hdcMonitor, ref RECT lprcMonitor, IntPtr dwData);

        [StructLayout(LayoutKind.Sequential)]
        public struct RECT
        {
            public int left;
            public int top;
            public int right;
            public int bottom;
        }

        [DllImport("user32.dll")]
        private static extern bool EnumDisplayMonitors(IntPtr hdc, IntPtr lprcClip, MonitorEnumProc lpfnEnum, IntPtr dwData);

        [DllImport("dxva2.dll", SetLastError = true)]
        private static extern bool GetNumberOfPhysicalMonitorsFromHMONITOR(IntPtr hMonitor, out uint pdwNumberOfPhysicalMonitors);

        [DllImport("dxva2.dll", SetLastError = true)]
        private static extern bool GetPhysicalMonitorsFromHMONITOR(IntPtr hMonitor, uint dwPhysicalMonitorArraySize, [Out] PHYSICAL_MONITOR[] pPhysicalMonitorArray);

        [DllImport("dxva2.dll", SetLastError = true)]
        private static extern bool DestroyPhysicalMonitors(uint dwPhysicalMonitorArraySize, [In] PHYSICAL_MONITOR[] pPhysicalMonitorArray);

        [DllImport("dxva2.dll", SetLastError = true)]
        private static extern bool GetVCPFeatureAndVCPFeatureReply(IntPtr hMonitor, byte bVCPCode, IntPtr pvct, out uint pdwCurrentValue, out uint pdwMaximumValue);

        [DllImport("dxva2.dll", SetLastError = true)]
        private static extern bool SetVCPFeature(IntPtr hMonitor, byte bVCPCode, uint dwNewValue);

        private IntPtr _activeHandle = IntPtr.Zero;
        public string MonitorName { get; private set; } = "Xiaomi A24i";

        public MonitorService()
        {
            FindActiveMonitor();
        }

        public bool FindActiveMonitor()
        {
            var monitors = new List<IntPtr>();
            EnumDisplayMonitors(IntPtr.Zero, IntPtr.Zero, (IntPtr hMon, IntPtr hdc, ref RECT rect, IntPtr data) =>
            {
                monitors.Add(hMon);
                return true;
            }, IntPtr.Zero);

            foreach (var hMon in monitors)
            {
                if (!GetNumberOfPhysicalMonitorsFromHMONITOR(hMon, out uint numPhys) || numPhys == 0)
                    continue;

                var physArray = new PHYSICAL_MONITOR[numPhys];
                if (GetPhysicalMonitorsFromHMONITOR(hMon, numPhys, physArray))
                {
                    foreach (var p in physArray)
                    {
                        if (GetVCPFeatureAndVCPFeatureReply(p.hPhysicalMonitor, 0x10, IntPtr.Zero, out uint cur, out uint max))
                        {
                            _activeHandle = p.hPhysicalMonitor;
                            if (!string.IsNullOrEmpty(p.szPhysicalMonitorDescription) && !p.szPhysicalMonitorDescription.Contains("Generic"))
                            {
                                MonitorName = p.szPhysicalMonitorDescription;
                            }
                            return true;
                        }
                    }
                }
            }
            return false;
        }

        public (bool success, int brightness) GetBrightness()
        {
            if (_activeHandle == IntPtr.Zero && !FindActiveMonitor())
                return (false, 0);

            if (GetVCPFeatureAndVCPFeatureReply(_activeHandle, 0x10, IntPtr.Zero, out uint cur, out uint max))
            {
                return (true, (int)cur);
            }

            // Retry once if stale
            if (FindActiveMonitor() && GetVCPFeatureAndVCPFeatureReply(_activeHandle, 0x10, IntPtr.Zero, out cur, out max))
            {
                return (true, (int)cur);
            }

            return (false, 0);
        }

        public bool SetBrightness(int value)
        {
            value = Math.Max(0, Math.Min(100, value));
            if (_activeHandle == IntPtr.Zero && !FindActiveMonitor())
                return false;

            if (SetVCPFeature(_activeHandle, 0x10, (uint)value))
                return true;

            if (FindActiveMonitor())
                return SetVCPFeature(_activeHandle, 0x10, (uint)value);

            return false;
        }
    }
}
