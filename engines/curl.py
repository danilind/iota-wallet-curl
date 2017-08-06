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

    trunk_trits = trits(trunk_transaction)
    branch_trits = trits(branch_transaction)
    tx_trits = [trits(x) for x in tx_trytes]

    prev = None
    for trit in tx_trits:
        trit = array_copy(trunk_trits if prev is None else prev,
                          0, trit, TRUNK_TRANSACTION_TRINARY_OFFSET, TRUNK_TRANSACTION_TRINARY_SIZE)

        trit = array_copy(branch_trits if prev is None else trunk_trits,
                          0, trit, BRANCH_TRANSACTION_TRINARY_OFFSET, BRANCH_TRANSACTION_TRINARY_SIZE)

        # TryteString.from_trits(trit).as_string().encode() throws an exceptions. Hack away:
        tryte_input = ffi.new('char[]', bytes(TryteString.from_trits(trit)._trytes))
        processed_trytes = ffi.string(api.ccurl_pow(tryte_input, MIN_WEIGHT_MAGNITUDE))

        prev = Transaction.from_tryte_string(processed_trytes).hash.as_trits()

        yield processed_trytes.decode()
