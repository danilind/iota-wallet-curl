from datetime import datetime


class PendingBundle:
    time_last_attachment = None
    bundle_hash = None

    def __init__(self, bundle_hash):
        self.time_last_attachment = datetime.now()
        self.bundle_hash = bundle_hash
