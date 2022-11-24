from modules.color_spaces.colorspace import Colorspace
import numpy as np


class YCbCr709:
    @classmethod
    def to_rgb_pixmap(cls, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(ycbcr):
            pure_ycbcr = [ycbcr[0], ycbcr[1] - 0.5, ycbcr[2] - 0.5]
            matrix = np.array([[1.0, 0.0, 1.5748], [1.0, -0.1873, -0.4681], [1.0, 1.8556, 0.0]])
            rgb = matrix.dot(pure_ycbcr)
            brg = [rgb[2], rgb[0], rgb[1]]
            return brg

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]

    @classmethod
    def from_rgb_pixmap(cls, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(brg):
            rgb = [brg[1], brg[2], brg[0]]
            matrix = np.array([[0.2126, 0.7152, 0.0722], [-0.1146, -0.3854, 0.5], [0.5, -0.4542, -0.0458]])
            pure_ycbcr = matrix.dot(rgb)
            return [pure_ycbcr[0], pure_ycbcr[1] + 0.5, pure_ycbcr[2] + 0.5]

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]


