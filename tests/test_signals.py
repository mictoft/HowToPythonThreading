#!/usr/bin/env python3
"""
Tests for libs/signals.py
"""

import unittest
import threading
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from libs.signals import Signal, SignalGroup


class TestSignal(unittest.TestCase):
    """Test cases for Signal class."""

    def test_basic_signal_emission(self):
        """Test basic signal emission and slot calling."""
        signal = Signal()
        results = []

        def slot():
            results.append("called")

        signal.connect(slot)
        signal.emit()

        self.assertEqual(results, ["called"])

    def test_signal_with_arguments(self):
        """Test signal emission with arguments."""
        signal = Signal()
        results = []

        def slot(a, b, c=None):
            results.append((a, b, c))

        signal.connect(slot)
        signal.emit(1, 2, c=3)

        self.assertEqual(results, [(1, 2, 3)])

    def test_multiple_slots(self):
        """Test connecting multiple slots to one signal."""
        signal = Signal()
        results = []

        def slot1():
            results.append(1)

        def slot2():
            results.append(2)

        signal.connect(slot1)
        signal.connect(slot2)
        signal.emit()

        self.assertEqual(sorted(results), [1, 2])

    def test_disconnect(self):
        """Test disconnecting slots."""
        signal = Signal()
        results = []

        def slot():
            results.append("called")

        signal.connect(slot)
        signal.emit()
        self.assertEqual(len(results), 1)

        # Disconnect and emit again
        signal.disconnect(slot)
        signal.emit()
        self.assertEqual(len(results), 1)  # Should not have been called again

    def test_disconnect_all(self):
        """Test disconnecting all slots."""
        signal = Signal()
        results = []

        signal.connect(lambda: results.append(1))
        signal.connect(lambda: results.append(2))

        signal.disconnect_all()
        signal.emit()

        self.assertEqual(results, [])

    def test_slot_exception_handling(self):
        """Test that exceptions in slots don't prevent other slots from running."""
        signal = Signal()
        results = []

        def failing_slot():
            raise ValueError("Test error")

        def working_slot():
            results.append("success")

        signal.connect(failing_slot)
        signal.connect(working_slot)

        # Should not raise exception
        signal.emit()

        # Working slot should have been called
        self.assertEqual(results, ["success"])

    def test_thread_safety(self):
        """Test that signals are thread-safe."""
        signal = Signal()
        results = []
        lock = threading.Lock()

        def slot(value):
            with lock:
                results.append(value)

        signal.connect(slot)

        # Emit from multiple threads
        threads = []
        for i in range(10):
            t = threading.Thread(target=signal.emit, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(results), 10)
        self.assertEqual(sorted(results), list(range(10)))

    def test_slot_count(self):
        """Test slot count property."""
        signal = Signal()

        self.assertEqual(signal.slot_count, 0)

        signal.connect(lambda: None)
        self.assertEqual(signal.slot_count, 1)

        signal.connect(lambda: None)
        self.assertEqual(signal.slot_count, 2)

        signal.disconnect_all()
        self.assertEqual(signal.slot_count, 0)


class TestSignalGroup(unittest.TestCase):
    """Test cases for SignalGroup class."""

    def test_signal_group_creation(self):
        """Test creating a signal group."""
        signals = SignalGroup(['started', 'progress', 'finished'])

        self.assertTrue(hasattr(signals, 'started'))
        self.assertTrue(hasattr(signals, 'progress'))
        self.assertTrue(hasattr(signals, 'finished'))

        self.assertIsInstance(signals.started, Signal)
        self.assertIsInstance(signals.progress, Signal)
        self.assertIsInstance(signals.finished, Signal)

    def test_signal_group_usage(self):
        """Test using signals from a signal group."""
        signals = SignalGroup(['event1', 'event2'])
        results = []

        signals.event1.connect(lambda: results.append('event1'))
        signals.event2.connect(lambda: results.append('event2'))

        signals.event1.emit()
        signals.event2.emit()

        self.assertEqual(results, ['event1', 'event2'])

    def test_signal_group_disconnect_all(self):
        """Test disconnecting all signals in a group."""
        signals = SignalGroup(['sig1', 'sig2'])
        results = []

        signals.sig1.connect(lambda: results.append(1))
        signals.sig2.connect(lambda: results.append(2))

        signals.disconnect_all()

        signals.sig1.emit()
        signals.sig2.emit()

        self.assertEqual(results, [])


if __name__ == '__main__':
    unittest.main()
