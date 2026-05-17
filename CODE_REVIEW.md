# 代码审查记录

审查范围：`unit01_hello` 到 `unit08_styling`，以及 `final_project/task_tracker.py`。

验证命令：

```bash
PYTHONPYCACHEPREFIX=/private/tmp/pyqt6-2-pycache python3 -m compileall -q .
```

结果：语法编译通过。当前机器没有为本任务安装 PyQt6，因此没有启动 GUI 做运行时交互测试。

## Unit 01

- 检查点：`QApplication` 只创建一次，窗口显示后进入 `app.exec()`。
- 结果：通过。

## Unit 02

- 检查点：布局无手写坐标，表单校验能阻止空姓名提交。
- 结果：通过。

## Unit 03

- 检查点：业务对象用自定义信号通知 UI，滑块回写时避免重复设置导致循环更新。
- 结果：通过。

## Unit 04

- 检查点：`QAction` 复用在菜单和工具栏；文件读写使用 UTF-8；对话框取消时直接返回。
- 结果：通过。

## Unit 05

- 检查点：`rowCount` / `columnCount` 正确处理有效 parent；勾选列使用 `CheckStateRole`；插入删除包在 begin/end 调用中。
- 结果：通过。

## Unit 06

- 检查点：`QSettings` 只保存偏好，JSON 保存业务数据；JSON 损坏时不让应用崩溃。
- 结果：通过。

## Unit 07

- 发现并修正：窗口关闭时后台线程可能仍在运行，存在 `QThread` 生命周期风险。
- 修正：添加 `closeEvent`，关闭时请求 worker 取消并等待线程退出。
- 结果：通过。

## Unit 08

- 检查点：QSS 文件独立；动态属性变化后重新 polish 让样式立即生效。
- 结果：通过。

## Final Project

- 发现并修正：重载任务时窗口类直接修改模型私有字段 `_tasks`。
- 修正：给 `TaskTableModel` 增加 `replace_tasks()`，由模型自己发出 reset 信号。
- 发现并修正：生成报告时关闭窗口可能留下后台线程。
- 修正：`closeEvent` 保存数据后等待报告线程退出。
- 加固：`schedule_autosave(*args)` 兼容 `dataChanged`、`rowsInserted`、`rowsRemoved` 的不同信号参数。
- 结果：通过。
