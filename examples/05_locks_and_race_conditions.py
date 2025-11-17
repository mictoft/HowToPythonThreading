#!/usr/bin/env python3
"""
Example 05: Locks and Race Conditions

Demonstrates:
- Race conditions when accessing shared data
- Using threading.Lock to protect critical sections
- Lock context manager (with statement)
- RLock (reentrant lock) for recursive locking
- Difference between Lock and RLock

Key Concepts:
- Race condition: multiple threads access shared data concurrently
- Critical section: code that must not be executed by multiple threads simultaneously
- Lock.acquire() and Lock.release() protect critical sections
- Context manager (with lock:) is safer (auto-releases on exception)
- RLock allows same thread to acquire lock multiple times
"""

import threading
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)-12s] %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class Counter:
    """A simple counter to demonstrate race conditions."""

    def __init__(self):
        self.value = 0

    def increment_unsafe(self):
        """
        Increment counter WITHOUT thread safety.
        This will cause race conditions!
        """
        # The += operation is NOT atomic. It's actually:
        # 1. Read self.value
        # 2. Add 1
        # 3. Write back to self.value
        # Another thread can interrupt between these steps!
        temp = self.value
        time.sleep(0.0001)  # Exaggerate the race window
        self.value = temp + 1


class ThreadSafeCounter:
    """A thread-safe counter using Lock."""

    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()

    def increment(self):
        """Thread-safe increment using lock."""
        with self._lock:  # Context manager automatically acquires and releases
            temp = self.value
            time.sleep(0.0001)  # Even with delay, this is now safe
            self.value = temp + 1

    def get_value(self) -> int:
        """Thread-safe read."""
        with self._lock:
            return self.value


class BankAccount:
    """Demonstrates RLock for methods that call other locked methods."""

    def __init__(self, initial_balance: float = 0.0):
        self.balance = initial_balance
        self._lock = threading.RLock()  # Reentrant lock

    def deposit(self, amount: float):
        """Deposit money (thread-safe)."""
        with self._lock:
            logger.info(f"Depositing {amount}")
            self.balance += amount
            self._log_balance()  # Calls another method that also acquires the lock

    def withdraw(self, amount: float) -> bool:
        """Withdraw money if sufficient balance (thread-safe)."""
        with self._lock:
            if self.balance >= amount:
                logger.info(f"Withdrawing {amount}")
                self.balance -= amount
                self._log_balance()  # Calls another method that also acquires the lock
                return True
            else:
                logger.warning(f"Insufficient funds for withdrawal of {amount}")
                return False

    def _log_balance(self):
        """Log current balance (also uses lock - RLock allows this!)."""
        with self._lock:  # Same thread can acquire RLock again
            logger.info(f"Current balance: {self.balance}")


def worker_unsafe(counter: Counter, iterations: int):
    """Worker that increments counter unsafely."""
    for _ in range(iterations):
        counter.increment_unsafe()


def worker_safe(counter: ThreadSafeCounter, iterations: int):
    """Worker that increments counter safely."""
    for _ in range(iterations):
        counter.increment()


def bank_operations(account: BankAccount, thread_id: int):
    """Perform various bank operations."""
    account.deposit(100)
    time.sleep(0.1)
    account.withdraw(50)
    time.sleep(0.1)
    account.withdraw(30)


def main():
    """Demonstrates locks and race conditions."""
    logger.info("=== Example 05: Locks and Race Conditions ===")

    # Example 1: Race condition demonstration
    logger.info("\n--- Example 1: UNSAFE counter (race condition) ---")
    unsafe_counter = Counter()
    iterations = 1000
    num_threads = 5

    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=worker_unsafe, args=(unsafe_counter, iterations))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    expected = num_threads * iterations
    actual = unsafe_counter.value
    logger.info(f"Expected: {expected}, Actual: {actual}")
    if actual != expected:
        logger.warning(f"RACE CONDITION! Lost {expected - actual} increments!")
    else:
        logger.info("No race condition detected (got lucky this time)")

    # Example 2: Thread-safe counter with Lock
    logger.info("\n--- Example 2: Thread-safe counter with Lock ---")
    safe_counter = ThreadSafeCounter()

    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=worker_safe, args=(safe_counter, iterations))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    expected = num_threads * iterations
    actual = safe_counter.get_value()
    logger.info(f"Expected: {expected}, Actual: {actual}")
    if actual == expected:
        logger.info("SUCCESS! No data lost with proper locking")

    # Example 3: Lock context manager vs manual acquire/release
    logger.info("\n--- Example 3: Lock usage patterns ---")
    lock = threading.Lock()

    # Pattern 1: Context manager (recommended)
    logger.info("Using context manager (with statement):")
    with lock:
        logger.info("  Inside critical section")
        # Lock automatically released even if exception occurs

    # Pattern 2: Manual acquire/release (not recommended)
    logger.info("Using manual acquire/release:")
    lock.acquire()
    try:
        logger.info("  Inside critical section")
    finally:
        lock.release()  # Must release in finally block!

    # Example 4: RLock for recursive locking
    logger.info("\n--- Example 4: RLock for recursive locking ---")
    account = BankAccount(initial_balance=200.0)

    # Start multiple threads doing bank operations
    threads = []
    for i in range(3):
        t = threading.Thread(
            target=bank_operations,
            args=(account, i),
            name=f"Customer-{i}"
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    logger.info(f"Final balance: {account.balance}")

    # Example 5: Demonstrate why RLock is needed
    logger.info("\n--- Example 5: Regular Lock vs RLock ---")

    # This would DEADLOCK with regular Lock:
    # regular_lock = threading.Lock()
    # with regular_lock:
    #     with regular_lock:  # Same thread tries to acquire again - DEADLOCK!
    #         pass

    # But works fine with RLock:
    reentrant_lock = threading.RLock()
    with reentrant_lock:
        logger.info("Acquired RLock first time")
        with reentrant_lock:  # Same thread can acquire again
            logger.info("Acquired RLock second time (reentrant)")
        logger.info("Released RLock inner acquisition")
    logger.info("Released RLock outer acquisition")

    logger.info("\n=== Example completed ===")


if __name__ == "__main__":
    main()
