import random

import numpy as np


class Dithering:
    def __init__(self, raster_map, bitrate):
        self.raster_map = np.array(raster_map) / 255
        self.bitrate = bitrate
        self.height = len(raster_map)
        self.width = len(raster_map[0])

    @classmethod
    def ppm_gradient(cls, height, width, channel):
        def values(j):
            val = j / width * 255
            arr = [0, 0, 0]
            arr[channel - 1] = val
            return arr

        return [[values(j) for j in range(width)] for _ in range(height)]

    @classmethod
    def pgm_gradient(cls, height, width):
        def values(j):
            val = j / width * 255
            return val

        return [[values(j) for j in range(width)] for _ in range(height)]

    def nearest_color(self, value):
        return np.round(value * (2 ** self.bitrate - 1)) / (2 ** self.bitrate - 1)

    def ordered_pgm(self):
        M = np.array([[0, 32, 8, 40, 2, 34, 10, 42],
                      [48, 16, 56, 24, 50, 18, 58, 26],
                      [12, 44, 4, 36, 14, 46, 6, 38],
                      [60, 28, 52, 20, 62, 30, 54, 22],
                      [3, 35, 11, 43, 1, 33, 9, 41],
                      [51, 19, 59, 27, 49, 17, 57, 25],
                      [15, 47, 7, 39, 13, 45, 5, 37],
                      [63, 31, 55, 23, 61, 29, 53, 21]
                      ]) / 64

        def new_value(i, j, value):
            return self.nearest_color((M[i % 8, j % 8] - 0.5) * 2 / (2 ** self.bitrate) + value)

        return [[255 * new_value(i, j, self.raster_map[i, j]) for j in range(self.width)] for i in range(self.height)]

    def ordered_ppm(self):
        M = np.array([[0, 32, 8, 40, 2, 34, 10, 42],
                      [48, 16, 56, 24, 50, 18, 58, 26],
                      [12, 44, 4, 36, 14, 46, 6, 38],
                      [60, 28, 52, 20, 62, 30, 54, 22],
                      [3, 35, 11, 43, 1, 33, 9, 41],
                      [51, 19, 59, 27, 49, 17, 57, 25],
                      [15, 47, 7, 39, 13, 45, 5, 37],
                      [63, 31, 55, 23, 61, 29, 53, 21]
                      ]) / 64

        def new_value(i, j, value):
            return self.nearest_color((M[i % 8, j % 8] - 0.5) * 2 / (2 ** self.bitrate) + value)

        return [[[255 * new_value(i, j, self.raster_map[i, j, k]) for k in range(3)]
                 for j in range(self.width)] for i in range(self.height)]

    def random_pgm(self):
        def new_value(value):
            return self.nearest_color((random.random() - 0.5) * 2 / (2 ** self.bitrate) + value)

        return [[255 * new_value(self.raster_map[i, j]) for j in range(self.width)] for i in range(self.height)]

    def random_ppm(self):
        def new_value(value):
            return self.nearest_color((random.random() - 0.5) * 2 / (2 ** self.bitrate) + value)

        return [[[255 * new_value(self.raster_map[i, j, k]) for k in range(3)]
                 for j in range(self.width)] for i in range(self.height)]

    def floyd_steinberg_pgm(self):
        new_map = self.raster_map.copy()
        for i in range(self.height):
            for j in range(self.width):
                error = new_map[i, j] - self.nearest_color(new_map[i, j])
                if j + 1 < self.width:
                    new_map[i, j + 1] += 7 / 16 * error
                if i + 1 < self.height:
                    if j > 0:
                        new_map[i + 1, j - 1] += 3 / 16 * error
                    new_map[i + 1, j] += 5 / 16 * error
                    if j + 1 < self.width:
                        new_map[i + 1, j + 1] += 1 / 16 * error
                new_map[i, j] = self.nearest_color(new_map[i, j])

        return new_map * 255

    def floyd_steinberg_ppm(self):
        new_map = self.raster_map.copy()
        for k in range(3):
            for i in range(self.height):
                for j in range(self.width):
                    error = new_map[i, j, k] - self.nearest_color(new_map[i, j, k])
                    if j + 1 < self.width:
                        new_map[i, j + 1, k] += 7 / 16 * error
                    if i + 1 < self.height:
                        if j > 0:
                            new_map[i + 1, j - 1, k] += 3 / 16 * error
                        new_map[i + 1, j, k] += 5 / 16 * error
                        if j + 1 < self.width:
                            new_map[i + 1, j + 1, k] += 1 / 16 * error
                    new_map[i, j, k] = self.nearest_color(new_map[i, j, k])

        return new_map * 255

    def atkinson_pgm(self):
        new_map = self.raster_map.copy()
        for i in range(self.height):
            for j in range(self.width):
                error = new_map[i, j] - self.nearest_color(new_map[i, j])
                if j + 1 < self.width:
                    new_map[i, j + 1] += 1 / 8 * error
                if j + 2 < self.width:
                    new_map[i, j + 2] += 1 / 8 * error
                if i + 1 < self.height:
                    if j > 0:
                        new_map[i + 1, j - 1] += 1 / 8 * error
                    new_map[i + 1, j] += 1 / 8 * error
                    if j + 1 < self.width:
                        new_map[i + 1, j + 1] += 1 / 8 * error
                if i + 2 < self.height:
                    new_map[i + 2, j] += 1 / 8 * error
                new_map[i, j] = self.nearest_color(new_map[i, j])

        return new_map * 255

    def atkinson_ppm(self):
        new_map = self.raster_map.copy()
        for k in range(3):
            for i in range(self.height):
                for j in range(self.width):
                    error = new_map[i, j, k] - self.nearest_color(new_map[i, j, k])
                    if j + 1 < self.width:
                        new_map[i, j + 1, k] += 1 / 8 * error
                    if j + 2 < self.width:
                        new_map[i, j + 2, k] += 1 / 8 * error
                    if i + 1 < self.height:
                        if j > 0:
                            new_map[i + 1, j - 1, k] += 1 / 8 * error
                        new_map[i + 1, j, k] += 1 / 8 * error
                        if j + 1 < self.width:
                            new_map[i + 1, j + 1, k] += 1 / 8 * error
                    if i + 2 < self.height:
                        new_map[i + 2, j, k] += 1 / 8 * error
                    new_map[i, j, k] = self.nearest_color(new_map[i, j, k])

        return new_map * 255
