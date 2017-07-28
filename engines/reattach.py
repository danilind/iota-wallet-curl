import time
from datetime import datetime

import const
from collections import deque
from multiprocessing import Lock
from multiprocessing import Process

from entities import PendingBundle
from engines.curl import POW

from iota import Iota
from iota.transaction import Transaction


class ReattachEngine:
    # TODO: What happens if the connection closes?
    iota = Iota('https://d3c5drf0y7sksv.cloudfront.net/')

    queue = deque(maxlen=const.MAX_NUM_PENDING_TXS)
    queue_lock = Lock()

    def add(self, bundle):
        # Has to be thread safe because of the usage by the server
        if not self.queue_lock.acquire():
            return

        try:
            if not self.queue.size >= const.MAX_NUM_PENDING_TXS - 1:
                self.queue.append(bundle)
        except:
            pass

        self.queue_lock.release()

    def add_by_bundle_hash(self, bundle_hash):

        bundle_hash = bundle_hash.encode('ascii')

        tx_hashes = self.iota.find_transactions(bundles=[bundle_hash])['hashes']
        trytes = self.iota.get_trytes(tx_hashes)['trytes']
        txs = [Transaction.from_tryte_string(t) for t in trytes]

        bundle = PendingBundle(bundle_hash, txs)
        self.add(bundle)

    def survey(self):
        print('Starting survey')
        # Not thread safe (don't need to be)
        try:
            while self._is_time_to_reattach(self.queue[0]):
                queued_bundle = self.queue.popleft()

                if self._is_reattachable(queued_bundle):
                    self._reattach(queued_bundle)
                    self.add(queued_bundle)
                # else: The bundle has confirmed, and can remain discarded

        except Exception as e:
            print(str(e))
            return

    def _is_time_to_reattach(self, entry):
        # TODO: Also check if the server is busy
        return (datetime.now() - entry.time_last_attachment).total_seconds() > const.MIN_NUM_SECS_BETWEEN_ATTACHMENTS

    def _is_reattachable(self, queued_bundle):
        # Returns true if all balances from the input addresses are larger or equal to the outgoing amount in the bundle
        spent_addresses = set([x.address for x in queued_bundle.txs if x.value < 0])
        balances = self.iota.get_balances(spent_addresses, 100)

        out_txs = {addr: 0 for addr in spent_addresses}
        for tx in queued_bundle.txs:
            if tx.address in out_txs:
                out_txs[tx.address] += abs(tx.value)

        return all([out_txs[addr] >= balance for addr, balance in zip(spent_addresses, balances)])

    def _reattach(self, queued_bundle):
        tx_to_approve = self.iota.get_transactions_to_approve(const.DEPTH)
        branch = tx_to_approve['branchTransaction']
        trunk = tx_to_approve['trunkTransaction']

        # Attach to tangle
        processed_trytes = []
        for trytes in POW(trunk, branch, queued_bundle.txs):
            processed_trytes.append(trytes)

        self.iota.broadcast_and_store(processed_trytes)


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
