from modules.color_spaces.colorspace import ColorSpace
import numpy as np


class YCoCg(ColorSpace):
    @classmethod
    def to_rgb_pixmap(cls, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(ycocg):
            matrix = np.array([[1, 1, -1], [1, 0, 1], [1, -1, -1]])
            return matrix.dot(ycocg)

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]

    @classmethod
    def from_rgb_pixmap(cls, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(rgb):
            matrix = np.array([[1/4, 1/2, 1/4], [1/2, 0, -1/2], [-1/4, 1/2, -1/4]])
            return matrix.dot(rgb)

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]
