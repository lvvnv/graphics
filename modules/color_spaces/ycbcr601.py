import numpy as np


class YCbCr601:
    @classmethod
    def to_rgb_pixmap(cls, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(ycbcr):
            pure_ycbcr = [ycbcr[0], ycbcr[1] - 0.5, ycbcr[2] - 0.5]
            matrix = np.array([[1.0, 0.0, 1.403], [1.0, -0.344, -0.714], [1.0, 1.733, 0.0]])
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
            matrix = np.array([[0.299, 0.587, 0.114], [-0.169, -0.331, 0.5], [0.5, -0.419, -0.081]])
            pure_ycbcr = matrix.dot(rgb)
            return [pure_ycbcr[0], pure_ycbcr[1] + 0.5, pure_ycbcr[2] + 0.5]

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]

