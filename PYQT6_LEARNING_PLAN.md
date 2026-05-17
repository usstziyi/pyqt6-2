# PyQt6 循序渐进学习计划

本仓库把 PyQt6 学习拆成 8 个 unit 和 1 个综合项目。每个 unit 都有独立入口，可以按顺序运行、阅读、改动。代码注释偏教学用途，重点解释“为什么这样写”，而不是只说明“这一行做了什么”。

## 参考资料

- [Riverbank PyQt 介绍](https://riverbankcomputing.com/software/pyqt)：PyQt 是 Qt 的 Python 绑定，PyQt6 支持 Qt6。
- [PyQt6 Reference Guide](https://www.riverbankcomputing.com/static/Docs/PyQt6/)：PyQt6 官方参考入口。
- [Qt Signals & Slots](https://doc.qt.io/qt-6.9/signalsandslots.html)：Qt 对象通信机制，PyQt6 中对应 `pyqtSignal` / `pyqtSlot`。
- [Qt Model/View Programming](https://doc.qt.io/qt-6/model-view-programming.html)：表格、列表、树视图背后的模型/视图架构。
- [Qt for Python QThread](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QThread.html)：线程、worker object、跨线程信号的核心思想。示例使用 PySide6 名称，迁移到 PyQt6 时主要把 `Signal` / `Slot` 换成 `pyqtSignal` / `pyqtSlot`。
- [Qt for Python Examples](https://doc.qt.io/qtforpython-6/examples/index.html)：官方示例集合，适合查找 widgets、model-view、thread 等主题。
- [pyqt/examples GitHub 仓库](https://github.com/pyqt/examples)：PyQt6 示例仓库，适合对照常见桌面应用写法。

## 依赖

不需要在本任务中安装环境。你本地运行时建议使用：

```text
Python >= 3.10
PyQt6 >= 6.7
```

可选工具：

```text
ruff 或 flake8：静态检查
pytest：以后给非 GUI 逻辑补测试
```

运行方式示例：

```bash
python unit01_hello/main.py
python unit05_model_view/main.py
python final_project/task_tracker.py
```

## 学习路线

| Unit | 主题 | 目标 |
| --- | --- | --- |
| 01 | 应用入口和窗口 | 理解 `QApplication`、事件循环、`QMainWindow`、状态栏。 |
| 02 | 布局和常用控件 | 掌握 `QVBoxLayout`、`QFormLayout`、输入控件和基础校验。 |
| 03 | 信号与槽 | 使用内置信号、自定义信号、`pyqtSlot` 解耦控件和业务逻辑。 |
| 04 | 菜单、工具栏、对话框 | 写出更像桌面应用的主窗口骨架。 |
| 05 | Model/View | 用 `QAbstractTableModel` 管理表格数据，避免直接堆 `QTableWidget`。 |
| 06 | 持久化 | 用 `QSettings` 保存窗口偏好，用 JSON 保存应用数据。 |
| 07 | 线程 | 用 `QObject + QThread` 执行后台任务，避免 UI 卡死。 |
| 08 | 样式 | 用 QSS 和动态属性组织界面风格。 |
| Project | 任务追踪器 | 综合演练：表格模型、筛选、增删改、自动保存、导出、后台报告。 |

## 建议节奏

1. 第 1-2 天：跑通 unit01 和 unit02，重点观察事件循环和布局如何影响窗口。
2. 第 3-4 天：学习 unit03 和 unit04，把按钮点击、菜单动作、弹窗动作串起来。
3. 第 5-7 天：深入 unit05。Model/View 是 Qt 桌面应用的分水岭，建议多改表格列和数据结构。
4. 第 8-9 天：学习 unit06，把“界面状态”和“业务数据”分开保存。
5. 第 10-11 天：学习 unit07，记住 UI 只能在主线程更新，后台线程通过信号汇报结果。
6. 第 12 天：学习 unit08，体会 QSS 和控件属性如何配合。
7. 第 13-14 天：阅读并运行综合项目，尝试增加“标签”“截止日期提醒”或“按优先级排序”。

## 常见原则

- 一个进程通常只创建一个 `QApplication`。
- 不要在主线程里执行耗时任务，否则事件循环无法处理重绘和输入。
- 控件之间尽量用信号/槽通信，少写“一个控件直接强行操作另一个控件”的耦合代码。
- 表格或列表数据一旦复杂，优先考虑 Model/View，而不是手动维护大量 widget。
- `QSettings` 适合保存窗口大小、主题、最近文件等偏好；业务数据更适合 JSON、SQLite 或服务端。

## 审查记录

代码创建后已逐个 unit 做语法编译审查，审查摘要见 [CODE_REVIEW.md](/Users/usst_ziyi/Programs/solo/pyqt6-2/CODE_REVIEW.md)。
