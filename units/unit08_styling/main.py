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
        self.setProperty("card", True)
        self.setProperty("status", status)

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
        layout.addStretch(1)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        style_path = Path(__file__).with_name("style.qss")
        self.setStyleSheet(style_path.read_text(encoding="utf-8"))

    def toggle_first_card(self) -> None:
        next_status = "urgent" if self.first_card.property("status") == "done" else "done"
        self.first_card.setProperty("status", next_status)
        # 动态属性改变后，重新 polish 可以让 QSS 立即重新计算。
        self.first_card.style().unpolish(self.first_card)
        self.first_card.style().polish(self.first_card)
        self.first_card.update()


def main() -> int:
    app = QApplication(sys.argv)
    window = StylingWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
