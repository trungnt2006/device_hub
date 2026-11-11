using System;
using System.IO;
using System.Threading;
using System.Windows;

namespace DeviceHub
{
    public partial class App : System.Windows.Application
    {
        private const string MutexName = "DeviceHub_SingleInstance_Mutex_9001";
        private const string EventName = "DeviceHub_ShowEvent_9001";

        private static Mutex? _singleInstanceMutex;
        private static EventWaitHandle? _showEventHandle;
        private static Thread? _waitThread;

        protected override void OnStartup(StartupEventArgs e)
        {
            bool createdNew = true;
            try
            {
                _singleInstanceMutex = new Mutex(true, MutexName, out createdNew);
            }
            catch
            {
                createdNew = true;
            }

            if (!createdNew)
            {
                // Ứng dụng đã đang chạy ngầm trong khay hệ thống!
                // Báo hiệu instance cũ mở flyout lên
                try
                {
                    if (EventWaitHandle.TryOpenExisting(EventName, out var handle))
                    {
                        handle.Set();
                    }
                }
                catch { }

                // Thoát tiến trình trùng lặp ngay lập tức
                Shutdown();
                return;
            }

            // Tạo Event để lắng nghe tín hiệu từ các lần mở sau
            try
            {
                _showEventHandle = new EventWaitHandle(false, EventResetMode.AutoReset, EventName);
                _waitThread = new Thread(() =>
                {
                    while (_showEventHandle != null && _showEventHandle.WaitOne())
                    {
                        Dispatcher.Invoke(() =>
                        {
                            if (MainWindow is MainWindow mw)
                            {
                                mw.ToggleFlyout();
                            }
                        });
                    }
                })
                {
                    IsBackground = true
                };
                _waitThread.Start();
            }
            catch { }

            base.OnStartup(e);
        }

        protected override void OnExit(ExitEventArgs e)
        {
            _showEventHandle?.Dispose();
            _singleInstanceMutex?.Dispose();
            base.OnExit(e);
        }
    }
}
