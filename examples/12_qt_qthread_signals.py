#!/usr/bin/env python3
"""
Example 12: Qt QThread and Signals/Slots

Demonstrates:
- Using QThread for threading in Qt applications
- Qt signals and slots (type-safe, cross-thread)
- Worker object pattern (moveToThread)
- Thread-safe communication with GUI
- Proper QThread lifecycle management

Key Concepts:
- QThread is Qt's threading mechanism
- Qt signals/slots are thread-safe automatically
- moveToThread() pattern is preferred over subclassing QThread
- Signals can carry typed data between threads
- Qt's event loop handles cross-thread calls

OPTIONAL DEPENDENCY:
- This example requires PyQt6 or PySide6
- Install with: pip install PyQt6
- Or: pip install PySide6
- The example will skip if Qt is not available
"""

import logging
import time
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)-12s] %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Try to import Qt (optional dependency)
QT_AVAILABLE = False
try:
    from PyQt6.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QCoreApplication
    from PyQt6.QtWidgets import QApplication
    QT_AVAILABLE = True
    logger.info("Using PyQt6")
except ImportError:
    try:
        from PySide6.QtCore import QThread, QObject, Signal as pyqtSignal, Slot as pyqtSlot, QCoreApplication
        from PySide6.QtWidgets import QApplication
        QT_AVAILABLE = True
        logger.info("Using PySide6")
    except ImportError:
        logger.warning("Qt not available. Install PyQt6 or PySide6 to run this example.")


if QT_AVAILABLE:
    class Worker(QObject):
        """
        Worker object that runs in a separate thread.
        Uses the moveToThread() pattern.
        """

        # Define signals (must be class attributes)
        started = pyqtSignal()
        progress = pyqtSignal(int)  # Carries an integer
        message = pyqtSignal(str)   # Carries a string
        finished = pyqtSignal()
        error = pyqtSignal(str)

        def __init__(self):
            super().__init__()
            self._is_running = False

        @pyqtSlot()
        def do_work(self):
            """Main work method (runs in worker thread)."""
            logger.info("Worker starting...")
            self._is_running = True
            self.started.emit()

            try:
                for i in range(10):
                    if not self._is_running:
                        logger.info("Worker cancelled")
                        break

                    # Simulate work
                    time.sleep(0.3)

                    # Emit progress
                    progress_value = (i + 1) * 10
                    self.progress.emit(progress_value)
                    self.message.emit(f"Completed step {i + 1}/10")

                logger.info("Worker finished")
                self.finished.emit()

            except Exception as e:
                logger.error(f"Worker error: {e}")
                self.error.emit(str(e))

        @pyqtSlot()
        def stop(self):
            """Stop the worker."""
            logger.info("Stopping worker...")
            self._is_running = False


    class Controller(QObject):
        """
        Controller that manages the worker thread.
        """

        # Signal to start work
        start_work = pyqtSignal()
        stop_work = pyqtSignal()

        def __init__(self):
            super().__init__()

            # Create worker and thread
            self.worker = Worker()
            self.thread = QThread()

            # Move worker to thread
            self.worker.moveToThread(self.thread)

            # Connect signals and slots
            self.start_work.connect(self.worker.do_work)
            self.stop_work.connect(self.worker.stop)

            self.worker.started.connect(self.on_started)
            self.worker.progress.connect(self.on_progress)
            self.worker.message.connect(self.on_message)
            self.worker.finished.connect(self.on_finished)
            self.worker.error.connect(self.on_error)

            # Start thread
            self.thread.start()
            logger.info("Thread started")

        @pyqtSlot()
        def on_started(self):
            """Called when worker starts."""
            logger.info("[Controller] Worker started")

        @pyqtSlot(int)
        def on_progress(self, value: int):
            """Called on progress update."""
            logger.info(f"[Controller] Progress: {value}%")

        @pyqtSlot(str)
        def on_message(self, msg: str):
            """Called on message."""
            logger.info(f"[Controller] Message: {msg}")

        @pyqtSlot()
        def on_finished(self):
            """Called when worker finishes."""
            logger.info("[Controller] Worker finished")
            QCoreApplication.quit()

        @pyqtSlot(str)
        def on_error(self, error: str):
            """Called on error."""
            logger.error(f"[Controller] Error: {error}")
            QCoreApplication.quit()

        def shutdown(self):
            """Clean shutdown of thread."""
            logger.info("Shutting down thread...")
            self.stop_work.emit()
            self.thread.quit()
            self.thread.wait()
            logger.info("Thread shut down")


    class LongRunningTask(QThread):
        """
        Alternative pattern: Subclass QThread (less preferred).
        Use this when you need simple background task.
        """

        progress = pyqtSignal(int)
        finished_signal = pyqtSignal(str)

        def __init__(self, task_name: str):
            super().__init__()
            self.task_name = task_name

        def run(self):
            """This runs in the thread (override QThread.run())."""
            logger.info(f"Task '{self.task_name}' starting...")

            for i in range(5):
                time.sleep(0.5)
                self.progress.emit((i + 1) * 20)

            result = f"Task '{self.task_name}' completed"
            self.finished_signal.emit(result)
            logger.info(result)


