"""Unit 07: 用 QThread 执行后台任务。

运行：
    python unit07_threads/main.py
"""

from __future__ import annotations

import sys
import time
from threading import Event

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication, QLabel, QProgressBar, QPushButton, QVBoxLayout, QWidget


class CountingWorker(QObject):
    """后台 worker：只做耗时工作，不直接操作任何 UI 控件。"""

    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, limit: int = 100) -> None:
        super().__init__()
        self.limit = limit
        # Event() 是 Python 标准库 threading 里的线程同步工具。
        # 一个线程安全的布尔开关，初始状态：False
        # 在这段代码里，它被用来做一个“取消标志”：主线程点击“取消”按钮后，把标志设为 True；
        # 后台线程在循环中不断检查这个标志，一旦发现被设置，就主动退出任务。
        self._cancel_requested = Event() 

    @pyqtSlot()
    def run(self) -> None:
        """
        每循环一次：
        先检查是否有人请求取消
        如果请求取消：
            发出 finished 信号
            退出 run()
        如果没有取消：
            继续 sleep
            发出进度
        """
        try:
            for value in range(self.limit + 1):
                if self._cancel_requested.is_set():
                    self.finished.emit("任务已取消")
                    return
                time.sleep(0.03)
                self.progress.emit(value)
            self.finished.emit("任务完成")
        except Exception as exc:  # pragma: no cover - 教学示例中保留兜底错误信号
            self.failed.emit(str(exc))

    def cancel(self) -> None:
        self._cancel_requested.set()


class ThreadWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Unit 07 - Threads")
        self.resize(420, 220)

        self.thread: QThread | None = None
        self.worker: CountingWorker | None = None

        self.label = QLabel("点击开始，后台线程会汇报进度。")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)

        self.start_button = QPushButton("开始")
        self.start_button.clicked.connect(self.start_work)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_work)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addWidget(self.start_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def start_work(self) -> None:
        if self.thread is not None:
            return

        self.progress.setValue(0)
        self.label.setText("后台任务运行中...")
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        # 创建新线程，并将 worker 
        # Worker-Object 模式
        self.thread = QThread(self)                  # 创建子线程
        self.worker = CountingWorker()               # 创建 worker 对象（在主线程）
        self.worker.moveToThread(self.thread)        # 把 worker 移到子线程

        # 同一个信号激发的槽函数，默认先注册的先执行
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress.setValue)

        self.worker.finished.connect(self.handle_finished) # 更新UI提示
        self.worker.finished.connect(self.thread.quit) # 通知线程退出
        self.worker.finished.connect(self.worker.deleteLater) # 清理worker

        self.worker.failed.connect(self.handle_failed)
        self.worker.failed.connect(self.thread.quit)
        self.worker.failed.connect(self.worker.deleteLater)

        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.clear_thread_refs)

        self.thread.start()

    # 由button驱动
    def cancel_work(self) -> None:
        if self.worker is not None:
            self.worker.cancel() # 设置取消标志

    @pyqtSlot(str)
    def handle_finished(self, message: str) -> None:
        self.label.setText(message)
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    @pyqtSlot(str)
    def handle_failed(self, message: str) -> None:
        self.label.setText(f"任务失败：{message}")
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def clear_thread_refs(self) -> None:
        self.thread = None
        self.worker = None



    def closeEvent(self, event) -> None:
        """
        quit()          → 优雅退出（等事件循环处理完）
        ↓ 超时
        terminate()     → 强制终止（系统级杀死）
        ↓ 
        wait()          → 确认线程已死（正常情况瞬返）
        """
        # 如果 worker 存在，发送取消信号请求后台任务终止
        if self.worker is not None:
            self.worker.cancel()
        # 如果线程存在且正在运行，请求线程退出并等待最多 1500 毫秒
        if self.thread is not None and self.thread.isRunning():
            self.thread.quit() # 请求线程退出
            if not self.thread.wait(3000):        # 检查返回值
                self.thread.terminate()           # 超时则强制终止（最后手段）
                self.thread.wait()                # terminate() 是 立刻 把线程标记为终止状态， wait() 几乎瞬间就能返回。所以这里不传超时参数是安全的。
        # 调用父类的关闭事件处理，确保窗口正常关闭
        super().closeEvent(event)


def main() -> int:
    app = QApplication(sys.argv)
    window = ThreadWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    # 启动 Qt 程序，等程序退出后，把 Qt 返回的退出码交给操作系统。
    # 这对命令行程序、脚本、自动化测试、CI 工具有意义。
    raise SystemExit(main())
    # sys.exit(main()) #等价写法
