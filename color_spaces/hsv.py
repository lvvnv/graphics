from color_spaces.colorspace import ColorSpace
import numpy as np


class Hsv(ColorSpace):
    def from_this(self, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(hsv):
            H = hsv[0] / 255 * 359
            S = hsv[1] / 255
            V = hsv[2] / 255
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
            r_prime, g_prime, b_prime = rgb_dict[H // 6]
            rgb = [(r_prime + m) * 255, (g_prime + m) * 255, (b_prime + m) * 255]
            return rgb

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]

    def to_this(self, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(rgb):
            r_prime = rgb[0] / 255
            g_prime = rgb[1] / 255
            b_prime = rgb[2] / 255
            cmax = max(r_prime, g_prime, b_prime)
            cmin = min(r_prime, g_prime, b_prime)
            delta = cmax - cmin
            V = cmax
            H = 0
            S = 0
            if cmax != 0:
                S = delta / cmax
            if delta != 0:
                H = 60 / 359
                if cmax == r_prime:
                    H *= np.mod((g_prime - b_prime) / delta, 6)
                if cmax == g_prime:
                    H *= (b_prime - r_prime) / delta + 2
                if cmax == b_prime:
                    H *= (r_prime - g_prime) / delta + 4
            hsv = [H * 255, S * 255, V * 255]
            return hsv

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]
