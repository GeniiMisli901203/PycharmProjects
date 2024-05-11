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


def read_structure_D(data, offset):
    d1_size, offset = read_uint16(data, offset)
    d1_address, offset = read_uint16(data, offset)

    d2, offset = read_uint8(data, offset)
    d3, offset = read_double(data, offset)

    d4_size, offset = read_uint16(data, offset)
    d4_address, offset = read_uint32(data, offset)

    d1 = read_int64_array(data, offset, d1_size, d1_address)
    d4 = read_int16_array(data, offset, d4_size, d4_address)

    return {"D1": d1, "D2": d2, "D3": d3, "D4": d4}, offset


def read_structure_C(data, offset):
    c1, offset = read_int8(data, offset)
    c2, offset = read_int32(data, offset)
    c3_address, offset = read_uint32(data, offset)

    c3 = {}
    if c3_address != 0:
        struct_d, _ = read_structure_D(data, c3_address)
        c3 = struct_d

    return {"C1": c1, "C2": c2, "C3": c3}, offset


def read_structure_B(data, offset):
    b1, offset = read_float(data, offset)
    b2, offset = read_char(data, offset, 2)
    b3, offset = read_uint8(data, offset)
    return {"B1": b1, "B2": b2, "B3": b3}, offset


def read_structure_A(data, offset):
    a1, offset = read_int8(data, offset)
    b_size, offset = read_uint32(data, offset)
    b_address, offset = read_uint32(data, offset)

    a2 = []
    if b_address + b_size * 12 > len(data):
        raise ValueError(
            "Array size or address for structure B is out of the data bounds"
        )
    else:
        for _ in range(b_size):
            struct_b, _ = read_structure_B(data, b_address + _ * 7)
            a2.append(struct_b)

    a3, offset = read_structure_C(data, offset)
    a4, offset = read_double(data, offset)
    a5, offset = read_double(data, offset)

    return {"A1": a1, "A2": a2, "A3": a3, "A4": a4, "A5": a5}, offset


def main(data):
    if data[:5] != b"\x7cRXLP":
        raise ValueError("Invalid data signature")

    offset = 5  # skip signature
    result, _ = read_structure_A(data, offset)
    return result
