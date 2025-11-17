#!/usr/bin/env python3
"""
Example 13: Threading and Asyncio Interoperability

Demonstrates:
- Running asyncio in a separate thread
- Calling async functions from sync code
- Calling sync functions from async code
- Using asyncio.run_in_executor for blocking operations
- Using asyncio.run_coroutine_threadsafe for thread-to-async communication
- Best practices for mixing threading and asyncio

Key Concepts:
- Asyncio runs in a single thread with an event loop
- Thread pool executor can run sync code from async context
- run_coroutine_threadsafe() schedules coroutines from other threads
- Each thread should have at most one event loop
- Use asyncio for I/O-bound tasks, threads for CPU-bound or blocking operations
"""

import asyncio
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)-12s] %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# Example 1: Run asyncio in a separate thread
class AsyncioThread:
    """Runs an asyncio event loop in a dedicated thread."""

    def __init__(self):
        self.loop = None
        self.thread = None

    def start(self):
        """Start the event loop in a new thread."""
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

        # Wait for loop to be initialized
        while self.loop is None:
            time.sleep(0.01)

        logger.info("Asyncio event loop started in separate thread")

    def _run_loop(self):
        """Run the event loop (runs in thread)."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        logger.info("Event loop running")
        self.loop.run_forever()

    def run_coroutine(self, coro):
        """
        Schedule a coroutine to run in the event loop (thread-safe).

        Args:
            coro: Coroutine to run

        Returns:
            Future object
        """
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self):
        """Stop the event loop and thread."""
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join(timeout=5.0)
            logger.info("Asyncio event loop stopped")


# Example async functions
async def async_fetch_data(url: str, delay: float) -> dict:
    """
    Simulate fetching data asynchronously.

    Args:
        url: URL to fetch
        delay: Simulated network delay

    Returns:
        Dictionary with results
    """
    logger.info(f"Async fetching: {url}")
    await asyncio.sleep(delay)
    logger.info(f"Async fetch complete: {url}")
    return {"url": url, "data": f"Content from {url}"}


async def async_process_multiple_urls(urls: list) -> list:
    """
    Process multiple URLs concurrently using asyncio.

    Args:
        urls: List of URLs

    Returns:
        List of results
    """
    logger.info(f"Processing {len(urls)} URLs concurrently")
    tasks = [async_fetch_data(url, 0.5) for url in urls]
    results = await asyncio.gather(*tasks)
    logger.info("All URLs processed")
    return results


# Blocking/CPU-bound function
def blocking_operation(n: int) -> int:
    """
    A blocking CPU-bound operation.

    Args:
        n: Input number

    Returns:
        Result
    """
    logger.info(f"Blocking operation starting with n={n}")
    time.sleep(1.0)  # Simulate blocking work
    result = n * n
    logger.info(f"Blocking operation complete: {result}")
    return result


async def async_with_blocking_calls():
    """
    Async function that needs to call blocking operations.
    Uses run_in_executor to avoid blocking the event loop.
    """
    logger.info("Async function calling blocking operations")

    loop = asyncio.get_event_loop()

    # Run blocking operations in thread pool
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Schedule multiple blocking operations
        futures = [
            loop.run_in_executor(executor, blocking_operation, i)
            for i in range(3)
        ]

        # Wait for all to complete
        results = await asyncio.gather(*futures)
        logger.info(f"All blocking operations complete: {results}")

    return results


def sync_function_calling_async():
    """
    Synchronous function that needs to call async functions.
    Uses asyncio.run() to execute async code.
    """
    logger.info("Sync function calling async code")

    urls = [
        "http://example.com/page1",
        "http://example.com/page2",
        "http://example.com/page3",
    ]

    # Run async code from sync context
    results = asyncio.run(async_process_multiple_urls(urls))
    logger.info(f"Got {len(results)} results")

    return results


def thread_worker_calling_async(asyncio_thread: AsyncioThread, worker_id: int):
    """
    Thread worker that schedules async tasks.

    Args:
        asyncio_thread: AsyncioThread instance
        worker_id: Worker ID
    """
    logger.info(f"Thread worker {worker_id} starting")

    # Schedule async work from this thread
    future = asyncio_thread.run_coroutine(
        async_fetch_data(f"http://worker{worker_id}.com/data", 0.5)
    )

    # Wait for result
    result = future.result(timeout=5.0)
    logger.info(f"Thread worker {worker_id} got result: {result}")


async def monitor_queue(queue: asyncio.Queue):
    """
    Monitor an async queue.

    Args:
        queue: Asyncio queue to monitor
    """
    logger.info("Queue monitor starting")

    for _ in range(5):
        item = await queue.get()
        logger.info(f"Queue monitor received: {item}")
        queue.task_done()

    logger.info("Queue monitor finished")


async def queue_producer(queue: asyncio.Queue):
    """
    Produce items into async queue.

    Args:
        queue: Asyncio queue
    """
    logger.info("Queue producer starting")

    for i in range(5):
        await asyncio.sleep(0.2)
        await queue.put(f"Item-{i}")
        logger.info(f"Produced: Item-{i}")

    logger.info("Queue producer finished")


def main():
    """Demonstrates threading and asyncio interoperability."""
    logger.info("=== Example 13: Threading and Asyncio ===")

    # Example 1: Sync calling async
    logger.info("\n--- Example 1: Sync function calling async ---")
    sync_function_calling_async()

    # Example 2: Async calling blocking/sync code
    logger.info("\n--- Example 2: Async calling blocking operations ---")
    asyncio.run(async_with_blocking_calls())

    # Example 3: Running asyncio in a dedicated thread
    logger.info("\n--- Example 3: Asyncio in separate thread ---")
    asyncio_thread = AsyncioThread()
    asyncio_thread.start()

    # Schedule async work from main thread
    future1 = asyncio_thread.run_coroutine(
        async_fetch_data("http://main-thread.com/data", 0.3)
    )
    result1 = future1.result(timeout=5.0)
    logger.info(f"Main thread got result: {result1}")

    # Start multiple threads that schedule async work
    threads = []
    for i in range(3):
        t = threading.Thread(
            target=thread_worker_calling_async,
            args=(asyncio_thread, i),
            name=f"ThreadWorker-{i}"
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    asyncio_thread.stop()

    # Example 4: Asyncio queue with multiple coroutines
    logger.info("\n--- Example 4: Asyncio queue ---")

    async def queue_demo():
        queue = asyncio.Queue(maxsize=3)

        # Start monitor and producer concurrently
        await asyncio.gather(
            monitor_queue(queue),
            queue_producer(queue)
        )

    asyncio.run(queue_demo())

    # Example 5: When to use threads vs asyncio
    logger.info("\n--- Example 5: Best practices ---")
    logger.info("Use ASYNCIO for:")
    logger.info("  - I/O-bound operations (network, file I/O)")
    logger.info("  - High concurrency with many connections")
    logger.info("  - Cooperative multitasking")
    logger.info("\nUse THREADS for:")
    logger.info("  - CPU-bound operations")
    logger.info("  - Blocking operations that can't be made async")
    logger.info("  - Interfacing with blocking libraries")
    logger.info("\nCombine BOTH when:")
    logger.info("  - Async app needs to call blocking code (run_in_executor)")
    logger.info("  - Need multiple event loops")
    logger.info("  - Bridging sync and async worlds")

    logger.info("\n=== Example completed ===")


if __name__ == "__main__":
    main()
