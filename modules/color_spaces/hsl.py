import numpy as np


class Hsl:
    @classmethod
    def to_rgb_pixmap(cls, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(hsl):
            H, S, L = hsl[0] * 359, hsl[1], hsl[2]
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
            r_prime, g_prime, b_prime = rgb_dict[H // 60]
            brg = [b_prime + m, r_prime + m, g_prime + m]
            return brg

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]

    @classmethod
    def from_rgb_pixmap(cls, pixmap):
        height = len(pixmap)
        width = len(pixmap[0])

        def values(rgb):
            b, r, g = rgb[0], rgb[1], rgb[2]
            cmax = max(r, g, b)
            cmin = min(r, g, b)
            delta = cmax - cmin
            L = (cmax + cmin) / 2
            H = 0
            S = 0
            if delta != 0:
                S = delta / (1 - np.abs(2 * L - 1))
                H = 60 / 359
                if cmax == r:
                    H *= np.mod((g - b) / delta, 6)
                elif cmax == g:
                    H *= (b - r) / delta + 2
                elif cmax == b:
                    H *= (r - g) / delta + 4
            hsl = [H, S, L]
            return hsl

        return [[values(pixmap[i][j]) for j in range(width)] for i in range(height)]
