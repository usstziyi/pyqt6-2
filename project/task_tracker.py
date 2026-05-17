"""综合项目：任务追踪器。

运行：
    python final_project/task_tracker.py

这个项目串起前面 unit 的知识：
    - QMainWindow、菜单、工具栏
    - 信号/槽
    - QAbstractTableModel + QSortFilterProxyModel
    - JSON 持久化
    - QThread 后台生成报告
"""

from __future__ import annotations

import csv
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from PyQt6.QtCore import (
    QAbstractTableModel,
    QDate,
    QModelIndex,
    QObject,
    QSortFilterProxyModel,
    Qt,
    QThread,
    QTimer,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


@dataclass
class Task:
    title: str
    priority: str
    due_date: str
    done: bool = False

    # 把一个方法绑定到“类”本身，而不是绑定到某个对象实例。
    # 等价于定义了一个“类级别的构造辅助方法”，用于从字典创建 Task 对象。
    # 它适合用来写“从某种数据创建对象”的工厂方法。这里的 cls 表示当前类，
    # 通常用它来创建并返回一个新的对象。
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            title=str(data.get("title", "")).strip() or "未命名任务",
            priority=str(data.get("priority", "Medium")),
            due_date=str(data.get("due_date", QDate.currentDate().toString("yyyy-MM-dd"))),
            done=bool(data.get("done", False)),
        )


class TaskRepository:
    """负责文件读写，让窗口类不关心 JSON 细节。"""

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> list[Task]:
        if not self.path.exists():
            return [
                Task("完成 PyQt6 unit05 Model/View", "High", QDate.currentDate().toString("yyyy-MM-dd")),
                Task("给任务追踪器增加筛选", "Medium", QDate.currentDate().addDays(2).toString("yyyy-MM-dd")),
            ]
        try:
            raw_items = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return [Task.from_dict(item) for item in raw_items if isinstance(item, dict)]

    def save(self, tasks: list[Task]) -> None:
        self.path.write_text(json.dumps([asdict(task) for task in tasks], ensure_ascii=False, indent=2), encoding="utf-8")

