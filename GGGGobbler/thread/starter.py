import threading
import queue
import time
import enum

from GGGGobbler.thread.private import tasks
from config import config
from util import timemath


def start_threads(r):
    job_queue = queue.Queue()
    close_event = threading.Event()
    t_consumer                = threading.Thread(group=None, target=consume_jobs,
                                                 args=(job_queue, r))
    t_produce_main_jobs       = threading.Thread(group=None, target=produce_main_jobs,
                                                 args=(job_queue, close_event))
    t_produce_check_msgs_jobs = threading.Thread(group=None, target=produce_check_messages_jobs,
                                                 args=(job_queue, close_event))
    t_close_monitor           = threading.Thread(group=None, target=wait_for_close,
                                                 args=(job_queue, close_event))
    t_consumer.start()
    t_produce_main_jobs.start()
    t_produce_check_msgs_jobs.start()
    t_close_monitor.start()

def consume_jobs(job_queue, r):
    retry_counter = config.retry_cap()
    while True:
        job = job_queue.get()
        # this is the consumer thread's close signal - job_queue.put(none)
        if job is None:
            return
        # process job
        if job == TaskID.MAIN:
            retry_counter = tasks.scan_reddit(r, retry_counter)
        elif job == TaskID.CHECK_MESSAGES:
            tasks.check_messages(r)
        job_queue.task_done()

def produce_main_jobs(job_queue, close_event):
    while not close_event.is_set():
        job_queue.put(TaskID.MAIN)
        c = timemath.secs_to_next_fraction_of_hour(config.wait_time_main())
        while not close_event.is_set() and c > 0:
            time.sleep(1)
            c -= 1

def produce_check_messages_jobs(job_queue, close_event):
    while not close_event.is_set():
        job_queue.put(TaskID.CHECK_MESSAGES)
        c = timemath.secs_to_next_fraction_of_hour(config.wait_time_check_messages())
        while not close_event.is_set() and c > 0:
            time.sleep(1)
            c -= 1

# this thread monitors a console input for a (q)uit instruction
def wait_for_close(job_queue, close_event):
    s = input("Type Q to end: ")
    while s != "q" and s != "Q":
        s = input("Type Q to end: ")
    # signal consumer to halt
    job_queue.put(None)
    # signal other threads to halt
    close_event.set()

class TaskID(enum.Enum):
    MAIN = 1
    CHECK_MESSAGES = 2