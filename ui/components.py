import math
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont

class CircularBatteryGauge(QWidget):
    """Widget vòng tròn đo pin hiện đại phong cách Apple / Gaming Hub"""
    
    def __init__(self, size=64, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.percentage = 0
        self.is_charging = False
        self.is_connected = False

    def set_data(self, percentage: int, is_charging: bool = False, is_connected: bool = True):
        self.percentage = max(0, min(100, percentage))
        self.is_charging = is_charging
        self.is_connected = is_connected
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        margin = 6
        rect = QRectF(margin, margin, w - 2 * margin, h - 2 * margin)
        stroke_width = 5.0

        # 1. Vẽ vòng tròn nền mờ
        pen_bg = QPen(QColor(45, 45, 50), stroke_width)
        pen_bg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bg)
        painter.drawEllipse(rect)

        # 2. Xác định màu sắc theo % pin
        if not self.is_connected:
            color = QColor(100, 100, 105)
        elif self.is_charging:
            color = QColor(0, 210, 255)  # Cyan khi đang sạc
        elif self.percentage > 40:
            color = QColor(16, 185, 129)  # Xanh ngọc neon
        elif self.percentage >= 20:
            color = QColor(245, 158, 11)  # Vàng cam cảnh báo
        else:
            color = QColor(244, 63, 94)   # Đỏ pin yếu

        # 3. Vẽ vòng cung % pin
        if self.is_connected and self.percentage > 0:
            pen_fg = QPen(color, stroke_width)
            pen_fg.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_fg)
            # Góc bắt đầu 90 độ (đỉnh trên cùng), xoay theo chiều kim đồng hồ (âm)
            start_angle = 90 * 16
            span_angle = -int(self.percentage * 3.6 * 16)
            painter.drawArc(rect, start_angle, span_angle)

        # 4. Vẽ số % ở tâm vòng tròn
        painter.setPen(QColor(255, 255, 255) if self.is_connected else QColor(140, 140, 145))
        
        if not self.is_connected:
            font = QFont("Segoe UI", 9, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "OFF")
        else:
            font = QFont("Segoe UI Variable Display", 11, QFont.Weight.Bold)
            painter.setFont(font)
            text = f"{self.percentage}%"
            if self.is_charging:
                text = f"⚡{self.percentage}%"
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)

        painter.end()
