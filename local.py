from data.test.attachToTangeTestInputs import *
import json

import asyncio
import websockets

async def runner():
    async with websockets.connect('ws://localhost:8765/pow') as websocket:
        print('Sending')
        await websocket.send(json.dumps({'trunk': trunk, 'branch': branch, 'tx_trytes': tx_trytes, 'type': 'POW'}))

        for i in range(len(tx_trytes)):
            message = await websocket.recv()
            print('Got {}'.format(message))

asyncio.get_event_loop().run_until_complete(runner())
