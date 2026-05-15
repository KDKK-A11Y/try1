from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QLabel, QPushButton, QTextEdit,
                             QGroupBox, QFrame, QProgressBar, QSizePolicy, QComboBox,
                             QInputDialog, QLineEdit, QScrollArea, QDialog, QListWidget,
                             QListWidgetItem, QMessageBox)
from PyQt5.QtGui import QFont, QLinearGradient, QRadialGradient, QPalette, QBrush, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QRect, QPointF
from config.config import DEVICE_NAMES, ROOMS, DEVICE_TYPES, DEFAULT_ROOM_DEVICES
from modules.device_manager import DeviceManager
from voice.voiceprint_recognizer import VoiceprintRecognizer
import os
import pygame

class DeviceIcon(QWidget):
    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id
        self.state = False
        self.rotation = 0
        self.blink_state = True
        self.wind_offset = 0
        self.water_drop_offset = 0
        self.sweep_angle = 0
        self.pulse_scale = 1.0
        self.pulse_direction = 1
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.setFixedSize(90, 90)
    
    def set_state(self, state):
        self.state = state
        if state:
            self.animation_timer.start(50)
        else:
            self.animation_timer.stop()
            self.rotation = 0
            self.wind_offset = 0
            self.water_drop_offset = 0
            self.sweep_angle = 0
            self.pulse_scale = 1.0
        self.update()
    
    def update_animation(self):
        if self.device_id in ['fan', 'robot_vacuum']:
            self.rotation += 8
            if self.rotation >= 360:
                self.rotation = 0
        elif self.device_id in ['aircon', 'purifier', 'air_purifier']:
            self.wind_offset += 5
            if self.wind_offset >= 60:
                self.wind_offset = 0
        elif self.device_id == 'light':
            self.blink_state = not self.blink_state
        elif self.device_id in ['humidifier', 'water_valve']:
            self.water_drop_offset += 3
            if self.water_drop_offset >= 100:
                self.water_drop_offset = 0
        elif self.device_id == 'camera':
            self.sweep_angle += 2
            if self.sweep_angle >= 360:
                self.sweep_angle = 0
        elif self.device_id in ['speaker', 'smoke_detector']:
            self.pulse_scale += 0.02 * self.pulse_direction
            if self.pulse_scale >= 1.1 or self.pulse_scale <= 0.9:
                self.pulse_direction *= -1
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # 根据设备类型绘制不同图标
        device_drawers = {
            'light': self.draw_light,
            'fan': self.draw_fan,
            'aircon': self.draw_aircon,
            'tv': self.draw_tv,
            'curtain': self.draw_curtain,
            'heater': self.draw_heater,
            'humidifier': self.draw_humidifier,
            'dehumidifier': self.draw_dehumidifier,
            'purifier': self.draw_purifier,
            'speaker': self.draw_speaker,
            'projector': self.draw_projector,
            'robot_vacuum': self.draw_robot_vacuum,
            'smart_lock': self.draw_smart_lock,
            'camera': self.draw_camera,
            'door_sensor': self.draw_door_sensor,
            'motion_sensor': self.draw_motion_sensor,
            'smoke_detector': self.draw_smoke_detector,
            'water_heater': self.draw_water_heater,
            'oven': self.draw_oven,
            'microwave': self.draw_microwave,
            'refrigerator': self.draw_refrigerator,
            'washing_machine': self.draw_washing_machine,
            'dishwasher': self.draw_dishwasher,
            'coffee_maker': self.draw_coffee_maker,
            'air_purifier': self.draw_air_purifier,
            'rgb_strip': self.draw_rgb_strip,
            'smart_socket': self.draw_smart_socket,
            'water_valve': self.draw_water_valve
        }
        
        drawer = device_drawers.get(self.device_id, self.draw_default)
        drawer(painter, center_x, center_y)
    
    def draw_light(self, painter, cx, cy):
        if self.state:
            gradient = QLinearGradient(cx-30, cy-30, cx+30, cy+30)
            gradient.setColorAt(0, QColor(255, 255, 150))
            gradient.setColorAt(0.5, QColor(255, 255, 0))
            gradient.setColorAt(1, QColor(200, 200, 0))
            
            if self.blink_state:
                painter.setOpacity(1)
            else:
                painter.setOpacity(0.8)
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(255, 255, 100), 2))
            painter.drawEllipse(cx-20, cy-25, 40, 50)
            
            painter.setBrush(QBrush(QColor(200, 200, 200)))
            painter.setPen(QPen(QColor(150, 150, 150), 2))
            painter.drawPolygon(
                QPointF(cx-8, cy+25),
                QPointF(cx+8, cy+25),
                QPointF(cx+5, cy+35),
                QPointF(cx-5, cy+35)
            )
            
            glow = QRadialGradient(cx, cy, 50)
            glow.setColorAt(0, QColor(255, 255, 100, 80))
            glow.setColorAt(1, QColor(255, 255, 0, 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(cx-40, cy-40, 80, 80)
        else:
            painter.setBrush(QBrush(QColor(60, 60, 60)))
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            painter.drawEllipse(cx-18, cy-22, 36, 45)
            
            painter.setBrush(QBrush(QColor(80, 80, 80)))
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            painter.drawPolygon(
                QPointF(cx-7, cy+23),
                QPointF(cx+7, cy+23),
                QPointF(cx+4, cy+32),
                QPointF(cx-4, cy+32)
            )
    
    def draw_fan(self, painter, cx, cy):
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.rotation)
        
        if self.state:
            pen_color = QColor(100, 200, 255)
            brush_color = QColor(100, 200, 255, 30)
        else:
            pen_color = QColor(80, 80, 80)
            brush_color = QColor(80, 80, 80, 30)
        
        painter.setPen(QPen(pen_color, 2))
        painter.setBrush(QBrush(brush_color))
        
        for i in range(3):
            painter.save()
            painter.rotate(i * 120)
            painter.drawEllipse(-25, -5, 50, 10)
            painter.restore()
        
        painter.setBrush(QBrush(QColor(120, 120, 120)))
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        painter.drawEllipse(-6, -6, 12, 12)
        
        if self.state:
            glow = QRadialGradient(0, 0, 40)
            glow.setColorAt(0, QColor(100, 200, 255, 30))
            glow.setColorAt(1, QColor(100, 200, 255, 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(-35, -35, 70, 70)
        
        painter.restore()
    
    def draw_aircon(self, painter, cx, cy):
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        painter.setBrush(QBrush(QColor(80, 80, 80)))
        painter.drawRect(cx-30, cy-15, 60, 30)
        
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawLine(cx-25, cy-5, cx+25, cy-5)
        painter.drawLine(cx-25, cy+5, cx+25, cy+5)
        
        if self.state:
            for i in range(3):
                offset = (self.wind_offset + i * 20) % 60
                alpha = 100 + (offset % 30) * 5
                y_pos = cy + 15 + (offset % 30)
                
                painter.setPen(QPen(QColor(100, 200, 255, alpha), 2))
                painter.setBrush(Qt.NoBrush)
                
                start_x = cx - 15 + i * 15
                painter.drawLine(start_x, cy + 15, start_x + 10, y_pos)
    
    def draw_tv(self, painter, cx, cy):
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        painter.drawRect(cx-30, cy-25, 60, 40)
        
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        painter.setBrush(QBrush(QColor(40, 40, 40)))
        painter.drawRect(cx-26, cy-21, 52, 32)
        
        if self.state:
            gradient = QLinearGradient(cx-24, cy-19, cx+24, cy+11)
            gradient.setColorAt(0, QColor(0, 50, 100))
            gradient.setColorAt(0.5, QColor(0, 100, 200))
            gradient.setColorAt(1, QColor(0, 50, 100))
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawRect(cx-24, cy-19, 48, 28)
            
            painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
            painter.drawLine(cx-15, cy-8, cx+15, cy-8)
            painter.drawLine(cx-15, cy+2, cx+5, cy+2)
        
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx+20, cy+15, 6, 6)
    
    def draw_curtain(self, painter, cx, cy):
        painter.setPen(QPen(QColor(120, 120, 120), 2))
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        
        if self.state:
            painter.drawRect(cx-35, cy-35, 20, 70)
            painter.drawRect(cx+15, cy-35, 20, 70)
            
            painter.setBrush(QBrush(QColor(100, 150, 200, 50)))
            painter.drawRect(cx-15, cy-35, 30, 70)
            
            painter.setPen(QPen(QColor(150, 180, 220), 1))
            for i in range(3):
                painter.drawLine(cx-10 + i*10, cy-30, cx-10 + i*10, cy+30)
        else:
            painter.drawRect(cx-35, cy-35, 70, 70)
            
            painter.setPen(QPen(QColor(150, 150, 150), 1))
            for i in range(7):
                offset = i * 10
                painter.drawLine(cx-30 + offset, cy-30, cx-30 + offset, cy+30)
        
        painter.setBrush(QBrush(QColor(80, 80, 80)))
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawRect(cx-38, cy-38, 76, 8)
    
    def draw_heater(self, painter, cx, cy):
        painter.setPen(QPen(QColor(120, 120, 120), 2))
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        painter.drawRect(cx-30, cy-20, 60, 40)
        
        if self.state:
            painter.setPen(QPen(QColor(255, 100, 50), 2))
            for i in range(3):
                y = cy - 10 + i * 15
                alpha = 100 + ((self.wind_offset + i * 20) % 30) * 5
                painter.setPen(QPen(QColor(255, 150, 100, alpha), 2))
                painter.drawLine(cx-20, y, cx+20, y)
            
            glow = QRadialGradient(cx, cy, 40)
            glow.setColorAt(0, QColor(255, 150, 100, 30))
            glow.setColorAt(1, QColor(255, 100, 50, 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(cx-35, cy-35, 70, 70)
    
    def draw_humidifier(self, painter, cx, cy):
        painter.setPen(QPen(QColor(120, 180, 220), 2))
        painter.setBrush(QBrush(QColor(60, 120, 180)))
        painter.drawEllipse(cx-25, cy-15, 50, 35)
        
        painter.setPen(QPen(QColor(80, 140, 200), 2))
        painter.setBrush(QBrush(QColor(100, 160, 220)))
        painter.drawEllipse(cx-15, cy-25, 30, 15)
        
        if self.state:
            for i in range(3):
                offset = (self.water_drop_offset + i * 30) % 100
                y_pos = cy + 10 - offset * 0.4
                alpha = int(150 - offset * 1.5)
                if alpha > 0:
                    painter.setPen(QPen(QColor(150, 200, 255, alpha), 1))
                    painter.setBrush(QBrush(QColor(150, 200, 255, alpha)))
                    painter.drawEllipse(cx-8 + i*8, int(y_pos), 4, 6)
    
    def draw_dehumidifier(self, painter, cx, cy):
        painter.setPen(QPen(QColor(120, 180, 150), 2))
        painter.setBrush(QBrush(QColor(60, 120, 100)))
        painter.drawRect(cx-25, cy-20, 50, 40)
        
        painter.setPen(QPen(QColor(80, 140, 120), 2))
        painter.drawRect(cx-20, cy+5, 40, 10)
        
        if self.state:
            for i in range(3):
                offset = (self.wind_offset + i * 20) % 60
                alpha = 100 + (offset % 30) * 5
                painter.setPen(QPen(QColor(100, 200, 150, alpha), 2))
                painter.drawLine(cx-15 + i*10, cy-5, cx-10 + i*10, cy-15)
    
    def draw_purifier(self, painter, cx, cy):
        painter.setPen(QPen(QColor(120, 180, 200), 2))
        painter.setBrush(QBrush(QColor(60, 100, 120)))
        painter.drawEllipse(cx-25, cy-30, 50, 60)
        
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QBrush(QColor(80, 130, 160)))
        painter.drawEllipse(cx-20, cy-25, 40, 50)
        
        if self.state:
            for i in range(4):
                offset = (self.wind_offset + i * 15) % 60
                alpha = 80 + (offset % 30) * 4
                angle = i * 90
                painter.save()
                painter.translate(cx, cy)
                painter.rotate(angle)
                painter.setPen(QPen(QColor(150, 220, 255, alpha), 2))
                painter.drawLine(0, -15, 0, -25)
                painter.restore()
    
    def draw_speaker(self, painter, cx, cy):
        painter.save()
        painter.translate(cx, cy)
        painter.scale(self.pulse_scale, self.pulse_scale)
        
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawRect(-30, -25, 60, 50)
        
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        for row in range(4):
            for col in range(6):
                painter.drawRect(-25 + col*8, -20 + row*10, 5, 5)
        
        if self.state:
            glow = QRadialGradient(0, 0, 40)
            glow.setColorAt(0, QColor(100, 150, 255, 20))
            glow.setColorAt(1, QColor(100, 150, 255, 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(-35, -35, 70, 70)
        
        painter.restore()
    
    def draw_projector(self, painter, cx, cy):
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        painter.drawRect(cx-30, cy-15, 60, 30)
        
        painter.setPen(QPen(QColor(120, 120, 120), 2))
        painter.setBrush(QBrush(QColor(80, 80, 80)))
        painter.drawRect(cx+20, cy-10, 15, 20)
        
        if self.state:
            painter.setPen(QPen(QColor(255, 255, 200, 150), 2))
            painter.drawLine(cx+35, cy, cx+60, cy-10)
            painter.drawLine(cx+35, cy, cx+60, cy+10)
            painter.drawLine(cx+35, cy, cx+60, cy)
    
    def draw_robot_vacuum(self, painter, cx, cy):
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.rotation)
        
        painter.setPen(QPen(QColor(100, 150, 200), 2))
        painter.setBrush(QBrush(QColor(60, 100, 150)))
        painter.drawEllipse(-25, -20, 50, 40)
        
        painter.setPen(QPen(QColor(80, 130, 180), 2))
        painter.setBrush(QBrush(QColor(100, 150, 200)))
        painter.drawEllipse(-8, -5, 16, 10)
        
        painter.setPen(QPen(QColor(120, 170, 220), 1))
        painter.drawArc(-15, -10, 30, 20, 0, 360 * 16)
        
        painter.restore()
    
    def draw_smart_lock(self, painter, cx, cy):
        painter.setPen(QPen(QColor(120, 120, 120), 2))
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        painter.drawRect(cx-15, cy-25, 30, 50)
        
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(80, 80, 80)))
        painter.drawRect(cx-10, cy+10, 20, 15)
        
        if self.state:
            painter.setPen(QPen(QColor(50, 200, 50), 3))
            painter.drawLine(cx-5, cy+15, cx+5, cy+20)
            painter.drawLine(cx+5, cy+20, cx+5, cy+12)
        else:
            painter.setPen(QPen(QColor(200, 50, 50), 3))
            painter.drawLine(cx-5, cy+12, cx+5, cy+22)
            painter.drawLine(cx+5, cy+12, cx-5, cy+22)
    
    def draw_camera(self, painter, cx, cy):
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawRect(cx-20, cy-20, 40, 40)
        
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.drawEllipse(cx-8, cy-8, 16, 16)
        
        if self.state:
            painter.setPen(QPen(QColor(0, 150, 255), 1))
            painter.drawArc(cx-15, cy-15, 30, 30, -30 * 16, 60 * 16)
    
    def draw_door_sensor(self, painter, cx, cy):
        painter.setPen(QPen(QColor(120, 120, 120), 2))
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        
        painter.drawRect(cx-25, cy-30, 15, 60)
        painter.drawRect(cx+10, cy-30, 15, 60)
        
        if self.state:
            painter.setPen(QPen(QColor(50, 200, 50), 2))
            painter.drawLine(cx-10, cy, cx+10, cy)
        else:
            painter.setPen(QPen(QColor(200, 50, 50), 2))
            painter.drawLine(cx-10, cy-10, cx+10, cy+10)
            painter.drawLine(cx-10, cy+10, cx+10, cy-10)
    
    def draw_motion_sensor(self, painter, cx, cy):
        painter.setPen(QPen(QColor(100, 150, 180), 2))
        painter.setBrush(QBrush(QColor(60, 100, 130)))
        painter.drawEllipse(cx-20, cy-25, 40, 50)
        
        painter.setPen(QPen(QColor(80, 130, 160), 2))
        painter.setBrush(QBrush(QColor(80, 130, 160)))
        painter.drawEllipse(cx-10, cy-5, 20, 30)
        
        if self.state:
            painter.setPen(QPen(QColor(255, 200, 100, 100), 1))
            for i in range(3):
                angle = -60 + i * 60
                painter.drawArc(cx-30, cy-30, 60, 60, angle * 16, 30 * 16)
    
    def draw_smoke_detector(self, painter, cx, cy):
        painter.save()
        painter.translate(cx, cy)
        painter.scale(self.pulse_scale, self.pulse_scale)
        
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(80, 80, 80)))
        painter.drawEllipse(-20, -15, 40, 30)
        
        painter.setPen(QPen(QColor(120, 120, 120), 2))
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.drawEllipse(-8, -18, 16, 8)
        
        if self.state:
            painter.setPen(QPen(QColor(255, 100, 100), 2))
            painter.drawArc(-15, -25, 30, 30, 0, 360 * 16)
        
        painter.restore()
    
    def draw_water_heater(self, painter, cx, cy):
        painter.setPen(QPen(QColor(120, 100, 80), 2))
        painter.setBrush(QBrush(QColor(60, 50, 40)))
        painter.drawRect(cx-15, cy-30, 30, 60)
        
        painter.setPen(QPen(QColor(100, 80, 60), 2))
        painter.drawRect(cx-12, cy-25, 24, 50)
        
        if self.state:
            painter.setPen(QPen(QColor(255, 150, 100), 2))
            for i in range(4):
                y = cy - 20 + i * 12
                alpha = 100 + ((self.wind_offset + i * 15) % 30) * 5
                painter.setPen(QPen(QColor(255, 150, 100, alpha), 2))
                painter.drawLine(cx-5, y, cx+5, y)
    
    def draw_oven(self, painter, cx, cy):
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawRect(cx-25, cy-20, 50, 40)
        
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        painter.setBrush(QBrush(QColor(40, 40, 40)))
        painter.drawRect(cx-20, cy-15, 40, 30)
        
        if self.state:
            painter.setPen(QPen(QColor(255, 150, 100), 2))
            painter.drawRect(cx-18, cy-13, 36, 26)
            painter.setPen(QPen(QColor(255, 200, 150, 100), 1))
            painter.drawLine(cx-8, cy-5, cx+8, cy-5)
            painter.drawLine(cx-8, cy+5, cx+8, cy+5)
    
    def draw_microwave(self, painter, cx, cy):
        painter.setPen(QPen(QColor(100, 120, 150), 2))
        painter.setBrush(QBrush(QColor(50, 60, 80)))
        painter.drawRect(cx-25, cy-20, 50, 40)
        
        painter.setPen(QPen(QColor(80, 100, 130), 2))
        painter.setBrush(QBrush(QColor(40, 50, 70)))
        painter.drawRect(cx-20, cy-15, 25, 30)
        
        painter.setPen(QPen(QColor(80, 100, 130), 1))
        painter.drawRect(cx+5, cy-10, 12, 20)
        
        if self.state:
            painter.setPen(QPen(QColor(100, 200, 255), 2))
            painter.drawRect(cx-18, cy-13, 21, 26)
    
    def draw_refrigerator(self, painter, cx, cy):
        painter.setPen(QPen(QColor(120, 150, 180), 2))
        painter.setBrush(QBrush(QColor(60, 90, 120)))
        painter.drawRect(cx-20, cy-30, 40, 60)
        
        painter.setPen(QPen(QColor(100, 130, 160), 2))
        painter.drawLine(cx-18, cy, cx+18, cy)
        
        if self.state:
            painter.setPen(QPen(QColor(100, 180, 255, 50), 1))
            painter.drawLine(cx-15, cy-25, cx+15, cy-25)
            painter.drawLine(cx-15, cy-20, cx+15, cy-20)
    
    def draw_washing_machine(self, painter, cx, cy):
        painter.setPen(QPen(QColor(100, 100, 120), 2))
        painter.setBrush(QBrush(QColor(50, 50, 70)))
        painter.drawRect(cx-25, cy-25, 50, 50)
        
        painter.setPen(QPen(QColor(80, 80, 100), 2))
        painter.setBrush(QBrush(QColor(40, 40, 60)))
        painter.drawEllipse(cx-15, cy-15, 30, 30)
        
        if self.state:
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(self.rotation)
            painter.setPen(QPen(QColor(100, 150, 200), 2))
            painter.drawLine(-10, 0, 10, 0)
            painter.drawLine(0, -10, 0, 10)
            painter.restore()
    
    def draw_dishwasher(self, painter, cx, cy):
        painter.setPen(QPen(QColor(100, 120, 140), 2))
        painter.setBrush(QBrush(QColor(50, 60, 70)))
        painter.drawRect(cx-25, cy-20, 50, 40)
        
        painter.setPen(QPen(QColor(80, 100, 120), 2))
        painter.setBrush(QBrush(QColor(40, 50, 60)))
        painter.drawRect(cx-20, cy-15, 40, 30)
        
        if self.state:
            painter.setPen(QPen(QColor(100, 180, 220), 1))
            for i in range(3):
                y = cy - 10 + i * 10
                painter.drawLine(cx-15, y, cx+15, y)
    
    def draw_coffee_maker(self, painter, cx, cy):
        painter.setPen(QPen(QColor(100, 80, 60), 2))
        painter.setBrush(QBrush(QColor(60, 40, 30)))
        painter.drawRect(cx-15, cy-30, 30, 50)
        
        painter.setPen(QPen(QColor(80, 60, 40), 2))
        painter.setBrush(QBrush(QColor(40, 30, 20)))
        painter.drawRect(cx-12, cy-25, 24, 15)
        
        painter.setPen(QPen(QColor(80, 60, 40), 2))
        painter.drawRect(cx-8, cy+5, 16, 20)
        
        if self.state:
            painter.setPen(QPen(QColor(150, 100, 50), 2))
            painter.setBrush(QBrush(QColor(150, 100, 50)))
            painter.drawEllipse(cx-5, cy+25, 10, 8)
    
    def draw_air_purifier(self, painter, cx, cy):
        painter.setPen(QPen(QColor(100, 180, 150), 2))
        painter.setBrush(QBrush(QColor(50, 100, 80)))
        painter.drawEllipse(cx-20, cy-30, 40, 60)
        
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QBrush(QColor(70, 130, 110)))
        painter.drawEllipse(cx-15, cy-25, 30, 50)
        
        if self.state:
            for i in range(4):
                offset = (self.wind_offset + i * 15) % 60
                alpha = 80 + (offset % 30) * 4
                painter.setPen(QPen(QColor(100, 220, 180, alpha), 2))
                painter.drawLine(cx-10 + i*5, cy-20, cx-10 + i*5, cy+20)
    
    def draw_rgb_strip(self, painter, cx, cy):
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        painter.setBrush(QBrush(QColor(40, 40, 40)))
        painter.drawRect(cx-35, cy-8, 70, 16)
        
        if self.state:
            colors = [QColor(255, 0, 0), QColor(255, 128, 0), QColor(255, 255, 0), 
                      QColor(0, 255, 0), QColor(0, 0, 255), QColor(128, 0, 255)]
            for i in range(6):
                painter.setBrush(QBrush(colors[i]))
                painter.drawRect(cx-30 + i*10, cy-5, 8, 10)
        else:
            painter.setBrush(QBrush(QColor(60, 60, 60)))
            for i in range(6):
                painter.drawRect(cx-30 + i*10, cy-5, 8, 10)
    
    def draw_smart_socket(self, painter, cx, cy):
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        painter.drawRect(cx-20, cy-20, 40, 40)
        
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        painter.setBrush(QBrush(QColor(40, 40, 40)))
        painter.drawRect(cx-15, cy-15, 30, 30)
        
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawEllipse(cx-5, cy-5, 10, 10)
        
        if self.state:
            painter.setPen(QPen(QColor(50, 200, 50), 2))
            painter.drawLine(cx, cy-10, cx, cy+10)
    
    def draw_water_valve(self, painter, cx, cy):
        painter.setPen(QPen(QColor(100, 150, 200), 2))
        painter.setBrush(QBrush(QColor(50, 100, 150)))
        painter.drawEllipse(cx-20, cy-20, 40, 40)
        
        painter.setPen(QPen(QColor(80, 130, 180), 2))
        painter.drawRect(cx-8, cy-30, 16, 15)
        
        if self.state:
            painter.setPen(QPen(QColor(150, 200, 255), 2))
            for i in range(3):
                offset = (self.water_drop_offset + i * 30) % 100
                y_pos = cy + 10 + offset * 0.3
                alpha = int(150 - offset * 1.5)
                if alpha > 0:
                    painter.setBrush(QBrush(QColor(150, 200, 255, alpha)))
                    painter.drawEllipse(cx-3 + i*6, int(y_pos), 4, 6)
    
    def draw_default(self, painter, cx, cy):
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(60, 60, 60)))
        painter.drawRect(cx-20, cy-20, 40, 40)
        
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.drawText(cx-10, cy+5, "?")
    
    def stop_animation(self):
        self.animation_timer.stop()

