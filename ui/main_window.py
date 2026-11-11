import sys
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame
)
from PyQt6.QtGui import QColor, QFont, QIcon, QPixmap, QPainter, QBrush, QPen

from qfluentwidgets import (
    setTheme, Theme, CardWidget, SimpleCardWidget, Slider, 
    PushButton, PrimaryPushButton, InfoBadge, TitleLabel, 
    SubtitleLabel, CaptionLabel, StrongBodyLabel, BodyLabel,
    FluentIcon as FIF, ToolButton
)

def generate_app_icon() -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    painter.setBrush(QBrush(QColor(0, 120, 212)))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(1, 1, 30, 30, 7, 7)

    painter.setPen(QPen(QColor(255, 255, 255), 1.8))
    painter.drawRoundedRect(6, 7, 20, 13, 2, 2)
    painter.drawLine(16, 20, 16, 24)
    painter.drawLine(12, 24, 20, 24)
    painter.end()
    return QIcon(pixmap)

generate_fluent_icon = generate_app_icon

class MainWindow(QMainWindow):
    def __init__(self, monitor_ctrl, peripheral_ctrl, parent=None):
        super().__init__(parent)
        self.monitor_ctrl = monitor_ctrl
        self.peripheral_ctrl = peripheral_ctrl

        # Kích hoạt Dark Mode chuẩn Fluent WinUI 3
        setTheme(Theme.DARK)

        self.setWindowTitle("Device Hub")
        self.setFixedSize(460, 620)
        self.setWindowIcon(generate_app_icon())

        self.brightness_debounce = QTimer()
        self.brightness_debounce.setSingleShot(True)
        self.brightness_debounce.timeout.connect(self._apply_brightness)
        self._target_brightness = 50

        self.init_ui()
        self.refresh_all_devices()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 18, 20, 18)
        main_layout.setSpacing(12)

        # 1. Header chuẩn Windows 11
        header = QHBoxLayout()
        header.setSpacing(12)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = TitleLabel("Device Hub")
        self.subtitle = CaptionLabel("Thiết bị & Màn hình ngoại vi")
        self.subtitle.setTextColor("#9d9d9d", "#9d9d9d")
        title_box.addWidget(title)
        title_box.addWidget(self.subtitle)
        header.addLayout(title_box)

        header.addStretch()

        self.btn_refresh = ToolButton(FIF.SYNC)
        self.btn_refresh.setFixedSize(36, 36)
        self.btn_refresh.setToolTip("Làm mới trạng thái thiết bị")
        self.btn_refresh.clicked.connect(self.refresh_all_devices)
        header.addWidget(self.btn_refresh)
        main_layout.addLayout(header)

        # ----------------------------------------------------
        # 2. Section: MÀN HÌNH
        # ----------------------------------------------------
        sec_mon_label = CaptionLabel("MÀN HÌNH")
        sec_mon_label.setTextColor("#8a8a8e", "#8a8a8e")
        main_layout.addWidget(sec_mon_label)

        self.mon_card = CardWidget()
        mon_layout = QVBoxLayout(self.mon_card)
        mon_layout.setContentsMargins(16, 14, 16, 14)
        mon_layout.setSpacing(12)

        # Hàng tiêu đề màn hình + Badge %
        mon_top = QHBoxLayout()
        m_text = QVBoxLayout()
        m_text.setSpacing(1)
        m_name = StrongBodyLabel("Xiaomi A24i")
        m_desc = CaptionLabel("Giao thức DDC/CI • HDMI / DP")
        m_desc.setTextColor("#9d9d9d", "#9d9d9d")
        m_text.addWidget(m_name)
        m_text.addWidget(m_desc)
        mon_top.addLayout(m_text)

        mon_top.addStretch()

        self.mon_val_badge = InfoBadge("50%")
        mon_top.addWidget(self.mon_val_badge)
        mon_layout.addLayout(mon_top)

        # WinUI 3 Fluent Slider chuẩn Microsoft
        self.slider = Slider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self._on_slider_change)
        mon_layout.addWidget(self.slider)

        # Hàng nút tắt nhanh 20% 50% 75% 100%
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        for val in [20, 50, 75, 100]:
            b = PushButton(f"{val}%")
            b.setFixedHeight(26)
            b.clicked.connect(lambda _, v=val: self.slider.setValue(v))
            btn_row.addWidget(b)
        mon_layout.addLayout(btn_row)

        hotkey_tip = CaptionLabel("Phím tắt nhanh: Ctrl + Alt + \u2191 / \u2193 để tăng/giảm 10%")
        hotkey_tip.setTextColor("#808080", "#808080")
        mon_layout.addWidget(hotkey_tip)

        main_layout.addWidget(self.mon_card)

        # ----------------------------------------------------
        # 3. Section: THIẾT BỊ KHÔNG DÂY
        # ----------------------------------------------------
        sec_peri_label = CaptionLabel("THIẾT BỊ KHÔNG DÂY")
        sec_peri_label.setTextColor("#8a8a8e", "#8a8a8e")
        main_layout.addWidget(sec_peri_label)

        # Card Chuột VXE R1 SE+
        self.mouse_card = CardWidget()
        mouse_layout = QHBoxLayout(self.mouse_card)
        mouse_layout.setContentsMargins(16, 12, 16, 12)
        mouse_layout.setSpacing(12)

        m_info_box = QVBoxLayout()
        m_info_box.setSpacing(1)
        m_title = StrongBodyLabel("VXE Dragonfly R1 SE+")
        self.mouse_subtext = CaptionLabel("2.4 GHz Không dây")
        self.mouse_subtext.setTextColor("#9d9d9d", "#9d9d9d")
        m_info_box.addWidget(m_title)
        m_info_box.addWidget(self.mouse_subtext)
        mouse_layout.addLayout(m_info_box)

        mouse_layout.addStretch()

        self.mouse_pill = InfoBadge.success("85%")
        mouse_layout.addWidget(self.mouse_pill)
        main_layout.addWidget(self.mouse_card)

        # Card Bàn phím AULA F75
        self.kb_card = CardWidget()
        kb_layout = QHBoxLayout(self.kb_card)
        kb_layout.setContentsMargins(16, 12, 16, 12)
        kb_layout.setSpacing(12)

        k_info_box = QVBoxLayout()
        k_info_box.setSpacing(1)
        k_title = StrongBodyLabel("AULA F75 Mechanical Keyboard")
        self.kb_subtext = CaptionLabel("2.4 GHz Không dây")
        self.kb_subtext.setTextColor("#9d9d9d", "#9d9d9d")
        k_info_box.addWidget(k_title)
        k_info_box.addWidget(self.kb_subtext)
        kb_layout.addLayout(k_info_box)

        kb_layout.addStretch()

        self.kb_pill = InfoBadge.success("100%")
        kb_layout.addWidget(self.kb_pill)
        main_layout.addWidget(self.kb_card)

        # ----------------------------------------------------
        # 4. Section: PHÍM TẮT ĐÈN LED AULA F75
        # ----------------------------------------------------
        sec_led_label = CaptionLabel("PHÍM TẮT ĐÈN LED (AULA F75)")
        sec_led_label.setTextColor("#8a8a8e", "#8a8a8e")
        main_layout.addWidget(sec_led_label)

        self.led_card = SimpleCardWidget()
        led_card_layout = QVBoxLayout(self.led_card)
        led_card_layout.setContentsMargins(16, 12, 16, 12)
        led_card_layout.setSpacing(8)

        shortcuts = [
            ("Fn + \\", "Chuyển 16 chế độ hiệu ứng LED"),
            ("Fn + Tab", "Đổi các màu đèn tĩnh đơn sắc"),
            ("Fn + \u2191 / \u2193", "Tăng hoặc giảm độ sáng LED"),
            ("Fn + B", "Kiểm tra % pin trực tiếp trên thanh số")
        ]
        for key, desc in shortcuts:
            row = QHBoxLayout()
            row.setSpacing(10)
            
            badge = QLabel(key)
            badge.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
            badge.setStyleSheet("""
                color: #ffffff;
                background-color: #383838;
                border: 1px solid #4a4a4a;
                padding: 2px 8px;
                border-radius: 4px;
            """)
            
            desc_lbl = CaptionLabel(desc)
            desc_lbl.setTextColor("#b0b0b0", "#b0b0b0")
            
            row.addWidget(badge)
            row.addWidget(desc_lbl)
            row.addStretch()
            led_card_layout.addLayout(row)

        main_layout.addWidget(self.led_card)

        # 5. Footer
        self.footer = CaptionLabel("Đã đồng bộ")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setTextColor("#707070", "#707070")
        main_layout.addWidget(self.footer)

    def _on_slider_change(self, value):
        self.mon_val_badge.setText(f"{value}%")
        self._target_brightness = value
        self.brightness_debounce.start(80)

    def _apply_brightness(self):
        self.monitor_ctrl.set_brightness(self._target_brightness)

    def step_brightness(self, delta: int):
        val = max(0, min(100, self.slider.value() + delta))
        self.slider.setValue(val)

    def refresh_all_devices(self):
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
            self.mouse_pill.setText(f"{pct}%")
            sub = "Đang sạc qua cáp" if mouse["is_charging"] else f"2.4 GHz Không dây • {mouse['voltage_mv']/1000:.2f} V"
            self.mouse_subtext.setText(sub)
        else:
            self.mouse_pill.setText("Ngoại tuyến")
            self.mouse_subtext.setText("Không tìm thấy đầu thu")

        # 3. Phím Aula F75
        kb = self.peripheral_ctrl.get_keyboard_status()
        if kb["connected"]:
            pct = kb["battery"]
            self.kb_pill.setText(f"{pct}%")
            sub = "Đang sạc qua cáp" if kb["is_charging"] else "2.4 GHz Không dây"
            self.kb_subtext.setText(sub)
        else:
            self.kb_pill.setText("Ngoại tuyến")
            self.kb_subtext.setText("Không tìm thấy đầu thu")

        self.footer.setText(f"Đã đồng bộ lúc: {now}")
