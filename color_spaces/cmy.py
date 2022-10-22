from color_spaces.colorspace import ColorSpace


class Cmy(ColorSpace):
    def from_this(self, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])
        return [[[1 - pixmap[i][j][k] for k in range(3)] for j in range(width)] for i in range(height)]

    def to_this(self, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])
        return [[[1 - pixmap[i][j][k] for k in range(3)] for j in range(width)] for i in range(height)]
