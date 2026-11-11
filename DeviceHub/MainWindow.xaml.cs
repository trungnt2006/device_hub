using System;
using System.ComponentModel;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Threading;
using DeviceHub.Services;
using Wpf.Ui.Appearance;
using Wpf.Ui.Controls;
using Color = System.Windows.Media.Color;
using Brush = System.Windows.Media.Brush;

namespace DeviceHub
{
    public partial class MainWindow : FluentWindow
    {
        private readonly MonitorService _monitorService;
        private readonly PeripheralService _peripheralService;
        private readonly TrayService _trayService;
        private HotkeyService? _hotkeyService;
        private readonly DispatcherTimer _debounceTimer;
        private readonly DispatcherTimer _autoRefreshTimer;
        private int _targetBrightness = 50;
        private bool _isInitialized = false;
        private bool _isExplicitExit = false;
        private DateTime _lastDeactivatedTime = DateTime.MinValue;

        // Custom warning & critical brushes for low battery
        private static readonly SolidColorBrush WarningBrush = new(Color.FromRgb(245, 166, 35));
        private static readonly SolidColorBrush CriticalBrush = new(Color.FromRgb(232, 17, 35));

        public MainWindow()
        {
            _monitorService = new MonitorService();
            _peripheralService = new PeripheralService();

            _debounceTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromMilliseconds(150)
            };
            _debounceTimer.Tick += DebounceTimer_Tick;

            _autoRefreshTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(45)
            };
            _autoRefreshTimer.Tick += async (s, e) => await RefreshAllDevicesAsync();

            // Khởi tạo giao diện XAML
            InitializeComponent();
            _isInitialized = true;

            // Kích hoạt theme Dark và hiệu ứng Mica Windows 11
            ApplicationThemeManager.Apply(this);

            // Tự động áp dụng Accent Color thực tế của hệ thống người dùng (không cố định màu tím)
            try
            {
                ApplicationAccentColorManager.ApplySystemAccent();
            }
            catch { }

            // Khởi tạo Tray Service
            _trayService = new TrayService(
                onToggle: ToggleFlyout,
                onRefresh: () => Dispatcher.Invoke(async () => await RefreshAllDevicesAsync()),
                onExit: ExitApplication
            );

            _autoRefreshTimer.Start();

            Loaded += MainWindow_Loaded;
            Deactivated += MainWindow_Deactivated;
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            var helper = new WindowInteropHelper(this);
            _hotkeyService = new HotkeyService(
                helper.Handle,
                onUp: () => Dispatcher.Invoke(() => StepBrightness(10)),
                onDown: () => Dispatcher.Invoke(() => StepBrightness(-10))
            );

            var args = Environment.GetCommandLineArgs();
            bool startInTray = Array.Exists(args, a => a.Equals("--tray", StringComparison.OrdinalIgnoreCase) || a.Equals("--autostart", StringComparison.OrdinalIgnoreCase));
            if (startInTray)
            {
                Hide();
            }
            else
            {
                AnimateShow();
            }

