from const import *
from engines.curl import POW
import json

import asyncio
from asyncio.queues import Queue, QueueFull
import websockets


# A queue to monitor and limit the number of connected clients.
# Only allow MAX_NUM_CONNECTED_CLIENTS to be connected at the same time
connected = Queue(MAX_NUM_CONNECTED_CLIENTS)

async def POWService(websocket, path):
    global connected

    # Test the limit
    try:
        connected.put_nowait(0)
    except QueueFull:
        await websocket.close(503, 'Concurrency limit reached')
        return

    # All is good. Proceed
    try:
        message = await websocket.recv()
        print('Got message')

        message = json.loads(message)

        trunk = message['trunk']
        branch = message['branch']
        tx_trytes = message['tx_trytes']

        for trytes in POW(trunk, branch, tx_trytes):
            await websocket.send(trytes)
    finally:
        connected.get_nowait()
        # TODO: If curl is running, stop it.

    await websocket.close(200, 'Done')


start_server = websockets.serve(POWService, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
