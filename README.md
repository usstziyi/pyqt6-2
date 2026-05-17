# PyQt6 循序渐进学习项目

这是一个系统化学习 PyQt6 的实践项目，通过 8 个循序渐进的学习单元和 1 个综合项目，帮助你掌握 PyQt6 开发桌面应用程序的核心技能。

## 项目特点

- **循序渐进**：从基础概念到高级特性，逐步深入
- **实践导向**：每个单元都有可运行的代码，边学边练
- **代码即教程**：代码注释详细解释"为什么这样写"，而非仅说明"这一行做了什么"
- **综合项目**：通过任务追踪器整合所有知识点

## 环境要求

- Python >= 3.11
- PyQt6 >= 6.11.0

## 快速开始

### 安装依赖

使用 uv（推荐）：

```bash
uv sync
```

或使用 pip：

```bash
pip install pyqt6>=6.11.0
```

### 运行示例

```bash
# 运行单元01 - 应用入口和窗口
python units/unit01_hello/main.py

# 运行单元05 - Model/View
python units/unit05_model_view/main.py

# 运行综合项目 - 任务追踪器
python project/task_tracker.py
```

## 项目结构

```
pyqt6-2/
├── units/                    # 学习单元目录
│   ├── unit01_hello/         # 应用入口和窗口
│   ├── unit02_layouts_widgets/  # 布局和常用控件
│   ├── unit03_signals_slots/     # 信号与槽
│   ├── unit04_actions_dialogs/   # 菜单、工具栏、对话框
│   ├── unit05_model_view/        # Model/View 架构
│   ├── unit06_persistence/       # 数据持久化
│   ├── unit07_threads/           # 多线程编程
│   └── unit08_styling/           # 样式和主题
├── project/
│   └── task_tracker.py       # 综合项目：任务追踪器
├── notes/                    # 学习笔记
├── CODE_REVIEW.md           # 代码审查记录
└── PYQT6_LEARNING_PLAN.md   # 详细学习计划
```

## 学习路线

| 单元 | 主题 | 核心内容 |
|------|------|----------|
| 01 | 应用入口和窗口 | `QApplication`、事件循环、`QMainWindow`、状态栏 |
| 02 | 布局和常用控件 | `QVBoxLayout`、`QFormLayout`、输入控件、基础校验 |
| 03 | 信号与槽 | 内置信号、自定义信号、`pyqtSlot`、解耦设计 |
| 04 | 菜单和对话框 | 菜单栏、工具栏、文件对话框、消息框 |
| 05 | Model/View | `QAbstractTableModel`、代理模型、数据与界面分离 |
| 06 | 持久化 | `QSettings` 保存偏好、JSON 保存业务数据 |
| 07 | 线程 | `QObject + QThread`、后台任务、跨线程信号 |
| 08 | 样式 | QSS 样式表、动态属性、主题切换 |
| 项目 | 任务追踪器 | 综合演练：表格、筛选、增删改、自动保存、导出、报告生成 |

## 综合项目：任务追踪器

任务追踪器整合了前 8 个单元的核心知识点：

- **Model/View 架构**：使用 `QAbstractTableModel` 管理任务数据，`QSortFilterProxyModel` 实现筛选功能
- **信号与槽**：按钮点击、菜单动作、表格编辑等交互
- **数据持久化**：JSON 格式存储任务数据
- **多线程**：后台线程生成任务报告
- **自动保存**：修改后自动保存，无需手动操作
- **CSV 导出**：将任务导出为 CSV 格式

运行命令：

```bash
python project/task_tracker.py
```

## 常见原则

1. **一个进程创建一个 `QApplication`**
2. **不要在主线程执行耗时任务**，否则界面会卡死
3. **控件之间用信号/槽通信**，避免直接操作其他控件
4. **复杂数据优先使用 Model/View**，而非手动维护大量 widget
5. **`QSettings` 适合保存偏好设置**，业务数据更适合 JSON/SQLite

## 推荐学习节奏

- **第 1-2 天**：完成 unit01 和 unit02，理解事件循环和布局
- **第 3-4 天**：完成 unit03 和 unit04，掌握交互和界面骨架
- **第 5-7 天**：深入 unit05，Model/View 是 Qt 开发的重要分水岭
- **第 8-9 天**：完成 unit06 和 unit07，理解数据保存和后台任务
- **第 10-11 天**：完成 unit08，学习样式设计
- **第 12-14 天**：运行综合项目，尝试扩展功能

## 学习资源

- [Riverbank PyQt 介绍](https://riverbankcomputing.com/software/pyqt)
- [PyQt6 官方参考文档](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Qt 信号与槽机制](https://doc.qt.io/qt-6.9/signalsandslots.html)
- [Qt Model/View 编程](https://doc.qt.io/qt-6/model-view-programming.html)
- [Qt for Python 示例](https://doc.qt.io/qtforpython-6/examples/index.html)
- [PyQt 示例仓库](https://github.com/pyqt/examples)

## 相关文档

- [详细学习计划](PYQT6_LEARNING_PLAN.md)
- [代码审查记录](CODE_REVIEW.md)

## 许可证

本项目仅供学习交流使用。
