"""Unit 05: Model/View 表格。

运行：
    python unit05_model_view/main.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QInputDialog,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)


@dataclass
class Task:
    title: str
    owner: str
    done: bool = False

"""任务表格模型，继承自 QAbstractTableModel。

    该类实现了 Model/View 架构中的 Model 部分，负责：
    - 存储和管理任务数据（Task 对象列表）
    - 提供数据的读取、修改接口
    - 通知视图数据变化
    这就是面向对象继承的标准用法，
    父类提供基础设施（通知机制），子类提供业务逻辑（数据操作） 。
"""
class TaskTableModel(QAbstractTableModel):
    """把数据和表格视图分离。

    View 负责显示和交互，Model 负责提供数据、修改数据、通知数据变化。
    """

    headers = ["任务", "负责人", "完成"]

    def __init__(self, tasks: list[Task]) -> None:
        super().__init__()
        self._tasks = tasks

    # "顶层有 N 行，每个节点下没有子行" ——这定义了一个扁平的表格模型，不支持树形展开。
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._tasks)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        task = self._tasks[index.row()]
        column = index.column()

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if column == 0:
                return task.title
            if column == 1:
                return task.owner
            if column == 2:
                return "是" if task.done else "否"

        if role == Qt.ItemDataRole.CheckStateRole and column == 2:
            return Qt.CheckState.Checked if task.done else Qt.CheckState.Unchecked

        return None

    def setData(self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid():
            return False

        task = self._tasks[index.row()]
        column = index.column()

        if role == Qt.ItemDataRole.EditRole and column in (0, 1):
            text = str(value).strip()
            if not text:
                return False
            if column == 0:
                task.title = text
            else:
                task.owner = text
            self.dataChanged.emit(index, index, [role, Qt.ItemDataRole.DisplayRole])
            return True

        if role == Qt.ItemDataRole.CheckStateRole and column == 2:
            state = Qt.CheckState(value) if isinstance(value, int) else value
            task.done = state == Qt.CheckState.Checked
            self.dataChanged.emit(index, index, [role, Qt.ItemDataRole.DisplayRole])
            return True

        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        if index.column() in (0, 1):
            flags |= Qt.ItemFlag.ItemIsEditable
        if index.column() == 2:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        return flags

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

    def add_task(self, task: Task) -> None:
        row = len(self._tasks)
        self.beginInsertRows(QModelIndex(), row, row)
        self._tasks.append(task)
        self.endInsertRows()

    def remove_rows(self, rows: list[int]) -> None:
        for row in sorted(set(rows), reverse=True):
            # 这对函数继承自 QAbstractTableModel，负责删除指定行的数据。
            # 发送"即将删行"信号给 View
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._tasks[row]
            # 发送"删除完成"信号，触发 View 刷新
            self.endRemoveRows()


class TaskWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Unit 05 - Model/View")
        self.resize(640, 360)

        # 创建任务表格模型，并初始化一些示例数据
        self.model = TaskTableModel(
            [
                Task("阅读 signals/slots 文档", "Ada"),
                Task("实现第一个表格模型", "Grace"),
                Task("给表格增加删除功能", "Linus", True),
            ]
        )

        # 创建表格视图，设置模型，并自动调整列宽以适应内容
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()

        add_button = QPushButton("新增任务")
        add_button.clicked.connect(self.add_task)

        remove_button = QPushButton("删除选中")
        remove_button.clicked.connect(self.remove_selected)

        button_row = QHBoxLayout()
        button_row.addWidget(add_button)
        button_row.addWidget(remove_button)
        button_row.addStretch(1)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(button_row)
        self.setLayout(layout)

    def add_task(self) -> None:
        title, accepted = QInputDialog.getText(self, "新增任务", "任务标题：")
        if not accepted or not title.strip():
            return
        owner, accepted = QInputDialog.getText(self, "负责人", "负责人：")
        if not accepted or not owner.strip():
            return
        self.model.add_task(Task(title.strip(), owner.strip()))

    def remove_selected(self) -> None:
        selection = self.table.selectionModel()
        rows = [index.row() for index in selection.selectedRows()]
        self.model.remove_rows(rows)


def main() -> int:
    app = QApplication(sys.argv)
    window = TaskWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
