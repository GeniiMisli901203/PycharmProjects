import struct

def read_int8(data, offset):
    return struct.unpack_from("<b", data, offset)[0], offset + 1

def read_uint8(data, offset):
    return struct.unpack_from("<B", data, offset)[0], offset + 1

def read_int16(data, offset):
    return struct.unpack_from("<h", data, offset)[0], offset + 2

def read_uint16(data, offset):
    return struct.unpack_from("<H", data, offset)[0], offset + 2

def read_int32(data, offset):
    return struct.unpack_from("<i", data, offset)[0], offset + 4

def read_uint32(data, offset):
    return struct.unpack_from("<I", data, offset)[0], offset + 4

def read_int64(data, offset):
    return struct.unpack_from("<q", data, offset)[0], offset + 8

def read_uint64(data, offset):
    return struct.unpack_from("<Q", data, offset)[0], offset + 8

def read_float(data, offset):
    return struct.unpack_from("<f", data, offset)[0], offset + 4

def read_double(data, offset):
    return struct.unpack_from("<d", data, offset)[0], offset + 8

def read_char(data, offset, size):
    return (
        struct.unpack_from(
            f"<{size}s", data, offset)[0].decode("iso-8859-1", "replace"),
        offset + size,
    )

def read_int64_array(data, offset, size, address):
    array = []
    if address + size * 8 > len(data):
        raise ValueError(
            "Array size or address for int64 is out of the data bounds")
    else:
        for _ in range(size):
            value, offset = read_int64(data, address + _ * 8)
            array.append(value)
    return array

def read_int16_array(data, offset, size, address):
    array = []
    if address + size * 2 > len(data):
        raise ValueError(
            "Array size or address for int16 is out of the data bounds")
    else:
        for _ in range(size):
            value, offset = read_int16(data, address + _ * 2)
            array.append(value)
    return array

def read_structure_E(data, offset):
    e1_size, offset = read_uint16(data, offset)
    e1_address, offset = read_uint32(data, offset)

    e2, offset = read_int16(data, offset)
    e3, offset = read_uint8(data, offset)

    e4_size, offset = read_uint32(data, offset)
    e4_address, offset = read_uint32(data, offset)

    e1 = []
    if e1_address + e1_size * 4 > len(data):
        print(f"e1_size: {e1_size}, e1_address: {e1_address}, len(data): {len(data)}")
        raise ValueError("Array size or address for float in E1 is out of the data bounds")
    else:
        for _ in range(e1_size):
            value, offset = read_float(data, e1_address + _ * 4)
            e1.append(value)

    e4 = []
    if e4_address + e4_size * 8 > len(data):
        print(f"e4_size: {e4_size}, e4_address: {e4_address}, len(data): {len(data)}")
        raise ValueError("Array size or address for int64 in E4 is out of the data bounds")
    else:
        for _ in range(e1_size):
            float_address = e1_address + _ * 4
            if float_address + 4 > len(data):
                print(f"float_address: {float_address}, len(data): {len(data)}")
                raise ValueError("Float address in E1 is out of the data bounds")
            value, offset = read_float(data, float_address)
            e1.append(value)

    return {"E1": e1, "E2": e2, "E3": e3, "E4": e4}, offset


def read_structure_D(data, offset):
    d1, offset = read_float(data, offset)
    d2, offset = read_uint8(data, offset)

    d3_size, offset = read_uint16(data, offset)
    d3_address, offset = read_uint32(data, offset)

    d3 = []
    if d3_address + d3_size * 8 > len(data):
        raise ValueError("Array size or address for double in D3 is out of the data bounds")
    else:
        for _ in range(d3_size):
            value, offset = read_double(data, d3_address + _ * 8)
            d3.append(value)

    return {"D1": d1, "D2": d2, "D3": d3}, offset

def read_structure_C(data, offset):
    c1_address, offset = read_uint16(data, offset)

    c2, offset = read_structure_E(data, offset)

    c3, offset = read_uint8(data, offset)
    c4, offset = read_int16(data, offset)

    c1 = {}
    if c1_address != 0:
        struct_d, _ = read_structure_D(data, c1_address)
        c1 = struct_d

    return {"C1": c1, "C2": c2["E1"], "C3": c3, "C4": c4}, offset

def read_structure_B(data, offset):
    b1, offset = read_uint64(data, offset)
    b2, offset = read_int8(data, offset)
    return {"B1": b1, "B2": b2}, offset

def read_uint32_array(data, offset, size):
    array = []
    for _ in range(size):
        value, offset = read_uint32(data, offset)
        array.append(value)
    return array, offset

def read_structure_A(data, offset):
    a1, offset = read_uint32_array(data, offset, 5)

    a2, offset = read_uint8(data, offset)

    a3, offset = read_structure_C(data, offset)

    return {"A1": a1, "A2": a2, "A3": a3}, offset

def main(data):
    if data[:5] != b"\x3e\x56\x45\x54\x43":
        raise ValueError("Invalid data signature")

    offset = 5  # skip signature
    result, _ = read_structure_A(data, offset)
    return result

if __name__ == "__main__":
    data = b'>VETC\x00\x00\x000\x00\x00\x009\x00\x00\x00B\x00\x00\x00K\x00\x00\x00T3\x00]' \
            b'\x00\x05\x00\x00\x00\x82l\x06\x84\x00\x00\x00\x03\x00\x00\x00\x96\xbd\xf0\t' \
            b'\xcfd\x92\x848\xce\x11\xb7\x07^7\xe2D\xf7\t!k\xbe0$7\xd9F\xd4:_,\x02' \
            b'\x8c\xfe\xb1\x10j\xb5/e\xe8S\x12\x85o\xdc\x17\x84\x96\xbc\xe1\x88' \
            b'\x0e\xc5?\xdc\xd7\x89\x1du3\xb0\xbf\xe5\x19U\xdf\xcbj\xd8?\xbf\xaeG\x8b\xcb' \
            b'\x9e\xf0\xbf\xe6\x1c;\x99\xd1\xa7\x08\xbfTP\\\xbf\x08\xc9\xe4\xbfbz)?b' \
            b'\x83%\xbdEs"\xb3\xfe\xda\x04\x00\x00\x00C\xb8\xa2\xf8\x82F\x83\x0c\x04>d\x1b\rp' \
            b'3\xfb\xa1\xbb\x91\x0b'

    print(main(data))
