# Threading Examples Guide

This document provides detailed descriptions of each threading example in this project.

## Table of Contents

1. [Simple Thread Creation](#01-simple-thread-creation)
2. [Daemon Threads and Timers](#02-daemon-threads-and-timers)
3. [Producer-Consumer Pattern](#03-producer-consumer-pattern)
4. [Thread Pools and Futures](#04-thread-pools-and-futures)
5. [Locks and Race Conditions](#05-locks-and-race-conditions)
6. [Semaphores, Conditions, and Barriers](#06-semaphores-conditions-and-barriers)
7. [Event, Cancellation, and Shutdown](#07-event-cancellation-and-shutdown)
8. [Thread-Local Storage](#08-thread-local-storage)
9. [Deadlock Demo and Avoidance](#09-deadlock-demo-and-avoidance)
10. [POSIX Signals](#10-posix-signals)
11. [Application Signals/Slots](#11-application-signalsslots)
12. [Qt QThread and Signals](#12-qt-qthread-and-signals)
13. [Threading and Asyncio](#13-threading-and-asyncio)
14. [Profiling and Debugging](#14-profiling-and-debugging)

---

## 01. Simple Thread Creation

**File:** `examples/01_simple_thread.py`

### What You'll Learn
- Creating threads with `threading.Thread`
- Passing arguments to thread functions
- Joining threads (waiting for completion)
- Difference between daemon and non-daemon threads
- Thread naming for debugging

### Key Concepts
- Threads execute functions in parallel with the main thread
- `thread.join()` blocks until the thread completes
- Daemon threads are terminated when the main program exits
- Non-daemon threads keep the program alive until completion

### Usage
```bash
python -m launcher.cli 01
```

---

## 02. Daemon Threads and Timers

**File:** `examples/02_daemon_timer.py`

### What You'll Learn
- Using `threading.Timer` for scheduled execution
- Creating repeating timers
- Daemon thread lifecycle
- Cancelling timers

### Key Concepts
- `Timer` is a thread that waits before executing a function
- Timers can be cancelled before they fire
- Daemon threads don't prevent program exit
- Repeating timers must be manually re-scheduled

### Usage
```bash
python -m launcher.cli 02
```

---

## 03. Producer-Consumer Pattern

**File:** `examples/03_producer_consumer.py`

### What You'll Learn
- Thread-safe communication using `queue.Queue`
- Producer-consumer pattern
- Multiple producers and consumers
- Queue blocking behavior
- Graceful shutdown with sentinel values

### Key Concepts
- Queue is thread-safe (no manual locking needed)
- `Queue.get()` blocks if queue is empty
- `Queue.put()` blocks if queue is full (when maxsize is set)
- Use sentinel values (like None) to signal shutdown

### Usage
```bash
python -m launcher.cli 03
```

---

## 04. Thread Pools and Futures

**File:** `examples/04_thread_pool_futures.py`

### What You'll Learn
- Using `concurrent.futures.ThreadPoolExecutor`
- Submitting tasks and getting Future objects
- Exception handling in thread pools
- `as_completed()` for processing results as they finish
- `map()` for batch processing

### Key Concepts
- ThreadPoolExecutor manages a pool of worker threads
- `submit()` returns a Future representing pending result
- `Future.result()` blocks until the task completes
- Exceptions in worker threads are re-raised when calling `result()`

### Usage
```bash
python -m launcher.cli 04
```

---

## 05. Locks and Race Conditions

**File:** `examples/05_locks_and_race_conditions.py`

### What You'll Learn
- What race conditions are and how they occur
- Using `threading.Lock` to protect critical sections
- Lock context manager (with statement)
- RLock (reentrant lock) for recursive locking
- Difference between Lock and RLock

### Key Concepts
- Race condition: multiple threads access shared data concurrently
- Critical section: code that must not be executed by multiple threads simultaneously
- `with lock:` is safer than manual acquire/release
- RLock allows same thread to acquire lock multiple times

### Usage
```bash
python -m launcher.cli 05
```

---

## 06. Semaphores, Conditions, and Barriers

**File:** `examples/06_semaphores_conditions_barrier.py`

### What You'll Learn
- Semaphore for limiting concurrent access
- BoundedSemaphore (prevents releasing too many times)
- Condition for wait/notify patterns
- Barrier for synchronizing multiple threads

### Key Concepts
- Semaphore: Counter-based synchronization (limits N concurrent accesses)
- Condition: Wait for specific condition, notify when it becomes true
- Barrier: Wait for N threads to reach a point before all continue

### Usage
```bash
python -m launcher.cli 06
```

---

## 07. Event, Cancellation, and Shutdown

**File:** `examples/07_event_cancellation_shutdown.py`

### What You'll Learn
- Using `threading.Event` for signaling
- Cooperative cancellation pattern
- Graceful shutdown of worker threads
- Timeout-based waiting

### Key Concepts
- Event is a simple boolean flag shared between threads
- `wait()` blocks until event is set
- `set()` wakes up all waiting threads
- Events are perfect for cancellation signals

### Usage
```bash
python -m launcher.cli 07
```

---

## 08. Thread-Local Storage

**File:** `examples/08_thread_local_storage.py`

### What You'll Learn
- Using `threading.local()` for thread-specific data
- Database connections per thread
- Request context in web servers
- Avoiding global state issues

### Key Concepts
- `threading.local()` creates an object with thread-specific attributes
- Each thread sees its own values for attributes
- Useful for per-thread resources (DB connections, sessions, etc.)
- Avoids passing context through every function call

### Usage
```bash
python -m launcher.cli 08
```

---

## 09. Deadlock Demo and Avoidance

**File:** `examples/09_deadlock_demo_and_avoidance.py`

### What You'll Learn
- What deadlock is and how it occurs
- Classic deadlock scenario (circular wait)
- Deadlock avoidance strategies (lock ordering, timeouts)
- Try-lock pattern

### Key Concepts
- Deadlock: Two or more threads waiting for each other indefinitely
- Circular wait: Thread A waits for resource held by B, B waits for resource held by A
- Prevention: Establish global lock ordering
- Detection: Use timeouts and handle lock acquisition failures

### Usage
```bash
python -m launcher.cli 09
```

---

## 10. POSIX Signals

**File:** `examples/10_signals_posix.py`

### What You'll Learn
- How POSIX signals interact with Python threads
- Handling SIGINT (Ctrl+C) and SIGTERM gracefully
- Signal handlers always run in the main thread
- Using signals for shutdown coordination
- Platform differences (Unix vs Windows)

### Key Concepts
- Signal handlers are called in the main thread only
- Use `threading.Event` to communicate shutdown to worker threads
- Windows has limited signal support

### Usage
```bash
python -m launcher.cli 10
```

---

## 11. Application Signals/Slots

**File:** `examples/11_app_signals_slots.py`

### What You'll Learn
- Using the pure-Python Signal/Slot implementation
- Observer pattern for decoupling components
- Thread-safe event notification
- Multiple subscribers to a single signal

### Key Concepts
- Signals allow decoupling: emitter doesn't know who's listening
- Slots are callbacks connected to signals
- Thread-safe by design (using locks internally)
- Similar to Qt signals/slots but pure Python

### Usage
```bash
python -m launcher.cli 11
```

---

## 12. Qt QThread and Signals

**File:** `examples/12_qt_qthread_signals.py`

### What You'll Learn
- Using QThread for threading in Qt applications
- Qt signals and slots (type-safe, cross-thread)
- Worker object pattern (moveToThread)
- Proper QThread lifecycle management

### Key Concepts
- QThread is Qt's threading mechanism
- Qt signals/slots are thread-safe automatically
- `moveToThread()` pattern is preferred over subclassing QThread
- Signals can carry typed data between threads

### Requirements
This example requires PyQt6 or PySide6:
```bash
pip install PyQt6
# OR
pip install PySide6
```

### Usage
```bash
python -m launcher.cli 12
```

---

## 13. Threading and Asyncio

**File:** `examples/13_threads_and_asyncio.py`

### What You'll Learn
- Running asyncio in a separate thread
- Calling async functions from sync code
- Calling sync functions from async code
- Using `asyncio.run_in_executor` for blocking operations
- Using `asyncio.run_coroutine_threadsafe`

### Key Concepts
- Asyncio runs in a single thread with an event loop
- Thread pool executor can run sync code from async context
- `run_coroutine_threadsafe()` schedules coroutines from other threads
- Each thread should have at most one event loop

### Usage
```bash
python -m launcher.cli 13
```

---

## 14. Profiling and Debugging

**File:** `examples/14_profiling_and_debugging.py`

### What You'll Learn
- Using `threading.enumerate()` to list active threads
- Thread stack inspection with `sys._current_frames()`
- Using faulthandler for debugging deadlocks
- Exception handling in threads
- GIL impact measurement

### Key Concepts
- Thread debugging is harder than single-threaded code
- Good logging with thread names is essential
- Stack traces help identify where threads are stuck
- The GIL can limit parallelism for CPU-bound tasks

### Usage
```bash
python -m launcher.cli 14
```

---

## Running Examples

### CLI Launcher
```bash
# List all examples
python -m launcher.cli --list

# Run a specific example
python -m launcher.cli 05

# Run all examples sequentially
python -m launcher.cli --all
```

### GUI Launcher (Optional)
Requires PyQt6 or PySide6:
```bash
python -m launcher.gui
```

### Direct Execution
```bash
python examples/01_simple_thread.py
```

---

## Learning Path

### Beginner
Start with these examples to learn the basics:
1. Simple Thread Creation (01)
2. Daemon Threads and Timers (02)
3. Producer-Consumer Pattern (03)
4. Thread Pools and Futures (04)

### Intermediate
Move on to synchronization primitives:
5. Locks and Race Conditions (05)
6. Semaphores, Conditions, and Barriers (06)
7. Event, Cancellation, and Shutdown (07)
8. Thread-Local Storage (08)

### Advanced
Tackle advanced topics:
9. Deadlock Demo and Avoidance (09)
10. POSIX Signals (10)
11. Application Signals/Slots (11)
13. Threading and Asyncio (13)
14. Profiling and Debugging (14)

### Framework-Specific
12. Qt QThread and Signals (12) - For Qt/GUI applications

---

## Additional Resources

- [Python threading documentation](https://docs.python.org/3/library/threading.html)
- [concurrent.futures documentation](https://docs.python.org/3/library/concurrent.futures.html)
- [Real Python: Threading Tutorial](https://realpython.com/intro-to-python-threading/)
- [threading_concepts.md](threading_concepts.md) - Conceptual explanations
