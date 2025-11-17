#!/usr/bin/env python3
"""
Example 14: Profiling and Debugging Threaded Code

Demonstrates:
- Using threading.enumerate() to list active threads
- Thread names for easier debugging
- sys._current_frames() for thread stack inspection
- faulthandler for debugging deadlocks
- traceback module for exception handling
- Performance profiling with cProfile
- GIL impact measurement

Key Concepts:
- Thread debugging is harder than single-threaded code
- Good logging with thread names is essential
- Stack traces help identify where threads are stuck
- The GIL can limit parallelism for CPU-bound tasks
- Profiling helps identify bottlenecks
"""

import threading
import time
import sys
import traceback
import logging
import faulthandler
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)-12s] %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def list_active_threads():
    """List all active threads with details."""
    logger.info("=== Active Threads ===")
    for thread in threading.enumerate():
        logger.info(f"  Thread: {thread.name}")
        logger.info(f"    - Ident: {thread.ident}")
        logger.info(f"    - Daemon: {thread.daemon}")
        logger.info(f"    - Alive: {thread.is_alive()}")
    logger.info(f"Total active threads: {threading.active_count()}")


def dump_thread_stacks():
    """Dump stack traces for all threads (useful for debugging hangs)."""
    logger.info("\n=== Thread Stack Traces ===")

    # Get frames for all threads
    frames = sys._current_frames()

    for thread_id, frame in frames.items():
        # Find thread name
        thread_name = "Unknown"
        for thread in threading.enumerate():
            if thread.ident == thread_id:
                thread_name = thread.name
                break

        logger.info(f"\nThread: {thread_name} (ID: {thread_id})")
        logger.info("Stack trace:")

        # Extract stack trace
        stack = traceback.extract_stack(frame)
        for filename, lineno, func_name, text in stack:
            logger.info(f"  File '{filename}', line {lineno}, in {func_name}")
            if text:
                logger.info(f"    {text.strip()}")


def worker_with_exception(worker_id: int):
    """
    Worker that raises an exception to demonstrate error handling.

    Args:
        worker_id: Worker identifier
    """
    logger.info(f"Worker {worker_id} starting")
    time.sleep(0.5)

    try:
        if worker_id == 2:
            raise ValueError(f"Worker {worker_id} intentionally failed!")

        logger.info(f"Worker {worker_id} completed successfully")

    except Exception as e:
        logger.error(f"Worker {worker_id} caught exception:")
        logger.error(traceback.format_exc())
        raise  # Re-raise for ThreadPoolExecutor


def busy_worker(worker_id: int, duration: float):
    """
    CPU-intensive worker (demonstrates GIL impact).

    Args:
        worker_id: Worker identifier
        duration: How long to work
    """
    logger.info(f"Busy worker {worker_id} starting")
    start = time.time()

    # CPU-intensive work
    count = 0
    while time.time() - start < duration:
        count += 1
        _ = sum(range(1000))  # Busy work

    logger.info(f"Busy worker {worker_id} finished ({count} iterations)")


def measure_gil_impact():
    """
    Measure GIL impact by comparing single-threaded vs multi-threaded performance.
    For CPU-bound tasks, threads may not provide speedup due to GIL.
    """
    logger.info("\n=== GIL Impact Measurement ===")

    duration = 1.0

    # Single thread
    logger.info("Running single-threaded...")
    start = time.time()
    busy_worker(0, duration)
    single_thread_time = time.time() - start
    logger.info(f"Single thread time: {single_thread_time:.2f}s")

    # Multiple threads
    logger.info("\nRunning multi-threaded (2 threads)...")
    start = time.time()

    threads = []
    for i in range(2):
        t = threading.Thread(target=busy_worker, args=(i, duration))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    multi_thread_time = time.time() - start
    logger.info(f"Multi-threaded time: {multi_thread_time:.2f}s")

    speedup = single_thread_time / multi_thread_time
    logger.info(f"\nSpeedup factor: {speedup:.2f}x")

    if speedup < 1.5:
        logger.warning("Limited speedup due to GIL (expected for CPU-bound tasks)")
    else:
        logger.info("Good speedup achieved")


