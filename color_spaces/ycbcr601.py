from color_spaces.colorspace import ColorSpace
import numpy as np


class YCbCr601(ColorSpace):
    def from_this(self, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(ycbcr):
            matrix = np.array([[0.2126, 0.7152, 0.0722], [-0.1146, -0.3854, 0.5], [0.5, -0.4542, -0.0458]])
            return matrix.dot(ycbcr)

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]

    def to_this(self, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(rgb):
            matrix = np.array([[0.299, 0.587, 0.114], [-0.169, -0.331, 0.5], [0.5, -0.419, -0.081]])
            return matrix.dot(rgb)

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]

