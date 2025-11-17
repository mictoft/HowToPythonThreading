#!/usr/bin/env python3
"""
Integration tests for common threading patterns.
"""

import unittest
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor


class TestProducerConsumer(unittest.TestCase):
    """Test producer-consumer pattern."""

    def test_basic_producer_consumer(self):
        """Test basic producer-consumer with queue."""
        q = queue.Queue()
        results = []

        def producer(count):
            for i in range(count):
                q.put(i)

        def consumer(count):
            for _ in range(count):
                item = q.get()
                results.append(item)
                q.task_done()

        items = 10

        prod_thread = threading.Thread(target=producer, args=(items,))
        cons_thread = threading.Thread(target=consumer, args=(items,))

        prod_thread.start()
        cons_thread.start()

        prod_thread.join()
        cons_thread.join()

        self.assertEqual(len(results), items)
        self.assertEqual(sorted(results), list(range(items)))

    def test_multiple_producers_consumers(self):
        """Test multiple producers and consumers."""
        q = queue.Queue()
        results = []
        lock = threading.Lock()

        def producer(prod_id, count):
            for i in range(count):
                q.put((prod_id, i))

        def consumer(count):
            for _ in range(count):
                item = q.get()
                with lock:
                    results.append(item)
                q.task_done()

        num_producers = 3
        num_consumers = 2
        items_per_producer = 5
        total_items = num_producers * items_per_producer

        # Start producers
        producers = []
        for i in range(num_producers):
            t = threading.Thread(target=producer, args=(i, items_per_producer))
            producers.append(t)
            t.start()

        # Start consumers
        consumers = []
        items_per_consumer = total_items // num_consumers
        for _ in range(num_consumers):
            t = threading.Thread(target=consumer, args=(items_per_consumer,))
            consumers.append(t)
            t.start()

        # Wait for all
        for t in producers:
            t.join()
        for t in consumers:
            t.join()

        self.assertEqual(len(results), total_items)


class TestThreadPool(unittest.TestCase):
    """Test thread pool pattern."""

    def test_thread_pool_executor(self):
        """Test ThreadPoolExecutor."""

        def square(n):
            return n * n

        with ThreadPoolExecutor(max_workers=3) as executor:
            numbers = list(range(10))
            results = list(executor.map(square, numbers))

        expected = [n * n for n in range(10)]
        self.assertEqual(results, expected)

    def test_thread_pool_futures(self):
        """Test ThreadPoolExecutor with futures."""

        def add(a, b):
            return a + b

        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(add, 1, 2)
            future2 = executor.submit(add, 3, 4)

            result1 = future1.result()
            result2 = future2.result()

        self.assertEqual(result1, 3)
        self.assertEqual(result2, 7)


class TestSynchronization(unittest.TestCase):
    """Test synchronization primitives."""

    def test_lock_prevents_race_condition(self):
        """Test that Lock prevents race conditions."""
        counter = [0]  # Use list to make it mutable
        lock = threading.Lock()

        def increment(count):
            for _ in range(count):
                with lock:
                    counter[0] += 1

        threads = []
        iterations = 1000
        num_threads = 5

        for _ in range(num_threads):
            t = threading.Thread(target=increment, args=(iterations,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        expected = num_threads * iterations
        self.assertEqual(counter[0], expected)

    def test_event_signaling(self):
        """Test Event for signaling."""
        event = threading.Event()
        results = []

        def waiter():
            event.wait()
            results.append("signaled")

        threads = [threading.Thread(target=waiter) for _ in range(3)]
        for t in threads:
            t.start()

        time.sleep(0.1)  # Give threads time to start waiting

        event.set()

        for t in threads:
            t.join(timeout=1.0)

        self.assertEqual(len(results), 3)

    def test_barrier_synchronization(self):
        """Test Barrier for synchronizing threads."""
        barrier = threading.Barrier(3)
        results = []
        lock = threading.Lock()

        def worker(worker_id):
            with lock:
                results.append(f"before_{worker_id}")

            barrier.wait()

            with lock:
                results.append(f"after_{worker_id}")

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # All "before" should come before all "after"
        before_count = sum(1 for r in results if r.startswith("before"))
        self.assertEqual(before_count, 3)

        # First "after" should not appear before last "before"
        first_after_idx = next(i for i, r in enumerate(results) if r.startswith("after"))
        last_before_idx = len([r for r in results if r.startswith("before")]) - 1
        self.assertGreaterEqual(first_after_idx, last_before_idx)


class TestThreadLocal(unittest.TestCase):
    """Test thread-local storage."""

    def test_thread_local_isolation(self):
        """Test that thread-local data is isolated per thread."""
        local_data = threading.local()
        results = {}
        lock = threading.Lock()

        def worker(thread_id):
            local_data.value = thread_id
            time.sleep(0.1)  # Let other threads set their values
            with lock:
                results[thread_id] = local_data.value

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Each thread should see its own value
        for thread_id, value in results.items():
            self.assertEqual(thread_id, value)


if __name__ == '__main__':
    unittest.main()
