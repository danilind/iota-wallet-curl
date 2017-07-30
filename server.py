from engines import reattach
from utils.pow_queue import pow_queue
from engines.curl import POW

import json
import datetime

from tornado import websocket, web, ioloop


class PowService(websocket.WebSocketHandler):
    timeout = None

    def data_received(self, chunk):
        pass

    def open(self):
        print('Open')

        # Sets a hard limit on the time a connection can be open
        self.timeout = ioloop.IOLoop.current().add_timeout(datetime.timedelta(minutes=2), self.close)

    def on_message(self, message):
        print('Got message')

        message = json.loads(message)
        if message['type'] == 'POW':
            self._do_pow(message)
        elif message['type'] == 'survey_bundle':
            self._add_to_pending(message)
            self.close(202, "We're done")

    def _do_pow(self, message):
        # Test the limit
        if not pow_queue.try_push():
            return 'Concurrency limit reached'

        trunk = message['trunk']
        branch = message['branch']
        tx_trytes = message['tx_trytes']

        for trytes in POW(trunk, branch, tx_trytes):
            self.write_message({ 'trytes': trytes })

        pow_queue.pop()

    def _add_to_pending(self, message):
        if 'bundle_hash' in message:
            reattach.reattach_engine.add_by_bundle_hash(message['bundle_hash'])

    def on_close(self):
        print("WebSocket closed")

    def check_origin(self, origin):
        return True


app = web.Application([
    (r'/pow', PowService),
])

if __name__ == '__main__':
    reattach.start()

    app.listen(8765)
    ioloop.IOLoop.instance().start()
