#!/usr/bin/env python3
"""
Example 11: Application-Level Signals and Slots (Observer Pattern)

Demonstrates:
- Using the pure-Python Signal/Slot implementation from libs.signals
- Observer pattern for decoupling components
- Thread-safe event notification
- Multiple subscribers to a single signal
- Signal/slot pattern in multi-threaded applications

Key Concepts:
- Signals allow decoupling: emitter doesn't know who's listening
- Slots are callbacks connected to signals
- Thread-safe by design (using locks internally)
- Useful for event-driven architectures
- Similar to Qt signals/slots but pure Python
"""

import sys
import os

# Add parent directory to path to import libs
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import time
import random
import logging
from libs.signals import Signal, SignalGroup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)-12s] %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class DownloadManager:
    """
    Simulates a download manager that emits signals for progress updates.
    """

    def __init__(self):
        # Define signals
        self.signals = SignalGroup(['started', 'progress', 'completed', 'failed'])

    def download(self, url: str):
        """
        Simulate downloading a file.

        Args:
            url: URL to download
        """
        logger.info(f"Starting download: {url}")
        self.signals.started.emit(url)

        try:
            # Simulate download in chunks
            total_chunks = 10
            for chunk in range(total_chunks):
                time.sleep(random.uniform(0.1, 0.3))

                # Random failure simulation
                if random.random() < 0.1:
                    raise Exception(f"Network error downloading {url}")

                progress = int((chunk + 1) / total_chunks * 100)
                self.signals.progress.emit(url, progress)

            self.signals.completed.emit(url)
            logger.info(f"Download completed: {url}")

        except Exception as e:
            logger.error(f"Download failed: {url} - {e}")
            self.signals.failed.emit(url, str(e))


class UIObserver:
    """Simulates a UI component observing download events."""

    def __init__(self, name: str):
        self.name = name

    def on_started(self, url: str):
        """Called when download starts."""
        logger.info(f"[{self.name}] Download started: {url}")

    def on_progress(self, url: str, progress: int):
        """Called on progress update."""
        if progress % 25 == 0:  # Only log every 25%
            logger.info(f"[{self.name}] Progress: {url} - {progress}%")

    def on_completed(self, url: str):
        """Called when download completes."""
        logger.info(f"[{self.name}] Download completed: {url}")

    def on_failed(self, url: str, error: str):
        """Called when download fails."""
        logger.warning(f"[{self.name}] Download failed: {url} - {error}")


class Logger Observer:
    """Simulates a logging component observing download events."""

    def log_started(self, url: str):
        logger.info(f"[Logger] STARTED: {url}")

    def log_completed(self, url: str):
        logger.info(f"[Logger] COMPLETED: {url}")


class WorkerThread:
    """
    Worker thread that performs tasks and emits signals.
    """

    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.task_started = Signal()
        self.task_progress = Signal()
        self.task_completed = Signal()
        self._stop_event = threading.Event()

    def run(self):
        """Main worker loop."""
        logger.info(f"Worker {self.worker_id} starting")

        for task_num in range(3):
            if self._stop_event.is_set():
                break

            task_id = f"W{self.worker_id}-T{task_num}"
            self.task_started.emit(task_id)

            # Simulate work
            for progress in range(0, 101, 20):
                if self._stop_event.is_set():
                    break
                time.sleep(0.2)
                self.task_progress.emit(task_id, progress)

            self.task_completed.emit(task_id)

        logger.info(f"Worker {self.worker_id} finished")

    def stop(self):
        """Request worker to stop."""
        self._stop_event.set()


def main():
    """Demonstrates application-level signals and slots."""
    logger.info("=== Example 11: Application Signals/Slots ===")

    # Example 1: Basic signal/slot usage
    logger.info("\n--- Example 1: Basic signal/slot ---")

    # Create a signal
    button_clicked = Signal()

    # Define slot functions
    def on_click():
        logger.info("Button was clicked!")

    def another_handler():
        logger.info("Another handler also received the click")

    # Connect slots to signal
    button_clicked.connect(on_click)
    button_clicked.connect(another_handler)

    # Emit the signal
    logger.info("Emitting button_clicked signal...")
    button_clicked.emit()

    # Example 2: Signals with arguments
    logger.info("\n--- Example 2: Signals with arguments ---")

    data_received = Signal()

    def handle_data(data: str, timestamp: float):
        logger.info(f"Received data: '{data}' at {timestamp:.2f}")

    data_received.connect(handle_data)
    data_received.emit("Hello, World!", time.time())

    # Example 3: Download manager with multiple observers
    logger.info("\n--- Example 3: Download manager (multiple observers) ---")

    dm = DownloadManager()

    # Create observers
    ui1 = UIObserver("MainUI")
    ui2 = UIObserver("StatusBar")
    log_obs = LoggerObserver()

    # Connect observers to signals
    dm.signals.started.connect(ui1.on_started)
    dm.signals.progress.connect(ui1.on_progress)
    dm.signals.completed.connect(ui1.on_completed)
    dm.signals.failed.connect(ui1.on_failed)

    dm.signals.started.connect(ui2.on_started)
    dm.signals.completed.connect(ui2.on_completed)

    dm.signals.started.connect(log_obs.log_started)
    dm.signals.completed.connect(log_obs.log_completed)

    # Perform downloads
    urls = ["http://example.com/file1.zip", "http://example.com/file2.zip"]
    for url in urls:
        dm.download(url)
        time.sleep(0.5)

    # Example 4: Threaded workers with signals
    logger.info("\n--- Example 4: Multi-threaded workers with signals ---")

    workers = []
    threads = []

    def on_task_started(task_id: str):
        logger.info(f"[Observer] Task started: {task_id}")

    def on_task_progress(task_id: str, progress: int):
        if progress % 50 == 0:
            logger.info(f"[Observer] Task {task_id} progress: {progress}%")

    def on_task_completed(task_id: str):
        logger.info(f"[Observer] Task completed: {task_id}")

    # Create workers
    for i in range(2):
        worker = WorkerThread(i)

        # Connect to worker signals
        worker.task_started.connect(on_task_started)
        worker.task_progress.connect(on_task_progress)
        worker.task_completed.connect(on_task_completed)

        workers.append(worker)

        # Start thread
        t = threading.Thread(target=worker.run, name=f"Worker-{i}")
        threads.append(t)
        t.start()

    # Wait for workers
    for t in threads:
        t.join()

    # Example 5: Disconnecting signals
    logger.info("\n--- Example 5: Disconnecting signals ---")

    signal = Signal()

    def handler1():
        logger.info("Handler 1 called")

    def handler2():
        logger.info("Handler 2 called")

    signal.connect(handler1)
    signal.connect(handler2)

    logger.info("Emitting with both handlers:")
    signal.emit()

    logger.info("Disconnecting handler1...")
    signal.disconnect(handler1)

    logger.info("Emitting with only handler2:")
    signal.emit()

    logger.info(f"Active slot count: {signal.slot_count}")

    logger.info("\n=== Example completed ===")


if __name__ == "__main__":
    main()
