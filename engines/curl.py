from iota.types import *
import cffi
from const import *
from utils.list import *


class POW:
    def __init__(self):
        self.ffi = cffi.FFI()
        self.ffi.cdef("""
        char* ccurl_pow(char* trytes, int min_weight_magnitude);
        """)
        self.api = self.ffi.dlopen("C:\\Users\\Daniel\\PycharmProjects\\IOTAWalletCurl\\ccurl\\build\Release\\ccurl.dll")

    def attach_to_tangle(self, trunk_transaction, branch_transaction, min_weight_magnitude, tx_trytes):
        trunk_trits = Hash(trunk_transaction.encode()).as_trits()
        branch_trits = Hash(branch_transaction.encode()).as_trits()
        tx_trytes = [TryteString.from_string(x) for x in tx_trytes]
        tx_trits = [x.as_trits() for x in tx_trytes]

        processed_tx_trytes = []
        for tryte, trit, i in zip(tx_trytes, tx_trits, range(len(tx_trits))):

            # TODO: Not even gen addr works. Probably arraycopy or conversions
            array_copy(trunk_trits if i == 0 else processed_tx_trytes[-1].as_trits(),
                       0, trit, TRUNK_TRANSACTION_TRINARY_OFFSET, TRUNK_TRANSACTION_TRINARY_SIZE)

            array_copy(branch_trits if i == 0 else trunk_trits,
                       0, trit, BRANCH_TRANSACTION_TRINARY_OFFSET, BRANCH_TRANSACTION_TRINARY_SIZE)

            tryte_input = self.ffi.new('char[]', tryte.as_string().encode())
            processed_trytes = self.ffi.string(self.api.ccurl_pow(tryte_input, min_weight_magnitude)).decode()
            processed_tx_trytes.append(TryteString.from_string(processed_trytes))

        return [x.as_string() for x in reversed(processed_tx_trytes)]
