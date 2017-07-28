from datetime import datetime


class PendingBundle:
    def __init__(self, bundle_hash, txs):
        self.time_last_attachment = datetime.now()
        self.bundle_hash = bundle_hash
        self.txs = txs