# 源模型
class TaskTableModel(QAbstractTableModel):
    headers = ["标题", "优先级", "截止日期", "完成"]
    priorities = ["Low", "Medium", "High"]

    def __init__(self, tasks: list[Task]) -> None:
        super().__init__()
        self._tasks = tasks

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._tasks)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        """
        当表格需要显示、编辑、勾选、对齐某个单元格时，Qt 会问 Model：“这个位置、这个用途下，应该返回什么数据？”
        """
        if not index.isValid():
            return None

        task = self._tasks[index.row()]
        column = index.column()
        
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if column == 0:
                return task.title
            if column == 1:
                return task.priority
            if column == 2:
                return task.due_date
            if column == 3:
                return "是" if task.done else "否"

        if role == Qt.ItemDataRole.CheckStateRole and column == 3:
            return Qt.CheckState.Checked if task.done else Qt.CheckState.Unchecked

        if role == Qt.ItemDataRole.TextAlignmentRole and column in (1, 2, 3):
            return Qt.AlignmentFlag.AlignCenter

        return None

    def setData(self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid():
            return False

        task = self._tasks[index.row()]
        column = index.column()

        if role == Qt.ItemDataRole.EditRole:
            text = str(value).strip()
            if column == 0 and text:
                task.title = text
            elif column == 1 and text in self.priorities:
                task.priority = text
            elif column == 2 and text:
                task.due_date = text
            else:
                return False
            self.dataChanged.emit(index, index, [role, Qt.ItemDataRole.DisplayRole])
            return True

        if role == Qt.ItemDataRole.CheckStateRole and column == 3:
            state = Qt.CheckState(value) if isinstance(value, int) else value
            task.done = state == Qt.CheckState.Checked
            self.dataChanged.emit(index, index, [role, Qt.ItemDataRole.DisplayRole])
            return True

        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.column() in (0, 1, 2):
            flags |= Qt.ItemFlag.ItemIsEditable
        if index.column() == 3:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        return flags

    # headerData() 负责把headers这些文字交给 QTableView，让表格顶部显示
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

    def task_at(self, row: int) -> Task:
        return self._tasks[row]

    def tasks(self) -> list[Task]:
        return list(self._tasks)

    def replace_tasks(self, tasks: list[Task]) -> None:
        self.beginResetModel()
        self._tasks = tasks
        self.endResetModel()

    def add_task(self, task: Task) -> None:
        row = len(self._tasks)
        self.beginInsertRows(QModelIndex(), row, row)
        self._tasks.append(task)
        self.endInsertRows()

    def remove_rows(self, rows: list[int]) -> None:
        for row in sorted(set(rows), reverse=True):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._tasks[row]
            self.endRemoveRows()

# 代理模型
class TaskFilterProxyModel(QSortFilterProxyModel):
    """把筛选逻辑放进代理模型，源模型仍然只关心原始数据。
    self.model = TaskTableModel(self.repository.load())  # 源模型
    self.proxy = TaskFilterProxyModel()                  # 代理模型
    self.proxy.setSourceModel(self.model)                # 代理模型包住源模型
    self.table.setModel(self.proxy)                      # 表格使用代理模型

    TaskRepository
        ↓
    TaskTableModel        ← 源模型，保存原始任务数据
        ↓
    TaskFilterProxyModel  ← 代理模型，负责筛选、排序
        ↓
    QTableView            ← 表格视图，负责显示
    """

    def __init__(self) -> None:
        super().__init__()
        self.search_text = ""
        self.status = "全部"

    def set_search_text(self, text: str) -> None:
        self.search_text = text.strip().lower()
        self.invalidateFilter()

    def set_status(self, status: str) -> None:
        self.status = status
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        model = self.sourceModel()
        if not isinstance(model, TaskTableModel):
            return True

        task = model.task_at(source_row)
        matches_text = self.search_text in task.title.lower()
        matches_status = self.status == "全部" or (self.status == "已完成" and task.done) or (self.status == "未完成" and not task.done)
        return matches_text and matches_status


class ReportWorker(QObject):
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, tasks: list[Task], output_path: Path) -> None:
        super().__init__()
        self.tasks = tasks
        self.output_path = output_path

    @pyqtSlot()
    def run(self) -> None:
        try:
            time.sleep(0.5)
            total = len(self.tasks)
            done = sum(1 for task in self.tasks if task.done)
            pending = total - done
            high_pending = sum(1 for task in self.tasks if task.priority == "High" and not task.done)
            lines = [
                "# 任务报告",
                "",
                f"- 总任务数：{total}",
                f"- 已完成：{done}",
                f"- 未完成：{pending}",
                f"- 高优先级未完成：{high_pending}",
            ]
            self.output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            self.finished.emit(str(self.output_path))
        except Exception as exc:  # pragma: no cover - GUI 后台任务兜底
            self.failed.emit(str(exc))


class TaskTrackerWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PyQt6 实战项目 - 任务追踪器")
        self.resize(900, 560)

        self.repository = TaskRepository(Path(__file__).with_name("tasks.json"))  # 初始化任务仓库，指定数据文件路径
        self.model = TaskTableModel(self.repository.load())  # 源模型，加载任务数据
        self.proxy = TaskFilterProxyModel()  # 代理模型，用于筛选和排序
        self.proxy.setSourceModel(self.model)  # 将代理模型绑定到源模型

        self.report_thread: QThread | None = None
        self.report_worker: ReportWorker | None = None

        # 自动保存定时器：延迟保存机制，避免频繁操作文件
        # - 使用 QTimer 实现防抖（debounce），用户停止操作 600ms 后才触发保存
        # - setSingleShot(True) 确保每次修改只触发一次保存，而不是周期性保存
        # - 当模型数据发生变化时，调用 schedule_autosave() 重启定时器
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.setInterval(600)
        self.autosave_timer.timeout.connect(self.save_tasks)

        self._build_actions()
        self._build_ui()
        self._connect_model_changes()

    def _build_actions(self) -> None:
        save_action = QAction("保存", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_tasks)

        reload_action = QAction("重新载入", self)
        reload_action.triggered.connect(self.reload_tasks)

        export_action = QAction("导出 CSV", self)
        export_action.triggered.connect(self.export_csv)

        report_action = QAction("生成报告", self)
        report_action.triggered.connect(self.generate_report)

        
        # 构建菜单栏：提供文件操作入口，符合桌面应用标准交互模式
        file_menu = self.menuBar().addMenu("文件")
        file_menu.addAction(save_action)
        file_menu.addAction(reload_action)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        file_menu.addAction(report_action)

        # 构建工具栏：将常用操作以图标按钮形式呈现，提升操作效率
        toolbar = QToolBar("任务工具栏")
        toolbar.setMovable(False)
        toolbar.addAction(save_action)
        toolbar.addAction(export_action)
        toolbar.addAction(report_action)
        self.addToolBar(toolbar)

    def _build_ui(self) -> None:
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("任务标题")

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(TaskTableModel.priorities)
        self.priority_combo.setCurrentText("Medium")

        self.due_date_input = QDateEdit(QDate.currentDate())
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDisplayFormat("yyyy-MM-dd")

        add_button = QPushButton("新增")
        add_button.clicked.connect(self.add_task)

        remove_button = QPushButton("删除选中")
        remove_button.clicked.connect(self.remove_selected)

        toggle_button = QPushButton("切换完成")
        toggle_button.clicked.connect(self.toggle_done_selected)

        # 创建表单行布局：用于放置任务输入控件和操作按钮
        # 布局结构：标题输入框(3倍拉伸) + 优先级选择(1倍) + 截止日期(1倍) + 三个操作按钮(固定宽度)
        # stretch 参数说明：大于0的值表示该控件参与剩余空间的拉伸分配，数值越大分配越多空间
        # stretch=0 表示该控件不参与拉伸，只占据自身的 sizeHint() 大小
        form_row = QHBoxLayout()
        form_row.addWidget(self.title_input, 3)
        form_row.addWidget(self.priority_combo, 1)
        form_row.addWidget(self.due_date_input, 1)
        form_row.addWidget(add_button, 0)
        form_row.addWidget(remove_button, 0)
        form_row.addWidget(toggle_button, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("按标题搜索")
        self.search_input.textChanged.connect(self.proxy.set_search_text)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["全部", "未完成", "已完成"])
        self.status_combo.currentTextChanged.connect(self.proxy.set_status)

        # 创建筛选行布局：用于放置搜索输入框和状态筛选下拉框
        # 布局结构：搜索输入框(3倍拉伸) + 状态筛选(1倍)
        # 搜索框支持实时过滤任务标题，状态筛选支持按完成状态过滤
        filter_row = QHBoxLayout()
        filter_row.addWidget(self.search_input, 3)
        filter_row.addWidget(self.status_combo, 1)

        self.table = QTableView()  # 创建表格视图控件，用于显示任务列表
        self.table.setModel(self.proxy)  # 将代理模型设置到表格视图，实现筛选和排序功能
        self.table.setSortingEnabled(True)  # 启用表格排序功能，用户可点击表头进行排序
        self.table.resizeColumnsToContents()  # 根据内容自动调整列宽，确保数据完整显示
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)  # 设置选择行为为整行选择，方便用户批量操作任务

        root = QVBoxLayout()
        root.addLayout(form_row)
        root.addLayout(filter_row)
        root.addWidget(self.table)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)
        self.statusBar().showMessage("任务追踪器已就绪")

    def _connect_model_changes(self) -> None:
        self.model.dataChanged.connect(self.schedule_autosave)
        self.model.rowsInserted.connect(self.schedule_autosave)
        self.model.rowsRemoved.connect(self.schedule_autosave)

    def schedule_autosave(self, *args) -> None:
        self.autosave_timer.start()

    def add_task(self) -> None:
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "缺少标题", "请先输入任务标题。")
            self.title_input.setFocus()
            return

        task = Task(
            title=title,
            priority=self.priority_combo.currentText(),
            due_date=self.due_date_input.date().toString("yyyy-MM-dd"),
        )
        self.model.add_task(task)
        self.title_input.clear()
        self.table.resizeColumnsToContents()

    def selected_source_rows(self) -> list[int]:
        # 获取表格的选择模型，用于获取用户当前选中的行
        selection = self.table.selectionModel()
        rows = []
        for proxy_index in selection.selectedRows():
            # 核心原因一句话： 表格显示的是代理模型（过滤/排序后的视图），
            # 表格绑定的是 self.proxy （代理模型），
            # 所以用户的选中操作返回的是 代理模型坐标系 下的行号。
            # 但数据操作必须针对源模型（原始数据）。
            # 通过 mapToSource 将代理行号映射回源行号，才能正确操作原始数据。
            rows.append(self.proxy.mapToSource(proxy_index).row())
        return rows

    def remove_selected(self) -> None:
        rows = self.selected_source_rows()
        if not rows:
            return
        # 从源模型中删除记录
        self.model.remove_rows(rows)

    def toggle_done_selected(self) -> None:
        for row in self.selected_source_rows():
            task = self.model.task_at(row)
            # 创建一个 QModelIndex ，定位到源模型第 row 行、第 3 列的单元格 。
            index = self.model.index(row, 3)
            state = Qt.CheckState.Unchecked if task.done else Qt.CheckState.Checked
            self.model.setData(index, state, Qt.ItemDataRole.CheckStateRole)

    def save_tasks(self) -> None:
        self.repository.save(self.model.tasks())
        self.statusBar().showMessage("已保存任务", 2000)

    def reload_tasks(self) -> None:
        self.model.replace_tasks(self.repository.load())
        self.table.resizeColumnsToContents()
        self.statusBar().showMessage("已重新载入任务", 2000)

    def export_csv(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "导出 CSV", "tasks.csv", "CSV Files (*.csv)")
        if not filename:
            return
        path = Path(filename)
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(TaskTableModel.headers)
            for task in self.model.tasks():
                writer.writerow([task.title, task.priority, task.due_date, "是" if task.done else "否"])
        self.statusBar().showMessage(f"已导出：{path.name}", 3000)

    def generate_report(self) -> None:
        if self.report_thread is not None:
            return

        output_path = Path(__file__).with_name("task_report.md")
        self.report_thread = QThread(self)
        self.report_worker = ReportWorker(self.model.tasks(), output_path)
        self.report_worker.moveToThread(self.report_thread)

        self.report_thread.started.connect(self.report_worker.run)

        self.report_worker.finished.connect(self.handle_report_finished)
        self.report_worker.failed.connect(self.handle_report_failed)

        self.report_worker.finished.connect(self.report_thread.quit)
        self.report_worker.failed.connect(self.report_thread.quit)
        
        self.report_worker.finished.connect(self.report_worker.deleteLater)
        self.report_worker.failed.connect(self.report_worker.deleteLater)

        self.report_thread.finished.connect(self.report_thread.deleteLater)
        self.report_thread.finished.connect(self.clear_report_refs)

        self.statusBar().showMessage("正在后台生成报告...")
        self.report_thread.start()

    @pyqtSlot(str)
    def handle_report_finished(self, path: str) -> None:
        self.statusBar().showMessage(f"报告已生成：{Path(path).name}", 4000)

    @pyqtSlot(str)
    def handle_report_failed(self, message: str) -> None:
        QMessageBox.critical(self, "报告失败", message)

    def clear_report_refs(self) -> None:
        self.report_thread = None
        self.report_worker = None

    def closeEvent(self, event) -> None:
        self.save_tasks()
        if self.report_thread is not None and self.report_thread.isRunning():
            self.report_thread.quit()
            self.report_thread.wait(1500)
        super().closeEvent(event)


def main() -> int:
    app = QApplication(sys.argv)
    window = TaskTrackerWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
