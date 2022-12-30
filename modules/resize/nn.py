class NearestNeighbours:
    @classmethod
    def convert_image_ppm(cls, raster_map, width, height):
        if raster_map is None:
            print("no raster map")
            return
        percentage_y = height / len(raster_map)
        percentage_x = width / len(raster_map[0])
        new_raster_map = []

        """
        Initialization
        """
        for y in range(height):
            new_raster_map.append([])
            for x in range(width):
                new_raster_map[y].append([0, 0, 0])

        """
        Resizing
        """
        for y in range(height):
            for x in range(width):
                y1 = round(min(y / percentage_y, len(raster_map) - 1))
                x1 = round(min(x / percentage_x, len(raster_map[0]) - 1))
                new_raster_map[y][x] = raster_map[y1][x1]
        return new_raster_map

    @classmethod
    def convert_image_pgm(cls, raster_map, width, height):
        if raster_map is None:
            print("no raster map")
            return
        percentage_y = height / len(raster_map)
        percentage_x = width / len(raster_map[0])
        new_raster_map = []

        """
        Initialization
        """
        for y in range(height):
            new_raster_map.append([])
            for x in range(width):
                new_raster_map[y].append(0)

        """
        Resizing
        """
        for y in range(height):
            for x in range(width):
                y1 = round(min(y / percentage_y, len(raster_map) - 1))
                x1 = round(min(x / percentage_x, len(raster_map[0]) - 1))
                new_raster_map[y][x] = raster_map[y1][x1]
        return new_raster_map



"""
saved variant with interpolation


        for y in range(len(raster_map)):
            quantities.append([])
            for x in range(len(raster_map[0])):
                y1 = round(min(y * percentage_y, height - 1))
                x1 = round(min(x * percentage_x, width - 1))
                new_raster_map_values[y1][x1][0] += raster_map[y][x][0]
                new_raster_map_values[y1][x1][1] += raster_map[y][x][1]
                new_raster_map_values[y1][x1][2] += raster_map[y][x][2]
                quantities[y1][x1] += 1
        for y in range(height):
            for x in range(width):
                if quantities[y][x] == 0:
                    y1 = max(y - 1, 0)
                    y2 = min(y + 1, height - 1)
                    x1 = max(x - 1, 0)
                    x2 = min(x + 1, width - 1)
                    potential_comps = [
                        (quantities[y1][x1], y1, x1),
                        (quantities[y2][x1], y2, x1),
                        (quantities[y1][x2], y1, x2),
                        (quantities[y2][x2], y2, x2)
                    ]
                    for i in range(len(potential_comps)):
                        if potential_comps[i][0] != 0:
                            new_raster_map_values[y][x] = new_raster_map_values[potential_comps[i][1]][potential_comps[i][2]]
                            quantities[y][x] = quantities[potential_comps[i][1]][potential_comps[i][2]]
                for comp in range(3):
                    new_raster_map[y][x][comp] = new_raster_map_values[y][x][comp] / quantities[y][x]

"""
