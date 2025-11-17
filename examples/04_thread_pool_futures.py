#!/usr/bin/env python3
"""
Example 04: Thread Pools and Futures

Demonstrates:
- Using concurrent.futures.ThreadPoolExecutor
- Submitting tasks and getting Future objects
- Waiting for futures (result(), as_completed())
- Exception handling in thread pools
- Context manager usage for automatic cleanup
- map() for batch processing

Key Concepts:
- ThreadPoolExecutor manages a pool of worker threads
- submit() returns a Future representing pending result
- Future.result() blocks until the task completes
- Exceptions in worker threads are re-raised when calling result()
- as_completed() yields futures as they finish (in completion order)
"""

import concurrent.futures
import time
import random
import logging
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)-12s] %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def compute_square(n: int) -> int:
    """
    Compute the square of a number (simulating some work).

    Args:
        n: Number to square

    Returns:
        n squared
    """
    logger.info(f"Computing square of {n}")
    time.sleep(random.uniform(0.1, 0.5))  # Simulate work
    result = n * n
    logger.info(f"Square of {n} = {result}")
    return result


def task_that_fails(n: int) -> int:
    """
    A task that raises an exception to demonstrate error handling.

    Args:
        n: Input value

    Returns:
        Never returns, always raises

    Raises:
        ValueError: Always
    """
    logger.info(f"Task {n} starting (will fail)")
    time.sleep(0.2)
    raise ValueError(f"Task {n} intentionally failed!")


def download_simulation(url: str) -> dict:
    """
    Simulates downloading data from a URL.

    Args:
        url: URL to "download"

    Returns:
        Dictionary with URL and simulated data
    """
    logger.info(f"Downloading: {url}")
    time.sleep(random.uniform(0.5, 1.5))  # Simulate network delay
    return {"url": url, "data": f"Content from {url}", "size": random.randint(100, 1000)}


def main():
    """Demonstrates thread pool executor and futures."""
    logger.info("=== Example 04: Thread Pool and Futures ===")

    # Example 1: Basic thread pool with submit()
    logger.info("\n--- Example 1: Basic ThreadPoolExecutor ---")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Submit tasks and get futures
        futures = []
        for i in range(5):
            future = executor.submit(compute_square, i)
            futures.append(future)

        logger.info("All tasks submitted")

        # Get results
        results = []
        for future in futures:
            result = future.result()  # Blocks until this future completes
            results.append(result)

        logger.info(f"Results: {results}")

    # Example 2: as_completed() - process results as they finish
    logger.info("\n--- Example 2: Processing results with as_completed() ---")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Submit tasks with varying completion times
        future_to_n = {}
        for i in range(5):
            future = executor.submit(compute_square, i)
            future_to_n[future] = i

        # Process results in completion order (not submission order)
        logger.info("Waiting for results in completion order...")
        for future in concurrent.futures.as_completed(future_to_n):
            n = future_to_n[future]
            try:
                result = future.result()
                logger.info(f"Got result for n={n}: {result}")
            except Exception as e:
                logger.error(f"Task for n={n} failed: {e}")

    # Example 3: Exception handling
    logger.info("\n--- Example 3: Exception handling in thread pools ---")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Submit mix of successful and failing tasks
        futures = []
        futures.append(executor.submit(compute_square, 5))
        futures.append(executor.submit(task_that_fails, 1))
        futures.append(executor.submit(compute_square, 7))
        futures.append(executor.submit(task_that_fails, 2))

        # Collect results, handling exceptions
        for i, future in enumerate(futures):
            try:
                result = future.result(timeout=5.0)
                logger.info(f"Task {i} succeeded: {result}")
            except ValueError as e:
                logger.warning(f"Task {i} failed with ValueError: {e}")
            except Exception as e:
                logger.error(f"Task {i} failed with unexpected error: {e}")

    # Example 4: map() for batch processing
    logger.info("\n--- Example 4: Using map() for batch processing ---")
    numbers = [1, 2, 3, 4, 5, 6]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # map() maintains order and returns results in submission order
        logger.info(f"Computing squares of {numbers}")
        results = list(executor.map(compute_square, numbers))
        logger.info(f"Results (in order): {results}")

    # Example 5: Simulating concurrent downloads
    logger.info("\n--- Example 5: Concurrent downloads simulation ---")
    urls = [
        "http://example.com/page1",
        "http://example.com/page2",
        "http://example.com/page3",
        "http://example.com/page4",
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all downloads
        future_to_url = {executor.submit(download_simulation, url): url for url in urls}

        # Process as they complete
        downloads = []
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                downloads.append(data)
                logger.info(f"Downloaded {data['size']} bytes from {url}")
            except Exception as e:
                logger.error(f"Failed to download {url}: {e}")

        logger.info(f"Downloaded {len(downloads)} URLs successfully")

    logger.info("\n=== Example completed ===")


if __name__ == "__main__":
    main()
