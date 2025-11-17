PRD — Python Threading Learning App

Document version: 1.0
Author: Assistant (draft)
Last updated: 2025-11-17

Assumptions (read first)

You are using Python 3.8+ (recommendation: 3.11+) on a POSIX or Windows system. Some signal behaviors are POSIX-only — see "Signals" section.

You want runnable, well-commented example programs and a small harness to run/inspect them.

When you asked for “signals and slots”, I interpreted that two ways:

Unix-style signals via the signal module (process-level signals, delivered only to the main thread).

Signals & slots as implemented by GUI frameworks (Qt-style) and by lightweight Python signal libraries (observer pattern). I include PyQt/PySide QThread & signals/slots examples and a pure-Python observer example (using blinker-style pattern implemented in-app so you don't have to install extras).

I will not ask clarifying questions — instead I deliver a comprehensive PRD that covers a broad, practical set of examples. If you want the doc specialized (e.g., only asyncio/threading interplay, or only embedded systems), tell me and I will adapt.

1. Purpose & Goal

Create a small, opinionated Python application (collection of example programs + a launcher/harness) that teaches Python threading end-to-end, covering:

Core threading primitives (threading.Thread, Lock, RLock, Semaphore, Event, Condition, Barrier, Timer)

Thread-safe communication (queue.Queue, concurrent.futures, threading.local)

Thread lifecycle management (daemon vs non-daemon, graceful shutdown, cancellation patterns)

Timers & scheduled work

Common concurrency patterns (producer/consumer, worker pool, pipeline, barrier sync)

Pitfalls: race conditions, deadlocks, livelocks, priority misconceptions, GIL implications

Interop with signals:

POSIX signal module (constraints: delivered only to main thread)

application-level signals: observer/publish-subscribe pattern

Qt signals & slots and how to safely update GUI from threads (QThread vs threading.Thread)

Comparison to other concurrency approaches (multiprocessing, asyncio) and when to use threads

Unit & integration tests demonstrating correctness, race detection (where possible), and performance assertions (small-scale)

The app is learning-first: readable, commented, small self-contained files, and a simple CLI/GUI launcher to run each example, view logs, and experiment with parameters.

2. Target Users

Python developers (beginners → intermediate) who want a hands-on, runnable catalogue of threading patterns.

Developers who need to understand safe multi-threading in desktop apps (GUI), backend services, and simple device scripts.

Educators who want example programs and tests to assign to students.

3. Non-Goals

Provide production-grade, enterprise-ready job schedulers (the app is educational).

Replace complete GUI frameworks’ threading guides; instead show safe patterns for integrating with GUI frameworks (Qt, Tkinter).

Cover every external library — only include a minimal set of optional dependencies (PyQt/PySide optional).

4. High-level Requirements
Functional Requirements

Launcher: A CLI (and optional minimal Qt GUI) that lists and runs examples with configurable parameters.

Examples: Each of the example scenarios below must be present as a file with clear docstrings and a main() entry:

01_simple_thread.py — basic Thread usage and join

02_daemon_timer.py — daemon threads, threading.Timer

03_producer_consumer.py — queue.Queue producer/consumer with graceful shutdown

04_thread_pool_futures.py — concurrent.futures.ThreadPoolExecutor and handling results/exceptions

05_locks_and_race_conditions.py — race, Lock, RLock, and safe counters

06_semaphores_conditions_barrier.py — Semaphore, Condition, Barrier examples

07_event_cancellation_shutdown.py — using Event to cancel/stop threads

08_thread_local_storage.py — threading.local() usage demonstration

09_deadlock_demo_and_avoidance.py — deadlock scenarios and fixes (ordered lock acquisition, timeout)

10_signals_posix.py — POSIX signal handling + interaction with background threads (safe shutdown)

11_app_signals_slots.py — small pure-Python signals & slots (observer) implementation and examples

12_qt_qthread_signals.py (optional dependency: PyQt6/PySide6) — QThread, signals/slots, thread-safe GUI updates

13_threads_and_asyncio.py — mixing asyncio and threads safely (run_in_executor, event loop thread confinement)

14_profiling_and_debugging.py — tools and techniques: logging, faulthandler, threading.enumerate(), sys.settrace, py-spy notes (no external calls)

Test suite: tests/ with unit tests for the small helper libraries and integration tests to validate expected behavior (producer/consumer throughput, correct shutdown).

Documentation: A README.md and this PRD.md plus an EXAMPLES.md describing how to run each example and what to expect.

Logging: Each example uses the logging module with structured logs that can be piped into the launcher UI.

Safety: Examples should not rely on indefinite blocking—use timeouts and sensible defaults so they can be run in CI.

Non-Functional Requirements

Code quality: readable, PEP8-ish, type hints where helpful.

Minimal dependencies: stdlib only, except optional GUI example (PyQt/PySide) and optional dev/test extras (pytest).

Cross-platform where possible; note platform-specific behavior in docs (signals on Windows).

Examples should be small (≤ ~150 lines typical) and independent.

5. Detailed Use Cases / Example Scenarios

Each example file includes:

Problem statement (what it demonstrates)

Code

Expected output & failure modes

Exercises for the learner (e.g., “modify to use RLock”, or “explain why this deadlocks”)

Use case list (mapping to files)

Simple thread — spawn thread, pass args, use join(), show daemon flag behavior.

Daemon and Timers — threading.Timer, scheduled tasks, program exit behavior with daemon threads.

Producer/Consumer — bounded Queue, multiple producers/workers, backpressure, graceful stop token.

Thread pool — ThreadPoolExecutor, map vs submit, cancelling futures, handling exceptions.

Shared state & locks — counter update, race detection by toggling Lock, using RLock for nested safe locking.

Semaphores & Conditions — limited resource pool via Semaphore, Condition for signaling between threads.

Event-driven cancellation — Event used as a cancellation token, combining with blocking operations (timeouts).

Barrier — synchronizing thread phases in a simulated parallel step.

Deadlock patterns — two threads lock resources in opposite order; show prevention via ordered locking or timeout.

Signals (POSIX) — signal.signal() + main thread handling; demonstrate how threads can be signaled indirectly (via Event).

App-level signals & slots — lightweight Signal class (connect/emit) and examples of decoupling producers and consumers.

Qt signals & slots — QThread, pyqtSignal/Signal usage, worker thread emits to GUI, proper thread affinity techniques.

Threads + asyncio — long-running IO-bound tasks run via run_in_executor, sharing Queue between threads and coroutine.

Debugging & profiling — how to inspect thread stack traces at runtime, use faulthandler.dump_traceback and logging.

6. Architecture & File Layout
python-threading-examples/
├── PRD.md                      # this file
├── README.md
├── EXAMPLES.md                 # What each example does, commands
├── launcher/
│   ├── cli.py                  # CLI to list/run examples, set params
│   └── (optional) gui.py       # Minimal Qt-based launcher (optional)
├── examples/
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
│   ├── 12_qt_qthread_signals.py   # optional
│   ├── 13_threads_and_asyncio.py
│   └── 14_profiling_and_debugging.py
├── libs/
│   └── signals.py               # tiny pure-Python observer implementation
├── tests/
│   ├── test_signals.py
│   ├── test_queue_shutdown.py
│   └── ...
├── docs/
│   └── threading_concepts.md
└── pyproject.toml

7. Technical Details & Constraints
Python threading caveats to call out in docs

GIL: Threads are best for I/O-bound tasks in CPython. CPU-bound tasks need multiprocessing or native extensions.

Signals: POSIX signals delivered only to main thread. signal.signal() called in non-main thread raises ValueError.

Daemon threads: Python will not wait for daemon threads at process exit — useful for background tasks but can lose state.

Thread cancellation: Python has no safe way to forcibly kill a thread; use cooperative cancellation (Event, condition flags).

GUI frameworks: GUI elements must be updated on the GUI/main thread. For Qt, use pyqtSignal/Signal, QThread, and QObject.moveToThread patterns.

Exception propagation: Exceptions in threads won't raise in the parent thread; always capture them and propagate (via Queue or Future).

Logging convention

Use logging.getLogger(__name__).

Each example accepts a --verbose flag to set logging.DEBUG.

Structured logs include threadName and optionally worker_id.

8. Acceptance Criteria

Each example runs standalone (python examples/03_producer_consumer.py) and terminates cleanly with default parameters.

Tests in tests/ run under pytest with no external dependencies (except optional test requiring Qt if present).

EXAMPLES.md describes expected output for each example and lists exercises.

Code includes docstrings & inline comments explaining why the code is written the way it is (not only how).

Launcher lists examples and can run them with a simple flag (CLI: python launcher/cli.py --list and --run examples/03).

9. Example API / CLI

launcher/cli.py sample usage:

$ python launcher/cli.py --list
Available examples:
  01_simple_thread
  02_daemon_timer
  03_producer_consumer
  ...

$ python launcher/cli.py --run 03 --producers 2 --consumers 4 --duration 10


Flags are passed through to the example modules. Each example implements parse_args() and main() to allow CLI and importable execution.

10. Testing Strategy

Unit tests for libs/signals.py (connect/disconnect/emit).

Integration test for 03_producer_consumer.py: start producers/consumers for short duration, assert queue drained on shutdown.

Test for 05_locks_and_race_conditions.py that shows the counter is wrong without lock and correct with lock.

CI configuration is optional; tests are written to be fast and deterministic with timeouts.

11. Security & Safety Considerations

Avoid running untrusted code in examples.

Examples that use network or system signals are benign (no privileged ops).

Provide warnings in docs about running signal examples on Windows (behavior differs from POSIX).

12. Deliverables

PRD.md (this file)

README.md and EXAMPLES.md

Example modules under examples/ (listing above)

libs/signals.py

launcher/cli.py (and optional launcher/gui.py)

tests/ for key behaviors

Optional: interactive Jupyter notebook demonstrating a few examples and showing thread states live

13. Example Code Snippets (short extracts)

These are short illustrative snippets. Full implementations will appear in examples/.

Producer / Consumer (pattern)
# examples/03_producer_consumer.py (excerpt)
import threading, queue, time, logging

log = logging.getLogger(__name__)

def producer(q: queue.Queue, stop_event: threading.Event, id: int):
    i = 0
    while not stop_event.is_set():
        item = f"item-{id}-{i}"
        q.put(item)
        log.debug("Produced %s", item)
        i += 1
        time.sleep(0.1)

def consumer(q: queue.Queue, stop_event: threading.Event):
    while not stop_event.is_set() or not q.empty():
        try:
            item = q.get(timeout=0.5)
        except queue.Empty:
            continue
        log.debug("Consumed %s", item)
        q.task_done()

def main():
    q = queue.Queue(maxsize=10)
    stop = threading.Event()
    producers = [threading.Thread(target=producer, args=(q, stop, i)) for i in range(2)]
    consumers = [threading.Thread(target=consumer, args=(q, stop)) for _ in range(3)]

    for t in producers + consumers:
        t.start()

    try:
        time.sleep(5)  # runtime
    finally:
        stop.set()
        for t in producers:
            t.join()
        q.join()  # wait until all items processed
        for t in consumers:
            t.join()

POSIX signal safe shutdown pattern
# examples/10_signals_posix.py (excerpt)
import signal, threading, logging, time

stop = threading.Event()
log = logging.getLogger(__name__)

def handle_sigint(signum, frame):
    log.info("SIGINT received")
    stop.set()

def worker():
    while not stop.is_set():
        time.sleep(0.1)

def main():
    signal.signal(signal.SIGINT, handle_sigint)  # must be main thread
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    while not stop.is_set():
        time.sleep(0.2)
    t.join()

Qt worker emitting to GUI (conceptual)
# examples/12_qt_qthread_signals.py (requires PyQt6/PySide6)
from PyQt6.QtCore import QObject, QThread, pyqtSignal

class Worker(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def run(self):
        for i in range(10):
            # long work...
            self.progress.emit(i)
        self.finished.emit()

# GUI creates QThread, moves Worker to thread,
# connects signals to main-window slots safely.

14. Learning Exercises (for each example)

Every example includes 3 short exercises, for example:

Modify 03_producer_consumer to implement backpressure where producers block when queue is full and log time spent waiting.

Add a timeout to the deadlock demo and detect livelock.

Convert 04_thread_pool_futures to use ProcessPoolExecutor and compare performance on CPU-bound workloads.

15. Open Questions / Follow-ups (I made assumptions)

I avoided asking clarifying questions. I assumed you want a broad coverage rather than a narrow, deep dive. If you prefer one of these changes, tell me which and I will produce concrete code files or a repo scaffold (I can also generate the example files right here):

Include full runnable code for all examples (I can generate them).

Include the optional Qt GUI examples — requires you to install PyQt6 or PySide6.

Prefer a web UI (Flask) instead of a Qt GUI for the launcher.

Add a Jupyter notebook that demonstrates live thread state and plots scheduling timelines.

Tell me which of the above you want next (or ask me to generate the full repository files now) and I will produce them in the next reply.