#!/usr/bin/env python3
"""
Example 02: Daemon Threads and Timers

Demonstrates:
- Using threading.Timer for scheduled execution
- Repeating timers (implementing a periodic task)
- Daemon thread behavior and lifecycle
- Graceful cancellation of timers

Key Concepts:
- Timer is a thread that waits before executing a function
- Timers can be cancelled before they fire
- Daemon threads don't prevent program exit
- Repeating timers must be manually re-scheduled
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


def timed_greeting(name: str) -> None:
    """Called by a timer after a delay."""
    logger.info(f"Hello, {name}! (This was delayed by a timer)")


class RepeatingTimer:
    """
    A repeating timer that calls a function at regular intervals.

    Unlike threading.Timer which fires once, this timer repeats
    until explicitly cancelled.
    """

    def __init__(self, interval: float, function, *args, **kwargs):
        """
        Create a repeating timer.

        Args:
            interval: Time in seconds between calls
            function: Function to call
            *args, **kwargs: Arguments to pass to function
        """
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self._timer: Optional[threading.Timer] = None
        self._running = False
        self._lock = threading.Lock()

    def _run(self):
        """Internal method that calls the function and reschedules."""
        self._running = True
        try:
            self.function(*self.args, **self.kwargs)
        except Exception as e:
            logger.error(f"Error in repeating timer: {e}")
        finally:
            # Reschedule if not cancelled
            with self._lock:
                if self._running:
                    self._timer = threading.Timer(self.interval, self._run)
                    self._timer.daemon = True
                    self._timer.start()

    def start(self):
        """Start the repeating timer."""
        with self._lock:
            if not self._running:
                self._running = True
                self._timer = threading.Timer(self.interval, self._run)
                self._timer.daemon = True
                self._timer.start()
                logger.debug("Repeating timer started")

    def cancel(self):
        """Stop the repeating timer."""
        with self._lock:
            self._running = False
            if self._timer:
                self._timer.cancel()
                self._timer = None
                logger.debug("Repeating timer cancelled")

    def is_running(self) -> bool:
        """Check if the timer is currently running."""
        with self._lock:
            return self._running


def periodic_status(counter: list) -> None:
    """
    Periodic function called by RepeatingTimer.

    Args:
        counter: A list used as a mutable counter
    """
    counter[0] += 1
    logger.info(f"Periodic status check #{counter[0]}")


def main():
    """Demonstrates timers and daemon thread behavior."""
    logger.info("=== Example 02: Daemon Threads and Timers ===")

    # Example 1: Basic Timer
    logger.info("\n--- Example 1: Basic one-shot timer ---")
    timer1 = threading.Timer(1.0, timed_greeting, args=("World",))
    timer1.start()
    logger.info("Timer scheduled for 1 second from now...")
    time.sleep(1.5)  # Wait for it to fire
    logger.info("Timer should have fired by now")

    # Example 2: Cancelling a timer
    logger.info("\n--- Example 2: Cancelling a timer ---")
    timer2 = threading.Timer(3.0, timed_greeting, args=("Cancelled",))
    timer2.start()
    logger.info("Timer scheduled for 3 seconds, but we'll cancel it...")
    time.sleep(0.5)
    timer2.cancel()
    logger.info("Timer cancelled (function won't be called)")
    time.sleep(1.0)

    # Example 3: Multiple timers
    logger.info("\n--- Example 3: Multiple timers with different delays ---")
    timers = []
    for i in range(3):
        delay = (i + 1) * 0.5
        t = threading.Timer(delay, timed_greeting, args=(f"Timer-{i}",))
        t.start()
        timers.append(t)
        logger.info(f"Timer {i} scheduled for {delay}s delay")

    # Wait for all timers
    for t in timers:
        t.join()
    logger.info("All timers completed")

    # Example 4: Repeating timer
    logger.info("\n--- Example 4: Repeating timer ---")
    counter = [0]  # Use list to make it mutable in nested scope
    repeating = RepeatingTimer(0.5, periodic_status, counter)
    repeating.start()
    logger.info("Repeating timer started (every 0.5s)")

    # Let it run for a while
    time.sleep(2.5)

    logger.info("Cancelling repeating timer...")
    repeating.cancel()
    time.sleep(0.8)  # Verify it stopped
    logger.info(f"Timer stopped. Final count: {counter[0]}")

    # Example 5: Daemon behavior
    logger.info("\n--- Example 5: Daemon timer on program exit ---")
    daemon_timer = threading.Timer(10.0, timed_greeting, args=("Won't fire",))
    daemon_timer.daemon = True
    daemon_timer.start()
    logger.info("Started daemon timer with 10s delay")
    logger.info("Program will exit before timer fires (daemon threads don't block exit)")

    time.sleep(0.5)
    logger.info("Main thread exiting...")


if __name__ == "__main__":
    main()
