#!/usr/bin/env python3
"""
Example 08: Thread-Local Storage

Demonstrates:
- Using threading.local() for thread-specific data
- Why thread-local storage is useful
- Database connections per thread
- Request context in web servers
- Avoiding global state issues

Key Concepts:
- threading.local() creates an object with thread-specific attributes
- Each thread sees its own values for attributes on the local object
- Useful for per-thread resources (DB connections, sessions, etc.)
- Avoids passing context through every function call
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


# Global thread-local storage
thread_local = threading.local()


class DatabaseConnection:
    """Simulates a database connection."""

    _connection_count = 0
    _lock = threading.Lock()

    def __init__(self, thread_id: int):
        with DatabaseConnection._lock:
            DatabaseConnection._connection_count += 1
            self.connection_id = DatabaseConnection._connection_count

        self.thread_id = thread_id
        logger.info(f"Created DB connection #{self.connection_id} for thread {thread_id}")

    def query(self, sql: str) -> str:
        """Simulate a database query."""
        logger.info(f"Connection #{self.connection_id} executing: {sql}")
        time.sleep(random.uniform(0.1, 0.3))
        return f"Result from connection #{self.connection_id}"

    def close(self):
        """Close the connection."""
        logger.info(f"Closing DB connection #{self.connection_id}")


def get_db_connection():
    """
    Get a database connection for the current thread.
    Creates one if it doesn't exist (lazy initialization).
    """
    if not hasattr(thread_local, 'db_connection'):
        thread_id = threading.current_thread().name
        thread_local.db_connection = DatabaseConnection(thread_id)

    return thread_local.db_connection


def worker_with_db(worker_id: int, num_queries: int):
    """
    Worker that performs database queries.
    Each worker gets its own DB connection via thread-local storage.

    Args:
        worker_id: Worker identifier
        num_queries: Number of queries to perform
    """
    logger.info(f"Worker {worker_id} starting")

    # Get thread-local DB connection
    db = get_db_connection()

    for i in range(num_queries):
        result = db.query(f"SELECT * FROM table WHERE id={i}")
        logger.info(f"Worker {worker_id} got: {result}")

    # Clean up
    db.close()
    logger.info(f"Worker {worker_id} completed")


def worker_with_context(worker_id: int):
    """
    Demonstrates storing arbitrary context in thread-local storage.
    """
    # Set thread-local context
    thread_local.request_id = f"REQ-{worker_id}"
    thread_local.user = f"User{worker_id}"

    logger.info(f"Worker {worker_id} starting with context: "
                f"request_id={thread_local.request_id}, user={thread_local.user}")

    # Call nested functions that access thread-local context
    process_request()
    log_activity()

    logger.info(f"Worker {worker_id} completed")


def process_request():
    """
    Function that accesses thread-local context without it being passed as parameter.
    """
    # Access thread-local data set by caller
    request_id = getattr(thread_local, 'request_id', 'UNKNOWN')
    logger.info(f"Processing request {request_id}")
    time.sleep(0.2)


def log_activity():
    """Another function accessing thread-local context."""
    user = getattr(thread_local, 'user', 'UNKNOWN')
    request_id = getattr(thread_local, 'request_id', 'UNKNOWN')
    logger.info(f"Logging activity for user={user}, request={request_id}")


class ThreadLocalCounter:
    """
    Demonstrates a counter that maintains separate values per thread.
    """

    def __init__(self):
        self._local = threading.local()

    def increment(self):
        """Increment the counter for the current thread."""
        if not hasattr(self._local, 'count'):
            self._local.count = 0
        self._local.count += 1

    def get_value(self) -> int:
        """Get the counter value for the current thread."""
        return getattr(self._local, 'count', 0)


def counter_worker(counter: ThreadLocalCounter, increments: int, worker_id: int):
    """
    Worker that increments a thread-local counter.

    Args:
        counter: ThreadLocalCounter instance
        increments: Number of times to increment
        worker_id: Worker identifier
    """
    logger.info(f"Counter worker {worker_id} starting")

    for _ in range(increments):
        counter.increment()
        time.sleep(0.05)

    final_value = counter.get_value()
    logger.info(f"Counter worker {worker_id} final count: {final_value}")


def main():
    """Demonstrates thread-local storage."""
    logger.info("=== Example 08: Thread-Local Storage ===")

    # Example 1: Thread-local database connections
    logger.info("\n--- Example 1: Thread-local DB connections ---")
    workers = []
    for i in range(3):
        t = threading.Thread(
            target=worker_with_db,
            args=(i, 2),
            name=f"DBWorker-{i}"
        )
        workers.append(t)
        t.start()

    for t in workers:
        t.join()

    logger.info("All DB workers completed")

    # Example 2: Thread-local context (like web request context)
    logger.info("\n--- Example 2: Thread-local request context ---")
    workers = []
    for i in range(3):
        t = threading.Thread(
            target=worker_with_context,
            args=(i,),
            name=f"RequestWorker-{i}"
        )
        workers.append(t)
        t.start()

    for t in workers:
        t.join()

    logger.info("All request workers completed")

    # Example 3: Thread-local counter
    logger.info("\n--- Example 3: Thread-local counter ---")
    shared_counter = ThreadLocalCounter()

    workers = []
    for i in range(4):
        increments = (i + 1) * 2  # Different increments per thread
        t = threading.Thread(
            target=counter_worker,
            args=(shared_counter, increments, i),
            name=f"CounterWorker-{i}"
        )
        workers.append(t)
        t.start()

    for t in workers:
        t.join()

    # Check main thread's counter value (should be 0)
    logger.info(f"Main thread counter value: {shared_counter.get_value()}")

    # Example 4: Demonstrate thread-local isolation
    logger.info("\n--- Example 4: Thread-local isolation ---")

    def show_isolation(thread_id: int):
        # Each thread gets its own copy
        thread_local.value = thread_id * 10
        time.sleep(0.1)  # Let other threads modify their values
        logger.info(f"Thread {thread_id}: thread_local.value = {thread_local.value}")

    threads = []
    for i in range(3):
        t = threading.Thread(target=show_isolation, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    logger.info("\n=== Example completed ===")


if __name__ == "__main__":
    main()
