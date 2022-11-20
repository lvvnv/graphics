from modules.pgm_image import PgmImage


class PpmImage:
    def __init__(self, raster_map):
        self.pixmap = raster_map

    def to_rgb(self, colorspace):
        return colorspace.to_rgb_pixmap(self.pixmap)

    def from_rgb(self, colorspace):
        return colorspace.from_rgb_pixmap(self.pixmap)

    def transform_to_rgb(self, colorspace):
        self.pixmap = self.to_rgb(colorspace)

    def transform_from_rgb(self, colorspace):
        self.pixmap = self.from_rgb(colorspace)

    def one_channel_to_pgm(self, channel):
        if channel not in (0, 1, 2):
            channel = 0
        height = len(self.pixmap)
        width = len(self.pixmap[0])
        return PgmImage([[self.pixmap[i][j][channel] for j in range(width)] for i in range(height)])
