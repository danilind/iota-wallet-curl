from engines import reattach

from const import *
from engines.curl import POW
import json

from tornado import websocket, web, ioloop

from multiprocessing import Queue
from queue import Full, Empty


# A queue to monitor and limit the number of connected clients.
# Only allow MAX_NUM_CONNECTED_CLIENTS to be connected at the same time
connected = Queue(MAX_NUM_CONNECTED_CLIENTS)


class POWService(websocket.WebSocketHandler):
    def open(self):
        global connected

        # Test the limit
        try:
            connected.put_nowait(0)
        except Full:
            print('Full')
            self.close(code=503, reason='Concurrency limit reached')

    def on_message(self, message):
        print('Got message')

        message = json.loads(message)
        if message['type'] == 'POW':
            self._do_pow(message)
        elif message['type'] == 'survey_tx':
            self._add_to_pending(message)

    def _do_pow(self, message):
        trunk = message['trunk']
        branch = message['branch']
        tx_trytes = message['tx_trytes']

        for trytes in POW(trunk, branch, tx_trytes):
            self.write_message(trytes)

    def _add_to_pending(self, message):
        if 'bundle_hash' in message['bundle_hash']:
            reattach.reattach_engine.add(message['bundle_hash'])

    def on_close(self):
        global connected
        connected.get_nowait()

        print("WebSocket closed")


app = web.Application([
    (r'/', POWService),
])

if __name__ == '__main__':
    reattach.start()

    app.listen(8765)
    ioloop.IOLoop.instance().start()
