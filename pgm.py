import numpy as np


# P5
def read_pgm(file):
    header = file.readline()
    assert header[:2] == b'P5'
    width, height = [int(i) for i in file.readline()[:7].split()]
    return [[ord(file.read(1)) for _ in range(width)] for _ in range(height)]


def crete_raster_sample_map():
    pgm_path = "./sample_640×426.pgm"
    f = open(pgm_path, 'rb')
    im = read_pgm(f)
    f.close()
    im = np.array(im)
    return im
