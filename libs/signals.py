"""
Pure-Python Signal/Slot (Observer Pattern) Implementation

This module provides a simple, thread-safe signal/slot mechanism similar to Qt signals
but using only Python's standard library. Useful for decoupling components in
multi-threaded applications.

Usage:
    signal = Signal()
    signal.connect(callback_function)
    signal.emit(arg1, arg2, ...)
"""

import threading
from typing import Callable, Any, List
import weakref
import logging

logger = logging.getLogger(__name__)


class Signal:
    """
    A thread-safe signal that can be connected to multiple slots (callbacks).

    Signals allow you to decouple components: the emitter doesn't need to know
    who's listening, and slots don't need to poll for events.
    """

    def __init__(self):
        """Initialize a new signal with an empty list of slots."""
        self._slots: List[weakref.ref] = []
        self._lock = threading.Lock()

    def connect(self, slot: Callable) -> None:
        """
        Connect a callable (slot) to this signal.

        Args:
            slot: A callable that will be invoked when signal is emitted.
                  Stored as a weak reference to avoid memory leaks.
        """
        with self._lock:
            # Use weak reference to avoid keeping objects alive unnecessarily
            try:
                weak_slot = weakref.ref(slot)
            except TypeError:
                # Some callables (like lambdas) can't be weakly referenced
                # In that case, we'll store a strong reference
                weak_slot = lambda: slot
                weak_slot._strong_ref = slot

            self._slots.append(weak_slot)
            logger.debug(f"Connected slot {slot.__name__ if hasattr(slot, '__name__') else slot} to signal")

    def disconnect(self, slot: Callable) -> bool:
        """
        Disconnect a callable from this signal.

        Args:
            slot: The callable to disconnect.

        Returns:
            True if the slot was found and removed, False otherwise.
        """
        with self._lock:
            initial_count = len(self._slots)
            # Remove all references to this slot
            self._slots = [s for s in self._slots if s() is not None and s() != slot]
            removed = len(self._slots) < initial_count
            if removed:
                logger.debug(f"Disconnected slot {slot.__name__ if hasattr(slot, '__name__') else slot}")
            return removed

    def emit(self, *args, **kwargs) -> None:
        """
        Emit the signal, calling all connected slots with the given arguments.

        Args:
            *args: Positional arguments to pass to slots
            **kwargs: Keyword arguments to pass to slots
        """
        with self._lock:
            # Clean up dead weak references and get live slots
            live_slots = []
            for weak_slot in self._slots:
                slot = weak_slot()
                if slot is not None:
                    live_slots.append(slot)

            # Update slots list to remove dead references
            self._slots = [s for s in self._slots if s() is not None]

        # Call slots outside the lock to avoid potential deadlocks
        for slot in live_slots:
            try:
                slot(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in slot {slot}: {e}", exc_info=True)

    def disconnect_all(self) -> None:
        """Disconnect all slots from this signal."""
        with self._lock:
            count = len(self._slots)
            self._slots.clear()
            logger.debug(f"Disconnected all {count} slots")

    @property
    def slot_count(self) -> int:
        """Return the number of connected slots (including dead weak references)."""
        with self._lock:
            return len([s for s in self._slots if s() is not None])


class SignalGroup:
    """
    A collection of named signals for an object.

    This is useful when an object needs to emit multiple different types of events.

    Usage:
        signals = SignalGroup(['started', 'progress', 'finished'])
        signals.started.connect(on_started)
        signals.progress.connect(on_progress)
        signals.started.emit()
    """

    def __init__(self, signal_names: List[str]):
        """
        Initialize a group of signals.

        Args:
            signal_names: List of signal names to create
        """
        self._signals = {}
        for name in signal_names:
            signal = Signal()
            self._signals[name] = signal
            setattr(self, name, signal)

    def disconnect_all(self) -> None:
        """Disconnect all slots from all signals in this group."""
        for signal in self._signals.values():
            signal.disconnect_all()
