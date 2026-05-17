"""Unit 03: 信号、槽和自定义事件。

运行：
    python unit03_signals_slots/main.py
"""

from __future__ import annotations

import sys

from PyQt6.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget


class TemperatureModel(QObject):
    """业务对象也可以发信号，不必继承 QWidget。

    这样 UI 可以订阅业务变化，但业务对象不需要知道 UI 的存在。
    """

    changed = pyqtSignal(float)

    def __init__(self) -> None:
        super().__init__()
        self._celsius = 20.0

    @property
    def celsius(self) -> float:
        return self._celsius

    @pyqtSlot(int)
    def set_from_slider(self, value: int) -> None:
        self._set_celsius(float(value))

    def reset(self) -> None:
        self._set_celsius(20.0)

    def _set_celsius(self, value: float) -> None:
        if value == self._celsius:
            return
        self._celsius = value
        self.changed.emit(self._celsius)


class TemperatureWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Unit 03 - Signals and Slots")
        self.resize(420, 220)

        self.model = TemperatureModel()
        self.title = QLabel()
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(-20, 50)
        self.slider.setValue(int(self.model.celsius))
        self.slider.valueChanged.connect(self.model.set_from_slider)

        reset_button = QPushButton("重置到 20°C")
        reset_button.clicked.connect(self.model.reset)

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.slider)
        layout.addWidget(reset_button)
        self.setLayout(layout)

        self.model.changed.connect(self.render_temperature)
        self.render_temperature(self.model.celsius)

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
