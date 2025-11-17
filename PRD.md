# Python Threading Learning App — Product Requirements Document (PRD)

**Document Version:** 1.0  
**Author:** ChatGPT  
**Last Updated:** 2025-11-17

---

# 1. Purpose & Goal

This project aims to create a comprehensive Python learning application that demonstrates *every major threading concept* through practical, runnable examples. It includes:

- Core Python threading (`threading.Thread`, synchronization primitives)
- Thread-safe IPC mechanisms (`queue.Queue`, futures, thread-local storage)
- Cancellation and lifecycle patterns
- Debugging and profiling techniques
- POSIX process signals (`signal` module)
- Application-level “signals & slots” (observer pattern)
- Qt-style signals/slots using QThread (optional dependency)
- Interop with asyncio
- Common pitfalls: deadlock, race conditions, GIL behavior

The goal is to let developers experiment hands-on with modern, safe threading patterns through clear, self-contained example programs.

---

# 2. Target Users

- Developers who want to learn Python threading in depth  
- Intermediate Python learners expanding into concurrency  
- Educators teaching threading techniques  
- Engineers building GUI apps, backend services, or embedded Python scripts  

---

# 3. Non-Goals

- Creating production-grade concurrency frameworks  
- Replacing GUI framework documentation  
- High-performance parallel computation (focus is on learning)  
- Installing or depending on many third-party packages (except optional Qt example)  

---

# 4. High-Level Requirements

## 4.1 Functional Requirements

### A. Launcher
A simple **CLI launcher** (and optional Qt-based GUI) that:
- Lists all available threading examples  
- Runs any example with configurable parameters  
- Pipes example logs to the console or GUI  

### B. Threading Examples
Each example is a standalone `.py` file with a `main()` entry, docstrings, and comments. All examples must run safely and terminate cleanly.

Required examples:

1. `01_simple_thread.py` — Creating threads, start/join, daemon vs non-daemon  
2. `02_daemon_timer.py` — `threading.Timer`, scheduled work, daemon behavior  
3. `03_producer_consumer.py` — Queue-based producer/consumer pattern  
4. `04_thread_pool_futures.py` — `ThreadPoolExecutor`, futures, exception handling  
5. `05_locks_and_race_conditions.py` — Lock, RLock, race condition demo  
6. `06_semaphores_conditions_barrier.py` — Semaphore, Condition, Barrier  
7. `07_event_cancellation_shutdown.py` — Cooperative cancellation using Event  
8. `08_thread_local_storage.py` — Using `threading.local()`  
9. `09_deadlock_demo_and_avoidance.py` — Deadlock and prevention strategies  
10. `10_signals_posix.py` — POSIX signals & thread-safe shutdown  
11. `11_app_signals_slots.py` — Pure Python signal/slot (observer pattern)  
12. `12_qt_qthread_signals.py` — Qt QThread + signals/slots (optional)  
13. `13_threads_and_asyncio.py` — Asyncio + threading interop  
14. `14_profiling_and_debugging.py` — Tools for inspecting thread execution  

### C. Supporting Libraries
- `libs/signals.py` — Minimal pure-Python observer/signal implementation  
- `launcher/cli.py` — Lists/runs examples  
- `launcher/gui.py` — Optional Qt-based launcher  

### D. Documentation
- `README.md` — Getting started  
- `EXAMPLES.md` — Detailed example descriptions  
- `threading_concepts.md` — Theory and conceptual explanations  

### E. Tests
- Unit tests for helper libraries  
- Integration tests for producer/consumer and thread pools  
- Tests must run deterministically and avoid infinite waits  

---

# 5. Non-Functional Requirements

- Python 3.8+ (recommended: 3.11+)  
- Minimal dependencies  
- Cross-platform where possible  
  - POSIX signals example includes Windows limitations  
- Clear inline comments and docstrings  
- Examples ≤ ~150 LOC each  
- Logging must use `logging` module with thread names included  

---

# 6. Architecture & Directory Structure

