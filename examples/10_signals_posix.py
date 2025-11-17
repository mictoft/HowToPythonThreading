#!/usr/bin/env python3
"""
Example 10: POSIX Signals and Threading

Demonstrates:
- How POSIX signals interact with Python threads
- Handling SIGINT (Ctrl+C) and SIGTERM gracefully
- Signal handlers always run in the main thread
- Using signals for shutdown coordination
- Platform differences (Unix vs Windows)

Key Concepts:
- Signal handlers are called in the main thread only
- signal.signal() registers a signal handler
- Common signals: SIGINT (Ctrl+C), SIGTERM (kill), SIGUSR1/2 (custom)
- Use threading.Event to communicate shutdown to worker threads
- Windows has limited signal support

Platform Note:
- Full signal support: Unix/Linux/macOS
- Limited support: Windows (SIGINT, SIGTERM only)
"""

import signal
import threading
import time
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)-12s] %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# Global shutdown event
shutdown_event = threading.Event()


def signal_handler(signum, frame):
    """
    Signal handler function (runs in main thread).

    Args:
        signum: Signal number
        frame: Current stack frame
    """
    signal_name = signal.Signals(signum).name
    logger.info(f"Received signal {signal_name} ({signum})")
    logger.info("Setting shutdown event...")
    shutdown_event.set()


def worker_loop(worker_id: int):
    """
    Worker thread that responds to shutdown signal.

    Args:
        worker_id: Worker identifier
    """
    logger.info(f"Worker {worker_id} starting")
    iteration = 0

    while not shutdown_event.is_set():
        iteration += 1
        logger.info(f"Worker {worker_id} iteration {iteration}")

        # Use wait() instead of sleep() for responsive shutdown
        if shutdown_event.wait(timeout=1.0):
            break

    logger.info(f"Worker {worker_id} shutting down gracefully (completed {iteration} iterations)")


def long_running_task(task_id: int):
    """
    Simulates a long-running task that checks for shutdown.

    Args:
        task_id: Task identifier
    """
    logger.info(f"Task {task_id} starting long operation...")

    for step in range(10):
        if shutdown_event.is_set():
            logger.info(f"Task {task_id} interrupted at step {step}")
            return

        logger.info(f"Task {task_id} step {step}/10")
        time.sleep(0.5)

    logger.info(f"Task {task_id} completed all steps")


def custom_signal_handler(signum, frame):
    """
    Handler for custom signals (Unix only).

    Args:
        signum: Signal number
        frame: Current stack frame
    """
    if sys.platform != 'win32':
        signal_name = signal.Signals(signum).name
        logger.info(f"Custom signal handler: received {signal_name}")
        logger.info(f"Current thread: {threading.current_thread().name}")
        logger.info(f"Active threads: {threading.active_count()}")


def main():
    """Demonstrates signal handling with threads."""
    logger.info("=== Example 10: POSIX Signals and Threading ===")
    logger.info(f"Platform: {sys.platform}")

    # Example 1: Basic signal handling
    logger.info("\n--- Example 1: Graceful shutdown with SIGINT ---")
    logger.info("Press Ctrl+C to trigger graceful shutdown")

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start worker threads
    workers = []
    for i in range(2):
        t = threading.Thread(
            target=worker_loop,
            args=(i,),
            name=f"Worker-{i}",
            daemon=False  # Non-daemon so they can shutdown gracefully
        )
        workers.append(t)
        t.start()

    logger.info("Workers started. Waiting for signal or timeout (10s)...")

    # Wait for shutdown event (from signal) or timeout
    shutdown_event.wait(timeout=10.0)

    if not shutdown_event.is_set():
        logger.info("Timeout reached, shutting down...")
        shutdown_event.set()

    # Wait for workers to complete
    for t in workers:
        t.join(timeout=5.0)

    logger.info("All workers stopped")

    # Example 2: Signal handling with long-running tasks
    logger.info("\n--- Example 2: Interrupting long-running tasks ---")
    shutdown_event.clear()  # Reset

    # Re-register handler
    signal.signal(signal.SIGINT, signal_handler)

    # Start tasks
    tasks = []
    for i in range(2):
        t = threading.Thread(
            target=long_running_task,
            args=(i,),
            name=f"Task-{i}"
        )
        tasks.append(t)
        t.start()

    logger.info("Tasks running. Press Ctrl+C to interrupt or wait 6s for completion...")

    # Wait for completion or shutdown
    for t in tasks:
        t.join(timeout=6.0)

    if not shutdown_event.is_set():
        logger.info("Tasks completed normally")
    else:
        logger.info("Tasks interrupted by signal")

    # Example 3: Custom signals (Unix only)
    if sys.platform != 'win32':
        logger.info("\n--- Example 3: Custom signals (Unix only) ---")
        logger.info("Run: kill -USR1 <pid> to send SIGUSR1 to this process")
        logger.info(f"Process ID: {threading.current_thread().ident}")

        # Register custom signal handler
        signal.signal(signal.SIGUSR1, custom_signal_handler)

        # Start a worker
        shutdown_event.clear()
        worker = threading.Thread(
            target=worker_loop,
            args=(99,),
            name="CustomSignalWorker"
        )
        worker.start()

        logger.info("Worker running for 5 seconds (send SIGUSR1 to test)...")
        time.sleep(5.0)

        shutdown_event.set()
        worker.join()
    else:
        logger.info("\n--- Example 3: Skipped (Windows has limited signal support) ---")

    # Example 4: Signal handler thread safety notes
    logger.info("\n--- Example 4: Signal handler best practices ---")
    logger.info("Key points:")
    logger.info("1. Signal handlers ALWAYS run in the main thread")
    logger.info("2. Keep signal handlers simple and fast")
    logger.info("3. Use threading.Event to communicate with worker threads")
    logger.info("4. Don't call complex functions from signal handlers")
    logger.info("5. Be aware of race conditions in signal handlers")

    # Restore default handlers
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)

    logger.info("\n=== Example completed ===")
    logger.info("Signal handlers restored to default")


if __name__ == "__main__":
    main()
