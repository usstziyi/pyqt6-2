"""Unit 03: 信号、槽和自定义事件。

运行：
    python unit03_signals_slots/main.py
"""

from __future__ import annotations

import sys

from PyQt6.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget

# 温度数据模型类，继承自 QObject 以支持信号机制
class TemperatureModel(QObject):  
    """业务对象也可以发信号，不必继承 QWidget。

    这样 UI 可以订阅业务变化，但业务对象不需要知道 UI 的存在。
    """

    # 自定义信号:PyQt 信号必须定义在类级别，不能写在 __init__ 里
    # 可以通过 self.changed 正常访问
    changed = pyqtSignal(float)

    def __init__(self) -> None:
        super().__init__()
        self._celsius = 20.0

    @property
    def celsius(self) -> float:
        return self._celsius

    # 自定义槽函数
    @pyqtSlot(int)
    def set_from_slider(self, value: int) -> None:
        """根据滑块值设置温度值。"""
        self._set_celsius(float(value))

    # 自定义槽函数
    @pyqtSlot()
    def reset(self) -> None:
        """将温度值重置为默认值 20.0。"""
        self._set_celsius(20.0)

    def _set_celsius(self, value: float) -> None:
        if value == self._celsius:
            return
        self._celsius = value
        # 发送 changed 信号，通知 UI 更新温度显示
        self.changed.emit(self._celsius)


# 温度窗口类，继承自 QWidget 以显示温度相关的 UI 元素
class TemperatureWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Unit 03 - Signals and Slots")
        self.resize(420, 220)

        # 创建温度模型实例，用于管理温度数据和业务逻辑
        self.model = TemperatureModel()
        self.title = QLabel()
        # 设置内部标题标签居中对齐(水平+垂直居中)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(-20, 50)
        self.slider.setValue(int(self.model.celsius))
        # 连接滑块值变化信号到模型的槽函数
        self.slider.valueChanged.connect(self.model.set_from_slider)

        reset_button = QPushButton("重置到 20°C")
        # 连接重置按钮点击信号到模型的槽函数
        reset_button.clicked.connect(self.model.reset)

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.slider)
        layout.addWidget(reset_button)
        self.setLayout(layout)

        # 连接模型的 changed 信号到窗口的槽函数
        self.model.changed.connect(self.render_temperature)
        self.render_temperature(self.model.celsius)
    # 渲染温度显示，更新标题和滑块

    # 显示温度的槽函数
    @pyqtSlot(float)
    def render_temperature(self, celsius: float) -> None:
        fahrenheit = celsius * 9 / 5 + 32
        self.title.setText(f"当前温度：{celsius:.0f}°C / {fahrenheit:.1f}°F")
        if self.slider.value() != int(celsius):
            self.slider.setValue(int(celsius))


def main() -> int:
    app = QApplication(sys.argv)
    window = TemperatureWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
