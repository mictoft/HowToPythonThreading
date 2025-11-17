#!/usr/bin/env python3
"""
Example 06: Semaphores, Conditions, and Barriers

Demonstrates:
- Semaphore for limiting concurrent access
- BoundedSemaphore (prevents releasing too many times)
- Condition for wait/notify patterns
- Barrier for synchronizing multiple threads at a checkpoint

Key Concepts:
- Semaphore: Counter-based synchronization (limits N concurrent accesses)
- Condition: Wait for specific condition, notify when it becomes true
- Barrier: Wait for N threads to reach a point before all continue together
"""

import threading
import time
import random
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)-12s] %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def limited_resource_worker(worker_id: int, semaphore: threading.Semaphore):
    """
    Worker that uses a limited resource protected by a semaphore.

    Args:
        worker_id: Worker identifier
        semaphore: Semaphore limiting concurrent access
    """
    logger.info(f"Worker {worker_id} waiting for resource...")

    with semaphore:
        logger.info(f"Worker {worker_id} acquired resource")
        # Simulate work with the resource
        time.sleep(random.uniform(0.5, 1.5))
        logger.info(f"Worker {worker_id} releasing resource")


class DataBuffer:
    """
    A buffer that uses Condition for producer-consumer coordination.

    This demonstrates wait/notify patterns.
    """

    def __init__(self, max_size: int = 5):
        self.buffer = []
        self.max_size = max_size
        self.condition = threading.Condition()

    def produce(self, item):
        """Add item to buffer, waiting if full."""
        with self.condition:
            # Wait while buffer is full
            while len(self.buffer) >= self.max_size:
                logger.info(f"Buffer full, producer waiting...")
                self.condition.wait()

            self.buffer.append(item)
            logger.info(f"Produced: {item} (buffer size: {len(self.buffer)})")

            # Notify waiting consumers
            self.condition.notify()

    def consume(self):
        """Remove and return item from buffer, waiting if empty."""
        with self.condition:
            # Wait while buffer is empty
            while len(self.buffer) == 0:
                logger.info(f"Buffer empty, consumer waiting...")
                self.condition.wait()

            item = self.buffer.pop(0)
            logger.info(f"Consumed: {item} (buffer size: {len(self.buffer)})")

            # Notify waiting producers
            self.condition.notify()

            return item


def producer_cond(buffer: DataBuffer, count: int):
    """Produce items into the buffer."""
    for i in range(count):
        time.sleep(random.uniform(0.1, 0.3))
        buffer.produce(f"Item-{i}")


def consumer_cond(buffer: DataBuffer, count: int):
    """Consume items from the buffer."""
    for _ in range(count):
        time.sleep(random.uniform(0.2, 0.6))
        buffer.consume()


def barrier_worker(worker_id: int, barrier: threading.Barrier):
    """
    Worker that performs work in phases, synchronized by a barrier.

    Args:
        worker_id: Worker identifier
        barrier: Barrier to synchronize with other workers
    """
    logger.info(f"Worker {worker_id} starting phase 1")
    time.sleep(random.uniform(0.5, 1.5))  # Simulate work
    logger.info(f"Worker {worker_id} finished phase 1, waiting at barrier...")

    # Wait for all threads to reach this point
    barrier.wait()

    logger.info(f"Worker {worker_id} starting phase 2 (all threads synchronized)")
    time.sleep(random.uniform(0.3, 0.8))  # Simulate work
    logger.info(f"Worker {worker_id} finished phase 2")


def main():
    """Demonstrates semaphores, conditions, and barriers."""
    logger.info("=== Example 06: Semaphores, Conditions, Barriers ===")

    # Example 1: Semaphore - limit concurrent access to resources
    logger.info("\n--- Example 1: Semaphore (max 2 concurrent workers) ---")
    semaphore = threading.Semaphore(2)  # Only 2 threads can access at once

    workers = []
    for i in range(5):
        t = threading.Thread(
            target=limited_resource_worker,
            args=(i, semaphore),
            name=f"Worker-{i}"
        )
        workers.append(t)
        t.start()

    for t in workers:
        t.join()

    logger.info("All workers completed")

    # Example 2: BoundedSemaphore - prevents releasing too many times
    logger.info("\n--- Example 2: BoundedSemaphore ---")
    bounded_sem = threading.BoundedSemaphore(2)

    bounded_sem.acquire()
    logger.info("Acquired once")
    bounded_sem.release()
    logger.info("Released once")

    # This would raise ValueError with BoundedSemaphore:
    try:
        bounded_sem.release()
        bounded_sem.release()
        bounded_sem.release()  # Too many releases!
    except ValueError as e:
        logger.warning(f"BoundedSemaphore prevented over-release: {e}")

    # Example 3: Condition variable for producer-consumer
    logger.info("\n--- Example 3: Condition variable (producer-consumer) ---")
    buffer = DataBuffer(max_size=3)

    # Start producer and consumer
    prod = threading.Thread(target=producer_cond, args=(buffer, 6), name="Producer")
    cons = threading.Thread(target=consumer_cond, args=(buffer, 6), name="Consumer")

    prod.start()
    cons.start()

    prod.join()
    cons.join()

    logger.info("Producer-consumer completed")

    # Example 4: Barrier for phase synchronization
    logger.info("\n--- Example 4: Barrier (synchronize 3 threads) ---")
    num_threads = 3
    barrier = threading.Barrier(num_threads)

    threads = []
    for i in range(num_threads):
        t = threading.Thread(
            target=barrier_worker,
            args=(i, barrier),
            name=f"BarrierWorker-{i}"
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    logger.info("All barrier workers completed")

    # Example 5: Barrier with action callback
    logger.info("\n--- Example 5: Barrier with action callback ---")

    def barrier_action():
        """Called when all threads reach the barrier."""
        logger.info("*** BARRIER ACTION: All threads synchronized! ***")

    barrier_with_action = threading.Barrier(3, action=barrier_action)

    threads = []
    for i in range(3):
        t = threading.Thread(target=lambda tid: (
            time.sleep(random.uniform(0.2, 0.8)),
            logger.info(f"Thread {tid} at barrier"),
            barrier_with_action.wait()
        ), args=(i,), name=f"Thread-{i}")
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    logger.info("\n=== Example completed ===")


if __name__ == "__main__":
    main()
