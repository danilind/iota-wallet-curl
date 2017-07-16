from engines.curl import POW
from data.test.attachToTangeTestInputs import *

if __name__ == '__main__':
    pow_engine = POW()
    pow_engine.attach_to_tangle(trunk, branch, 15, tx_trytes)