def debugging_worker(worker_id: int, lock: threading.Lock, event: threading.Event):
    """
    Worker for demonstrating debugging techniques.

    Args:
        worker_id: Worker identifier
        lock: Shared lock
        event: Synchronization event
    """
    logger.info(f"Debug worker {worker_id} starting")

    with lock:
        logger.info(f"Debug worker {worker_id} acquired lock")
        time.sleep(0.5)

    # Wait for event
    logger.info(f"Debug worker {worker_id} waiting for event...")
    event.wait(timeout=2.0)

    logger.info(f"Debug worker {worker_id} finishing")


def main():
    """Demonstrates profiling and debugging techniques."""
    logger.info("=== Example 14: Profiling and Debugging ===")

    # Example 1: List active threads
    logger.info("\n--- Example 1: Listing active threads ---")
    list_active_threads()

    # Example 2: Thread naming for easier debugging
    logger.info("\n--- Example 2: Thread naming ---")

    threads = []
    for i in range(3):
        t = threading.Thread(
            target=lambda tid: (time.sleep(0.5), logger.info(f"Thread {tid} done")),
            args=(i,),
            name=f"NamedWorker-{i}"  # Descriptive names!
        )
        threads.append(t)
        t.start()

    time.sleep(0.2)
    list_active_threads()

    for t in threads:
        t.join()

    # Example 3: Exception handling in threads
    logger.info("\n--- Example 3: Exception handling ---")

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for i in range(4):
            future = executor.submit(worker_with_exception, i)
            futures.append(future)

        # Collect results and handle exceptions
        for i, future in enumerate(futures):
            try:
                future.result()
                logger.info(f"Future {i} completed successfully")
            except Exception as e:
                logger.error(f"Future {i} failed: {e}")

    # Example 4: Dump thread stacks
    logger.info("\n--- Example 4: Thread stack dumps ---")

    lock = threading.Lock()
    event = threading.Event()

    debug_threads = []
    for i in range(2):
        t = threading.Thread(
            target=debugging_worker,
            args=(i, lock, event),
            name=f"DebugWorker-{i}"
        )
        debug_threads.append(t)
        t.start()

    time.sleep(0.8)  # Let them get into various states
    dump_thread_stacks()

    event.set()  # Release waiters
    for t in debug_threads:
        t.join()

    # Example 5: Using faulthandler for deadlock debugging
    logger.info("\n--- Example 5: Faulthandler for debugging ---")
    logger.info("Enabling faulthandler...")
    faulthandler.enable()

    logger.info("Faulthandler can dump tracebacks on:")
    logger.info("  - Segmentation faults")
    logger.info("  - SIGABRT, SIGFPE, SIGILL, etc.")
    logger.info("  - Timeout (using faulthandler.dump_traceback_later())")

    # Set up timeout-based dump
    logger.info("Setting up timeout dump (will dump if hung for >30s)...")
    faulthandler.dump_traceback_later(30, repeat=False)

    # Cancel it immediately for this example
    faulthandler.cancel_dump_traceback_later()
    logger.info("(Cancelled for this example)")

    # Example 6: GIL impact measurement
    logger.info("\n--- Example 6: GIL impact on CPU-bound tasks ---")
    measure_gil_impact()

    # Example 7: Best practices summary
    logger.info("\n--- Example 7: Debugging best practices ---")
    logger.info("1. Always name your threads descriptively")
    logger.info("2. Use logging with thread names in format string")
    logger.info("3. Handle exceptions in worker threads (they don't propagate)")
    logger.info("4. Use threading.enumerate() to check thread state")
    logger.info("5. Use sys._current_frames() to dump stacks when debugging hangs")
    logger.info("6. Enable faulthandler in production for crash debugging")
    logger.info("7. Profile CPU-bound code; consider multiprocessing if GIL is issue")
    logger.info("8. Use ThreadPoolExecutor for easier exception handling")
    logger.info("9. Test with different thread counts and timing")
    logger.info("10. Use race condition detectors (ThreadSanitizer, helgrind)")

    # Example 8: Thread information
    logger.info("\n--- Example 8: Main thread information ---")
    main_thread = threading.main_thread()
    current_thread = threading.current_thread()

    logger.info(f"Main thread: {main_thread.name}")
    logger.info(f"Current thread: {current_thread.name}")
    logger.info(f"Is main thread? {current_thread is main_thread}")

    logger.info("\n=== Example completed ===")


if __name__ == "__main__":
    main()
