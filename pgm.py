import array

import numpy as np

image_paint_path = "./images/paint.pgm"
image_sample_path = "./images/sample_640×426.pgm"


# P5
def read_pgm(file):
    header = file.readline()
    assert header[:2] == b'P5'
    width, height = [int(i) for i in file.readline()[:7].split()]
    return [[ord(file.read(1)) for _ in range(width)] for _ in range(height)]


def create_pgm(pixel_map):
    header = b'P5\n'
    size = bytes(f"{len(pixel_map[0])} {len(pixel_map)}\n", encoding='utf-8')
    depth = b'255\n'
    f = open(image_paint_path, 'wb')
    f.write(header)
    f.write(size)
    f.write(depth)
    buff = array.array('B')
    for row in pixel_map:
        for c in row:
            buff.append(int(c))
    buff.tofile(f)
    f.close()


def create_raster_sample_map(pgm_path):
    if pgm_path is None:
        pgm_path = image_sample_path
    f = open(pgm_path, 'rb')
    im = read_pgm(f)
    f.close()
    im = np.array(im)
    return im
