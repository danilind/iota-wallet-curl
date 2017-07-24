from data.test.attachToTangeTestInputs import *
import json

import asyncio
import websockets

from multiprocessing import Process


async def runner():
    async with websockets.connect('ws://localhost:8765') as websocket:
        print('Sending')
        await websocket.send(json.dumps({'trunk': trunk, 'branch': branch, 'tx_trytes': tx_trytes}))

        while True:
            message = await websocket.recv()
            print('Got {}'.format(message))


def start_runner():
    asyncio.get_event_loop().run_until_complete(runner())


if __name__ == '__main__':
    num_concurrent = 10

    # Expected result: 2 connections are accepted and gets a result. The others are rejected with a 503 code.
    for i in range(num_concurrent):
        print(i)
        p = Process(target=start_runner)
        p.start()
