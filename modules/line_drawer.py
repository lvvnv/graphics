import numpy as np


class LineDrawer:
    def __init__(self, b, g, r, _type, transparency, width):
        self.raster_map = None
        self.b = b
        self.g = g
        self.r = r
        self._type = _type
        self.transparency = transparency
        self.width = width

    def draw(self, raster_map, point_1, point_2):
        self.raster_map = raster_map
        if self.raster_map is None or point_1 is None or point_2 is None:
            return raster_map
        self.x1, self.y1 = point_1
        self.x2, self.y2 = point_2
        for y in range(len(self.raster_map)):
            row = self.raster_map[y]
            for x in range(len(row)):
                distance, on_segment = self.on_line(x, y, self.width)
                if self._type == "ppm":
                    self.set_color_for_ppm(x, y, on_segment, distance)
                else:
                    self.set_color_for_pgm(x, y, on_segment, distance)
        return self.raster_map

    def on_line(self, x0, y0, width):
        a = 1 / (self.x2 - self.x1)
        b = - 1 / (self.y2 - self.y1)
        c = - self.x1 * a - self.y1 * b
        line_equation = lambda x, y: a * x + b * y + c
        distance = abs(line_equation(x0, y0)) / np.sqrt(a ** 2 + b ** 2)
        on_segment = (min(self.x1, self.x2) <= x0 <= max(self.x1, self.x2)) and (min(self.y1, self.y2) <= y0 <= max(self.y1, self.y2))
        return distance, distance <= width / 2 and on_segment

    def set_color_for_ppm(self, x, y, on_segment, distance):
        new_color = self.raster_map[y][x]
        if on_segment:
            if abs(distance - self.width / 2) < 1:
                c = 1 - abs(distance - self.width / 2)
                new_color = [self.b, self.r, self.g]
                new_color = [new_color[i] * (1 - c) + self.raster_map[y][x][i] * c for i in range(3)]
            elif distance <= self.width / 2:
                new_color = [self.b, self.r, self.g]
        t = self.transparency / 100
        new_color = [new_color[i] * (1 - t) + self.raster_map[y][x][i] * t for i in range(3)]
        self.raster_map[y][x] = new_color

    def set_color_for_pgm(self, x, y, on_segment, distance):
        gray = rgb_to_gray(self.r, self.g, self.b)
        new_color = self.raster_map[y][x]
        if on_segment:
            if abs(distance - self.width / 2) < 1:
                c = 1 - abs(distance - self.width / 2)
                new_color = gray * (1 - c) + self.raster_map[y][x] * c
            elif distance <= self.width / 2:
                new_color = gray
        t = self.transparency / 100
        new_color = new_color * (1 - t) + self.raster_map[y][x] * t
        self.raster_map[y][x] = new_color


def rgb_to_gray(r, g, b):
    return 0.2989 * r + 0.5870 * g + 0.1140 * b