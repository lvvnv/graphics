import zlib
import numpy as np

from modules.png_filter import PngFilter


def read_png(file):
    header = file.read(8)
    assert header == b'\x89PNG\r\n\x1a\n'
    f = file.read()

    ihdr_pos = f.find(b'IHDR')

    width = int.from_bytes(f[ihdr_pos+4:ihdr_pos+8], "big")
    height = int.from_bytes(f[ihdr_pos+8:ihdr_pos+12], "big")
    bit_depth = int(f[ihdr_pos+12])
    if bit_depth != 8:
        png_exception("bit depth is not 8")
    color_type = int(f[ihdr_pos+13])
    if color_type not in [0, 2, 3]:
        png_exception("wrong color type")
    interlacing = int(f[ihdr_pos+16])
    if interlacing != 0:
        png_exception("interlacing is not supported")

    gamma_pos = f.find(b'gAMA')
    gamma = 0
    if gamma_pos != -1:
        gamma = round(100000 / int.from_bytes(f[gamma_pos+4:gamma_pos+8], "big"), 2)

    search_pos = 0
    idat = b''
    while True:
        idat_pos = f.find(b'IDAT', search_pos)
        if idat_pos == -1:
            break
        idat_len = int.from_bytes(f[idat_pos-4:idat_pos], "big")
        idat_part = f[idat_pos+4:idat_pos+4+idat_len]
        idat += idat_part
        search_pos = idat_pos + 5
    if idat == b'':
        png_exception("no data chunks")
    idat = list(zlib.decompress(idat))

    raw_data = np.resize(idat, (height, width * 3 + 1)) \
        if color_type == 2 else np.resize(idat, (height, width + 1))
    flatten_data = raw_data[:, 1:].flatten()
    if sum(raw_data[:, 0]) > 0:
        png_filter = PngFilter(raw_data, color_type)
        flatten_data = png_filter.filtered_data.flatten()

    data = np.resize(flatten_data, (height, width, 3)) \
        if color_type == 2 else np.resize(flatten_data, (height, width))

    if color_type == 3:
        palette_pos = f.find(b'PLTE')
        if palette_pos == -1:
            png_exception("no palette in palette image")
        pal_len = int.from_bytes(f[palette_pos - 4:palette_pos], "big")
        palette = np.array(list(f[palette_pos + 4:palette_pos + 4 + pal_len]))
        palette = np.resize(palette, (pal_len // 3, 3))
        data = np.array([[palette[data[i, j]] for j in range(width)] for i in range(height)])

    if len(data.shape) == 3:
        for i in range(len(data)):
            for j in range(len(data[0])):
                data[i, j] = [data[i, j, 2], data[i, j, 0], data[i, j, 1]]

    return data, width, height, gamma


def create_png(pixel_map, gamma, path):
    f = open(path, 'wb')

    header = b'\x89PNG\r\n\x1a\n'
    f.write(header)

    ihdr_size = int.to_bytes(13, 4, "big")
    ihdr_name = b'IHDR'
    width = int.to_bytes(len(pixel_map[0]), 4, "big")
    height = int.to_bytes(len(pixel_map), 4, "big")
    bit_depth = b'\x08'
    color_type = int.to_bytes(len(pixel_map.shape) * 2 - 4, 1, "big")
    other_ihdr = b'\x00\x00\x00'
    ihdr = ihdr_name + width + height + bit_depth + color_type + other_ihdr
    ihdr = ihdr_size + ihdr + crc(ihdr)
    f.write(ihdr)

    if gamma > 0:
        gama_size = int.to_bytes(4, 4, "big")
        gama = b'gAMA' + int.to_bytes(round(100000 / gamma), 4, "big")
        gama = gama_size + gama + crc(gama)
        f.write(gama)

    raster_map = pixel_map.copy()
    if len(pixel_map.shape) == 3:
        raster_map = np.array([[[pixel_map[i][j][1], pixel_map[i][j][2], pixel_map[i][j][0]]
                                for j in range(len(pixel_map[0]))] for i in range(len(pixel_map))])

    data = np.resize(raster_map.flatten(), (len(raster_map), len(raster_map[0]) * 3)) \
        if len(raster_map.shape) == 3 else np.resize(raster_map.flatten(), (len(raster_map), len(raster_map[0])))
    new_data = np.round(np.zeros((len(raster_map), len(raster_map[0]) * 3 + 1), dtype='>u1')) \
        if len(raster_map.shape) == 3 else np.round(np.zeros((len(raster_map), len(raster_map[0]) + 1), dtype='>u1'))
    new_data[:, 0] = np.zeros((len(raster_map)))
    new_data[:, 1:] = data
    compressed = zlib.compress(new_data.flatten().tobytes(), 8)
    idat_size = int.to_bytes(len(compressed), 4, "big")
    idat = b'IDAT' + compressed
    idat_crc = crc(idat)
    idat = idat_size + idat + idat_crc
    f.write(idat)

    iend = b'\x00\x00\x00\x00IEND\xaeB`\x82'
    f.write(iend)

    f.close()


def png_exception(msg):
    raise Exception("PNG exception: " + msg)


def crc(chunk):
    return int.to_bytes(zlib.crc32(chunk), 4, "big")
