from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QComboBox, QCheckBox, QSpinBox, QColorDialog)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

class DeviceControlWidget(QWidget):
    """设备控制控件组件 - 根据设备类型显示不同的交互控件"""
    
    def __init__(self, device_key, device_type, controls_config, state_manager, sound_manager=None):
        super().__init__()
        self.device_key = device_key
        self.device_type = device_type
        self.controls_config = controls_config
        self.state_manager = state_manager
        self.sound_manager = sound_manager
        
        # 存储控件引用
        self.controls = {}
        
        self.init_ui()
        
        # 连接状态管理器的属性变更信号
        self.state_manager.property_changed.connect(self.on_property_changed)
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 根据配置动态创建控件
        for prop_name, config in self.controls_config.items():
            control_widget = self.create_control(prop_name, config)
            if control_widget:
                layout.addWidget(control_widget)
        
        self.setLayout(layout)
    
    def create_control(self, prop_name, config):
        """根据配置创建控件"""
        control_type = config.get('type', 'slider')
        label = config.get('label', prop_name)
        
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签
        label_widget = QLabel(label)
        label_widget.setFont(QFont('微软雅黑', 11))
        label_widget.setStyleSheet("color: #aaa;")
        label_widget.setFixedWidth(50)
        layout.addWidget(label_widget)
        
        # 根据类型创建不同控件
        if control_type == 'slider':
            control = self.create_slider(prop_name, config)
        elif control_type == 'combo':
            control = self.create_combo(prop_name, config)
        elif control_type == 'toggle':
            control = self.create_toggle(prop_name, config)
        elif control_type == 'number':
            control = self.create_number(prop_name, config)
        elif control_type == 'color':
            control = self.create_color(prop_name, config)
        else:
            return None
        
        self.controls[prop_name] = control
        layout.addWidget(control)
        
        return widget
    
    def create_slider(self, prop_name, config):
        """创建滑块控件"""
        min_val = config.get('min', 0)
        max_val = config.get('max', 100)
        default_val = config.get('default', 50)
        unit = config.get('unit', '')
        
        # 获取当前值或默认值
        current_val = self.state_manager.get_property(self.device_key, prop_name, default_val)
        
        # 创建包含滑块和数值显示的容器
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(int(current_val))
        slider.setFixedWidth(120)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: rgba(255,255,255,0.1);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a90d9, stop:1 #357abd);
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
        """)
        
        # 数值显示
        value_label = QLabel(f"{int(current_val)}{unit}")
        value_label.setFont(QFont('微软雅黑', 11))
        value_label.setStyleSheet("color: #00ff00;")
        value_label.setFixedWidth(50)
        value_label.setAlignment(Qt.AlignRight)
        
        slider.valueChanged.connect(lambda val, label=value_label, unit=unit: 
                                    label.setText(f"{val}{unit}"))
        slider.valueChanged.connect(lambda val, prop=prop_name: 
                                    self.on_control_changed(prop, val))
        
        layout.addWidget(slider)
        layout.addWidget(value_label)
        
        return container
    
    def create_combo(self, prop_name, config):
        """创建下拉框控件"""
        options = config.get('options', [])
        default_val = config.get('default', options[0] if options else '')
        
        # 获取当前值或默认值
        current_val = self.state_manager.get_property(self.device_key, prop_name, default_val)
        
        combo = QComboBox()
        combo.addItems(options)
        combo.setCurrentText(str(current_val))
        combo.setFixedWidth(120)
        combo.setFont(QFont('微软雅黑', 11))
        combo.setStyleSheet("""
            QComboBox {
                background: rgba(255,255,255,0.1);
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 6px;
                padding: 4px 8px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #2a2a4a;
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 6px;
            }
        """)
        
        combo.currentTextChanged.connect(lambda val, prop=prop_name: 
                                         self.on_control_changed(prop, val))
        
        return combo
    
    def create_toggle(self, prop_name, config):
        """创建开关控件"""
        default_val = config.get('default', False)
        
        # 获取当前值或默认值
        current_val = self.state_manager.get_property(self.device_key, prop_name, default_val)
        
        toggle = QCheckBox()
        toggle.setChecked(current_val)
        toggle.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 40px;
                height: 22px;
            }
            QCheckBox::indicator::unchecked {
                background: #333;
                border-radius: 11px;
            }
            QCheckBox::indicator::unchecked::handle {
                background: #888;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: 2px;
            }
            QCheckBox::indicator::checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a90d9, stop:1 #357abd);
                border-radius: 11px;
            }
            QCheckBox::indicator::checked::handle {
                background: white;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: 2px 2px 2px 20px;
            }
        """)
        
        toggle.stateChanged.connect(lambda state, prop=prop_name: 
                                    self.on_control_changed(prop, state == Qt.Checked))
        
        return toggle
    
    def create_number(self, prop_name, config):
        """创建数字输入控件"""
        min_val = config.get('min', 1)
        max_val = config.get('max', 100)
        default_val = config.get('default', 1)
        
        # 获取当前值或默认值
        current_val = self.state_manager.get_property(self.device_key, prop_name, default_val)
        
        spin_box = QSpinBox()
        spin_box.setRange(min_val, max_val)
        spin_box.setValue(int(current_val))
        spin_box.setFixedWidth(100)
        spin_box.setFont(QFont('微软雅黑', 11))
        spin_box.setStyleSheet("""
            QSpinBox {
                background: rgba(255,255,255,0.1);
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 6px;
                padding: 4px 8px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background: rgba(255,255,255,0.1);
                width: 20px;
            }
        """)
        
        spin_box.valueChanged.connect(lambda val, prop=prop_name: 
                                      self.on_control_changed(prop, val))
        
        return spin_box
    
    def create_color(self, prop_name, config):
        """创建颜色选择控件"""
        default_val = config.get('default', '#ff6b6b')
        
        # 获取当前值或默认值
        current_val = self.state_manager.get_property(self.device_key, prop_name, default_val)
        
        # 创建颜色按钮
        color_btn = QWidget()
        color_btn.setFixedSize(30, 24)
        color_btn.setStyleSheet(f"background-color: {current_val}; border-radius: 4px;")
        
        # 添加点击事件
        color_btn.mousePressEvent = lambda event, btn=color_btn, prop=prop_name: \
            self.on_color_clicked(btn, prop)
        
        return color_btn
    
    def on_color_clicked(self, btn, prop_name):
        """颜色选择按钮点击事件"""
        current_color = self.state_manager.get_property(self.device_key, prop_name, '#ff6b6b')
        color = QColorDialog.getColor(QColor(current_color), self, "选择颜色")
        
        if color.isValid():
            color_hex = color.name()
            self.state_manager.set_property(self.device_key, prop_name, color_hex)
            btn.setStyleSheet(f"background-color: {color_hex}; border-radius: 4px;")
            if self.sound_manager:
                self.sound_manager.play_click()
    
    def on_control_changed(self, prop_name, value):
        """控件值变更处理"""
        self.state_manager.set_property(self.device_key, prop_name, value)
        if self.sound_manager:
            self.sound_manager.play_click()
    
    def on_property_changed(self, device, prop_name, value):
        """属性变更响应"""
        if device == self.device_key and prop_name in self.controls:
            control = self.controls[prop_name]
            if isinstance(control, QWidget) and control.layout():
                # 滑块控件
                for i in range(control.layout().count()):
                    child = control.layout().itemAt(i).widget()
                    if isinstance(child, QSlider):
                        child.setValue(int(value))
                    elif isinstance(child, QLabel) and child.styleSheet() == "color: #00ff00;":
                        unit = self.controls_config[prop_name].get('unit', '')
                        child.setText(f"{int(value)}{unit}")
            elif isinstance(control, QComboBox):
                control.setCurrentText(str(value))
            elif isinstance(control, QCheckBox):
                control.setChecked(value)
            elif isinstance(control, QSpinBox):
                control.setValue(int(value))
    
    def update_state(self, state):
        """更新控件状态（启用/禁用）"""
        for control in self.controls.values():
            control.setEnabled(state)
    
    def get_control_value(self, prop_name):
        """获取控件值"""
        if prop_name in self.controls:
            control = self.controls[prop_name]
            if isinstance(control, QWidget) and control.layout():
                for i in range(control.layout().count()):
                    child = control.layout().itemAt(i).widget()
                    if isinstance(child, QSlider):
                        return child.value()
            elif isinstance(control, QComboBox):
                return control.currentText()
            elif isinstance(control, QCheckBox):
                return control.isChecked()
            elif isinstance(control, QSpinBox):
                return control.value()
        return None