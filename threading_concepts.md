# Threading Concepts and Theory

This document explains the fundamental concepts of threading in Python, providing the theoretical foundation for the examples in this project.

## Table of Contents

1. [What is Threading?](#what-is-threading)
2. [Threads vs Processes](#threads-vs-processes)
3. [The Global Interpreter Lock (GIL)](#the-global-interpreter-lock-gil)
4. [Synchronization Primitives](#synchronization-primitives)
5. [Common Threading Patterns](#common-threading-patterns)
6. [Common Pitfalls](#common-pitfalls)
7. [When to Use Threading](#when-to-use-threading)
8. [Best Practices](#best-practices)

---

## What is Threading?

**Threading** is a way to achieve concurrent execution within a single process. A thread is the smallest unit of execution that can be scheduled by an operating system.

### Key Characteristics

- **Lightweight**: Threads share the same memory space (unlike processes)
- **Concurrent**: Multiple threads can run seemingly at the same time
- **Shared State**: Threads within a process share memory and resources
- **Independent Execution**: Each thread has its own call stack and program counter

### Thread Lifecycle

1. **Created**: Thread object is instantiated
2. **Ready**: Thread is ready to run but not yet started
3. **Running**: Thread is actively executing code
4. **Blocked**: Thread is waiting (for I/O, lock, etc.)
5. **Dead**: Thread has completed execution

---

## Threads vs Processes

### Threads
- Share memory space with parent process
- Lightweight (low memory overhead)
- Fast to create and switch between
- Communication via shared memory (requires synchronization)
- Best for I/O-bound tasks

### Processes
- Separate memory space
- Heavier (more memory overhead)
- Slower to create and switch between
- Communication via IPC (pipes, queues, sockets)
- Best for CPU-bound tasks (bypass GIL)

### When to Choose Which?

| Use Threads | Use Processes |
|-------------|---------------|
| I/O-bound operations | CPU-bound operations |
| Need to share state | Need true parallelism |
| Lower memory overhead acceptable | Python GIL is a bottleneck |
| Network requests, file I/O | Data processing, calculations |

---

## The Global Interpreter Lock (GIL)

The **GIL** is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecode at once.

### Impact

- **CPU-Bound**: Only one thread executes Python code at a time
  - Multiple threads won't speed up CPU-intensive tasks
  - Actually slower due to threading overhead

- **I/O-Bound**: Threads work well because GIL is released during I/O
  - Network requests, file reading, database queries
  - Significant speedup possible

### Working with the GIL

```python
# CPU-bound: GIL prevents parallelism
def cpu_bound_task():
    result = sum(range(1_000_000))  # Holds GIL throughout
    return result

# I/O-bound: GIL released during I/O
def io_bound_task():
    response = requests.get(url)  # GIL released during network wait
    return response
```

### Bypassing the GIL

1. **Use multiprocessing** for CPU-bound tasks
2. **Use C extensions** that release the GIL (NumPy, etc.)
3. **Use asyncio** for I/O-bound tasks
4. **Use alternative interpreters** (Jython, IronPython - no GIL)

---

## Synchronization Primitives

Synchronization primitives are tools for coordinating thread execution and protecting shared resources.

### Lock (Mutex)

Most basic synchronization primitive.

```python
lock = threading.Lock()

with lock:
    # Critical section - only one thread at a time
    shared_data += 1
```

**When to use**: Protecting access to shared mutable data

### RLock (Reentrant Lock)

A lock that can be acquired multiple times by the same thread.

```python
rlock = threading.RLock()

with rlock:
    with rlock:  # Same thread can acquire again
        # Nested critical section
        pass
```

**When to use**: When methods that acquire locks call other methods that also need locks

### Semaphore

Limits the number of threads that can access a resource.

```python
semaphore = threading.Semaphore(3)  # Max 3 concurrent accesses

with semaphore:
    # Only 3 threads can be here simultaneously
    access_limited_resource()
```

**When to use**: Rate limiting, connection pooling, limited resource access

### Event

Simple signaling mechanism (boolean flag).

```python
event = threading.Event()

# Thread A
event.wait()  # Block until set

# Thread B
event.set()  # Wake up waiting threads
```

**When to use**: Signaling between threads, cancellation, synchronization points

### Condition

Wait for a specific condition to become true.

```python
condition = threading.Condition()

# Producer
with condition:
    queue.append(item)
    condition.notify()  # Wake up waiting consumer

# Consumer
with condition:
    while not queue:
        condition.wait()  # Release lock and wait
    item = queue.pop(0)
```

**When to use**: Producer-consumer, waiting for specific state changes

### Barrier

Synchronize N threads at a specific point.

```python
barrier = threading.Barrier(3)  # Wait for 3 threads

# Each thread
barrier.wait()  # Block until all 3 threads reach here
```

**When to use**: Phased computations, synchronized start/end points

---

## Common Threading Patterns

### 1. Producer-Consumer

Producers create work items, consumers process them. Use `queue.Queue` for thread-safe communication.

```python
def producer(queue):
    item = create_item()
    queue.put(item)

def consumer(queue):
    item = queue.get()
    process_item(item)
    queue.task_done()
```

### 2. Thread Pool

Reuse a fixed set of worker threads for multiple tasks.

```python
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(task, arg) for arg in args]
    results = [f.result() for f in futures]
```

### 3. Fork-Join

Spawn multiple threads, wait for all to complete.

```python
threads = [Thread(target=task, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()  # Wait for all
```

### 4. Pipeline

Chain of processing stages, each in its own thread.

```python
stage1_queue = Queue()
stage2_queue = Queue()

Thread(target=stage1, args=(input_queue, stage1_queue)).start()
Thread(target=stage2, args=(stage1_queue, stage2_queue)).start()
Thread(target=stage3, args=(stage2_queue, output_queue)).start()
```

---

## Common Pitfalls

### 1. Race Conditions

Multiple threads accessing shared data without synchronization.

```python
# BAD: Race condition
counter = 0

def increment():
    global counter
    counter += 1  # NOT atomic!

# GOOD: Protected with lock
lock = Lock()

def increment():
    global counter
    with lock:
        counter += 1
```

### 2. Deadlock

Two or more threads waiting for each other indefinitely.

```python
# BAD: Potential deadlock
def thread1():
    with lock_a:
        with lock_b:  # Thread 2 might have lock_b
            pass

def thread2():
    with lock_b:
        with lock_a:  # Thread 1 might have lock_a
            pass

# GOOD: Consistent lock ordering
def thread1():
    with lock_a:
        with lock_b:
            pass

def thread2():
    with lock_a:  # Same order!
        with lock_b:
            pass
```

### 3. Forgetting to Join Threads

Non-daemon threads keep the program alive.

```python
# BAD: Program hangs if thread doesn't finish
t = Thread(target=long_running_task)
t.start()
# Program exits here but waits for t to finish

# GOOD: Join with timeout or make daemon
t = Thread(target=long_running_task, daemon=True)
t.start()
# OR
t.join(timeout=5.0)
```

### 4. Mutable Shared State

Sharing mutable objects without protection.

```python
# BAD: Shared list without protection
shared_list = []

def worker():
    shared_list.append(item)  # Not thread-safe!

# GOOD: Use queue or lock
queue = Queue()

def worker():
    queue.put(item)  # Thread-safe
```

---

## When to Use Threading

### ✅ Good Use Cases

1. **I/O-Bound Operations**
   - Network requests
   - File I/O
   - Database queries
   - User input

2. **GUI Applications**
   - Keep UI responsive
   - Background tasks

3. **Multiple Independent Tasks**
   - Concurrent downloads
   - Parallel API calls
   - Multiple client handlers

4. **Event-Driven Systems**
   - Responding to events
   - Callback-based architectures

### ❌ Poor Use Cases

1. **CPU-Bound Operations**
   - Mathematical computations
   - Data processing
   - Image/video processing
   - Use `multiprocessing` instead

2. **Simple Sequential Tasks**
   - Adds complexity without benefit
   - Overhead outweighs gains

3. **Memory-Intensive Operations**
   - Threads share memory
   - May hit memory limits

---

## Best Practices

### 1. Minimize Shared State

```python
# GOOD: Each thread has its own data
def worker(thread_id, data):
    local_result = process(data)
    return local_result

# AVOID: Sharing mutable state
shared_dict = {}

def worker(thread_id):
    shared_dict[thread_id] = result  # Requires synchronization
```

### 2. Use Thread-Safe Data Structures

```python
# GOOD: Thread-safe queue
from queue import Queue
q = Queue()

# AVOID: Regular list (requires manual locking)
shared_list = []
lock = Lock()
```

### 3. Always Name Your Threads

```python
# GOOD: Named threads for easier debugging
t = Thread(target=worker, name="WorkerThread-1")

# AVOID: Anonymous threads
t = Thread(target=worker)  # name will be "Thread-1", "Thread-2", etc.
```

### 4. Use Context Managers for Locks

```python
# GOOD: Automatic release even on exception
with lock:
    critical_section()

# AVOID: Manual acquire/release
lock.acquire()
try:
    critical_section()
finally:
    lock.release()  # Must remember to release!
```

### 5. Handle Exceptions in Threads

```python
# GOOD: Catch and log exceptions
def worker():
    try:
        risky_operation()
    except Exception as e:
        logger.error(f"Worker failed: {e}")

# AVOID: Unhandled exceptions (silently fail)
def worker():
    risky_operation()  # Exception kills thread silently
```

### 6. Use ThreadPoolExecutor for Simple Cases

```python
# GOOD: Easier exception handling and resource management
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(task, arg) for arg in args]
    results = [f.result() for f in futures]

# AVOID: Manual thread management for simple cases
threads = []
for arg in args:
    t = Thread(target=task, args=(arg,))
    threads.append(t)
    t.start()
for t in threads:
    t.join()
```

### 7. Graceful Shutdown

```python
# GOOD: Cooperative cancellation
stop_event = Event()

def worker():
    while not stop_event.is_set():
        work()

# Signal shutdown
stop_event.set()

# AVOID: Forceful termination (not possible in Python)
# No thread.kill() or thread.terminate()
```

### 8. Logging with Thread Information

```python
# GOOD: Include thread name in logs
logging.basicConfig(
    format='%(asctime)s [%(threadName)s] %(message)s'
)

# Helps debug multi-threaded issues
```

---

## Performance Considerations

### Thread Overhead

- Creating threads has overhead (memory, CPU)
- Context switching between threads has cost
- Too many threads can degrade performance

### Optimal Thread Count

- **I/O-bound**: Can use many threads (10-100+)
- **CPU-bound**: Limited by GIL (use processes instead)
- **Rule of thumb**: Start with `num_cores * 2` and tune

### Profiling

```python
import cProfile
import pstats

cProfile.run('main()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats()
```

---

## Alternatives to Threading

### 1. Asyncio

For I/O-bound tasks with many concurrent operations:
```python
import asyncio

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# Run concurrently
await asyncio.gather(fetch(url1), fetch(url2))
```

### 2. Multiprocessing

For CPU-bound tasks:
```python
from multiprocessing import Pool

with Pool(processes=4) as pool:
    results = pool.map(cpu_intensive_function, data)
```

### 3. Concurrent.futures

Unified interface for both:
```python
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

# For I/O-bound
with ThreadPoolExecutor() as executor:
    results = executor.map(io_task, items)

# For CPU-bound
with ProcessPoolExecutor() as executor:
    results = executor.map(cpu_task, items)
```

---

## Summary

- **Threading enables concurrent execution** within a process
- **GIL limits CPU parallelism** but doesn't affect I/O-bound tasks
- **Synchronization is critical** to avoid race conditions and deadlocks
- **Use the right tool**: threads for I/O, processes for CPU, asyncio for many I/O operations
- **Follow best practices**: minimize shared state, use thread-safe structures, handle exceptions

For practical examples of all these concepts, see the [Examples Guide](EXAMPLES.md).
