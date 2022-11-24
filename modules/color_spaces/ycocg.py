from modules.color_spaces.colorspace import Colorspace
import numpy as np


class YCoCg:
    @classmethod
    def to_rgb_pixmap(cls, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(ycocg):
            pure_ycocg = [ycocg[0], ycocg[1] - 0.5, ycocg[2] - 0.5]
            matrix = np.array([[1, 1, -1], [1, 0, 1], [1, -1, -1]])
            rgb = matrix.dot(pure_ycocg)
            brg = [rgb[2], rgb[0], rgb[1]]
            return brg

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]

    @classmethod
    def from_rgb_pixmap(cls, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(brg):
            rgb = [brg[1], brg[2], brg[0]]
            matrix = np.array([[1/4, 1/2, 1/4], [1/2, 0, -1/2], [-1/4, 1/2, -1/4]])
            ycocg = matrix.dot(rgb)
            return [ycocg[0], ycocg[1] + 0.5, ycocg[2] + 0.5]

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]
