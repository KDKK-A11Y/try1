from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QLabel, QPushButton, QTextEdit,
                             QGroupBox, QFrame, QProgressBar, QSizePolicy)
from PyQt5.QtGui import QFont, QLinearGradient, QRadialGradient, QPalette, QBrush, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QRect, QPointF
from config.config import DEVICE_NAMES

class DeviceIcon(QWidget):
    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id
        self.state = False
        self.rotation = 0
        self.blink_state = True
        self.wind_offset = 0
        
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
        self.update()
    
    def update_animation(self):
        if self.device_id == 'fan':
            self.rotation += 8
            if self.rotation >= 360:
                self.rotation = 0
        elif self.device_id == 'aircon':
            self.wind_offset += 5
            if self.wind_offset >= 60:
                self.wind_offset = 0
        elif self.device_id == 'light':
            self.blink_state = not self.blink_state
        elif self.device_id == 'curtain':
            pass
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        if self.device_id == 'light':
            self.draw_light(painter, center_x, center_y)
        elif self.device_id == 'fan':
            self.draw_fan(painter, center_x, center_y)
        elif self.device_id == 'aircon':
            self.draw_aircon(painter, center_x, center_y)
        elif self.device_id == 'tv':
            self.draw_tv(painter, center_x, center_y)
        elif self.device_id == 'curtain':
            self.draw_curtain(painter, center_x, center_y)
    
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
        
        self.init_ui()
        
        self.state_manager.state_changed.connect(self.update_device_state)
        
        if self.voice_recognizer:
            self.voice_recognizer.voice_detected.connect(self.on_voice_detected)
        if self.gesture_recognizer:
            self.gesture_recognizer.gesture_detected.connect(self.on_gesture_detected)
        
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.update_log)
        self.log_timer.start(1000)
    
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
        
        self.device_grid = QGridLayout()
        self.device_grid.setSpacing(25)
        self.device_widgets = {}
        
        devices = list(DEVICE_NAMES.items())
        for i, (device_id, device_name) in enumerate(devices):
            widget = DeviceWidget(device_id, device_name, self.sound_manager)
            widget.toggle_btn.clicked.connect(lambda checked, did=device_id: self.on_device_toggle(did))
            self.device_widgets[device_id] = widget
            row = i // 3
            col = i % 3
            self.device_grid.addWidget(widget, row, col)
        
        device_layout.addLayout(self.device_grid)
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
        
        info_label = QLabel("💡 提示：使用手势或语音控制设备")
        info_label.setFont(QFont('微软雅黑', 10))
        info_label.setStyleSheet("color: #888;")
        info_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(info_label)
        
        right_layout.addWidget(log_group)
        right_layout.addWidget(control_group)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
    
    @pyqtSlot(str, bool)
    def update_device_state(self, device, state):
        if device in self.device_widgets:
            self.device_widgets[device].set_state(state)
    
    def on_device_toggle(self, device_id):
        self.command_system.execute_command(device_id, 'toggle')
    
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
    
    def on_reset(self):
        if self.sound_manager:
            self.sound_manager.play_success()
        self.state_manager.reset_all()
        self.log_text.append("<span style='color:#00ff00;'>✅ [系统]</span> 所有设备已重置")
    
    def closeEvent(self, event):
        self.log_timer.stop()
        event.accept()