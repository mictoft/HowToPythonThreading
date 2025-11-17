#!/usr/bin/env python3
"""
Example 03: Producer-Consumer Pattern with Queue

Demonstrates:
- Thread-safe communication using queue.Queue
- Producer-consumer pattern
- Multiple producers and consumers
- Queue blocking behavior (get/put with timeout)
- Graceful shutdown with sentinel values
- Queue size limits and backpressure

Key Concepts:
- Queue is thread-safe (no manual locking needed)
- Producers add items, consumers remove items
- Queue.get() blocks if queue is empty
- Queue.put() blocks if queue is full (when maxsize is set)
- Use sentinel values (like None) to signal shutdown
"""

import threading
import queue
import time
import random
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)-12s] %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def producer(task_queue: queue.Queue, producer_id: int, num_items: int, stop_event: threading.Event) -> None:
    """
    Producer function that adds work items to the queue.

    Args:
        task_queue: Queue to put items into
        producer_id: ID of this producer
        num_items: Number of items to produce
        stop_event: Event to signal early termination
    """
    logger.info(f"Producer {producer_id} starting")

    for i in range(num_items):
        if stop_event.is_set():
            logger.info(f"Producer {producer_id} stopping early")
            break

        # Simulate work to create the item
        time.sleep(random.uniform(0.1, 0.3))

        item = f"P{producer_id}-Item{i}"
        task_queue.put(item)
        logger.info(f"Producer {producer_id} produced: {item} (queue size: {task_queue.qsize()})")

    logger.info(f"Producer {producer_id} finished")


def consumer(task_queue: queue.Queue, consumer_id: int, stop_event: threading.Event) -> None:
    """
    Consumer function that processes items from the queue.

    Args:
        task_queue: Queue to get items from
        consumer_id: ID of this consumer
        stop_event: Event to signal shutdown
    """
    logger.info(f"Consumer {consumer_id} starting")
    processed_count = 0

    while not stop_event.is_set():
        try:
            # Use timeout so we can check stop_event periodically
            item = task_queue.get(timeout=0.5)

            # Check for sentinel value (None means shutdown)
            if item is None:
                logger.info(f"Consumer {consumer_id} received shutdown signal")
                task_queue.task_done()
                break

            # Process the item
            logger.info(f"Consumer {consumer_id} processing: {item}")
            time.sleep(random.uniform(0.2, 0.5))  # Simulate work
            processed_count += 1

            task_queue.task_done()  # Mark item as processed

        except queue.Empty:
            # Queue is empty, continue checking
            continue

    logger.info(f"Consumer {consumer_id} finished (processed {processed_count} items)")


def main():
    """Demonstrates producer-consumer pattern with queues."""
    logger.info("=== Example 03: Producer-Consumer Pattern ===")

    # Example 1: Basic producer-consumer
    logger.info("\n--- Example 1: Single producer, single consumer ---")
    task_queue = queue.Queue(maxsize=5)  # Limited queue size
    stop_event = threading.Event()

    # Start one producer and one consumer
    prod_thread = threading.Thread(
        target=producer,
        args=(task_queue, 1, 5, stop_event),
        name="Producer-1"
    )
    cons_thread = threading.Thread(
        target=consumer,
        args=(task_queue, 1, stop_event),
        name="Consumer-1"
    )

    prod_thread.start()
    cons_thread.start()

    # Wait for producer to finish
    prod_thread.join()

    # Send shutdown signal to consumer
    task_queue.put(None)

    # Wait for consumer to finish
    cons_thread.join()

    logger.info("Single producer-consumer example completed")

    # Example 2: Multiple producers and consumers
    logger.info("\n--- Example 2: Multiple producers and consumers ---")
    task_queue2 = queue.Queue(maxsize=10)
    stop_event2 = threading.Event()

    num_producers = 2
    num_consumers = 3
    items_per_producer = 4

    # Start producers
    producers = []
    for i in range(num_producers):
        t = threading.Thread(
            target=producer,
            args=(task_queue2, i, items_per_producer, stop_event2),
            name=f"Producer-{i}"
        )
        t.start()
        producers.append(t)

    # Start consumers
    consumers = []
    for i in range(num_consumers):
        t = threading.Thread(
            target=consumer,
            args=(task_queue2, i, stop_event2),
            name=f"Consumer-{i}"
        )
        t.start()
        consumers.append(t)

    # Wait for all producers to finish
    for t in producers:
        t.join()

    logger.info("All producers finished")

    # Send shutdown signals to all consumers (one per consumer)
    for _ in range(num_consumers):
        task_queue2.put(None)

    # Wait for all consumers to finish
    for t in consumers:
        t.join()

    logger.info("All consumers finished")

    # Verify queue is empty
    logger.info(f"Final queue size: {task_queue2.qsize()}")

    # Example 3: Demonstrate queue full behavior
    logger.info("\n--- Example 3: Queue backpressure (put blocking) ---")
    small_queue = queue.Queue(maxsize=2)
    logger.info("Created queue with maxsize=2")

    # Fill the queue
    small_queue.put("Item1")
    small_queue.put("Item2")
    logger.info("Queue is now full (2/2 items)")

    # Try to put with timeout
    logger.info("Attempting to put another item (will block with timeout)...")
    try:
        small_queue.put("Item3", timeout=1.0)
        logger.info("Item added (queue had space)")
    except queue.Full:
        logger.info("Queue.Full exception raised (queue was full, timeout expired)")

    logger.info("\n=== Example completed ===")


if __name__ == "__main__":
    main()
