from modules.color_spaces.colorspace import ColorSpace


class Rgb(ColorSpace):
    @classmethod
    def to_rgb_pixmap(cls, pixmap):
        return pixmap

    @classmethod
    def from_rgb_pixmap(cls, pixmap):
        return pixmap
