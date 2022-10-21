import numpy as np
from pgm_image import PgmImage


class PpmImage:
    def __init__(self, raster_map):
        self.pixmap = raster_map

    def from_format(self, colorspace):
        return colorspace.from_this(self.pixmap)

    def to_format(self, colorspace):
        return colorspace.to_this(self.pixmap)

    def transform_from_format(self, colorspace):
        self.pixmap = self.from_format(colorspace)

    def transform_to_format(self, colorspace):
        self.pixmap = self.to_format(colorspace)

    def one_channel(self, channel):
        if channel not in (0, 1, 2):
            channel = 0
        height = len(self.pixmap)
        width = len(self.pixmap[0])
        return PgmImage([[self.pixmap[i][j][channel] for j in range(width)] for i in range(height)])
        # should return PgmImage with values of chosen channel from PpmImage map
