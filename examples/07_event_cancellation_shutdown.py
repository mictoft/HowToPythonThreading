#!/usr/bin/env python3
"""
Example 07: Event, Cancellation, and Shutdown

Demonstrates:
- Using threading.Event for signaling between threads
- Cooperative cancellation pattern
- Graceful shutdown of worker threads
- Timeout-based waiting
- Using Events as simple on/off flags

Key Concepts:
- Event is a simple boolean flag shared between threads
- wait() blocks until event is set
- set() wakes up all waiting threads
- clear() resets the event to unset state
- Events are perfect for cancellation signals
"""

import threading
import time
import logging
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)-12s] %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def worker_with_cancellation(worker_id: int, stop_event: threading.Event):
    """
    Worker that can be cancelled via an Event.

    Args:
        worker_id: Worker identifier
        stop_event: Event to signal cancellation
    """
    logger.info(f"Worker {worker_id} starting")
    iteration = 0

    while not stop_event.is_set():
        # Do work
        iteration += 1
        logger.info(f"Worker {worker_id} iteration {iteration}")
        time.sleep(0.5)

        # Check for cancellation periodically
        if iteration >= 10:  # Safety limit
            break

    logger.info(f"Worker {worker_id} shutting down (completed {iteration} iterations)")


def waiter_thread(ready_event: threading.Event, thread_id: int):
    """
    Thread that waits for an event to be set.

    Args:
        ready_event: Event to wait for
        thread_id: Thread identifier
    """
    logger.info(f"Waiter {thread_id} waiting for signal...")
    ready_event.wait()  # Block until event is set
    logger.info(f"Waiter {thread_id} received signal, proceeding!")
    time.sleep(0.2)
    logger.info(f"Waiter {thread_id} completed")


def waiter_with_timeout(ready_event: threading.Event, thread_id: int, timeout: float):
    """
    Thread that waits for an event with a timeout.

    Args:
        ready_event: Event to wait for
        thread_id: Thread identifier
        timeout: Maximum time to wait
    """
    logger.info(f"Waiter {thread_id} waiting (timeout={timeout}s)...")
    signaled = ready_event.wait(timeout=timeout)

    if signaled:
        logger.info(f"Waiter {thread_id} received signal!")
    else:
        logger.warning(f"Waiter {thread_id} timed out!")


class WorkerPool:
    """
    A pool of worker threads with graceful shutdown capability.
    """

    def __init__(self, num_workers: int):
        self.num_workers = num_workers
        self.stop_event = threading.Event()
        self.workers: List[threading.Thread] = []

    def _worker_loop(self, worker_id: int):
        """Main loop for worker thread."""
        logger.info(f"WorkerPool worker {worker_id} started")

        while not self.stop_event.is_set():
            # Simulate work
            logger.debug(f"Worker {worker_id} working...")
            # Use wait with timeout instead of sleep for responsive shutdown
            if self.stop_event.wait(timeout=0.5):
                break  # Stop event was set

        logger.info(f"WorkerPool worker {worker_id} stopped")

    def start(self):
        """Start all worker threads."""
        logger.info(f"Starting {self.num_workers} workers")
        for i in range(self.num_workers):
            t = threading.Thread(
                target=self._worker_loop,
                args=(i,),
                name=f"PoolWorker-{i}"
            )
            t.start()
            self.workers.append(t)

    def shutdown(self, timeout: float = 5.0):
        """
        Gracefully shutdown all workers.

        Args:
            timeout: Maximum time to wait for workers to finish
        """
        logger.info("Shutting down worker pool...")
        self.stop_event.set()  # Signal all workers to stop

        # Wait for all workers with timeout
        for t in self.workers:
            t.join(timeout=timeout)
            if t.is_alive():
                logger.warning(f"Worker {t.name} did not stop in time!")

        logger.info("Worker pool shutdown complete")


def main():
    """Demonstrates events for cancellation and shutdown."""
    logger.info("=== Example 07: Event, Cancellation, Shutdown ===")

    # Example 1: Basic Event usage
    logger.info("\n--- Example 1: Basic Event signaling ---")
    ready = threading.Event()

    # Start waiters
    waiters = []
    for i in range(3):
        t = threading.Thread(target=waiter_thread, args=(ready, i), name=f"Waiter-{i}")
        t.start()
        waiters.append(t)

    time.sleep(1.0)
    logger.info("Setting event (releasing all waiters)...")
    ready.set()  # Wake up all waiting threads

    for t in waiters:
        t.join()

    logger.info("All waiters completed")

    # Example 2: Event with timeout
    logger.info("\n--- Example 2: Event with timeout ---")
    signal = threading.Event()

    # Waiter with short timeout (will timeout)
    t1 = threading.Thread(
        target=waiter_with_timeout,
        args=(signal, 1, 0.5),
        name="Waiter-Timeout"
    )

    # Waiter with long timeout (will be signaled)
    t2 = threading.Thread(
        target=waiter_with_timeout,
        args=(signal, 2, 3.0),
        name="Waiter-Signal"
    )

    t1.start()
    t2.start()

    time.sleep(1.0)  # Wait past first timeout
    logger.info("Setting event...")
    signal.set()

    t1.join()
    t2.join()

    # Example 3: Cooperative cancellation
    logger.info("\n--- Example 3: Cooperative cancellation ---")
    stop_event = threading.Event()

    workers = []
    for i in range(2):
        t = threading.Thread(
            target=worker_with_cancellation,
            args=(i, stop_event),
            name=f"Worker-{i}"
        )
        t.start()
        workers.append(t)

    # Let workers run for a bit
    time.sleep(2.0)

    logger.info("Requesting workers to stop...")
    stop_event.set()

    for t in workers:
        t.join()

    logger.info("All workers stopped")

    # Example 4: Worker pool with graceful shutdown
    logger.info("\n--- Example 4: Worker pool shutdown ---")
    pool = WorkerPool(num_workers=3)
    pool.start()

    time.sleep(2.0)

    pool.shutdown()

    # Example 5: Event state checks
    logger.info("\n--- Example 5: Event state checking ---")
    event = threading.Event()

    logger.info(f"Event is_set: {event.is_set()}")  # False
    event.set()
    logger.info(f"After set(), is_set: {event.is_set()}")  # True
    event.clear()
    logger.info(f"After clear(), is_set: {event.is_set()}")  # False

    logger.info("\n=== Example completed ===")


if __name__ == "__main__":
    main()
