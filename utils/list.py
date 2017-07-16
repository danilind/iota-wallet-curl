

# A implementation of javas system.arraycopy()
def array_copy(src, src_pos, dest, dest_pos, length):
    dest[dest_pos:dest_pos+length] = src[src_pos:src_pos+length]
