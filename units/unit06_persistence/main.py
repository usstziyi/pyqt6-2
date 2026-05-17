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
        
        # 存储在
        # /Users/usst_ziyi/Library/Preferences/com.pyqt6learning.Unit06Persistence.plist
        self.settings = QSettings(
            organization="PyQt6Learning",  # 组织名称，用于存储设置的命名空间
            application="Unit06Persistence"  # 应用程序名称，用于区分同一组织下的不同应用
        )

        # 生成一个指向 和当前 .py 文件同目录 的 notes.json 路径
        self.notes_file = Path(__file__).with_name("notes.json")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("你的名字")

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["系统默认", "浅色", "深色"])

        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("输入一条备忘")

        add_button = QPushButton("添加备忘")
        add_button.clicked.connect(self.add_note)

    
        # QListWidget 是一个列表控件，用于显示和管理一系列文本项
        # 适合展示备忘列表、任务清单等数据，支持添加、删除、选中操作
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
        # 只有第一次访问时触发底层 I/O ，之后都在内存中操作，性能很高。
        self.name_input.setText(self.settings.value("name", "", type=str))
        self.theme_combo.setCurrentIndex(self.settings.value("theme_index", 0, type=int))
        geometry = self.settings.value("geometry")
        if isinstance(geometry, QByteArray):
            self.restoreGeometry(geometry)

    def save_settings(self) -> None:
        # 先写内存，最后写入文件
        self.settings.setValue("name", self.name_input.text())
        self.settings.setValue("theme_index", self.theme_combo.currentIndex())
        self.settings.setValue("geometry", self.saveGeometry())
        # self.settings.sync() # 强制刷新到磁盘（或程序退出时自动）

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

        self.notes_file.write_text(
            json.dumps(
                notes,                    # 要序列化的 Python 对象（备忘列表）
                ensure_ascii=False,       # 允许输出非 ASCII 字符（如中文），保证字符层面可读（中文不转义成 \uXXXX ）
                indent=2                  # 使用 2 个空格缩进，生成格式化的可读 JSON
            ),
                encoding="utf-8"          # 指定 UTF-8 编码，确保中文等多字节字符正确写入文件，保证字节层面正确
        )

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
        super().closeEvent(event) # 把事件传递给父类
"""
用户点关闭按钮
  → Qt 发出 QCloseEvent
    → closeEvent(self, event) 被调用
      → self.save_settings()         你的保存
      → self.save_notes()            你的保存
      → super().closeEvent(event)    父类 QMainWindow 执行默认关闭
        → 窗口真正关闭、释放资源
"""


def main() -> int:
    app = QApplication(sys.argv)
    window = PersistenceWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
