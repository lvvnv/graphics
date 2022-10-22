from color_spaces.colorspace import ColorSpace
import numpy as np


class YCbCr709(ColorSpace):
    def from_this(self, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(ycbcr):
            matrix = np.array([[1.0, 0.0, 1.5748], [1.0, -0.1873, -0.4681], [1.0, 1.8556, 0.0]])
            return matrix.dot(ycbcr)

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]

    def to_this(self, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(rgb):
            matrix = np.array([[0.2126, 0.7152, 0.0722], [-0.1146, -0.3854, 0.5], [0.5, -0.4542, -0.0458]])
            return matrix.dot(rgb)

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]