class DeviceWidget(QWidget):
    def __init__(self, device_id, device_name, sound_manager=None):
        super().__init__()
        self.device_id = device_id
        self.device_name = device_name
        self.sound_manager = sound_manager
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        
        self.icon_widget = DeviceIcon(device_id)
        
        self.status_label = QLabel(device_name)
        self.status_label.setFont(QFont('微软雅黑', 14, QFont.Medium))
        self.status_label.setStyleSheet("color: #aaa;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFixedHeight(30)
        
        self.toggle_btn = QPushButton('打开')
        self.toggle_btn.setFixedSize(110, 45)
        self.toggle_btn.setFont(QFont('微软雅黑', 12, QFont.Bold))
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a90d9, stop:1 #357abd);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                box-shadow: 0 3px 10px rgba(53, 122, 189, 0.4);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5a9fe9, stop:1 #4589cd);
                box-shadow: 0 4px 15px rgba(53, 122, 189, 0.6);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #357abd, stop:1 #2569ad);
                box-shadow: 0 2px 5px rgba(53, 122, 189, 0.3);
            }
        """)
        self.toggle_btn.clicked.connect(self.on_toggle)
        
        self.state_badge = QLabel('关闭')
        self.state_badge.setFont(QFont('微软雅黑', 10))
        self.state_badge.setStyleSheet("""
            QLabel {
                background-color: #333;
                color: #888;
                padding: 4px 12px;
                border-radius: 10px;
            }
        """)
        self.state_badge.setAlignment(Qt.AlignCenter)
        
        self.layout.addWidget(self.icon_widget, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.state_badge, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.toggle_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(self.layout)
        
        self.state = False
    
    def set_state(self, state):
        self.state = state
        self.icon_widget.set_state(state)
        
        if state:
            self.status_label.setStyleSheet("color: #00ff00;")
            self.toggle_btn.setText('关闭')
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d94a4a, stop:1 #bd3535);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 20px;
                    box-shadow: 0 3px 10px rgba(217, 74, 74, 0.4);
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e95a5a, stop:1 #cd4545);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #bd3535, stop:1 #ad2525);
                }
            """)
            self.state_badge.setText('开启')
            self.state_badge.setStyleSheet("""
                QLabel {
                    background-color: #006600;
                    color: #00ff00;
                    padding: 4px 12px;
                    border-radius: 10px;
                }
            """)
            if self.sound_manager:
                self.sound_manager.play_device_on()
        else:
            self.status_label.setStyleSheet("color: #aaa;")
            self.toggle_btn.setText('打开')
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a90d9, stop:1 #357abd);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 20px;
                    box-shadow: 0 3px 10px rgba(53, 122, 189, 0.4);
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5a9fe9, stop:1 #4589cd);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #357abd, stop:1 #2569ad);
                }
            """)
            self.state_badge.setText('关闭')
            self.state_badge.setStyleSheet("""
                QLabel {
                    background-color: #333;
                    color: #888;
                    padding: 4px 12px;
                    border-radius: 10px;
                }
            """)
            if self.sound_manager:
                self.sound_manager.play_device_off()
    
    def on_toggle(self):
        if self.sound_manager:
            self.sound_manager.play_click()

class MainWindow(QMainWindow):
    def __init__(self, state_manager, command_system, voice_recognizer=None, gesture_recognizer=None, logger=None, sound_manager=None):
        super().__init__()
        self.state_manager = state_manager
        self.command_system = command_system
        self.voice_recognizer = voice_recognizer
        self.gesture_recognizer = gesture_recognizer
        self.logger = logger
        self.sound_manager = sound_manager
        
        # 初始化设备管理器
        self.device_manager = DeviceManager()
        
        # 当前选中的房间
        self.current_room = 'living'
        
        # 初始化声纹识别器
        self.voiceprint_recognizer = VoiceprintRecognizer()
        self.voiceprint_recognizer.load_voiceprints()
        
        # 连接声纹识别信号
        self.voiceprint_recognizer.recording_started.connect(self.on_voiceprint_recording_started)
        self.voiceprint_recognizer.recording_finished.connect(self.on_voiceprint_recording_finished)
        self.voiceprint_recognizer.registration_finished.connect(self.on_voiceprint_registration_finished)
        self.voiceprint_recognizer.recognition_finished.connect(self.on_voiceprint_recognition_finished)
        self.voiceprint_recognizer.round_verified.connect(self.on_voiceprint_round_verified)
        
        self.init_ui()
        
        self.state_manager.state_changed.connect(self.update_device_state)
        
        if self.voice_recognizer:
            self.voice_recognizer.voice_detected.connect(self.on_voice_detected)
            self.voice_recognizer.recording_state_changed.connect(self.on_recording_state_changed)
            self.voice_recognizer.assistant_response.connect(self.on_assistant_response)
            self.voice_recognizer.smart_assistant.speak_ready.connect(self.on_speak_ready)
            self.voice_recognizer.smart_assistant.weather_updated.connect(self.on_weather_updated)
            self.voice_recognizer.wake_word_detected.connect(self.on_wake_word_detected)
        if self.gesture_recognizer:
            self.gesture_recognizer.gesture_detected.connect(self.on_gesture_detected)
        
        QTimer.singleShot(500, self.query_weather_on_startup)
        
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.update_log)
        self.log_timer.start(1000)
        
        pygame.mixer.init()
        self.current_audio_file = None
    
    def init_ui(self):
        self.setWindowTitle('智能语音交互控制系统')
        self.setGeometry(100, 100, 1100, 750)
        
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460);
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        left_panel = QWidget()
        left_panel.setStyleSheet("""
            QWidget {
                background: rgba(255,255,255,0.03);
                border-radius: 15px;
                border: 1px solid rgba(255,255,255,0.1);
            }
        """)
        left_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel('🤖 智能语音交互控制系统')
        title_label.setFont(QFont('微软雅黑', 26, QFont.Bold))
        title_label.setStyleSheet("color: #00ff00;")
        
        header_layout.addWidget(title_label)
        left_layout.addWidget(header_widget)
        
        self.weather_widget = QWidget()
        self.weather_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(64, 138, 236, 0.9),
                    stop:1 rgba(112, 176, 244, 0.9));
                border-radius: 18px;
                border: 1px solid rgba(255,255,255,0.15);
                padding: 15px 20px;
            }
        """)
        weather_layout = QHBoxLayout(self.weather_widget)
        weather_layout.setSpacing(25)
        weather_layout.setContentsMargins(15, 15, 15, 15)
        
        # 天气图标
        self.weather_icon_label = QLabel('🌞')
        self.weather_icon_label.setFont(QFont('Segoe UI Symbol', 60))
        self.weather_icon_label.setAlignment(Qt.AlignCenter)
        self.weather_icon_label.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 10px;
                min-width: 90px;
                min-height: 90px;
            }
        """)
        
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setSpacing(5)
        
        self.weather_info_label = QLabel('正在获取天气...')
        self.weather_info_label.setFont(QFont('微软雅黑', 14))
        self.weather_info_label.setStyleSheet("color: rgba(255,255,255,0.9);")
        
        self.weather_temp_label = QLabel('--°')
        self.weather_temp_label.setFont(QFont('微软雅黑', 40, QFont.Bold))
        self.weather_temp_label.setStyleSheet("color: #ffffff;")
        
        info_layout.addWidget(self.weather_info_label)
        info_layout.addWidget(self.weather_temp_label)
        
        weather_layout.addWidget(self.weather_icon_label)
        weather_layout.addWidget(info_container)
        weather_layout.addStretch()
        
        left_layout.addWidget(self.weather_widget)
        
        # 房间选择组件
        room_group = QGroupBox('🏠 房间选择')
        room_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(100,150,255,0.2);
                border-radius: 12px;
                padding: 15px;
                color: #6496ff;
                font-size: 14px;
                font-weight: bold;
                background: rgba(100,150,255,0.02);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
            }
        """)
        self.room_layout = QHBoxLayout(room_group)
        self.room_layout.setSpacing(10)
        
        self.room_buttons = {}
        for room_id, room_info in ROOMS.items():
            btn = QPushButton(f"{room_info['icon']} {room_info['name']}")
            btn.setFont(QFont('微软雅黑', 11))
            btn.setFixedHeight(38)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(255,255,255,0.05);
                    color: #aaa;
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 8px;
                    padding: 6px 12px;
                }}
                QPushButton:hover {{
                    background: rgba(100,150,255,0.2);
                    color: #6496ff;
                }}
                QPushButton:checked {{
                    background: {room_info['color']};
                    color: white;
                    border-color: {room_info['color']};
                }}
            """)
            btn.setCheckable(True)
            btn.setChecked(room_id == self.current_room)
            btn.clicked.connect(lambda checked, rid=room_id: self.on_room_selected(rid))
            self.room_buttons[room_id] = btn
            self.room_layout.addWidget(btn)
        
        add_room_btn = QPushButton('+ 添加房间')
        add_room_btn.setFont(QFont('微软雅黑', 11))
        add_room_btn.setFixedHeight(38)
        add_room_btn.setStyleSheet("""
            QPushButton {
                background: rgba(74,217,160,0.2);
                color: #4ad9a0;
                border: 1px solid rgba(74,217,160,0.4);
                border-radius: 8px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background: rgba(74,217,160,0.3);
            }
        """)
        add_room_btn.clicked.connect(self.on_add_room)
        self.room_layout.addWidget(add_room_btn)
        self.room_layout.addStretch()
        
        left_layout.addWidget(room_group)
        
        device_group = QGroupBox('设备控制中心')
        device_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(0,255,0,0.2);
                border-radius: 12px;
                padding: 20px;
                color: #00ff00;
                font-size: 16px;
                font-weight: bold;
                background: rgba(0,255,0,0.02);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
            }
        """)
        device_layout = QVBoxLayout(device_group)
        
        # 设备网格容器（可滚动）
        self.device_grid_container = QWidget()
        self.device_grid = QGridLayout(self.device_grid_container)
        self.device_grid.setSpacing(25)
        self.device_grid.setContentsMargins(0, 0, 0, 0)
        
        self.device_widgets = {}
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.device_grid_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255,255,255,0.05);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0,255,0,0.3);
                border-radius: 4px;
            }
        """)
        
        # 添加设备按钮
        add_device_btn = QPushButton('+ 添加设备到房间')
        add_device_btn.setFont(QFont('微软雅黑', 11))
        add_device_btn.setFixedHeight(35)
        add_device_btn.setStyleSheet("""
            QPushButton {
                background: rgba(74,144,217,0.2);
                color: #4a90d9;
                border: 1px solid rgba(74,144,217,0.4);
                border-radius: 8px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background: rgba(74,144,217,0.3);
            }
        """)
        add_device_btn.clicked.connect(self.on_add_device)
        
        device_layout.addWidget(add_device_btn)
        device_layout.addWidget(scroll_area)
        left_layout.addWidget(device_group)
        
        self.status_bar = QProgressBar()
        self.status_bar.setFixedHeight(25)
        self.status_bar.setStyleSheet("""
            QProgressBar {
                border-radius: 12px;
                background: rgba(255,255,255,0.1);
                text-align: center;
                color: #00ff00;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00ff00, stop:1 #00cc00);
                border-radius: 12px;
            }
        """)
        self.status_bar.setValue(100)
        self.status_bar.setFormat("系统状态: 正常运行")
        left_layout.addWidget(self.status_bar)
        
        right_panel = QWidget()
        right_panel.setStyleSheet("""
            QWidget {
                background: rgba(255,255,255,0.03);
                border-radius: 15px;
                border: 1px solid rgba(255,255,255,0.1);
            }
        """)
        right_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        right_panel.setFixedWidth(380)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(20)
        right_layout.setContentsMargins(20, 20, 20, 20)
        
        log_group = QGroupBox('📋 实时日志')
        log_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(0,255,0,0.2);
                border-radius: 12px;
                padding: 15px;
                color: #00ff00;
                font-size: 14px;
                font-weight: bold;
                background: rgba(0,255,0,0.02);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
            }
        """)
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont('Consolas', 11))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: rgba(0,0,0,0.4);
                color: #00ff00;
                border-radius: 8px;
                padding: 12px;
                border: 1px solid rgba(0,255,0,0.2);
            }
        """)
        self.log_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        log_layout.addWidget(self.log_text)
        
        control_group = QGroupBox('⚙️ 系统控制')
        control_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(0,255,0,0.2);
                border-radius: 12px;
                padding: 15px;
                color: #00ff00;
                font-size: 14px;
                font-weight: bold;
                background: rgba(0,255,0,0.02);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
            }
        """)
        control_layout = QVBoxLayout(control_group)
        control_layout.setSpacing(15)
        
        status_layout = QGridLayout()
        status_layout.setSpacing(10)
        
        self.voice_status = QLabel('🎤 语音识别')
        self.voice_status.setFont(QFont('微软雅黑', 12))
        self.voice_status.setStyleSheet("color: #00ff00;")
        self.voice_status.setAlignment(Qt.AlignCenter)
        
        self.voice_indicator = QFrame()
        self.voice_indicator.setFixedSize(12, 12)
        self.voice_indicator.setStyleSheet("""
            QFrame {
                border-radius: 6px;
                background-color: #00ff00;
                box-shadow: 0 0 10px #00ff00;
            }
        """)
        
        self.gesture_status = QLabel('🖐️ 手势识别')
        self.gesture_status.setFont(QFont('微软雅黑', 12))
        self.gesture_status.setStyleSheet("color: #00ff00;")
        self.gesture_status.setAlignment(Qt.AlignCenter)
        
        self.gesture_indicator = QFrame()
        self.gesture_indicator.setFixedSize(12, 12)
        self.gesture_indicator.setStyleSheet("""
            QFrame {
                border-radius: 6px;
                background-color: #00ff00;
                box-shadow: 0 0 10px #00ff00;
            }
        """)
        
        status_layout.addWidget(self.voice_status, 0, 0)
        status_layout.addWidget(self.voice_indicator, 0, 1)
        status_layout.addWidget(self.gesture_status, 1, 0)
        status_layout.addWidget(self.gesture_indicator, 1, 1)
        
        control_layout.addLayout(status_layout)
        
        lang_layout = QHBoxLayout()
        lang_label = QLabel('🌐 语言选择:')
        lang_label.setFont(QFont('微软雅黑', 12))
        lang_label.setStyleSheet("color: #aaa;")
        
        self.lang_combo = QComboBox()
        self.lang_combo.setFont(QFont('微软雅黑', 11))
        self.lang_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255,255,255,0.1);
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 6px 12px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #2a2a4a;
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
            }
        """)
        
        if self.voice_recognizer:
            languages = self.voice_recognizer.get_language_list()
            for key, info in languages.items():
                self.lang_combo.addItem(f"{info['name']} - {info['description']}", key)
            self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        control_layout.addLayout(lang_layout)
        
        self.mic_btn = QPushButton('🎤 按住说话')
        self.mic_btn.setFixedHeight(50)
        self.mic_btn.setFont(QFont('微软雅黑', 12, QFont.Bold))
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a90d9, stop:1 #357abd);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 8px 20px;
                box-shadow: 0 3px 10px rgba(53, 122, 189, 0.4);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5a9fe9, stop:1 #4589cd);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d94a4a, stop:1 #bd3535);
                box-shadow: 0 0 20px rgba(217, 74, 74, 0.6);
            }
        """)
        self.mic_btn.mousePressEvent = self.on_mic_press
        self.mic_btn.mouseReleaseEvent = self.on_mic_release
        self.mic_btn.setMouseTracking(True)
        control_layout.addWidget(self.mic_btn)
        
        reset_btn = QPushButton('🔄 重置所有设备')
        reset_btn.setFixedHeight(45)
        reset_btn.setFont(QFont('微软雅黑', 12, QFont.Bold))
        reset_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #666, stop:1 #444);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.3);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #777, stop:1 #555);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #555, stop:1 #333);
            }
        """)
        reset_btn.clicked.connect(self.on_reset)
        
        control_layout.addWidget(reset_btn)
        
        # 声纹识别按钮
        voiceprint_group = QGroupBox('🔊 声纹识别')
        voiceprint_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(100,150,255,0.3);
                border-radius: 12px;
                padding: 15px;
                color: #6496ff;
                font-size: 14px;
                font-weight: bold;
                background: rgba(100,150,255,0.03);
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
            }
        """)
        voiceprint_layout = QVBoxLayout(voiceprint_group)
        voiceprint_layout.setSpacing(12)
        
        self.register_voiceprint_btn = QPushButton('🎙️ 注册声纹')
        self.register_voiceprint_btn.setFixedHeight(42)
        self.register_voiceprint_btn.setFont(QFont('微软雅黑', 12, QFont.Bold))
        self.register_voiceprint_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a7cd9, stop:1 #356abd);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                box-shadow: 0 3px 10px rgba(53, 106, 189, 0.4);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5a8ce9, stop:1 #4579cd);
            }
        """)
        self.register_voiceprint_btn.clicked.connect(self.on_register_voiceprint)
        
        self.recognize_voiceprint_btn = QPushButton('👤 声纹识别')
        self.recognize_voiceprint_btn.setFixedHeight(42)
        self.recognize_voiceprint_btn.setFont(QFont('微软雅黑', 12, QFont.Bold))
        self.recognize_voiceprint_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4ad9a0, stop:1 #35bd8a);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                box-shadow: 0 3px 10px rgba(53, 189, 138, 0.4);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5ae9b0, stop:1 #45cd9a);
            }
        """)
        self.recognize_voiceprint_btn.clicked.connect(self.on_recognize_voiceprint)
        
        self.voiceprint_status = QLabel('声纹识别状态: 未识别')
        self.voiceprint_status.setFont(QFont('微软雅黑', 11))
        self.voiceprint_status.setStyleSheet("color: #888;")
        
        voiceprint_layout.addWidget(self.register_voiceprint_btn)
        voiceprint_layout.addWidget(self.recognize_voiceprint_btn)
        
        # 声纹管理按钮
        self.manage_voiceprint_btn = QPushButton('📋 声纹管理')
        self.manage_voiceprint_btn.setFixedHeight(42)
        self.manage_voiceprint_btn.setFont(QFont('微软雅黑', 12, QFont.Bold))
        self.manage_voiceprint_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #9664d9, stop:1 #7b4abd);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                box-shadow: 0 3px 10px rgba(123, 74, 189, 0.4);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a674e9, stop:1 #8b59cd);
            }
        """)
        self.manage_voiceprint_btn.clicked.connect(self.on_manage_voiceprint)
        voiceprint_layout.addWidget(self.manage_voiceprint_btn)
        
        voiceprint_layout.addWidget(self.voiceprint_status)
        
        control_layout.addWidget(voiceprint_group)
        
        self.wake_btn = QPushButton('🔔 开启语音唤醒')
        self.wake_btn.setFixedHeight(45)
        self.wake_btn.setFont(QFont('微软雅黑', 12, QFont.Bold))
        self.wake_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #444, stop:1 #333);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.3);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #555, stop:1 #444);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #666, stop:1 #555);
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4CAF50, stop:1 #388E3C);
            }
        """)
        self.wake_btn.setCheckable(True)
        self.wake_btn.clicked.connect(self.on_wake_toggled)
        control_layout.addWidget(self.wake_btn)
        
        # 手势绑定按钮
        self.gesture_bind_btn = QPushButton('🤟 手势绑定')
        self.gesture_bind_btn.setFixedHeight(42)
        self.gesture_bind_btn.setFont(QFont('微软雅黑', 12, QFont.Bold))
        self.gesture_bind_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4ad9d9, stop:1 #35bdbd);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                box-shadow: 0 3px 10px rgba(53, 189, 189, 0.4);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5ae9e9, stop:1 #45cdcd);
            }
        """)
        self.gesture_bind_btn.clicked.connect(self.on_gesture_binding)
        control_layout.addWidget(self.gesture_bind_btn)
        
        info_label = QLabel("💡 提示：按住麦克风按钮说话，松开自动识别 | 说'管家管家'唤醒语音助手")
        info_label.setFont(QFont('微软雅黑', 10))
        info_label.setStyleSheet("color: #888;")
        info_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(info_label)
        
        right_layout.addWidget(log_group)
        right_layout.addWidget(control_group)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        # 初始加载当前房间的设备（在log_text创建之后）
        self.load_room_devices(self.current_room)
    
    @pyqtSlot(str, bool)
    def update_device_state(self, device, state):
        if device in self.device_widgets:
            self.device_widgets[device].set_state(state)
    
    def on_device_toggle(self, device_id):
        # 直接切换设备状态
        self.state_manager.toggle_state(device_id)
        # 播放点击声音
        if self.sound_manager:
            self.sound_manager.play_click()
    
    @pyqtSlot(str)
    def on_voice_detected(self, text):
        if self.sound_manager:
            self.sound_manager.play_voice_detected()
        self.log_text.append(f"<span style='color:#00aaff;'>🎤 [语音]</span> {text}")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    @pyqtSlot(str)
    def on_gesture_detected(self, gesture):
        if self.sound_manager:
            self.sound_manager.play_gesture_detected()
        
        gesture_names = {
            'one': '一指(灯)',
            'two': '两指(空调)',
            'three': '三指(风扇)',
            'four': '四指(电视)',
            'five': '五指(窗帘)'
        }
        self.log_text.append(f"<span style='color:#ffaa00;'>🖐️ [手势]</span> {gesture_names.get(gesture, gesture)}")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def update_log(self):
        pass
    
    def on_mic_press(self, event):
        if self.voice_recognizer:
            import threading
            self.record_thread = threading.Thread(target=self.voice_recognizer.start_recording)
            self.record_thread.start()
        QPushButton.mousePressEvent(self.mic_btn, event)
    
    def on_mic_release(self, event):
        if self.voice_recognizer:
            self.voice_recognizer.stop_recording()
        QPushButton.mouseReleaseEvent(self.mic_btn, event)
    
    @pyqtSlot(bool)
    def on_recording_state_changed(self, is_recording):
        if is_recording:
            self.mic_btn.setText('🎤 松开停止')
            self.mic_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d94a4a, stop:1 #bd3535);
                    color: white;
                    border: none;
                    border-radius: 25px;
                    padding: 8px 20px;
                    box-shadow: 0 0 25px rgba(217, 74, 74, 0.7);
                }
            """)
            self.voice_indicator.setStyleSheet("""
                QFrame {
                    border-radius: 6px;
                    background-color: #ff0000;
                    box-shadow: 0 0 15px #ff0000;
                }
            """)
            self.log_text.append("<span style='color:#ff0000;'>🎤 [录音]</span> 正在录音...")
        else:
            self.mic_btn.setText('🎤 按住说话')
            self.mic_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a90d9, stop:1 #357abd);
                    color: white;
                    border: none;
                    border-radius: 25px;
                    padding: 8px 20px;
                    box-shadow: 0 3px 10px rgba(53, 122, 189, 0.4);
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5a9fe9, stop:1 #4589cd);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d94a4a, stop:1 #bd3535);
                    box-shadow: 0 0 20px rgba(217, 74, 74, 0.6);
                }
            """)
            self.voice_indicator.setStyleSheet("""
                QFrame {
                    border-radius: 6px;
                    background-color: #00ff00;
                    box-shadow: 0 0 10px #00ff00;
                }
            """)
    
    def on_language_changed(self, index):
        if self.voice_recognizer and self.lang_combo:
            lang_key = self.lang_combo.itemData(index)
            if lang_key:
                self.voice_recognizer.set_language(lang_key)
                lang_info = self.voice_recognizer.get_current_language()[1]
                self.log_text.append(f"<span style='color:#00aaff;'>🌐 [语言]</span> 已切换至: {lang_info['name']}")
    
    @pyqtSlot(list)
    def on_assistant_response(self, responses):
        for response in responses:
            self.log_text.append(f"<span style='color:#ffaa00;'>🤖 [管家]</span> {response}")
    
    def on_reset(self):
        if self.sound_manager:
            self.sound_manager.play_success()
        self.state_manager.reset_all()
        self.log_text.append("<span style='color:#00ff00;'>✅ [系统]</span> 所有设备已重置")
    
    @pyqtSlot(str)
    def on_speak_ready(self, audio_path):
        self._play_audio(audio_path)
    
    def _play_audio(self, audio_path):
        try:
            if self.current_audio_file and os.path.exists(self.current_audio_file):
                try:
                    pygame.mixer.music.stop()
                except:
                    pass
            
            self.current_audio_file = audio_path
            
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            self.log_text.append(f"<span style='color:#00ffaa;'>🔊 [语音]</span> 播放语音反馈")
        except Exception as e:
            self.logger.error(f"音频播放失败: {str(e)}")
    
    @pyqtSlot(bool)
    def on_wake_toggled(self, checked):
        if not self.voice_recognizer:
            return
        
        if checked:
            # 异步声纹验证
            self.wake_btn.setEnabled(False)
            self.log_text.append("<span style='color:#ff9900;'>🔊 [声纹]</span> 准备声纹验证...")
            self._wake_request_pending = True
            self.voiceprint_recognizer.recognize_async()
        else:
            self.voice_recognizer.stop_wake_listener()
            self.wake_btn.setText('🔔 开启语音唤醒')
            self.log_text.append("<span style='color:#ff6600;'>🔔 [唤醒]</span> 语音唤醒已关闭")
    
    def handle_wake_verification(self, success, user_id, score):
        """处理唤醒的声纹验证结果"""
        self._wake_request_pending = False
        
        if success and user_id:
            self.log_text.append(f"<span style='color:#4ad9a0;'>✅ [声纹]</span> 验证通过！{user_id}，相似度: {score:.2f}")
            success = self.voice_recognizer.start_wake_listener()
            if success:
                self.wake_btn.setText('🔔 关闭语音唤醒')
                self.log_text.append("<span style='color:#00ff00;'>🔔 [唤醒]</span> 语音唤醒已开启")
                if self.sound_manager:
                    self.sound_manager.play_device_on()
        else:
            self.log_text.append(f"<span style='color:#ff4a4a;'>❌ [声纹]</span> 验证失败，无法开启唤醒功能，相似度: {score:.2f}")
            self.wake_btn.setChecked(False)
            if self.sound_manager:
                self.sound_manager.play_device_off()
        
        self.wake_btn.setEnabled(True)
    
    @pyqtSlot(str)
    def on_wake_word_detected(self, wake_word):
        self.log_text.append(f"<span style='color:#ffaa00;'>✨ [唤醒]</span> 检测到唤醒词: {wake_word}，请说话...")
        if self.sound_manager:
            self.sound_manager.play_success()
    
    def query_weather_on_startup(self):
        if self.voice_recognizer and hasattr(self.voice_recognizer, 'smart_assistant'):
            self.log_text.append("<span style='color:#00aaff;'>🌤️ [天气]</span> 正在获取天气信息...")
            self.voice_recognizer.smart_assistant.query_weather()
    
    @pyqtSlot(dict)
    def on_weather_updated(self, weather_data):
        city = weather_data.get('city', '未知')
        temp = weather_data.get('temperature', '--')
        weather = weather_data.get('weather', '未知')
        wind = weather_data.get('wind', '')
        humidity = weather_data.get('humidity', '')
        today_high = weather_data.get('today_high', '')
        today_low = weather_data.get('today_low', '')
        
        self.weather_info_label.setText(f"{city} {weather}\n湿度: {humidity}% {wind}")
        self.weather_temp_label.setText(f"{temp}°C")
        
        weather_icons = {
            'Sunny': '🌞', 'Clear': '🌙', 'Partly cloudy': '⛅', 'Cloudy': '☁️',
            'Overcast': '☁️', 'Mist': '🌫️', 'Rain': '🌧️', 'Light rain': '🌦️',
            'Heavy rain': '⛈️', 'Snow': '❄️', 'Fog': '🌫️', 'Thunder': '🌩️',
            'Drizzle': '🌧️', 'Showers': '🌦️', 'Snow showers': '🌨️', 'Hail': '🧊',
            'Wind': '💨', 'Tornado': '🌪️', 'Hurricane': '🌀', 'Sleet': '🌨️'
        }
        icon = weather_icons.get(weather, '🌞')
        self.weather_icon_label.setText(icon)
        
        self.log_text.append(f"<span style='color:#00aaff;'>🌤️ [天气]</span> {city} {weather} {temp}°C (最低{today_low}, 最高{today_high})")
    
    def on_register_voiceprint(self):
        """注册声纹（异步）"""
        self.log_text.append("<span style='color:#6496ff;'>🔊 [声纹]</span> 准备录制声纹...")
        self.register_voiceprint_btn.setEnabled(False)
        self.recognize_voiceprint_btn.setEnabled(False)
        self.voiceprint_recognizer.register_voiceprint_async("master")
    
    def on_recognize_voiceprint(self):
        """识别声纹（异步）"""
        self.log_text.append("<span style='color:#6496ff;'>🔊 [声纹]</span> 准备进行声纹验证...")
        self.register_voiceprint_btn.setEnabled(False)
        self.recognize_voiceprint_btn.setEnabled(False)
        self.voiceprint_recognizer.recognize_async()
    
    @pyqtSlot(int, int)
    def on_voiceprint_recording_started(self, current_round, total_rounds):
        """录音开始（支持多轮录制）"""
        if total_rounds > 1:
            status_text = f'声纹识别状态: 🎙️ 正在录音 ({current_round}/{total_rounds})'
            log_text = f"<span style='color:#ff9900;'>🎙️ [声纹]</span> 第 {current_round}/{total_rounds} 次录音，请说'管家管家'..."
        else:
            status_text = '声纹识别状态: 🎙️ 正在录音...'
            log_text = "<span style='color:#ff9900;'>🎙️ [声纹]</span> 正在录音，请说'管家管家'..."
        
        self.voiceprint_status.setText(status_text)
        self.voiceprint_status.setStyleSheet("color: #ff9900;")
        self.log_text.append(log_text)
    
    @pyqtSlot(int, int)
    def on_voiceprint_recording_finished(self, current_round, total_rounds):
        """录音结束"""
        if total_rounds > 1 and current_round < total_rounds:
            status_text = f'声纹识别状态: 准备第 {current_round + 1} 次录音...'
            log_text = f"<span style='color:#6496ff;'>🔊 [声纹]</span> 第 {current_round} 次录音完成，准备下一次..."
        else:
            status_text = '声纹识别状态: 处理中...'
            log_text = "<span style='color:#6496ff;'>🔊 [声纹]</span> 录音结束，正在处理..."
        
        self.voiceprint_status.setText(status_text)
        self.log_text.append(log_text)
    
    @pyqtSlot(int, bool, str)
    def on_voiceprint_round_verified(self, round_num, success, message):
        """每轮录制验证结果"""
        if success:
            self.log_text.append(f"<span style='color:#4ad9a0;'>✅ [声纹]</span> 第 {round_num} 次录制成功！{message}")
            if self.sound_manager:
                self.sound_manager.play_device_on()
        else:
            self.log_text.append(f"<span style='color:#ff9900;'>⚠️ [声纹]</span> 第 {round_num} 次录制失败: {message}，请重试")
            if self.sound_manager:
                self.sound_manager.play_device_off()
    
    @pyqtSlot(bool, str)
    def on_voiceprint_registration_finished(self, success, message):
        """声纹注册完成"""
        if success:
            user_id = self.voiceprint_recognizer._current_user_id
            self.log_text.append(f"<span style='color:#4ad9a0;'>✅ [声纹]</span> {message}用户 '{user_id}' 声纹注册成功")
            self.voiceprint_status.setText(f'声纹识别状态: 已注册 {user_id}')
            self.voiceprint_status.setStyleSheet("color: #4ad9a0;")
            if self.sound_manager:
                self.sound_manager.play_device_on()
            # 更新状态显示
            user_count = self.voiceprint_recognizer.get_voiceprint_count()
            self.voiceprint_status.setText(f'声纹识别状态: 已注册 {user_count} 个用户')
        else:
            self.log_text.append(f"<span style='color:#ff4a4a;'>❌ [声纹]</span> {message}")
            self.voiceprint_status.setText('声纹识别状态: 注册失败')
            self.voiceprint_status.setStyleSheet("color: #ff4a4a;")
            if self.sound_manager:
                self.sound_manager.play_device_off()
        self.register_voiceprint_btn.setEnabled(True)
        self.recognize_voiceprint_btn.setEnabled(True)
    
    @pyqtSlot(bool, str, float)
    def on_voiceprint_recognition_finished(self, success, user_id, score):
        """声纹识别完成"""
        # 检查是否是唤醒请求
        if hasattr(self, '_wake_request_pending') and self._wake_request_pending:
            self.handle_wake_verification(success, user_id, score)
            return
        
        # 普通声纹识别请求
        if success and user_id:
            self.log_text.append(f"<span style='color:#4ad9a0;'>✅ [声纹]</span> 验证通过！欢迎回来，{user_id}，相似度: {score:.2f}")
            self.voiceprint_status.setText(f'声纹识别状态: 已验证 {user_id} ({score:.2f})')
            self.voiceprint_status.setStyleSheet("color: #4ad9a0;")
            if self.sound_manager:
                self.sound_manager.play_device_on()
            # 唤醒语音助手
            if self.voice_recognizer:
                self.voice_recognizer.start_recording()
        else:
            self.log_text.append(f"<span style='color:#ff4a4a;'>❌ [声纹]</span> 验证失败，相似度: {score:.2f}，未达到阈值")
            self.voiceprint_status.setText('声纹识别状态: 未通过')
            self.voiceprint_status.setStyleSheet("color: #ff4a4a;")
            if self.sound_manager:
                self.sound_manager.play_device_off()
        self.register_voiceprint_btn.setEnabled(True)
        self.recognize_voiceprint_btn.setEnabled(True)
    
    def closeEvent(self, event):
        self.log_timer.stop()
        if self.voice_recognizer:
            self.voice_recognizer.cleanup()
        event.accept()
    
    def load_room_devices(self, room_id):
        """加载指定房间的设备"""
        # 清空现有设备
        for device_id in list(self.device_widgets.keys()):
            widget = self.device_widgets.pop(device_id)
            widget.deleteLater()
        
        # 清空网格布局
        while self.device_grid.count():
            child = self.device_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 获取房间设备（先从默认配置获取，再添加自定义设备）
        room_devices = DEFAULT_ROOM_DEVICES.get(room_id, []).copy()
        
        # 如果有设备管理器，也获取自定义房间的设备
        if self.device_manager:
            custom_room_devices = self.device_manager.get_room_devices(room_id)
            # 添加自定义设备（排除已存在的设备）
            for device_type in custom_room_devices:
                if device_type not in room_devices:
                    room_devices.append(device_type)
        
        # 获取房间名称
        room_name = ROOMS.get(room_id, {}).get('name', room_id)
        if not room_name and self.device_manager:
            room_info = self.device_manager.get_room_info(room_id)
            room_name = room_info.get('name', room_id)
        
        # 添加设备到网格
        for i, device_type in enumerate(room_devices):
            device_key = f"{room_id}_{device_type}"
            
            # 获取设备名称
            if device_type in DEVICE_TYPES:
                device_name = f"{room_name}{DEVICE_TYPES[device_type]['name']}"
            elif self.device_manager:
                device_info = self.device_manager.get_all_device_types().get(device_type)
                device_name = f"{room_name}{device_info.get('name', device_type)}" if device_info else f"{room_name}{device_type}"
            else:
                device_name = f"{room_name}{device_type}"
            
            widget = DeviceWidget(device_type, device_name, self.sound_manager)
            widget.toggle_btn.clicked.connect(lambda checked, did=device_key: self.on_device_toggle(did))
            self.device_widgets[device_key] = widget
            
            # 恢复设备状态
            state = self.state_manager.get_state(device_key)
            widget.set_state(state)
            
            row = i // 3
            col = i % 3
            self.device_grid.addWidget(widget, row, col)
        
        if not room_devices:
            empty_label = QLabel(f"{room_name}暂无设备")
            empty_label.setFont(QFont('微软雅黑', 14))
            empty_label.setStyleSheet("color: #666;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.device_grid.addWidget(empty_label, 0, 0)
        
        self.log_text.append(f"<span style='color:#6496ff;'>🏠 [房间]</span> 已切换到{room_name}")
    
    def on_room_selected(self, room_id):
        """房间选择处理"""
        # 更新选中状态
        for rid, btn in self.room_buttons.items():
            btn.setChecked(rid == room_id)
        
        self.current_room = room_id
        
        # 更新命令系统的当前房间（用于手势控制）
        if self.command_system:
            self.command_system.set_current_room(room_id)
        
        self.load_room_devices(room_id)
    
    def on_add_room(self):
        """添加自定义房间"""
        room_name, ok = QInputDialog.getText(self, '添加房间', '请输入房间名称:', QLineEdit.Normal, '')
        if ok and room_name.strip():
            room_id = room_name.strip().lower().replace(' ', '_')
            success, message = self.device_manager.add_custom_room(room_id, room_name.strip())
            
            if success:
                self.log_text.append(f"<span style='color:#4ad9a0;'>✅ [房间]</span> {message}")
                if self.sound_manager:
                    self.sound_manager.play_device_on()
                # 更新房间按钮
                self.update_room_buttons()
            else:
                self.log_text.append(f"<span style='color:#ff4a4a;'>❌ [房间]</span> {message}")
                if self.sound_manager:
                    self.sound_manager.play_device_off()
    
    def update_room_buttons(self):
        """更新房间按钮列表"""
        # 清空现有按钮
        while self.room_layout.count():
            child = self.room_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 重新添加所有房间按钮
        self.room_buttons = {}
        for room_id, room_info in self.device_manager.get_all_rooms().items():
            btn = QPushButton(f"{room_info['icon']} {room_info['name']}")
            btn.setFont(QFont('微软雅黑', 11))
            btn.setFixedHeight(38)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(255,255,255,0.05);
                    color: #aaa;
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 8px;
                    padding: 6px 12px;
                }}
                QPushButton:hover {{
                    background: rgba(100,150,255,0.2);
                    color: #6496ff;
                }}
                QPushButton:checked {{
                    background: {room_info['color']};
                    color: white;
                    border-color: {room_info['color']};
                }}
            """)
            btn.setCheckable(True)
            btn.setChecked(room_id == self.current_room)
            btn.clicked.connect(lambda checked, rid=room_id: self.on_room_selected(rid))
            self.room_buttons[room_id] = btn
            self.room_layout.addWidget(btn)
        
        add_room_btn = QPushButton('+ 添加房间')
        add_room_btn.setFont(QFont('微软雅黑', 11))
        add_room_btn.setFixedHeight(38)
        add_room_btn.setStyleSheet("""
            QPushButton {
                background: rgba(74,217,160,0.2);
                color: #4ad9a0;
                border: 1px solid rgba(74,217,160,0.4);
                border-radius: 8px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background: rgba(74,217,160,0.3);
            }
        """)
        add_room_btn.clicked.connect(self.on_add_room)
        self.room_layout.addWidget(add_room_btn)
        self.room_layout.addStretch()
    
    def on_add_device(self):
        """向当前房间添加设备"""
        # 获取所有设备类型（包括自定义）
        device_types_dict = DEVICE_TYPES.copy()
        if self.device_manager:
            custom_device_types = self.device_manager.get_all_device_types()
            device_types_dict.update(custom_device_types)
        
        device_types = list(device_types_dict.keys())
        device_names = [f"{device_types_dict[d]['icon']} {device_types_dict[d]['name']}" for d in device_types]
        
        device_name, ok = QInputDialog.getItem(self, '添加设备', '选择设备类型:', device_names, 0, False)
        
        if ok and device_name:
            # 提取设备类型ID
            for device_id, info in device_types_dict.items():
                if f"{info['icon']} {info['name']}" == device_name:
                    success, message = self.device_manager.add_device_to_room(self.current_room, device_id)
                    
                    if success:
                        self.log_text.append(f"<span style='color:#4ad9a0;'>✅ [设备]</span> {message}")
                        if self.sound_manager:
                            self.sound_manager.play_device_on()
                        # 刷新设备列表
                        self.load_room_devices(self.current_room)
                    else:
                        self.log_text.append(f"<span style='color:#ff4a4a;'>❌ [设备]</span> {message}")
                        if self.sound_manager:
                            self.sound_manager.play_device_off()
                    break
    
    def on_manage_voiceprint(self):
        """打开声纹管理对话框"""
        dialog = VoiceprintManagerDialog(self.voiceprint_recognizer, self)
        dialog.exec_()
        # 刷新状态显示
        user_count = self.voiceprint_recognizer.get_voiceprint_count()
        self.voiceprint_status.setText(f'声纹识别状态: 已注册 {user_count} 个用户')
    
    def on_gesture_binding(self):
        """打开手势绑定对话框"""
        dialog = GestureBindingDialog(self.command_system, self.device_manager, self.state_manager, self)
        dialog.exec_()


