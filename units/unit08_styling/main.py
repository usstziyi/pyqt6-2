"""Unit 08: QSS 样式和动态属性。

运行：
    python unit08_styling/main.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QFrame, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget


class TaskCard(QFrame):
    """动态属性可以让同一类控件根据状态应用不同 QSS。"""

    def __init__(self, title: str, status: str) -> None:
        super().__init__()
        # 这是 动态属性 ——Qt 允许在运行时给任意 QObject 附加自定义的属性键值对。
        # "card": True — 标记"我是一个 TaskCard"，
        # 用于 QSS 选择器 QFrame[card="true"] 来匹配所有卡片，
        # 统一设置背景、圆角等通用样式。
        self.setProperty("card", True)
        # "status": status — 记录当前任务状态（ "done" 或 "urgent" ），
        # 用于 QSS 选择器 QFrame[status="done"] / QFrame[status="urgent"] 
        # 来给不同状态的卡片染上不同边框颜色。
        self.setProperty("status", status)
        """
        这两个属性的值本身对 Qt 布局/交互没有任何影响，
        它们 纯粹为 QSS 服务，相当于给控件贴了两张"标签"，样式表根据标签来匹配规则。
        """

        label = QLabel(title)
        label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)


class StylingWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Unit 08 - Styling")
        self.resize(520, 360)

        title = QLabel("任务看板")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        refresh_button = QPushButton("切换第一张卡片状态")
        refresh_button.clicked.connect(self.toggle_first_card)

        self.first_card = TaskCard("完成 Model/View 表格练习", "done")
        second_card = TaskCard("整理线程和持久化笔记", "urgent")

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.first_card)
        layout.addWidget(second_card)
        layout.addWidget(refresh_button)
        layout.addStretch(1) # 吃掉剩余空间

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        style_path = Path(__file__).with_name("style.qss")
        self.setStyleSheet(style_path.read_text(encoding="utf-8"))

    # 这段代码是 PyQt6 中 动态切换 QSS 属性样式 的经典写法。
    """
    这个方法的目的是：当用户点击按钮时，
    在第一张卡片（ first_card ）的 "done" 和 "urgent" 两个状态之间来回切换，
    QSS 会根据不同的 status 属性值给卡片染上不同的边框颜色。
    """
    def toggle_first_card(self) -> None:
        next_status = "urgent" if self.first_card.property("status") == "done" else "done"
        self.first_card.setProperty("status", next_status)
        # 动态属性改变后，重新 polish 可以让 QSS 立即重新计算。
        # 强制 QSS 重新应用 的标准三步走
        self.first_card.style().unpolish(self.first_card) # 清除该控件上之前计算好的 QSS 样式缓存
        self.first_card.style().polish(self.first_card) # 根据控件当前的属性值（包括刚修改的 status ），重新计算并应用 QSS
        self.first_card.update() # 触发重绘，让新样式立即生效


def main() -> int:
    app = QApplication(sys.argv)
    window = StylingWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
