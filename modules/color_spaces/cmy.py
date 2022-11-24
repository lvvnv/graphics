import numpy as np


class Cmy:
    @classmethod
    def to_rgb_pixmap(cls, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])
        return np.array([[[1 - pixmap[i][j][k] for k in range(3)] for j in range(width)] for i in range(height)])

    @classmethod
    def from_rgb_pixmap(cls, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])
        return np.array([[[1 - pixmap[i][j][k] for k in range(3)] for j in range(width)] for i in range(height)])