def example_worker_pattern():
    """Demonstrate the Worker + moveToThread pattern (preferred)."""
    logger.info("\n--- Example 1: Worker + moveToThread pattern ---")

    app = QCoreApplication(sys.argv)

    controller = Controller()

    # Start work after a short delay
    from PyQt6.QtCore import QTimer if 'PyQt6' in sys.modules else lambda: None

    def start_delayed():
        logger.info("Starting work...")
        controller.start_work.emit()

    if 'PyQt6' in sys.modules:
        QTimer.singleShot(500, start_delayed)
    else:
        from PySide6.QtCore import QTimer
        QTimer.singleShot(500, start_delayed)

    # Run event loop
    logger.info("Starting Qt event loop...")
    app.exec() if hasattr(app, 'exec') else app.exec_()

    # Cleanup
    controller.shutdown()


def example_qthread_subclass():
    """Demonstrate QThread subclass pattern."""
    logger.info("\n--- Example 2: QThread subclass pattern ---")

    app = QCoreApplication(sys.argv)

    task = LongRunningTask("BackgroundJob")

    @pyqtSlot(int)
    def on_progress(value):
        logger.info(f"[Main] Task progress: {value}%")

    @pyqtSlot(str)
    def on_finished(result):
        logger.info(f"[Main] {result}")
        app.quit()

    task.progress.connect(on_progress)
    task.finished_signal.connect(on_finished)

    # Start thread
    logger.info("Starting background task...")
    task.start()

    # Run event loop
    app.exec() if hasattr(app, 'exec') else app.exec_()

    # Wait for thread to finish
    task.wait()


def main():
    """Main entry point."""
    logger.info("=== Example 12: Qt QThread and Signals ===")

    if not QT_AVAILABLE:
        logger.error("Qt is not installed!")
        logger.info("Install with: pip install PyQt6")
        logger.info("Or: pip install PySide6")
        logger.info("\nThis example is SKIPPED")
        return

    # Example 1: Preferred pattern (Worker + moveToThread)
    try:
        example_worker_pattern()
    except Exception as e:
        logger.error(f"Example 1 failed: {e}")

    logger.info("\n" + "="*50 + "\n")

    # Example 2: QThread subclass
    try:
        example_qthread_subclass()
    except Exception as e:
        logger.error(f"Example 2 failed: {e}")

    logger.info("\n=== Key Takeaways ===")
    logger.info("1. Prefer Worker + moveToThread over QThread subclassing")
    logger.info("2. Qt signals/slots are automatically thread-safe")
    logger.info("3. Never access GUI from worker thread directly")
    logger.info("4. Use signals to communicate between threads")
    logger.info("5. Always clean up threads properly (quit + wait)")

    logger.info("\n=== Example completed ===")


if __name__ == "__main__":
    main()
