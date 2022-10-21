from color_spaces.colorspace import ColorSpace
import numpy as np


class Hsl(ColorSpace):
    def from_this(self, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(hsl):
            H = hsl[0] / 255 * 359
            S = hsl[1] / 255
            L = hsl[2] / 255
            C = (1 - np.abs(2 * L - 1)) * S
            X = C * (1 - np.abs(np.mod(H / 60, 2) - 1))
            m = L - C / 2
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
            L = (cmax + cmin) / 2
            H = 0
            S = 0
            if delta != 0:
                S = delta / (1 - np.abs(2 * L - 1))
                H = 60 / 359
                if cmax == r_prime:
                    H *= np.mod((g_prime - b_prime) / delta, 6)
                if cmax == g_prime:
                    H *= (b_prime - r_prime) / delta + 2
                if cmax == b_prime:
                    H *= (r_prime - g_prime) / delta + 4
            hsl = [H * 255, S * 255, L * 255]
            return hsl

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]
