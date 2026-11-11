using System;
using System.Reflection;
using Microsoft.Win32;

namespace DeviceHub.Services
{
    public static class StartupService
    {
        private const string AppName = "DeviceHub";
        private const string RunKeyPath = @"Software\Microsoft\Windows\CurrentVersion\Run";

        public static bool IsAutoStartEnabled()
        {
            try
            {
                using var key = Registry.CurrentUser.OpenSubKey(RunKeyPath, false);
                return key?.GetValue(AppName) != null;
            }
            catch
            {
                return false;
            }
        }

        public static void SetAutoStart(bool enable)
        {
            try
            {
                using var key = Registry.CurrentUser.OpenSubKey(RunKeyPath, true);
                if (key == null) return;

                if (enable)
                {
                    string exePath = Environment.ProcessPath ?? AppContext.BaseDirectory;
                    key.SetValue(AppName, $"\"{exePath}\" --tray");
                }
                else
                {
                    key.DeleteValue(AppName, false);
                }
            }
            catch
            {
                // Ignored
            }
        }
    }
}
