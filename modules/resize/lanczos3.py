import math


def func(x):
    a = 3
    if x == 0:
        return 1
    elif -a <= x < a:
        return a * math.sin(math.pi * x) * math.sin(math.pi * x / a) / (math.pi ** 2 * x ** 2)
    else:
        return 0


class Lanczos3:
    @classmethod
    def convert_image_ppm(cls, raster_map, width, height):
        if raster_map is None:
            print("No raster map")
            return
        new_raster_map = []
        for y in range(height):
            new_raster_map.append([])
            for x in range(width):
                new_raster_map[y].append([0, 0, 0])

        og_height = len(raster_map)
        og_width = len(raster_map[0])
        x_ratio = og_width / width
        y_ratio = og_height / height

        for i in range(height):
            for j in range(width):
                x = min(og_width - 1, int(x_ratio * j))
                y = min(og_height - 1, int(y_ratio * i))

                x_diff = x_ratio * j - x
                y_diff = y_ratio * i - y

                color = [0, 0, 0]

                for k in range(-2, 3):
                    for l in range(-2, 3):
                        if not (0 <= x + k < og_width and 0 <= y + l < og_height):
                            continue

                        for e in range(3):
                            color[e] += raster_map[y + l][x + k][e] * func(x_diff - k) * func(y_diff - l)
                new_raster_map[i][j] = color.copy()
        return new_raster_map

    @classmethod
    def convert_image_pgm(cls, raster_map, width, height):
        if raster_map is None:
            print("No raster map")
            return
        new_raster_map = []
        for y in range(height):
            new_raster_map.append([])
            for x in range(width):
                new_raster_map[y].append(0)

        og_height = len(raster_map)
        og_width = len(raster_map[0])
        x_ratio = og_width / width
        y_ratio = og_height / height

        for i in range(height):
            for j in range(width):
                x = min(og_width - 1, int(x_ratio * j))
                y = min(og_height - 1, int(y_ratio * i))

                x_diff = x_ratio * j - x
                y_diff = y_ratio * i - y

                color = 0

                for k in range(-2, 3):
                    for l in range(-2, 3):
                        if not (0 <= x + k < og_width and 0 <= y + l < og_height):
                            continue

                        color += raster_map[y + l][x + k] * func(x_diff - k) * func(y_diff - l)
                new_raster_map[i][j] = color
        return new_raster_map
