from multiprocessing import Queue
from queue import Full, Empty

from const import *


# A queue to monitor and limit the number of ongoing pows.
# Only allow MAX_NUM_CONCURRENT_POW to be active at the same time
class PowQueue:
    active_pow = Queue(MAX_NUM_CONCURRENT_POW)

    def pop(self):
        self.active_pow.get_nowait()

    def push(self):
        self.active_pow.put_nowait(0)

    def try_push(self):
        try:
            self.push()
        except Full:
            return False


pow_queue = PowQueue()
