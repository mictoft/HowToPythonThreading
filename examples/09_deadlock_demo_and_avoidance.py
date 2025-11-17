#!/usr/bin/env python3
"""
Example 09: Deadlock Demonstration and Avoidance

Demonstrates:
- What deadlock is and how it occurs
- Classic deadlock scenario (circular wait)
- Deadlock detection (timeout-based)
- Deadlock avoidance strategies:
  - Lock ordering
  - Try-lock pattern
  - Timeout-based acquisition
  - Using context managers

Key Concepts:
- Deadlock: Two or more threads waiting for each other indefinitely
- Circular wait: Thread A waits for resource held by B, B waits for resource held by A
- Prevention: Establish global lock ordering
- Detection: Use timeouts and handle lock acquisition failures
"""

import threading
import time
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)-12s] %(levelname)-8s %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# Resources protected by locks
lock_a = threading.Lock()
lock_b = threading.Lock()


def thread_1_deadlock():
    """
    Thread 1 that acquires locks in order A -> B.
    This WILL cause deadlock with thread_2_deadlock.
    """
    logger.info("Thread 1: Attempting to acquire Lock A...")
    with lock_a:
        logger.info("Thread 1: Acquired Lock A")
        time.sleep(0.5)  # Simulate work

        logger.info("Thread 1: Attempting to acquire Lock B...")
        with lock_b:  # DEADLOCK: thread_2 has lock_b and wants lock_a
            logger.info("Thread 1: Acquired Lock B")
            logger.info("Thread 1: Performing work with both locks")


def thread_2_deadlock():
    """
    Thread 2 that acquires locks in order B -> A.
    This WILL cause deadlock with thread_1_deadlock.
    """
    logger.info("Thread 2: Attempting to acquire Lock B...")
    with lock_b:
        logger.info("Thread 2: Acquired Lock B")
        time.sleep(0.5)  # Simulate work

        logger.info("Thread 2: Attempting to acquire Lock A...")
        with lock_a:  # DEADLOCK: thread_1 has lock_a and wants lock_b
            logger.info("Thread 2: Acquired Lock A")
            logger.info("Thread 2: Performing work with both locks")


def thread_1_ordered():
    """
    Thread 1 using lock ordering (A before B).
    This avoids deadlock.
    """
    logger.info("Thread 1 (ordered): Acquiring Lock A then B...")
    with lock_a:
        logger.info("Thread 1 (ordered): Got Lock A")
        time.sleep(0.1)
        with lock_b:
            logger.info("Thread 1 (ordered): Got Lock B")
            logger.info("Thread 1 (ordered): Working with both locks")
            time.sleep(0.2)


def thread_2_ordered():
    """
    Thread 2 also using lock ordering (A before B).
    This avoids deadlock.
    """
    logger.info("Thread 2 (ordered): Acquiring Lock A then B...")
    with lock_a:
        logger.info("Thread 2 (ordered): Got Lock A")
        time.sleep(0.1)
        with lock_b:
            logger.info("Thread 2 (ordered): Got Lock B")
            logger.info("Thread 2 (ordered): Working with both locks")
            time.sleep(0.2)


def thread_1_timeout():
    """
    Thread 1 using timeout to detect potential deadlock.
    """
    logger.info("Thread 1 (timeout): Attempting to acquire Lock A...")
    if lock_a.acquire(timeout=2.0):
        try:
            logger.info("Thread 1 (timeout): Got Lock A")
            time.sleep(0.5)

            logger.info("Thread 1 (timeout): Attempting to acquire Lock B...")
            if lock_b.acquire(timeout=2.0):
                try:
                    logger.info("Thread 1 (timeout): Got Lock B")
                    logger.info("Thread 1 (timeout): Working with both locks")
                    time.sleep(0.2)
                finally:
                    lock_b.release()
            else:
                logger.warning("Thread 1 (timeout): Timeout acquiring Lock B!")
        finally:
            lock_a.release()
    else:
        logger.warning("Thread 1 (timeout): Timeout acquiring Lock A!")


def thread_2_timeout():
    """
    Thread 2 using timeout to detect potential deadlock.
    """
    logger.info("Thread 2 (timeout): Attempting to acquire Lock B...")
    if lock_b.acquire(timeout=2.0):
        try:
            logger.info("Thread 2 (timeout): Got Lock B")
            time.sleep(0.5)

            logger.info("Thread 2 (timeout): Attempting to acquire Lock A...")
            if lock_a.acquire(timeout=2.0):
                try:
                    logger.info("Thread 2 (timeout): Got Lock A")
                    logger.info("Thread 2 (timeout): Working with both locks")
                    time.sleep(0.2)
                finally:
                    lock_a.release()
            else:
                logger.warning("Thread 2 (timeout): Timeout acquiring Lock A!")
        finally:
            lock_b.release()
    else:
        logger.warning("Thread 2 (timeout): Timeout acquiring Lock B!")


