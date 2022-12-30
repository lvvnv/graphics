import numpy as np

class PngFilter:
    def __init__(self, raw_data, color_type):
        self.bpp = 3 if color_type == 2 else 1
        self.filters = raw_data[:, 0]
        self.data = raw_data[:, 1:]
        self.height = len(self.data)
        self.width = len(self.data[0])
        self.filtered_data = self.data.copy()
        self.initUI()

    def initUI(self):
        for i in range(self.height):
            self.filter(i, self.filters[i])

    def filter(self, row_num, num):
        if num == 1:
            self.filter_1(row_num)
        elif num == 2:
            self.filter_2(row_num)
        elif num == 3:
            self.filter_3(row_num)
        elif num == 4:
            self.filter_4(row_num)

    def prior(self, row_num, i):
        return 0 if row_num == 0 else self.filtered_data[row_num - 1][i]

    def filter_1(self, row_num):
        for i in range(self.bpp, self.width):
            self.filtered_data[row_num][i] = \
                (self.data[row_num][i] + self.filtered_data[row_num][i - self.bpp]) % 256

    def filter_2(self, row_num):
        for i in range(self.bpp, self.width):
            self.filtered_data[row_num][i] = \
                (self.data[row_num][i] + self.prior(row_num, i)) % 256

    def filter_3(self, row_num):
        for i in range(self.bpp, self.width):
            self.filtered_data[row_num][i] = \
                (self.data[row_num][i] + np.floor(
                    (self.filtered_data[row_num][i - self.bpp] + self.prior(row_num, i)) / 2)) % 256

    def filter_4(self, row_num):
        def paeth(a, b, c):
            p = a + b - c
            pa = np.abs(p - a)
            pb = np.abs(p - b)
            pc = np.abs(p - c)
            if pa <= pb and pa <= pc:
                return a
            elif pb <= pc:
                return b
            else:
                return c

        for i in range(self.bpp, self.width):
            self.filtered_data[row_num][i] = (self.data[row_num][i] +
                 paeth(self.filtered_data[row_num][i - self.bpp],
                       self.prior(row_num, i), self.prior(row_num, i - self.bpp))) % 256