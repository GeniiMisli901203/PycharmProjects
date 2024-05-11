import struct

def read_double(data, offset):
    if offset + 8 > len(data):
        raise ValueError("Offset is beyond the length of the data")
    return struct.unpack_from('>d', data, offset)[0], offset + 8

def read_uint8(data, offset):
    if offset + 1 > len(data):
        raise ValueError("Offset is beyond the length of the data")
    return struct.unpack_from('>B', data, offset)[0], offset + 1

def read_float(data, offset):
    if offset + 4 > len(data):
        raise ValueError("Offset is beyond the length of the data")
    return struct.unpack_from('>f', data, offset)[0], offset + 4

def read_int8(data, offset):
    if offset + 1 > len(data):
        raise ValueError("Offset is beyond the length of the data")
    return struct.unpack_from('>b', data, offset)[0], offset + 1

def read_int16(data, offset):
    if offset + 2 > len(data):
        raise ValueError("Offset is beyond the length of the data")
    return struct.unpack_from('>h', data, offset)[0], offset + 2

def read_uint16(data, offset):
    if offset + 2 > len(data):
        raise ValueError("Offset is beyond the length of the data")
    return struct.unpack_from('>H', data, offset)[0], offset + 2

def read_int32(data, offset):
    if offset + 4 > len(data):
        raise ValueError("Offset is beyond the length of the data")
    return struct.unpack_from('>i', data, offset)[0], offset + 4

def read_int64(data, offset):
    if offset + 8 > len(data):
        raise ValueError("Offset is beyond the length of the data")
    return struct.unpack_from('>q', data, offset)[0], offset + 8

def read_uint64(data, offset):
    if offset + 8 > len(data):
        raise ValueError("Offset is beyond the length of the data")
    return struct.unpack_from('>Q', data, offset)[0], offset + 8

def read_uint32(data, offset):
    if offset + 4 > len(data):
        raise ValueError("Offset is beyond the length of the data")
    return struct.unpack_from('>I', data, offset)[0], offset + 4

def read_struct_D(data, offset):
    d1, offset = read_double(data, offset)
    d2, offset = read_uint8(data, offset)
    d3, offset = read_float(data, offset)

    d4_size, offset = read_uint32(data, offset)
    d4_address, offset = read_uint32(data, offset)

    if d4_address + d4_size > len(data):
        raise ValueError("Размер массива или адрес находятся за пределами")

    d4 = struct.unpack_from(f'>{d4_size}b', data, d4_address)
    d5, offset = read_float(data, offset)
    d6, offset = read_int8(data, offset)

    d7_size, offset = read_uint32(data, offset)
    d7_address, offset = read_uint16(data, offset)

    if d7_size > (len(data) - d7_address) // 2:
        print(f"Неверный размер для массива int16: size={d7_size}")
        raise ValueError("Неверный размер для массива int16")

    if d7_address + d7_size * 2 > len(data):
        print(f"Невесива int16: address={d7_address}")
        raise ValueError("Неверный адрес для массива int16")

    d7 = struct.unpack_from(f'>{d7_size}h', data, d7_address)
    return {'D1': d1, 'D2': d2, 'D3': d3, 'D4': list(d4), 'D5': d5,
            'D6': d6, 'D7': list(d7)}, offset


def main(data):
    result, _ = read_struct_D(data, 0)
    return result

