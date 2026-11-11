using System;
using System.Drawing;
using System.IO;
using System.Windows.Forms;

namespace DeviceHub.Services
{
    public class TrayService : IDisposable
    {
        private readonly NotifyIcon _notifyIcon;
        private readonly Action _onToggle;
        private readonly Action _onRefresh;
        private readonly Action _onExit;

        public TrayService(Action onToggle, Action onRefresh, Action onExit)
        {
            _onToggle = onToggle;
            _onRefresh = onRefresh;
            _onExit = onExit;

            _notifyIcon = new NotifyIcon
            {
                Text = "Device Hub",
                Visible = true
            };

            // Load icon
            try
            {
                string? exePath = Environment.ProcessPath;
                if (!string.IsNullOrEmpty(exePath) && File.Exists(exePath))
                {
                    _notifyIcon.Icon = Icon.ExtractAssociatedIcon(exePath) ?? SystemIcons.Application;
                }
                else
                {
                    string iconPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Assets", "app.ico");
                    if (File.Exists(iconPath))
                    {
                        _notifyIcon.Icon = new Icon(iconPath);
                    }
                    else
                    {
                        _notifyIcon.Icon = SystemIcons.Application;
                    }
                }
            }
            catch
            {
                _notifyIcon.Icon = SystemIcons.Application;
            }

            // Context Menu
            var menu = new ContextMenuStrip();
            
            var itemOpen = new ToolStripMenuItem("Mở Device Hub", null, (s, e) => _onToggle());
            itemOpen.Font = new Font(itemOpen.Font, FontStyle.Bold);
            menu.Items.Add(itemOpen);

            var itemRefresh = new ToolStripMenuItem("Làm mới thiết bị", null, (s, e) => _onRefresh());
            menu.Items.Add(itemRefresh);

            menu.Items.Add(new ToolStripSeparator());

            var itemAutoStart = new ToolStripMenuItem("Khởi động cùng Windows", null, (s, e) =>
            {
                if (s is ToolStripMenuItem mi)
                {
                    bool current = StartupService.IsAutoStartEnabled();
                    StartupService.SetAutoStart(!current);
                    mi.Checked = !current;
                }
            });
            itemAutoStart.Checked = StartupService.IsAutoStartEnabled();
            menu.Items.Add(itemAutoStart);

            menu.Items.Add(new ToolStripSeparator());

            var itemExit = new ToolStripMenuItem("Thoát", null, (s, e) => _onExit());
            menu.Items.Add(itemExit);

            _notifyIcon.ContextMenuStrip = menu;

            _notifyIcon.MouseClick += (s, e) =>
            {
                if (e.Button == MouseButtons.Left)
                {
                    _onToggle();
                }
            };
        }

        public void UpdateTooltip(string text)
        {
            if (text.Length > 63) text = text.Substring(0, 63);
            _notifyIcon.Text = text;
        }

        public void Dispose()
        {
            _notifyIcon.Visible = false;
            _notifyIcon.ContextMenuStrip?.Dispose();
            _notifyIcon.Dispose();
        }
    }
}
