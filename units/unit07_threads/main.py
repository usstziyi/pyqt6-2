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
        self._cancel_requested = Event()

    @pyqtSlot()
    def run(self) -> None:
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

        self.thread = QThread(self)
        self.worker = CountingWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.handle_finished)
        self.worker.failed.connect(self.handle_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.failed.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.clear_thread_refs)

        self.thread.start()

    def cancel_work(self) -> None:
        if self.worker is not None:
            self.worker.cancel()

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
        if self.worker is not None:
            self.worker.cancel()
        if self.thread is not None and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(1500)
        super().closeEvent(event)


def main() -> int:
    app = QApplication(sys.argv)
    window = ThreadWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
