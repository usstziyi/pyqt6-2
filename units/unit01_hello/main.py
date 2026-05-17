"""Unit 01: QApplication、主窗口和事件循环。

运行：
    python unit01_hello/main.py
"""

from __future__ import annotations

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget


class HelloWindow(QMainWindow):
    """第一个 PyQt6 主窗口。

    QMainWindow 自带菜单栏、工具栏、状态栏和 central widget 区域。
    复杂应用通常从 QMainWindow 开始；简单小窗也可以直接继承 QWidget。
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Unit 01 - Hello PyQt6")
        self.resize(420, 220)

        self.message_label = QLabel("你好，PyQt6")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.count = 0
        self.button = QPushButton("点击我")
        self.button.clicked.connect(self.handle_click)

        layout = QVBoxLayout()
        layout.addWidget(self.message_label)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.statusBar().showMessage("应用已启动，事件循环正在等待用户输入。")

    def handle_click(self) -> None:
        """按钮 clicked 信号触发后调用的槽函数。"""
        self.count += 1
        self.message_label.setText(f"你点击了 {self.count} 次")
        self.statusBar().showMessage("按钮点击事件已被处理。", 2000)


def main() -> int:
    app = QApplication(sys.argv)
    window = HelloWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
