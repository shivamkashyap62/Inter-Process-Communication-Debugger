import multiprocessing as mp
import time
import random

def producer(pipe_out, shared_value, debug_queue):
    for i in range(5):
        time.sleep(random.uniform(0.1, 0.5))
        message = f"Message {i} from Producer"
        pipe_out.send(message)
        with shared_value.get_lock():
            shared_value.value = i
        debug_queue.put(f"Producer sent: {message}, Shared Value: {i}")
    pipe_out.close()

def consumer(pipe_in, shared_value, debug_queue):
    while True:
        try:
            if pipe_in.poll(2):
                message = pipe_in.recv()
                with shared_value.get_lock():
                    current_shared = shared_value.value
                debug_queue.put(f"Consumer received: {message}, Shared Value: {current_shared}")
            else:
                debug_queue.put("Warning: Potential deadlock detected in Consumer!")
                break
        except EOFError:
            debug_queue.put("Consumer: Pipe closed, exiting.")
            break

def run_simulation():
    debug_queue = mp.Queue()
    parent_conn, child_conn = mp.Pipe()
    shared_value = mp.Value("i", 0)

    producer_proc = mp.Process(target=producer, args=(parent_conn, shared_value, debug_queue))
    consumer_proc = mp.Process(target=consumer, args=(child_conn, shared_value, debug_queue))

    producer_proc.start()
    consumer_proc.start()

    # Log messages to console
    running = True
    while running:
        if not debug_queue.empty():
            print(debug_queue.get())
        if not producer_proc.is_alive() and not consumer_proc.is_alive():
            running = False
        time.sleep(0.1)

    producer_proc.join()
    consumer_proc.join()

if _name_ == "_main_":
    run_simulation()