            _ = RefreshAllDevicesAsync();
        }

        private void MainWindow_Deactivated(object? sender, EventArgs e)
        {
            _lastDeactivatedTime = DateTime.UtcNow;
            Hide();
        }

        private void Window_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Escape)
            {
                Hide();
                e.Handled = true;
            }
            else if (e.Key == Key.F5)
            {
                _ = RefreshAllDevicesAsync();
                e.Handled = true;
            }
        }

        protected override void OnClosing(CancelEventArgs e)
        {
            if (!_isExplicitExit)
            {
                e.Cancel = true;
                Hide();
                return;
            }
            base.OnClosing(e);
        }

        public void ToggleFlyout()
        {
            Dispatcher.Invoke(() =>
            {
                if (IsVisible)
                {
                    Hide();
                    return;
                }

                // Chống hiện lại ngay lập tức khi click vào Tray Icon lúc flyout vừa mất focus
                if ((DateTime.UtcNow - _lastDeactivatedTime).TotalMilliseconds < 250)
                {
                    return;
                }

                AnimateShow();
            });
        }

        private void AnimateShow()
        {
            PositionNearTray();
            Show();
            Activate();

            // Hiệu ứng trượt nhẹ từ dưới lên (15px) và mờ dần trong 160ms chuẩn Windows 11
            double targetTop = Top;
            var topAnim = new DoubleAnimation(targetTop + 14, targetTop, TimeSpan.FromMilliseconds(160))
            {
                EasingFunction = new CubicEase { EasingMode = EasingMode.EaseOut }
            };
            var opacityAnim = new DoubleAnimation(0.0, 1.0, TimeSpan.FromMilliseconds(160))
            {
                EasingFunction = new CubicEase { EasingMode = EasingMode.EaseOut }
            };

            BeginAnimation(TopProperty, topAnim);
            BeginAnimation(OpacityProperty, opacityAnim);
        }

        public void PositionNearTray()
        {
            var workArea = SystemParameters.WorkArea;
            double margin = 12;
            Left = workArea.Right - Width - margin;
            Top = workArea.Bottom - Height - margin;
        }

        public void ExitApplication()
        {
            Dispatcher.Invoke(() =>
            {
                _isExplicitExit = true;
                _hotkeyService?.Dispose();
                _trayService?.Dispose();
                System.Windows.Application.Current.Shutdown();
            });
        }

        private void SliderBrightness_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (!_isInitialized || _debounceTimer == null) return;

            int val = (int)e.NewValue;
            if (TxtBrightness != null)
            {
                TxtBrightness.Text = $"{val}%";
            }

            UpdatePresetHighlight(val);

            _targetBrightness = val;
            _debounceTimer.Stop();
            _debounceTimer.Start();
        }

        private void UpdatePresetHighlight(int val)
        {
            if (BtnPreset20 == null) return;
            BtnPreset20.Appearance = val == 20 ? ControlAppearance.Primary : ControlAppearance.Secondary;
            BtnPreset50.Appearance = val == 50 ? ControlAppearance.Primary : ControlAppearance.Secondary;
            BtnPreset75.Appearance = val == 75 ? ControlAppearance.Primary : ControlAppearance.Secondary;
            BtnPreset100.Appearance = val == 100 ? ControlAppearance.Primary : ControlAppearance.Secondary;
        }

        private void DebounceTimer_Tick(object? sender, EventArgs e)
        {
            _debounceTimer.Stop();
            _monitorService.SetBrightness(_targetBrightness);
        }

        private void StepBrightness(int delta)
        {
            if (!_isInitialized) return;
            int next = Math.Max(0, Math.Min(100, (int)SliderBrightness.Value + delta));
            SliderBrightness.Value = next;
        }

        private void BtnPreset_Click(object sender, RoutedEventArgs e)
        {
            if (sender is FrameworkElement btn && btn.Tag != null)
            {
                if (int.TryParse(btn.Tag.ToString(), out int val))
                {
                    SliderBrightness.Value = val;
                }
            }
        }

        private async void BtnRefresh_Click(object sender, RoutedEventArgs e)
        {
            await RefreshAllDevicesAsync();
        }

        public async Task RefreshAllDevicesAsync()
        {
            if (!_isInitialized) return;

            RingRefreshing.Visibility = Visibility.Visible;
            BtnRefresh.IsEnabled = false;

            // Chạy việc đọc USB HID và DDC/CI ở background thread để UI tuyệt đối mượt mà
            await Task.Run(() =>
            {
                var monitorStatus = _monitorService.GetBrightness();
                var mouseStatus = _peripheralService.GetMouseStatus();
                var kbStatus = _peripheralService.GetKeyboardStatus();

                Dispatcher.Invoke(() =>
                {
                    ApplyDeviceStatuses(monitorStatus, mouseStatus, kbStatus);
                });
            });

            await Task.Delay(200);
            RingRefreshing.Visibility = Visibility.Collapsed;
            BtnRefresh.IsEnabled = true;
        }

        private void ApplyDeviceStatuses(
            (bool ok, int brightness) monitor,
            MouseStatus mouse,
            KeyboardStatus kb)
        {
            try
            {
                var now = DateTime.Now.ToString("HH:mm:ss");

                // 1. Màn hình
                if (monitor.ok)
                {
                    SliderBrightness.Value = monitor.brightness;
                    TxtBrightness.Text = $"{monitor.brightness}%";
                    SliderBrightness.IsEnabled = true;
                    TxtMonitorSub.Text = "Màn hình ngoài";
                    UpdatePresetHighlight(monitor.brightness);
                }
                else
                {
                    TxtBrightness.Text = "Ngoại tuyến";
                    SliderBrightness.IsEnabled = false;
                    TxtMonitorSub.Text = "Không phản hồi DDC/CI";
                    UpdatePresetHighlight(-1);
                }

                // 2. Chuột VXE Dragonfly R1 SE+
                if (mouse.Connected)
                {
                    IconMouseBattery.Visibility = Visibility.Visible;
                    TxtMouseBattery.Text = $"{mouse.Battery}%";
                    TxtMouseSub.Text = mouse.IsCharging ? "⚡ Đang sạc..." : "Chuột không dây";
                    CardMouse.ToolTip = $"Pin: {mouse.Battery}% | Điện áp: {mouse.VoltageMv / 1000.0:F2} V | Dongle 2.4 GHz";

                    UpdateBatteryVisual(IconMouseBattery, TxtMouseBattery, mouse.Battery, mouse.IsCharging);
                }
                else
                {
                    IconMouseBattery.Visibility = Visibility.Collapsed;
                    TxtMouseBattery.Text = "Ngoại tuyến";
                    TxtMouseSub.Text = "Không tìm thấy đầu thu 2.4 GHz";
                    SetNeutralBatteryBrush(IconMouseBattery, TxtMouseBattery, isMuted: true);
                    CardMouse.ToolTip = "Không tìm thấy đầu thu USB 2.4 GHz (Bấm F5 để quét lại)";
                }

                // 3. Phím Aula F75
                if (kb.Connected)
                {
                    IconKbBattery.Visibility = Visibility.Visible;
                    TxtKbBattery.Text = $"{kb.Battery}%";

                    if (kb.Battery >= 100)
                    {
                        TxtKbSub.Text = "Đã sạc đầy";
                    }
                    else if (kb.IsCharging)
                    {
                        TxtKbSub.Text = "⚡ Đang cắm sạc";
                    }
                    else
                    {
                        TxtKbSub.Text = "Bàn phím cơ";
                    }

                    CardKeyboard.ToolTip = $"Pin: {kb.Battery}% | Dongle 2.4 GHz (AULA F75)";
                    UpdateBatteryVisual(IconKbBattery, TxtKbBattery, kb.Battery, kb.IsCharging);
                }
                else
                {
                    IconKbBattery.Visibility = Visibility.Collapsed;
                    TxtKbBattery.Text = "Ngoại tuyến";
                    TxtKbSub.Text = "Không tìm thấy đầu thu 2.4 GHz";
                    SetNeutralBatteryBrush(IconKbBattery, TxtKbBattery, isMuted: true);
                    CardKeyboard.ToolTip = "Không tìm thấy đầu thu USB 2.4 GHz (Bấm F5 để quét lại)";
                }

                // Cập nhật tooltip nút làm mới & tray icon
                BtnRefresh.ToolTip = $"Làm mới (Đã đồng bộ lúc: {now})";
                _trayService.UpdateTooltip($"Device Hub | Màn: {(monitor.ok ? monitor.brightness + "%" : "--")} | Chuột: {(mouse.Connected ? mouse.Battery + "%" : "--")} | Phím: {(kb.Connected ? kb.Battery + "%" : "--")}");
            }
            catch { }
        }

        private static void UpdateBatteryVisual(SymbolIcon icon, Wpf.Ui.Controls.TextBlock text, int battery, bool isCharging)
        {
            if (isCharging)
            {
                icon.Symbol = SymbolRegular.BatteryCharge24;
                SetNeutralBatteryBrush(icon, text, isMuted: false);
                return;
            }

            // Chọn glyph chuẩn Segoe Fluent theo % pin
            if (battery >= 85) icon.Symbol = SymbolRegular.Battery1024;
            else if (battery >= 60) icon.Symbol = SymbolRegular.Battery724;
            else if (battery >= 40) icon.Symbol = SymbolRegular.Battery524;
            else if (battery >= 20) icon.Symbol = SymbolRegular.Battery224;
            else if (battery >= 10) icon.Symbol = SymbolRegular.Battery124;
            else icon.Symbol = SymbolRegular.Battery024;

            // Màu sắc Fluent: Chỉ đổi màu cảnh báo khi pin yếu
            if (battery <= 10)
            {
                icon.Opacity = 1.0;
                text.Opacity = 1.0;
                icon.Foreground = CriticalBrush;
                text.Foreground = CriticalBrush;
            }
            else if (battery <= 20)
            {
                icon.Opacity = 1.0;
                text.Opacity = 1.0;
                icon.Foreground = WarningBrush;
                text.Foreground = WarningBrush;
            }
            else
            {
                SetNeutralBatteryBrush(icon, text, isMuted: false);
            }
        }

        private static void SetNeutralBatteryBrush(SymbolIcon icon, Wpf.Ui.Controls.TextBlock text, bool isMuted)
        {
            if (isMuted)
            {
                icon.Opacity = 0.45;
                text.Opacity = 0.45;
            }
            else
            {
                icon.Opacity = 1.0;
                text.Opacity = 1.0;
                icon.ClearValue(ForegroundProperty);
                text.ClearValue(TextBlock.ForegroundProperty);
            }
        }
    }
}
