import time
from datetime import datetime

import const
from collections import deque
from threading import Lock
from multiprocessing import Process

from entities import PendingBundle

from iota import Iota


class ReattachEngine:
    queue = deque(maxlen=const.MAX_NUM_PENDING_TXS)
    queue_lock = Lock()

    def add(self, bundle_hash):
        # Has to be thread safe because of the usage by the server
        if not self.queue_lock.aquire():
            return

        try:
            if not self.queue.size >= const.MAX_NUM_PENDING_TXS - 1:
                self.queue.append(PendingBundle(bundle_hash))
        except:
            pass

        self.queue_lock.release()

    def survey(self):
        # Not thread safe (don't need to be)
        try:
            while self._is_time_to_reattach(self.queue[0]):
                queued_bundle = self.queue.pop(0)

                if self._is_reattachable(queued_bundle):
                    self._reattach(queued_bundle)
                    self.add(queued_bundle)

        except IndexError:
            return

    def _is_time_to_reattach(self, next):
        # TODO: Also check if the server is busy
        return (datetime.now() - next.time_last_attachment).total_seconds() > const.MIN_NUM_SECS_BETWEEN_ATTACHMENTS

    def _is_reattachable(self, queued_bundle):
        iota = Iota()
        bundle = iota.get_bundles(queued_bundle.tail)
        tx_to_approve = iota.get_transactions_to_approve(const.DEPTH)
        # Attach to tangle
        
        iota.broadcast_and_store(trytes)

    def _reattach(self, queued_bundle):
        pass


reattach_engine = ReattachEngine()


# Runs an infinite loop that executes the survey regularly
def run():
    while True:
        reattach_engine.survey()
        time.sleep(const.REATTACH_SURVEY_INTERVAL_IN_SECS)


# Starts the engine in a separate process
def start():
    p = Process(target=run)
    p.start()
