"""Unit 04: 菜单、工具栏、标准对话框。

运行：
    python unit04_actions_dialogs/main.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QColorDialog,
    QFileDialog,
    QFontDialog,
    QMainWindow,
    QMessageBox,
    QTextEdit,
    QToolBar,
)


class NotesWindow(QMainWindow):
    """一个迷你记事本。

    QAction 可以同时出现在菜单和工具栏中；同一个 action 触发同一个槽函数。
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Unit 04 - Actions and Dialogs")
        self.resize(720, 480)
        self.current_file: Path | None = None

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("写一点内容，然后试试打开、保存、字体和颜色对话框。")
        self.setCentralWidget(self.editor)

        # 构建所有 QAction、菜单栏和工具栏
        self._build_actions()
        self.statusBar().showMessage("就绪")

    # 构建所有 QAction、菜单栏和工具栏
    def _build_actions(self) -> None:
        open_action = QAction("打开", self)
        # 设置快捷键为 Ctrl+O 系统级别快捷键
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)

        save_action = QAction("保存", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)

        font_action = QAction("字体", self)
        font_action.triggered.connect(self.choose_font)

        color_action = QAction("颜色", self)
        color_action.triggered.connect(self.choose_color)

        about_action = QAction("关于", self)
        about_action.setMenuRole(QAction.MenuRole.AboutRole)
        about_action.triggered.connect(self.show_about)
        
        # 创建文件菜单，添加打开、保存动作
        file_menu = self.menuBar().addMenu("文件")
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        format_menu = self.menuBar().addMenu("格式")
        format_menu.addAction(font_action)
        format_menu.addAction(color_action)

        help_menu = self.menuBar().addMenu("帮助")
        help_menu.addAction(about_action)

        # 创建主工具栏，设置不可移动
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        toolbar.addSeparator()
        toolbar.addAction(font_action)
        toolbar.addAction(color_action)
        self.addToolBar(toolbar)

    def open_file(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "打开文本文件", "", "Text Files (*.txt);;All Files (*)")
        if not filename:
            return
        path = Path(filename)
        # 解码文件内容为 UTF-8 编码
        # 字节->字符串
        self.editor.setPlainText(path.read_text(encoding="utf-8"))
        self.current_file = path
        self.statusBar().showMessage(f"已打开：{path.name}", 3000)

    def save_file(self) -> None:
        if self.current_file is None:
            filename, _ = QFileDialog.getSaveFileName(self, "保存文本文件", "notes.txt", "Text Files (*.txt)")
            if not filename:
                return
            self.current_file = Path(filename)

        # 编码文件内容为 UTF-8 编码
        # 字符串->字节
        self.current_file.write_text(self.editor.toPlainText(), encoding="utf-8")
        self.statusBar().showMessage(f"已保存：{self.current_file.name}", 3000)

    def choose_font(self) -> None:
        font, accepted = QFontDialog.getFont(self.editor.font(), self, "选择字体")
        if accepted:
            self.editor.setFont(font)

    def choose_color(self) -> None:
        color = QColorDialog.getColor(self.editor.textColor(), self, "选择文字颜色")
        if color.isValid():
            self.editor.setTextColor(color)

    def show_about(self) -> None:
        QMessageBox.information(self, "关于", "这是一个用于学习 QAction 和标准对话框的迷你记事本。")


def main() -> int:
    app = QApplication(sys.argv)
    window = NotesWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