class GestureBindingDialog(QDialog):
    """手势绑定对话框"""
    
    def __init__(self, command_system, device_manager, state_manager, parent=None):
        super().__init__(parent)
        self.command_system = command_system
        self.device_manager = device_manager
        self.state_manager = state_manager
        self.setWindowTitle('🤟 手势绑定')
        self.setFixedSize(500, 450)
        self.setStyleSheet("""
            QDialog {
                background: rgba(30, 30, 50, 0.95);
                border-radius: 15px;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel('🤟 手势绑定设置')
        title_label.setFont(QFont('微软雅黑', 16, QFont.Bold))
        title_label.setStyleSheet("color: #4ad9d9;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 手势列表
        gesture_layout = QGridLayout()
        gesture_layout.setSpacing(10)
        
        self.gesture_buttons = {}
        gestures = ['one', 'two', 'three', 'four', 'five']
        gesture_names = {'one': '1指', 'two': '2指', 'three': '3指', 'four': '4指', 'five': '5指'}
        
        for i, gesture in enumerate(gestures):
            btn = QPushButton(gesture_names[gesture])
            btn.setFixedSize(80, 45)
            btn.setFont(QFont('微软雅黑', 12, QFont.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a90d9, stop:1 #357abd);
                    color: white;
                    border: none;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5a9fe9, stop:1 #4589cd);
                }
                QPushButton:checked {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4CAF50, stop:1 #388E3C);
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, g=gesture: self.on_gesture_selected(g))
            self.gesture_buttons[gesture] = btn
            
            # 当前绑定显示
            bindings = self.command_system.get_gesture_bindings()
            current_bind = bindings.get(gesture, '未绑定')
            bind_label = QLabel(f"→ {current_bind if current_bind != '未绑定' else '未绑定'}")
            bind_label.setFont(QFont('微软雅黑', 11))
            bind_label.setStyleSheet("color: #aaa;")
            
            gesture_layout.addWidget(btn, i, 0)
            gesture_layout.addWidget(bind_label, i, 1)
        
        layout.addLayout(gesture_layout)
        
        # 设备选择
        device_group = QGroupBox('选择要绑定的设备')
        device_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(100,150,255,0.3);
                border-radius: 12px;
                padding: 15px;
                color: #6496ff;
                font-size: 14px;
                font-weight: bold;
                background: rgba(100,150,255,0.03);
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
            }
        """)
        device_layout = QVBoxLayout(device_group)
        
        self.device_combo = QComboBox()
        self.device_combo.setFont(QFont('微软雅黑', 11))
        self.device_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255,255,255,0.1);
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 8px 12px;
                min-width: 200px;
            }
            QComboBox QAbstractItemView {
                background: #2a2a4a;
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
            }
        """)
        self.load_devices()
        device_layout.addWidget(self.device_combo)
        
        layout.addWidget(device_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        bind_btn = QPushButton('✅ 绑定')
        bind_btn.setFixedHeight(40)
        bind_btn.setFont(QFont('微软雅黑', 12, QFont.Bold))
        bind_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4CAF50, stop:1 #388E3C);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5CBF60, stop:1 #489E4C);
            }
        """)
        bind_btn.clicked.connect(self.on_bind)
        button_layout.addWidget(bind_btn)
        
        clear_btn = QPushButton('🗑️ 清除绑定')
        clear_btn.setFixedHeight(40)
        clear_btn.setFont(QFont('微软雅黑', 12, QFont.Bold))
        clear_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d94a4a, stop:1 #bd3535);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e95a5a, stop:1 #cd4545);
            }
        """)
        clear_btn.clicked.connect(self.on_clear)
        button_layout.addWidget(clear_btn)
        
        clear_all_btn = QPushButton('🗑️ 清除全部')
        clear_all_btn.setFixedHeight(40)
        clear_all_btn.setFont(QFont('微软雅黑', 12, QFont.Bold))
        clear_all_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #666, stop:1 #444);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #777, stop:1 #555);
            }
        """)
        clear_all_btn.clicked.connect(self.on_clear_all)
        button_layout.addWidget(clear_all_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        self.selected_gesture = None
    
    def load_devices(self):
        """加载所有设备"""
        self.device_combo.clear()
        
        # 获取所有设备
        all_devices = []
        
        # 默认房间设备
        from config.config import ROOMS, DEFAULT_ROOM_DEVICES, DEVICE_TYPES
        
        for room_id, devices in DEFAULT_ROOM_DEVICES.items():
            room_name = ROOMS.get(room_id, {}).get('name', room_id)
            for device_type in devices:
                device_name = DEVICE_TYPES.get(device_type, {}).get('name', device_type)
                device_key = f"{room_id}_{device_type}"
                all_devices.append((room_name, device_name, device_key))
        
        # 自定义房间设备
        if self.device_manager:
            custom_rooms = self.device_manager.get_custom_rooms()
            for room_id in custom_rooms:
                room_info = self.device_manager.get_room_info(room_id)
                room_name = room_info.get('name', room_id)
                room_devices = self.device_manager.get_room_devices(room_id)
                for device_type in room_devices:
                    device_name = DEVICE_TYPES.get(device_type, {}).get('name', device_type)
                    device_key = f"{room_id}_{device_type}"
                    all_devices.append((room_name, device_name, device_key))
        
        # 添加到下拉框
        for room_name, device_name, device_key in all_devices:
            self.device_combo.addItem(f"{room_name} - {device_name}", device_key)
    
    def on_gesture_selected(self, gesture):
        """手势选择"""
        # 取消其他手势的选中状态
        for g, btn in self.gesture_buttons.items():
            btn.setChecked(g == gesture)
        
        self.selected_gesture = gesture
    
    def on_bind(self):
        """绑定手势"""
        if not self.selected_gesture:
            QMessageBox.warning(self, '提示', '请先选择一个手势！')
            return
        
        device_key = self.device_combo.currentData()
        if not device_key:
            QMessageBox.warning(self, '提示', '请选择一个设备！')
            return
        
        success, message = self.command_system.set_gesture_binding(self.selected_gesture, device_key)
        
        if success:
            QMessageBox.information(self, '成功', message)
            # 更新显示
            self.load_devices()
            # 更新主窗口日志
            if self.parent():
                gesture_names = {'one': '1指', 'two': '2指', 'three': '3指', 'four': '4指', 'five': '5指'}
                self.parent().log_text.append(f"<span style='color:#4ad9d9;'>🤟 [手势]</span> {gesture_names.get(self.selected_gesture)} 绑定到 {device_key}")
        else:
            QMessageBox.warning(self, '失败', message)
    
    def on_clear(self):
        """清除当前手势绑定"""
        if not self.selected_gesture:
            QMessageBox.warning(self, '提示', '请先选择一个手势！')
            return
        
        bindings = self.command_system.get_gesture_bindings()
        if self.selected_gesture not in bindings:
            QMessageBox.warning(self, '提示', '该手势没有绑定！')
            return
        
        success, message = self.command_system.remove_gesture_binding(self.selected_gesture)
        
        if success:
            QMessageBox.information(self, '成功', message)
            # 更新主窗口日志
            if self.parent():
                gesture_names = {'one': '1指', 'two': '2指', 'three': '3指', 'four': '4指', 'five': '5指'}
                self.parent().log_text.append(f"<span style='color:#ff9900;'>🤟 [手势]</span> 已清除 {gesture_names.get(self.selected_gesture)} 的绑定")
        else:
            QMessageBox.warning(self, '失败', message)
    
    def on_clear_all(self):
        """清除所有手势绑定"""
        bindings = self.command_system.get_gesture_bindings()
        if not bindings:
            QMessageBox.information(self, '提示', '没有可清除的绑定')
            return
        
        reply = QMessageBox.question(self, '确认清除', '确定要清除所有手势绑定吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            for gesture in list(bindings.keys()):
                self.command_system.remove_gesture_binding(gesture)
            
            QMessageBox.information(self, '成功', '已清除所有手势绑定')
            if self.parent():
                self.parent().log_text.append(f"<span style='color:#ff9900;'>🤟 [手势]</span> 已清除所有手势绑定")


class VoiceprintManagerDialog(QDialog):
    """声纹管理对话框"""
    
    def __init__(self, voiceprint_recognizer, parent=None):
        super().__init__(parent)
        self.voiceprint_recognizer = voiceprint_recognizer
        self.setWindowTitle('📋 声纹管理')
        self.setFixedSize(450, 400)
        self.setStyleSheet("""
            QDialog {
                background: rgba(30, 30, 50, 0.95);
                border-radius: 15px;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel('🔊 声纹管理')
        title_label.setFont(QFont('微软雅黑', 16, QFont.Bold))
        title_label.setStyleSheet("color: #6496ff;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 声纹列表
        self.voiceprint_list = QListWidget()
        self.voiceprint_list.setFont(QFont('微软雅黑', 12))
        self.voiceprint_list.setStyleSheet("""
            QListWidget {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                color: white;
                padding: 10px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 5px;
            }
            QListWidget::item:hover {
                background: rgba(100, 150, 255, 0.2);
            }
            QListWidget::item:selected {
                background: rgba(100, 150, 255, 0.4);
            }
        """)
        layout.addWidget(self.voiceprint_list)
        
        # 统计信息
        self.stats_label = QLabel()
        self.stats_label.setFont(QFont('微软雅黑', 11))
        self.stats_label.setStyleSheet("color: #aaa;")
        self.stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 添加按钮
        add_btn = QPushButton('➕ 添加用户')
        add_btn.setFixedHeight(40)
        add_btn.setFont(QFont('微软雅黑', 11, QFont.Bold))
        add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a90d9, stop:1 #357abd);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5a9fe9, stop:1 #4589cd);
            }
        """)
        add_btn.clicked.connect(self.on_add_user)
        button_layout.addWidget(add_btn)
        
        # 重命名按钮
        rename_btn = QPushButton('✏️ 重命名')
        rename_btn.setFixedHeight(40)
        rename_btn.setFont(QFont('微软雅黑', 11, QFont.Bold))
        rename_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #9664d9, stop:1 #7b4abd);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a674e9, stop:1 #8b59cd);
            }
        """)
        rename_btn.clicked.connect(self.on_rename_user)
        button_layout.addWidget(rename_btn)
        
        # 删除按钮
        delete_btn = QPushButton('🗑️ 删除')
        delete_btn.setFixedHeight(40)
        delete_btn.setFont(QFont('微软雅黑', 11, QFont.Bold))
        delete_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d94a4a, stop:1 #bd3535);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e95a5a, stop:1 #cd4545);
            }
        """)
        delete_btn.clicked.connect(self.on_delete_user)
        button_layout.addWidget(delete_btn)
        
        # 清空按钮
        clear_btn = QPushButton('🗑️ 清空全部')
        clear_btn.setFixedHeight(40)
        clear_btn.setFont(QFont('微软雅黑', 11, QFont.Bold))
        clear_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #666, stop:1 #444);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #777, stop:1 #555);
            }
        """)
        clear_btn.clicked.connect(self.on_clear_all)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.refresh_list()
    
    def refresh_list(self):
        """刷新声纹列表"""
        self.voiceprint_list.clear()
        users = self.voiceprint_recognizer.get_registered_users()
        
        for user_id in sorted(users):
            item = QListWidgetItem(f'👤 {user_id}')
            item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.voiceprint_list.addItem(item)
        
        count = len(users)
        self.stats_label.setText(f'已注册 {count} 个声纹用户')
    
    def on_add_user(self):
        """添加新用户"""
        user_id, ok = QInputDialog.getText(self, '添加用户', '请输入用户名:', QLineEdit.Normal, '')
        
        if ok and user_id.strip():
            user_id = user_id.strip()
            # 检查是否已存在
            if user_id in self.voiceprint_recognizer.get_registered_users():
                QMessageBox.warning(self, '提示', '该用户名已存在！')
                return
            
            # 开始注册声纹
            self.parent().log_text.append(f"<span style='color:#6496ff;'>🔊 [声纹]</span> 准备为用户 '{user_id}' 注册声纹...")
            self.close()
            self.parent().register_voiceprint_btn.setEnabled(False)
            self.parent().recognize_voiceprint_btn.setEnabled(False)
            self.voiceprint_recognizer.register_voiceprint_async(user_id)
    
    def on_rename_user(self):
        """重命名用户"""
        selected_items = self.voiceprint_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '提示', '请先选择一个用户！')
            return
        
        old_user_id = selected_items[0].text().replace('👤 ', '')
        new_user_id, ok = QInputDialog.getText(self, '重命名', '请输入新用户名:', QLineEdit.Normal, old_user_id)
        
        if ok and new_user_id.strip():
            new_user_id = new_user_id.strip()
            success, message = self.voiceprint_recognizer.rename_voiceprint(old_user_id, new_user_id)
            
            if success:
                QMessageBox.information(self, '成功', message)
                self.refresh_list()
                # 更新主窗口状态
                if self.parent():
                    self.parent().log_text.append(f"<span style='color:#ff9900;'>✏️ [声纹]</span> 用户 '{old_user_id}' 已重命名为 '{new_user_id}'")
            else:
                QMessageBox.warning(self, '失败', message)
    
    def on_delete_user(self):
        """删除用户"""
        selected_items = self.voiceprint_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '提示', '请先选择一个用户！')
            return
        
        user_id = selected_items[0].text().replace('👤 ', '')
        
        reply = QMessageBox.question(self, '确认删除', f'确定要删除用户 "{user_id}" 的声纹吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success = self.voiceprint_recognizer.delete_voiceprint(user_id)
            if success:
                QMessageBox.information(self, '成功', f'已删除用户 "{user_id}" 的声纹')
                self.refresh_list()
                # 更新主窗口状态
                if self.parent():
                    user_count = self.voiceprint_recognizer.get_voiceprint_count()
                    self.parent().voiceprint_status.setText(f'声纹识别状态: 已注册 {user_count} 个用户')
                    self.parent().log_text.append(f"<span style='color:#ff9900;'>🗑️ [声纹]</span> 已删除用户 '{user_id}' 的声纹")
            else:
                QMessageBox.warning(self, '失败', '删除失败')
    
    def on_clear_all(self):
        """清空所有声纹"""
        count = len(self.voiceprint_recognizer.get_registered_users())
        if count == 0:
            QMessageBox.information(self, '提示', '没有可删除的声纹')
            return
        
        reply = QMessageBox.question(self, '确认清空', f'确定要清空所有 {count} 个声纹吗？此操作不可恢复！',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.voiceprint_recognizer.clear_all_voiceprints()
            QMessageBox.information(self, '成功', '已清空所有声纹')
            self.refresh_list()
            # 更新主窗口状态
            if self.parent():
                self.parent().voiceprint_status.setText('声纹识别状态: 已注册 0 个用户')
                self.parent().log_text.append(f"<span style='color:#ff9900;'>🗑️ [声纹]</span> 已清空所有声纹")