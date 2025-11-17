# Python Threading Learning App

A comprehensive collection of **Python threading examples**, designed to teach every major concept through clear, runnable, well-commented code.

This project covers:

- `threading.Thread` basics  
- Locking primitives (Lock, RLock, Semaphore, Event, Condition, Barrier)  
- Producer/consumer, worker pools, pipelines  
- Thread cancellation and shutdown patterns  
- Race conditions, deadlocks, debugging and profiling  
- Futures and `ThreadPoolExecutor`  
- Interaction with `asyncio`  
- POSIX signals and how they interact with threads  
- Pure-Python “signals & slots” (observer pattern)  
- Qt QThread + signals/slots (optional GUI example)

The goal is to help you *understand Python threading deeply* by running practical examples you can modify and experiment with.

---

## ✨ Features

- 14+ runnable threading examples, each with:
  - Clear docstrings
  - Inline code comments
  - Reference output
  - Small learning exercises  
- A simple **CLI launcher** to run examples  
- Optional **Qt GUI launcher**  
- Full documentation for each pattern  
- Test suite for important concurrency behaviors  
- Minimal external dependencies  

---

## 📁 Project Structure

```
HowToPythonThreading/
├── examples/              # All threading examples (01-14)
│   ├── 01_simple_thread.py
│   ├── 02_daemon_timer.py
│   ├── 03_producer_consumer.py
│   ├── 04_thread_pool_futures.py
│   ├── 05_locks_and_race_conditions.py
│   ├── 06_semaphores_conditions_barrier.py
│   ├── 07_event_cancellation_shutdown.py
│   ├── 08_thread_local_storage.py
│   ├── 09_deadlock_demo_and_avoidance.py
│   ├── 10_signals_posix.py
│   ├── 11_app_signals_slots.py
│   ├── 12_qt_qthread_signals.py
│   ├── 13_threads_and_asyncio.py
│   └── 14_profiling_and_debugging.py
├── libs/                  # Supporting libraries
│   └── signals.py        # Pure-Python signal/slot implementation
├── launcher/             # Example launchers
│   ├── cli.py           # Command-line launcher
│   └── gui.py           # Qt GUI launcher (optional)
├── tests/                # Test suite
│   ├── test_signals.py
│   └── test_threading_patterns.py
├── docs/                 # Additional documentation
├── EXAMPLES.md          # Detailed example descriptions
├── threading_concepts.md # Threading theory and concepts
├── README.md            # This file
├── requirements.txt     # Python dependencies
├── setup.py             # Package setup
└── LICENSE              # MIT License
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- No required dependencies (uses Python standard library only!)

### Optional Dependencies

- **PyQt6** or **PySide6** (for Qt examples and GUI launcher)
  ```bash
  pip install PyQt6
  # OR
  pip install PySide6
  ```

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd HowToPythonThreading
   ```

2. **No installation needed!** All examples use only Python's standard library.

3. **(Optional)** Install Qt for GUI launcher and Qt example:
   ```bash
   pip install PyQt6
   ```

---

## 📚 Usage

### CLI Launcher (Recommended)

List all available examples:
```bash
python -m launcher.cli --list
```

Run a specific example:
```bash
python -m launcher.cli 01    # Run example 01
python -m launcher.cli 05    # Run example 05
```

Run all examples sequentially:
```bash
python -m launcher.cli --all
```

### GUI Launcher (Optional - Requires Qt)

```bash
python -m launcher.gui
```

### Direct Execution

You can also run examples directly:
```bash
python examples/01_simple_thread.py
python examples/05_locks_and_race_conditions.py
```

---

## 📖 Examples Overview

| # | Example | Concepts |
|---|---------|----------|
| 01 | Simple Thread Creation | Thread basics, daemon threads, join() |
| 02 | Daemon Threads and Timers | Timer, repeating timers, daemon lifecycle |
| 03 | Producer-Consumer Pattern | Queue, multiple producers/consumers |
| 04 | Thread Pools and Futures | ThreadPoolExecutor, futures, exception handling |
| 05 | Locks and Race Conditions | Lock, RLock, race conditions |
| 06 | Semaphores, Conditions, Barriers | Semaphore, Condition, Barrier |
| 07 | Event, Cancellation, Shutdown | Event, cooperative cancellation |
| 08 | Thread-Local Storage | threading.local(), per-thread data |
| 09 | Deadlock Demo and Avoidance | Deadlock, lock ordering, timeouts |
| 10 | POSIX Signals | Signal handling, SIGINT, SIGTERM |
| 11 | Application Signals/Slots | Observer pattern, pure-Python signals |
| 12 | Qt QThread and Signals | QThread, Qt signals/slots (requires Qt) |
| 13 | Threading and Asyncio | Asyncio interop, run_in_executor |
| 14 | Profiling and Debugging | Stack traces, GIL impact, debugging |

For detailed descriptions, see [EXAMPLES.md](EXAMPLES.md).

---

## 🧪 Running Tests

Run the test suite:
```bash
python -m pytest tests/
```

Run tests with coverage:
```bash
python -m pytest --cov=libs --cov=launcher tests/
```

Run specific test file:
```bash
python -m pytest tests/test_signals.py
```

---

## 📖 Documentation

- **[EXAMPLES.md](EXAMPLES.md)** - Detailed guide for each example
- **[threading_concepts.md](threading_concepts.md)** - Threading theory and concepts
- **[PRD.md](PRD.md)** - Original product requirements document

---

## 🎓 Learning Path

### Beginner
1. Example 01: Simple Thread Creation
2. Example 02: Daemon Threads and Timers
3. Example 03: Producer-Consumer Pattern
4. Example 04: Thread Pools and Futures

### Intermediate
5. Example 05: Locks and Race Conditions
6. Example 06: Semaphores, Conditions, Barriers
7. Example 07: Event, Cancellation, Shutdown
8. Example 08: Thread-Local Storage

### Advanced
9. Example 09: Deadlock Demo and Avoidance
10. Example 10: POSIX Signals
11. Example 11: Application Signals/Slots
13. Example 13: Threading and Asyncio
14. Example 14: Profiling and Debugging

### Framework-Specific
12. Example 12: Qt QThread and Signals (requires Qt)

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add more examples
- Improve existing examples
- Fix bugs
- Enhance documentation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Resources

- [Python threading documentation](https://docs.python.org/3/library/threading.html)
- [concurrent.futures documentation](https://docs.python.org/3/library/concurrent.futures.html)
- [Real Python: Threading Tutorial](https://realpython.com/intro-to-python-threading/)
- [Python GIL explained](https://realpython.com/python-gil/)

---

## ⚠️ Important Notes

### About the GIL (Global Interpreter Lock)

Python's GIL means that only one thread can execute Python bytecode at a time. This affects threading performance:

- **I/O-bound tasks**: Threading works great! (network, files, databases)
- **CPU-bound tasks**: Use `multiprocessing` instead of threading

### Thread Safety

Always protect shared mutable state with locks or use thread-safe data structures like `queue.Queue`.

### Best Practices

1. Always name your threads for easier debugging
2. Use context managers (`with lock:`) for locks
3. Handle exceptions in worker threads
4. Use `ThreadPoolExecutor` for simple cases
5. Prefer `queue.Queue` over manual synchronization
6. Implement graceful shutdown with `Event`

---

## 🎯 Goals of This Project

- **Educational**: Learn threading through practical examples
- **Comprehensive**: Cover all major threading concepts
- **Hands-on**: Runnable, modifiable examples
- **Well-documented**: Clear explanations and comments
- **Best practices**: Demonstrate safe, correct patterns

Happy Threading! 🧵✨
