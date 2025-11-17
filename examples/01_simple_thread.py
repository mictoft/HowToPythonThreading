#!/usr/bin/env python3
"""
Example 01: Simple Thread Creation

Demonstrates:
- Creating and starting threads using threading.Thread
- Passing arguments to thread functions
- Joining threads (waiting for completion)
- Daemon vs non-daemon threads
- Thread naming for debugging

Key Concepts:
- A thread executes a target function in parallel with the main thread
- join() blocks until the thread completes
- Daemon threads are terminated when the main program exits
- Non-daemon threads keep the program alive until they complete
"""

import threading
import time
import logging

# Configure logging to show thread names
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)-12s] %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def worker_task(task_id: int, duration: float) -> None:
    """
    A simple worker function that simulates work.

    Args:
        task_id: Identifier for this task
        duration: How long to "work" (in seconds)
    """
    logger.info(f"Task {task_id} starting, will run for {duration}s")
    time.sleep(duration)
    logger.info(f"Task {task_id} completed")


def daemon_task() -> None:
    """
    A daemon thread that runs indefinitely.
    This will be terminated when the main program exits.
    """
    logger.info("Daemon task starting (runs forever)")
    count = 0
    try:
        while True:
            time.sleep(0.5)
            count += 1
            if count % 4 == 0:  # Log every 2 seconds
                logger.info(f"Daemon task still running... (iteration {count})")
    except Exception as e:
        logger.error(f"Daemon task interrupted: {e}")


def main():
    """Demonstrates basic thread creation and management."""
    logger.info("=== Example 01: Simple Thread Creation ===")

    # Example 1: Create and start a basic thread
    logger.info("\n--- Example 1: Basic thread with join() ---")
    thread1 = threading.Thread(target=worker_task, args=(1, 1.0))
    thread1.start()
    logger.info("Thread 1 started, main thread continues...")
    thread1.join()  # Wait for thread to complete
    logger.info("Thread 1 joined (completed)")

    # Example 2: Multiple threads with custom names
    logger.info("\n--- Example 2: Multiple threads with custom names ---")
    threads = []
    for i in range(3):
        t = threading.Thread(
            target=worker_task,
            args=(i + 2, 0.5),
            name=f"Worker-{i + 2}"  # Custom thread name for easier debugging
        )
        threads.append(t)
        t.start()

    logger.info("All threads started, waiting for completion...")
    for t in threads:
        t.join()
    logger.info("All worker threads completed")

    # Example 3: Daemon thread
    logger.info("\n--- Example 3: Daemon thread ---")
    daemon_thread = threading.Thread(target=daemon_task, daemon=True)
    daemon_thread.start()

    # Create a short-lived non-daemon thread
    regular_thread = threading.Thread(target=worker_task, args=(99, 2.0))
    regular_thread.start()

    logger.info("Daemon thread is running in background...")
    logger.info("Waiting for regular thread to complete...")
    regular_thread.join()

    logger.info("\n--- Main thread exiting ---")
    logger.info("Daemon thread will be terminated automatically")
    logger.info("(Notice the daemon thread doesn't get to finish)")

    # Give a moment to see daemon thread running
    time.sleep(0.5)


if __name__ == "__main__":
    main()
