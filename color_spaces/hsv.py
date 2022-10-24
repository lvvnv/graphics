from color_spaces.colorspace import ColorSpace
import numpy as np


class Hsv(ColorSpace):
    @classmethod
    def to_rgb_pixmap(cls, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(hsv):
            H, S, V = hsv[0] * 359, hsv[1], hsv[2]
            C = V * S
            X = C * (1 - np.abs(np.mod(H / 60, 2) - 1))
            m = V - C
            rgb_dict = {
                0: (C, X, 0),
                1: (X, C, 0),
                2: (0, C, X),
                3: (0, X, C),
                4: (X, 0, C),
                5: (C, 0, X)
            }
            r_prime, g_prime, b_prime = rgb_dict[H // 60]
            rgb = [r_prime + m, g_prime + m, b_prime + m]
            return rgb

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]

    @classmethod
    def from_rgb_pixmap(cls, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(rgb):
            r, g, b = rgb[0], rgb[1], rgb[2]
            cmax = max(r, g, b)
            cmin = min(r, g, b)
            delta = cmax - cmin
            V = cmax
            H = 0
            S = 0
            if cmax != 0:
                S = delta / cmax
            if delta != 0:
                H = 60 / 359
                if cmax == r:
                    H *= np.mod((g - b) / delta, 6)
                if cmax == g:
                    H *= (b - r) / delta + 2
                if cmax == b:
                    H *= (r - g) / delta + 4
            hsv = [H, S, V]
            return hsv

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]
