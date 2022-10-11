import numpy as np


# P6
def read_ppm(file):
    header = file.readline()
    assert header[:2] == b'P6'
    width, height = [int(i) for i in file.readline()[:7].split()]
    return [[[ord(file.read(1)) for _ in range(3)] for _ in range(width)] for _ in range(height)]


def crete_raster_sample_map():
    pgm_path = "./sample_640×426.ppm"
    f = open(pgm_path, 'rb')
    im = read_ppm(f)
    f.close()
    im = np.array(im)
    return im
