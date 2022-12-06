import pyqtgraph as pg
import numpy as np


class Histogram(pg.GraphicsWindow):
    def __init__(self, arr):
        super().__init__()
        self.setWindowTitle('Histogram')
        self.arr = arr

    def pgm(self):
        plt1 = self.addPlot()
        y, x = np.histogram(self.arr, bins=256)
        plt1.plot(x, y, stepMode=True, fillLevel=0, brush=(255, 255, 255, 150))

    def one_channel(self, channel):
        plt1 = self.addPlot()
        y, x = np.histogram(self.arr, bins=256)
        brush = [0, 0, 0, 150]
        brush[(channel + 1) % 3] = 255
        plt1.plot(x, y, stepMode=True, fillLevel=0, brush=tuple(brush))

    def three_channels(self):
        self.resize(1500, 500)

        plt1 = self.addPlot()
        y, x = np.histogram(self.arr[:, :, 0], bins=256)
        plt1.plot(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 150))

        plt2 = self.addPlot()
        y, x = np.histogram(self.arr[:, :, 1], bins=256)
        plt2.plot(x, y, stepMode=True, fillLevel=0, brush=(255, 0, 0, 150))

        plt3 = self.addPlot()
        y, x = np.histogram(self.arr[:, :, 2], bins=256)
        plt3.plot(x, y, stepMode=True, fillLevel=0, brush=(0, 255, 0, 150))

    @classmethod
    def filter(cls, raster_map):
        if len(raster_map.shape) == 2:
            for i in range(raster_map.shape[0]):
                for j in range(raster_map.shape[1]):
                    if raster_map[i, j] < 0:
                        raster_map[i, j] = 0
                    elif raster_map[i, j] > 1:
                        raster_map[i, j] = 1
        elif len(raster_map.shape) == 3:
            for i in range(raster_map.shape[0]):
                for j in range(raster_map.shape[1]):
                    for k in range(raster_map.shape[2]):
                        if raster_map[i, j, k] < 0:
                            raster_map[i, j, k] = 0
                        elif raster_map[i, j, k] > 1:
                            raster_map[i, j, k] = 1
        return raster_map

    @classmethod
    def correction(cls, raster_map, min_value, max_value):
        multiplier = 1 / (max_value - min_value)
        if multiplier <= 0:
            return raster_map
        offset = min_value
        return cls.filter((raster_map - offset) * multiplier)

    @classmethod
    def find_borders(cls, raster_map, ignore_rate):
        arr = raster_map.flatten()
        y, x = np.histogram(arr, bins=256)
        y_sum = 0
        max_sum = sum(y) * ignore_rate / 2
        bottom_border = 0
        for i in range(len(y)):
            y_sum += y[i]
            if y_sum > max_sum:
                bottom_border = i
                break
        top_border = len(y) - 1
        y_sum = 0
        for i in range(len(y) - 1, -1, -1):
            y_sum += y[i]
            if y_sum > max_sum:
                top_border = i
                break
        return bottom_border / 255, top_border / 255