class BankAccount:
    """Bank account for demonstrating transfer deadlock."""

    def __init__(self, account_id: str, balance: float):
        self.account_id = account_id
        self.balance = balance
        self.lock = threading.Lock()

    def __repr__(self):
        return f"Account({self.account_id}, balance={self.balance})"


def transfer_deadlock_prone(from_account: BankAccount, to_account: BankAccount, amount: float):
    """
    Transfer money between accounts (DEADLOCK PRONE).
    If two threads transfer in opposite directions, deadlock can occur.
    """
    logger.info(f"Transfer: {from_account.account_id} -> {to_account.account_id}, amount={amount}")

    with from_account.lock:
        time.sleep(0.1)  # Simulate processing
        with to_account.lock:  # Potential deadlock!
            from_account.balance -= amount
            to_account.balance += amount
            logger.info(f"Transfer completed: {from_account.account_id}={from_account.balance}, "
                        f"{to_account.account_id}={to_account.balance}")


def transfer_safe(from_account: BankAccount, to_account: BankAccount, amount: float):
    """
    Transfer money between accounts (DEADLOCK FREE).
    Always acquire locks in a consistent order (by account_id).
    """
    logger.info(f"Safe transfer: {from_account.account_id} -> {to_account.account_id}, amount={amount}")

    # Always acquire locks in sorted order by account_id
    first_lock = from_account if from_account.account_id < to_account.account_id else to_account
    second_lock = to_account if from_account.account_id < to_account.account_id else from_account

    with first_lock.lock:
        time.sleep(0.1)
        with second_lock.lock:
            from_account.balance -= amount
            to_account.balance += amount
            logger.info(f"Safe transfer completed: {from_account.account_id}={from_account.balance}, "
                        f"{to_account.account_id}={to_account.balance}")


def main():
    """Demonstrates deadlock scenarios and avoidance strategies."""
    logger.info("=== Example 09: Deadlock Demo and Avoidance ===")

    # Example 1: Deadlock demonstration (WILL HANG - commented out by default)
    logger.info("\n--- Example 1: Deadlock demonstration (DISABLED - would hang) ---")
    logger.info("Uncomment the code below to see actual deadlock (Ctrl+C to interrupt)")
    logger.info("Deadlock occurs when threads acquire locks in different orders")

    # UNCOMMENT TO SEE ACTUAL DEADLOCK (program will hang!):
    # t1 = threading.Thread(target=thread_1_deadlock, name="DeadlockThread-1")
    # t2 = threading.Thread(target=thread_2_deadlock, name="DeadlockThread-2")
    # t1.start()
    # t2.start()
    # t1.join()  # Will wait forever
    # t2.join()  # Will wait forever

    # Example 2: Avoiding deadlock with lock ordering
    logger.info("\n--- Example 2: Avoiding deadlock with lock ordering ---")
    t1 = threading.Thread(target=thread_1_ordered, name="OrderedThread-1")
    t2 = threading.Thread(target=thread_2_ordered, name="OrderedThread-2")
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    logger.info("No deadlock! Both threads completed successfully")

    # Example 3: Detecting potential deadlock with timeouts
    logger.info("\n--- Example 3: Deadlock detection with timeouts ---")
    t1 = threading.Thread(target=thread_1_timeout, name="TimeoutThread-1")
    t2 = threading.Thread(target=thread_2_timeout, name="TimeoutThread-2")
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    logger.info("Timeout approach completed (may have timed out, but didn't deadlock)")

    # Example 4: Bank transfer deadlock scenario
    logger.info("\n--- Example 4: Bank transfer with consistent lock ordering ---")
    account_a = BankAccount("A", 1000.0)
    account_b = BankAccount("B", 1000.0)

    # Safe transfers with lock ordering
    t1 = threading.Thread(
        target=transfer_safe,
        args=(account_a, account_b, 100),
        name="Transfer-A-to-B"
    )
    t2 = threading.Thread(
        target=transfer_safe,
        args=(account_b, account_a, 50),
        name="Transfer-B-to-A"
    )

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    logger.info(f"Final balances: {account_a}, {account_b}")

    logger.info("\n=== Key Takeaways ===")
    logger.info("1. Deadlock occurs when threads wait for each other's locks")
    logger.info("2. Prevention: Always acquire locks in a consistent global order")
    logger.info("3. Detection: Use timeouts on lock acquisition")
    logger.info("4. Avoidance: Minimize lock scope and hold time")

    logger.info("\n=== Example completed ===")


if __name__ == "__main__":
    main()
