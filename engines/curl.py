from iota.types import *
from iota.transaction import Transaction
import cffi
import sys
import os
from const import *
from utils.list import *
from utils.convert import *


def POW(trunk_transaction, branch_transaction, tx_trytes):
    ffi = cffi.FFI()
    ffi.cdef("""
            char* ccurl_pow(char* trytes, int min_weight_magnitude);
            """)

    root = os.path.dirname(sys.modules['__main__'].__file__)
    path = os.path.join(root, 'build', 'Release', 'ccurl.dll')
    api = ffi.dlopen(path)

    trunk_trits = TryteString.from_string(trunk_transaction).as_trits()
    branch_trits = TryteString.from_string(branch_transaction).as_trits()
    tx_trits = [trits(x) for x in tx_trytes]

    prev = None
    for trit, i in zip(tx_trits, range(len(tx_trits))):
        array_copy(trunk_trits if i == 0 else prev.as_trits(),
                   0, trit, TRUNK_TRANSACTION_TRINARY_OFFSET, TRUNK_TRANSACTION_TRINARY_SIZE)

        array_copy(branch_trits if i == 0 else trunk_trits,
                   0, trit, BRANCH_TRANSACTION_TRINARY_OFFSET, BRANCH_TRANSACTION_TRINARY_SIZE)

        # TryteString.from_trits(trit).as_string().encode() throws an exceptions. Hack away:
        tryte_input = ffi.new('char[]', bytes(TryteString.from_trits(trit)._trytes))
        processed_trytes = ffi.string(api.ccurl_pow(tryte_input, MIN_WEIGHT_MAGNITUDE))

        prev = Transaction.from_tryte_string(processed_trytes).hash

        yield processed_trytes.decode()
