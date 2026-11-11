import sys
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, 
    QPushButton, QFrame, QGraphicsDropShadowEffect, QProgressBar
)
from PyQt6.QtGui import QColor, QFont, QCursor, QGuiApplication

class DeviceCard(QFrame):
    """Card hiển thị từng thiết bị theo phong cách Fluent Windows 11"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            DeviceCard {
                background-color: #242426;
                border-radius: 10px;
                border: 1px solid #333336;
                padding: 12px;
            }
        """)

class FlyoutWindow(QWidget):
    brightness_changed = pyqtSignal(int)
    refresh_requested = pyqtSignal()

    def __init__(self, monitor_ctrl, peripheral_ctrl, parent=None):
        super().__init__(parent)
        self.monitor_ctrl = monitor_ctrl
        self.peripheral_ctrl = peripheral_ctrl

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Timer debounce cho độ sáng màn hình
        self.brightness_debounce = QTimer()
        self.brightness_debounce.setSingleShot(True)
        self.brightness_debounce.timeout.connect(self._apply_brightness)
        self._target_brightness = 50

        self.init_ui()
        self.refresh_all_devices()

    def init_ui(self):
        self.setFixedSize(360, 470)

        # Layout nền bao bọc để đổ bóng
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(10, 10, 10, 10)

        # Khung chính của Flyout
        self.main_container = QWidget()
        self.main_container.setObjectName("MainContainer")
        self.main_container.setStyleSheet("""
            QWidget#MainContainer {
                background-color: #1a1a1c;
                border-radius: 14px;
                border: 1px solid #2d2d30;
            }
        """)

        # Đổ bóng mềm
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 6)
        self.main_container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.main_container)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        # 1. Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Device Hub")
        title.setFont(QFont("Segoe UI Variable Display", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        
        self.subtitle = QLabel("Hệ sinh thái ngoại vi")
        self.subtitle.setFont(QFont("Segoe UI", 9))
        self.subtitle.setStyleSheet("color: #8e8e93;")
        title_box.addWidget(title)
        title_box.addWidget(self.subtitle)
        header.addLayout(title_box)

        header.addStretch()

        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedSize(30, 30)
        self.btn_refresh.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_refresh.setToolTip("Làm mới tình trạng thiết bị")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #2c2c2e;
                color: #ffffff;
                border-radius: 15px;
                border: 1px solid #3a3a3c;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3a3a3c;
            }
        """)
        self.btn_refresh.clicked.connect(self.refresh_all_devices)
        header.addWidget(self.btn_refresh)
        layout.addLayout(header)

        # 2. Card Màn hình Xiaomi A24i
        self.mon_card = DeviceCard()
        mon_layout = QVBoxLayout(self.mon_card)
        mon_layout.setSpacing(8)

        mon_header = QHBoxLayout()
        mon_title = QLabel("🖥️  Xiaomi A24i")
        mon_title.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        mon_title.setStyleSheet("color: #ffffff;")
        
        self.mon_val_badge = QLabel("50%")
        self.mon_val_badge.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.mon_val_badge.setStyleSheet("color: #00d2ff; background: #162a36; padding: 2px 8px; border-radius: 6px;")
        mon_header.addWidget(mon_title)
        mon_header.addStretch()
        mon_header.addWidget(self.mon_val_badge)
        mon_layout.addLayout(mon_header)

        # Slider chỉnh độ sáng
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #3a3a3c;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #0078D4;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 2px solid #0078D4;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #e0f2fe;
            }
        """)
        self.slider.valueChanged.connect(self._on_slider_change)
        mon_layout.addWidget(self.slider)

        # Phím tắt nhanh 25% 50% 75% 100%
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        for val in [20, 50, 75, 100]:
            b = QPushButton(f"{val}%")
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.setFixedHeight(22)
            b.setStyleSheet("""
                QPushButton {
                    background: #2c2c2e;
                    color: #d1d1d6;
                    border: 1px solid #3a3a3c;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #3a3a3c;
                    color: #ffffff;
                }
            """)
            b.clicked.connect(lambda _, v=val: self.slider.setValue(v))
            btn_row.addWidget(b)
        mon_layout.addLayout(btn_row)
        layout.addWidget(self.mon_card)

        # 3. Card Chuột VXE R1 SE+
        self.mouse_card = DeviceCard()
        mouse_layout = QVBoxLayout(self.mouse_card)
        mouse_layout.setSpacing(6)

        mouse_header = QHBoxLayout()
        mouse_title = QLabel("🖱️  VXE Dragonfly R1 SE+")
        mouse_title.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        mouse_title.setStyleSheet("color: #ffffff;")
        
        self.mouse_badge = QLabel("Chưa nhận")
        self.mouse_badge.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.mouse_badge.setStyleSheet("color: #30d158; background: #172d1f; padding: 2px 8px; border-radius: 6px;")
        mouse_header.addWidget(mouse_title)
        mouse_header.addStretch()
        mouse_header.addWidget(self.mouse_badge)
        mouse_layout.addLayout(mouse_header)

        self.mouse_progress = QProgressBar()
        self.mouse_progress.setFixedHeight(6)
        self.mouse_progress.setTextVisible(False)
        self.mouse_progress.setStyleSheet("""
            QProgressBar {
                background: #3a3a3c;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: #30d158;
                border-radius: 3px;
            }
        """)
        mouse_layout.addWidget(self.mouse_progress)

        self.mouse_info = QLabel("2.4GHz Không dây")
        self.mouse_info.setFont(QFont("Segoe UI", 9))
        self.mouse_info.setStyleSheet("color: #8e8e93;")
        mouse_layout.addWidget(self.mouse_info)
        layout.addWidget(self.mouse_card)

        # 4. Card Phím AULA F75
        self.kb_card = DeviceCard()
        kb_layout = QVBoxLayout(self.kb_card)
        kb_layout.setSpacing(6)

        kb_header = QHBoxLayout()
        kb_title = QLabel("⌨️  AULA F75")
        kb_title.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        kb_title.setStyleSheet("color: #ffffff;")

        self.kb_badge = QLabel("100%")
        self.kb_badge.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.kb_badge.setStyleSheet("color: #30d158; background: #172d1f; padding: 2px 8px; border-radius: 6px;")
        kb_header.addWidget(kb_title)
        kb_header.addStretch()
        kb_header.addWidget(self.kb_badge)
        kb_layout.addLayout(kb_header)

        self.kb_progress = QProgressBar()
        self.kb_progress.setFixedHeight(6)
        self.kb_progress.setTextVisible(False)
        self.kb_progress.setStyleSheet("""
            QProgressBar {
                background: #3a3a3c;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background: #30d158;
                border-radius: 3px;
            }
        """)
        kb_layout.addWidget(self.kb_progress)

        self.kb_info = QLabel("2.4GHz Không dây")
        self.kb_info.setFont(QFont("Segoe UI", 9))
        self.kb_info.setStyleSheet("color: #8e8e93;")
        kb_layout.addWidget(self.kb_info)
        layout.addWidget(self.kb_card)

        # 5. Footer Status
        self.footer = QLabel("Khởi động thành công")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setFont(QFont("Segoe UI", 8))
        self.footer.setStyleSheet("color: #636366;")
        layout.addWidget(self.footer)

        outer_layout.addWidget(self.main_container)

    def _on_slider_change(self, value):
        self.mon_val_badge.setText(f"{value}%")
        self._target_brightness = value
        # Chờ 80ms không kéo tiếp mới gửi lệnh xuống màn hình để tránh nghẽn DDC/CI
        self.brightness_debounce.start(80)

    def _apply_brightness(self):
        self.monitor_ctrl.set_brightness(self._target_brightness)

    def refresh_all_devices(self):
        """Làm mới dữ liệu cả 3 thiết bị"""
        now = datetime.now().strftime("%H:%M:%S")

        # 1. Màn hình
        ok, bright = self.monitor_ctrl.get_brightness()
        if ok:
            self.slider.blockSignals(True)
            self.slider.setValue(bright)
            self.mon_val_badge.setText(f"{bright}%")
            self.slider.blockSignals(False)
            self.slider.setEnabled(True)
        else:
            self.mon_val_badge.setText("Ngoại tuyến")
            self.slider.setEnabled(False)

        # 2. Chuột VXE
        mouse = self.peripheral_ctrl.get_mouse_status()
        if mouse["connected"]:
            pct = mouse["battery"]
            self.mouse_badge.setText(f"{pct}%")
            self.mouse_progress.setValue(pct)
            
            # Đổi màu pin: Xanh (>30%), Vàng (15-30%), Đỏ (<15%)
            color = "#30d158" if pct > 30 else ("#ffd60a" if pct >= 15 else "#ff453a")
            self.mouse_badge.setStyleSheet(f"color: {color}; background: #222723; padding: 2px 8px; border-radius: 6px;")
            self.mouse_progress.setStyleSheet(f"""
                QProgressBar {{ background: #3a3a3c; border-radius: 3px; }}
                QProgressBar::chunk {{ background: {color}; border-radius: 3px; }}
            """)
            
            status_text = "⚡ Đang sạc" if mouse["is_charging"] else f"2.4G Không dây ({mouse['voltage_mv']/1000:.2f}V)"
            self.mouse_info.setText(status_text)
        else:
            self.mouse_badge.setText("Ngoại tuyến")
            self.mouse_badge.setStyleSheet("color: #8e8e93; background: #2c2c2e; padding: 2px 8px; border-radius: 6px;")
            self.mouse_progress.setValue(0)
            self.mouse_info.setText("Không tìm thấy đầu thu")

        # 3. Phím Aula F75
        kb = self.peripheral_ctrl.get_keyboard_status()
        if kb["connected"]:
            pct = kb["battery"]
            self.kb_badge.setText(f"{pct}%")
            self.kb_progress.setValue(pct)
            color = "#30d158" if pct > 30 else ("#ffd60a" if pct >= 15 else "#ff453a")
            self.kb_badge.setStyleSheet(f"color: {color}; background: #222723; padding: 2px 8px; border-radius: 6px;")
            self.kb_progress.setStyleSheet(f"""
                QProgressBar {{ background: #3a3a3c; border-radius: 3px; }}
                QProgressBar::chunk {{ background: {color}; border-radius: 3px; }}
            """)
            status_text = "⚡ Đang sạc / Dây" if kb["is_charging"] else "2.4G Không dây"
            self.kb_info.setText(status_text)
        else:
            self.kb_badge.setText("Ngoại tuyến")
            self.kb_badge.setStyleSheet("color: #8e8e93; background: #2c2c2e; padding: 2px 8px; border-radius: 6px;")
            self.kb_progress.setValue(0)
            self.kb_info.setText("Không tìm thấy đầu thu")

        self.footer.setText(f"Cập nhật lúc: {now}")

    def position_above_tray(self):
        """Tự động canh vị trí Flyout nằm ngay trên góc Taskbar bên phải"""
        screen = QGuiApplication.primaryScreen().availableGeometry()
        x = screen.right() - self.width() - 12
        y = screen.bottom() - self.height() - 12
        self.move(x, y)

    def changeEvent(self, event):
        """Tự động ẩn khi người dùng click ra ngoài cửa sổ"""
        if event.type() == event.Type.ActivationChange:
            if not self.isActiveWindow():
                self.hide()
        super().changeEvent(event)
