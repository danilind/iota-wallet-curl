from engines import reattach

from const import *
from engines.curl import POW
import json

from tornado import websocket, web, ioloop

from multiprocessing import Queue
from queue import Full, Empty


# A queue to monitor and limit the number of ongoing pows.
# Only allow MAX_NUM_CONCURRENT_POW to be active at the same time
active_pow = Queue(MAX_NUM_CONCURRENT_POW)


class POWService(websocket.WebSocketHandler):
    def open(self):
        print('Open')

    def on_message(self, message):
        print('Got message')

        message = json.loads(message)
        if message['type'] == 'POW':
            self._do_pow(message)
        elif message['type'] == 'survey_bundle':
            self._add_to_pending(message)
            self.close(202, "We're done")

    def _do_pow(self, message):
        global active_pow

        # Test the limit
        try:
            active_pow.put_nowait(0)
        except Full:
            return 'Concurrency limit reached'

        trunk = message['trunk']
        branch = message['branch']
        tx_trytes = message['tx_trytes']

        for trytes in POW(trunk, branch, tx_trytes):
            self.write_message({ 'trytes': trytes })

        active_pow.get_nowait()

    def _add_to_pending(self, message):
        if 'bundle_hash' in message:
            reattach.reattach_engine.add_by_bundle_hash(message['bundle_hash'])

    def on_close(self):
        print("WebSocket closed")

    def check_origin(self, origin):
        return True


app = web.Application([
    (r'/pow', POWService),
])

if __name__ == '__main__':
    reattach.start()

    app.listen(8765)
    ioloop.IOLoop.instance().start()
