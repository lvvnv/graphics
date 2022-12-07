class Filter:

    @staticmethod
    def threshold(raster_map, _type, value=0):
        value = value / 255
        if _type == "pgm":
            for y in range(len(raster_map)):
                for x in range(len(raster_map[y])):
                    raster_map[y][x] = int(raster_map[y][x] > value)
        if _type == "ppm":
            for y in range(len(raster_map)):
                for x in range(len(raster_map[y])):
                    b, g, r = raster_map[y][x]
                    raster_map[y][x] = [0, 0, 0] if rgb_to_gray(r, g, b) < value else [1, 1, 1]
        return raster_map

    @staticmethod
    def otsu(raster_map, _type):
        if _type == "pgm":
            histogram = [0 for _ in range(256)]
            for y in range(len(raster_map)):
                for x in range(len(raster_map[y])):
                    histogram[int(raster_map[y][x] * 255)] += 1
            histogram_sum = sum(histogram)
            max_sigma = -1
            max_t = 0
            for t in range(256):
                w1 = sum(histogram[:t]) / histogram_sum
                w2 = 1 - w1
                if w1 == 0 or w2 == 0:
                    continue
                mu1 = sum([i * histogram[i] for i in range(t)]) / histogram_sum / w1
                mu2 = sum([i * histogram[i] for i in range(t, 256)]) / histogram_sum / w2
                sigma = w1 * w2 * (mu1 - mu2) ** 2
                if sigma > max_sigma:
                    max_sigma = sigma
                    max_t = t
            print(max_t)
            return Filter.threshold(raster_map, _type, max_t)
        return raster_map


def rgb_to_gray(r, g, b):
    return 0.2989 * r + 0.5870 * g + 0.1140 * b
