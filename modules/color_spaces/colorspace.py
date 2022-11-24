import numpy as np


class Colorspace:
    @classmethod
    def to_rgb_pixmap(cls, pixmap, colorspace):
        return np.array(colorspace.to_rgb_pixmap(np.array(pixmap) / 255)) * 255

    @classmethod
    def from_rgb_pixmap(cls, pixmap, colorspace):
        return np.array(colorspace.from_rgb_pixmap(np.array(pixmap) / 255)) * 255
