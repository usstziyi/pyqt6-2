"""Unit 02: 布局管理和常用输入控件。

运行：
    python unit02_layouts_widgets/main.py
"""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ProfileForm(QWidget):
    """用布局管理控件，而不是手写坐标。

    Qt 的布局会根据字体、窗口大小和系统缩放自动调整控件位置。
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Unit 02 - Layouts and Widgets")
        self.resize(520, 360)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如：Ada")

        self.role_combo = QComboBox()
        self.role_combo.addItems(["初学者", "桌面应用开发者", "数据工具开发者"])

        self.years_input = QSpinBox()
        self.years_input.setRange(0, 50)
        self.years_input.setSuffix(" 年")

        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("写下你想用 PyQt6 做什么。")

        form_layout = QFormLayout()
        form_layout.addRow("姓名", self.name_input)
        form_layout.addRow("目标角色", self.role_combo)
        form_layout.addRow("Python 经验", self.years_input)
        form_layout.addRow("学习目标", self.note_input)

        group = QGroupBox("学习者资料")
        group.setLayout(form_layout)

        self.preview = QLabel("填写表单后点击生成摘要。")
        self.preview.setWordWrap(True)

        submit_button = QPushButton("生成摘要")
        submit_button.clicked.connect(self.build_summary)

        clear_button = QPushButton("清空")
        clear_button.clicked.connect(self.clear_form)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(clear_button)
        button_row.addWidget(submit_button)

        root_layout = QVBoxLayout()
        root_layout.addWidget(group)
        root_layout.addWidget(self.preview)
        root_layout.addLayout(button_row)
        self.setLayout(root_layout)

    def build_summary(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "缺少姓名", "请先填写姓名。")
            self.name_input.setFocus()
            return

        role = self.role_combo.currentText()
        years = self.years_input.value()
        note = self.note_input.toPlainText().strip() or "暂未填写具体目标"
        self.preview.setText(f"{name}，目标是成为{role}，已有 {years} 年 Python 经验。目标：{note}")

    def clear_form(self) -> None:
        self.name_input.clear()
        self.role_combo.setCurrentIndex(0)
        self.years_input.setValue(0)
        self.note_input.clear()
        self.preview.setText("填写表单后点击生成摘要。")


def main() -> int:
    app = QApplication(sys.argv)
    window = ProfileForm()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
