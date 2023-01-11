import math


class BilinearResizing:
    @classmethod
    def convert_image_ppm(cls, raster_map, width, height):
        if raster_map is None:
            print("no raster map")
            return
        new_raster_map = []

        """
        Initialization
        """
        for y in range(height):
            new_raster_map.append([])
            for x in range(width):
                new_raster_map[y].append([0, 0, 0])

        og_width = len(raster_map[0])
        og_height = len(raster_map)
        y_ratio = og_height / height
        x_ratio = og_width / width

        for y in range(height):
            for x in range(width):
                x_l, y_l = min(og_width - 1, math.floor(x_ratio * x)), min(og_height - 1, math.floor(y_ratio * y))
                x_h, y_h = min(og_width - 1, math.ceil(x_ratio * x)), min(og_height - 1, math.ceil(y_ratio * y))

                x_weight = (x_ratio * x) - x_l
                y_weight = (y_ratio * y) - y_l

                a = raster_map[y_l][x_l]
                b = raster_map[y_l][x_h]
                c = raster_map[y_h][x_l]
                d = raster_map[y_h][x_h]

                pixel = [0, 0, 0]
                for comp in range(3):
                    pixel[comp] = a[comp] * (1 - x_weight) * (1 - y_weight) + b[comp] * x_weight * (1 - y_weight) +\
                                  c[comp] * y_weight * (1 - x_weight) + d[comp] * x_weight * y_weight

                new_raster_map[y][x] = pixel
        return new_raster_map

    @classmethod
    def convert_image_pgm(cls, raster_map, width, height):
        if raster_map is None:
            print("no raster map")
            return
        new_raster_map = []

        """
        Initialization
        """
        for y in range(height):
            new_raster_map.append([])
            for x in range(width):
                new_raster_map[y].append(0)

        og_width = len(raster_map[0])
        og_height = len(raster_map)
        y_ratio = og_height / height
        x_ratio = og_width / width

        for y in range(height):
            for x in range(width):
                x_l, y_l = min(og_width - 1, math.floor(x_ratio * x)), min(og_height - 1, math.floor(y_ratio * y))
                x_h, y_h = min(og_width - 1, math.ceil(x_ratio * x)), min(og_height - 1, math.ceil(y_ratio * y))

                x_weight = (x_ratio * x) - x_l
                y_weight = (y_ratio * y) - y_l

                a = raster_map[y_l][x_l]
                b = raster_map[y_l][x_h]
                c = raster_map[y_h][x_l]
                d = raster_map[y_h][x_h]

                pixel = a * (1 - x_weight) * (1 - y_weight) + b * x_weight * (1 - y_weight) +\
                            c * y_weight * (1 - x_weight) + d * x_weight * y_weight

                new_raster_map[y][x] = pixel
        return new_raster_map
