"""Unit 06: QSettings 和 JSON 持久化。

运行：
    python unit06_persistence/main.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PyQt6.QtCore import QByteArray, QSettings
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PersistenceWindow(QMainWindow):
    """把 UI 偏好和业务数据分开保存。

    QSettings 适合存窗口尺寸、主题等偏好；JSON 文件适合存用户创建的数据。
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Unit 06 - Persistence")
        self.resize(520, 420)

        self.settings = QSettings("PyQt6Learning", "Unit06Persistence")
        self.notes_file = Path(__file__).with_name("notes.json")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("你的名字")

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["系统默认", "浅色", "深色"])

        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("输入一条备忘")

        add_button = QPushButton("添加备忘")
        add_button.clicked.connect(self.add_note)

        self.notes_list = QListWidget()

        root = QVBoxLayout()
        root.addWidget(self.name_input)
        root.addWidget(self.theme_combo)
        root.addWidget(self.note_input)
        root.addWidget(add_button)
        root.addWidget(self.notes_list)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

        self.load_settings()
        self.load_notes()

    def load_settings(self) -> None:
        self.name_input.setText(self.settings.value("name", "", type=str))
        self.theme_combo.setCurrentIndex(self.settings.value("theme_index", 0, type=int))
        geometry = self.settings.value("geometry")
        if isinstance(geometry, QByteArray):
            self.restoreGeometry(geometry)

    def save_settings(self) -> None:
        self.settings.setValue("name", self.name_input.text())
        self.settings.setValue("theme_index", self.theme_combo.currentIndex())
        self.settings.setValue("geometry", self.saveGeometry())

    def load_notes(self) -> None:
        if not self.notes_file.exists():
            return
        try:
            notes = json.loads(self.notes_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            notes = []
        self.notes_list.addItems(str(note) for note in notes)

    def save_notes(self) -> None:
        notes = [self.notes_list.item(row).text() for row in range(self.notes_list.count())]
        self.notes_file.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_note(self) -> None:
        text = self.note_input.text().strip()
        if not text:
            return
        self.notes_list.addItem(text)
        self.note_input.clear()
        self.save_notes()

    def closeEvent(self, event) -> None:
        self.save_settings()
        self.save_notes()
        super().closeEvent(event)


def main() -> int:
    app = QApplication(sys.argv)
    window = PersistenceWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
