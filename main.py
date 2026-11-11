import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QTimer, pyqtSignal, QObject

from controllers.monitor import MonitorController
from controllers.peripherals import PeripheralController
from controllers.hotkeys import GlobalHotkeyManager
from ui.main_window import MainWindow, generate_app_icon

class HotkeyDispatcher(QObject):
    step_signal = pyqtSignal(int)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Device Hub")

    # Khởi tạo phần cứng
    monitor_ctrl = MonitorController()
    peripheral_ctrl = PeripheralController()

    # Cửa sổ chính
    window = MainWindow(monitor_ctrl, peripheral_ctrl)
    app_icon = generate_app_icon()
    app.setWindowIcon(app_icon)

    # Đăng ký phím tắt toàn hệ thống (Ctrl + Alt + Up / Down)
    dispatcher = HotkeyDispatcher()
    dispatcher.step_signal.connect(window.step_brightness)

    hotkey_mgr = GlobalHotkeyManager(
        on_up=lambda: dispatcher.step_signal.emit(10),
        on_down=lambda: dispatcher.step_signal.emit(-10)
    )
    hotkey_mgr.start()
    app.aboutToQuit.connect(hotkey_mgr.stop)

    # Khởi tạo System Tray Icon
    tray = QSystemTrayIcon(app_icon, app)
    tray.setToolTip("Device Control Hub — A24i, VXE, AULA")

    tray_menu = QMenu()
    tray_menu.setStyleSheet("""
        QMenu {
            background-color: #242429;
            color: #ffffff;
            border: 1px solid #33333a;
            border-radius: 8px;
            padding: 4px;
        }
        QMenu::item {
            padding: 6px 20px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background-color: #0078D4;
        }
    """)

    act_show = tray_menu.addAction("Mở Bảng Điều Khiển")
    act_refresh = tray_menu.addAction("Làm mới trạng thái")
    tray_menu.addSeparator()
    act_quit = tray_menu.addAction("Thoát hoàn toàn")

    act_show.triggered.connect(lambda: (window.show(), window.activateWindow()))
    act_refresh.triggered.connect(window.refresh_all_devices)
    act_quit.triggered.connect(app.quit)

    def on_tray_activated(reason):
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick
        ):
            if window.isVisible():
                window.hide()
            else:
                window.show()
                window.activateWindow()

    tray.activated.connect(on_tray_activated)
    tray.setContextMenu(tray_menu)
    tray.show()

    # Tự động cập nhật mỗi 45 giây
    timer = QTimer()
    timer.timeout.connect(window.refresh_all_devices)
    timer.start(45000)

    # Mở cửa sổ chính
    window.show()
    window.activateWindow()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
