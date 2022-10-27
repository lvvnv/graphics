from modules.color_spaces.colorspace import ColorSpace
import numpy as np


class YCbCr601(ColorSpace):
    @classmethod
    def to_rgb_pixmap(cls, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(ycbcr):
            matrix = np.array([[1.0, 0.0, 1.403], [1.0, -0.344, -0.714], [1.0, 1.733, 0.0]])
            return matrix.dot(ycbcr)

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]

    @classmethod
    def from_rgb_pixmap(cls, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(rgb):
            matrix = np.array([[0.299, 0.587, 0.114], [-0.169, -0.331, 0.5], [0.5, -0.419, -0.081]])
            return matrix.dot(rgb)

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]

