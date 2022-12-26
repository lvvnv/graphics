import copy

import numpy as np

from modules.color_spaces.hsv import Hsv


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
        def otsu_pgm(raster_map):
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
            return Filter.threshold(raster_map, "pgm", max_t)

        if _type == "pgm":
            return otsu_pgm(raster_map)
        if _type == "ppm":
            raster_map = raster_map_to_pgm(raster_map)
            raster_map = otsu_pgm(raster_map)
            return raster_map_to_ppm(raster_map)
        return raster_map

    @staticmethod
    def median(raster_map, _type, radius):
        if _type == "pgm":
            new_raster_map = copy.copy(raster_map)
            for y in range(len(raster_map)):
                for x in range(len(raster_map[y])):
                    p = get_variate_values(raster_map, x, y, radius)
                    k = len(p) // 2
                    if abs(p[k] - raster_map[y][x]) < abs(p[len(p) - k + 1] - raster_map[y][x]):
                        new_raster_map[y][x] = p[k]
                    else:
                        new_raster_map[y][x] = p[len(p) - k + 1]
            return new_raster_map
        if _type == "ppm":
            new_raster_map = copy.copy(raster_map)
            for y in range(len(raster_map)):
                for x in range(len(raster_map[y])):
                    p = get_variate_values_ppm(raster_map, x, y, radius)
                    k = len(p) // 2
                    if abs(rgb_to_gray_pixel(p[k]) - rgb_to_gray_pixel(raster_map[y][x])) < abs(
                            rgb_to_gray_pixel(p[len(p) - k + 1]) - rgb_to_gray_pixel(raster_map[y][x])):
                        new_raster_map[y][x] = p[k]
                    else:
                        new_raster_map[y][x] = p[len(p) - k + 1]
                if y % 10 == 0:
                    print(f'{y}/{len(raster_map)}')
            return new_raster_map
        return raster_map

    @staticmethod
    def gaussian_filter(raster_map, _type, sigma):
        radius = sigma * 3
        new_raster_map = copy.copy(raster_map)
        if _type == "pgm":
            for y in range(radius, len(raster_map) - radius - 1):
                for x in range(radius, len(raster_map[y]) - radius - 1):
                    a = raster_map[(y - radius):(y + radius + 1), (x - radius):(x + radius + 1)]
                    new_raster_map[y][x] = np.average(np.array(a), weights=np.array(gauss(sigma)))
        if _type == "ppm":
            for y in range(radius, len(raster_map) - radius - 1):
                for x in range(radius, len(raster_map[y]) - radius - 1):
                    a = Hsv.from_rgb_pixmap(raster_map[(y - radius):(y + radius + 1), (x - radius):(x + radius + 1)])
                    hs = []
                    ss = []
                    vs = []
                    for a_y in a:
                        hs_row = []
                        ss_row = []
                        vs_row = []
                        for a_x in a_y:
                            hs_row.append(a_x[0])
                            ss_row.append(a_x[1])
                            vs_row.append(a_x[2])
                        hs.append(hs_row)
                        ss.append(ss_row)
                        vs.append(vs_row)
                    a_h = np.average(np.array(hs), weights=np.array(gauss(sigma)))
                    a_s = np.average(np.array(ss), weights=np.array(gauss(sigma)))
                    a_v = np.average(np.array(vs), weights=np.array(gauss(sigma)))
                    new_raster_map[y][x] = Hsv.to_rgb_pixmap([[[a_h, a_s, a_v]]])[0][0]
                if y % 10 == 0:
                    print(f'{y}/{len(raster_map)}')
        return new_raster_map

    @staticmethod
    def box_blur_filter(raster_map, _type, radius):
        new_raster_map = copy.copy(raster_map)
        if _type == "pgm":
            for y in range(radius, len(raster_map) - radius - 1):
                for x in range(radius, len(raster_map[y]) - radius - 1):
                    a = raster_map[(y - radius):(y + radius + 1), (x - radius):(x + radius + 1)]
                    new_raster_map[y][x] = np.average(np.array(a))
        if _type == "ppm":
            for y in range(radius, len(raster_map) - radius - 1):
                for x in range(radius, len(raster_map[y]) - radius - 1):
                    a = Hsv.from_rgb_pixmap(raster_map[(y - radius):(y + radius + 1), (x - radius):(x + radius + 1)])
                    hs = []
                    ss = []
                    vs = []
                    for a_y in a:
                        hs_row = []
                        ss_row = []
                        vs_row = []
                        for a_x in a_y:
                            hs_row.append(a_x[0])
                            ss_row.append(a_x[1])
                            vs_row.append(a_x[2])
                        hs.append(hs_row)
                        ss.append(ss_row)
                        vs.append(vs_row)
                    a_h = np.average(np.array(hs))
                    a_s = np.average(np.array(ss))
                    a_v = np.average(np.array(vs))
                    new_raster_map[y][x] = Hsv.to_rgb_pixmap([[[a_h, a_s, a_v]]])[0][0]
                if y % 10 == 0:
                    print(f'{y}/{len(raster_map)}')
        return new_raster_map

    @staticmethod
    def sobel_filter(raster_map, _type):
        matrix_x = [
            [1, 0, -1],
            [2, 0, -2],
            [1, 0, -1]
        ]
        matrix_y = [
            [1, 2, 1],
            [0, 0, 0],
            [-1, -2, -1]
        ]
        new_raster_map = copy.copy(raster_map)
        if _type == "pgm":
            for y in range(1, len(raster_map) - 1):
                for x in range(1, len(raster_map[y]) - 1):
                    a = raster_map[(y - 1):(y + 2), (x - 1):(x + 2)]
                    G_x = np.sum(np.matmul(np.array(matrix_x), np.array(a)))
                    G_y = np.sum(np.matmul(np.array(matrix_y), np.array(a)))
                    new_raster_map[y][x] = np.sqrt(G_x ** 2 + G_y ** 2)
        if _type == "ppm":
            for y in range(1, len(raster_map) - 1):
                for x in range(1, len(raster_map[y]) - 1):
                    a = raster_map[(y - 1):(y + 2), (x - 1):(x + 2)]
                    for j in range(len(a)):
                        for i in range(len(a[j])):
                            b, g, r = a[j][i]
                            a[j][i] = rgb_to_gray(r, g, b)
                    G_x = np.sum(np.matmul(np.array(matrix_x), np.array(a)))
                    G_y = np.sum(np.matmul(np.array(matrix_y), np.array(a)))
                    c = np.sqrt(G_x ** 2 + G_y ** 2)
                    new_raster_map[y][x] = [c, c, c]
                if y % 10 == 0:
                    print(f'{y}/{len(raster_map)}')
        return new_raster_map

    @staticmethod
    def cas_filter(raster_map, _type, sharpness):
        new_raster_map = copy.copy(raster_map)
        if _type == "pgm":
            for y in range(1, len(raster_map) - 1):
                for x in range(1, len(raster_map[y]) - 1):
                    pixels = [raster_map[y][x], raster_map[y - 1][x], raster_map[y][x - 1], raster_map[y + 1][x], raster_map[y][x + 1]]
                    min_g = min(pixels)
                    max_g = max(pixels)
                    d_min_g = min_g
                    d_max_g = 1 - max_g
                    A = np.sqrt(min(d_min_g, d_max_g) / max_g)
                    developer_maximum = lerp(-0.125, -0.2, sharpness)
                    w = A * developer_maximum
                    output = (sum(pixels[1:]) * w + pixels[0]) / (w * 4 + 1)
                    new_raster_map[y][x] = output
        if _type == "ppm":
            for y in range(1, len(raster_map) - 1):
                for x in range(1, len(raster_map[y]) - 1):
                    output = []
                    for i in range(3):
                        pixels = [raster_map[y][x][i], raster_map[y - 1][x][i], raster_map[y][x - 1][i], raster_map[y + 1][x][i], raster_map[y][x + 1][i]]
                        min_g = min(pixels)
                        max_g = max(pixels)
                        d_min_g = min_g
                        d_max_g = 1 - max_g
                        if max_g == 0:
                            output.append(raster_map[y][x][i])
                            continue
                        A = np.sqrt(min(d_min_g, d_max_g) / max_g)
                        developer_maximum = lerp(-0.125, -0.2, sharpness)
                        w = A * developer_maximum
                        output.append(float((sum(pixels[1:]) * w + pixels[0]) / (w * 4 + 1)))
                    new_raster_map[y][x] = output
        return new_raster_map


def rgb_to_gray_pixel(pixel):
    return rgb_to_gray(pixel[2], pixel[1], pixel[0])


def rgb_to_gray(r, g, b):
    return 0.2989 * r + 0.5870 * g + 0.1140 * b


def raster_map_to_pgm(raster_map):
    raster_map_pgm = []
    for y in range(len(raster_map)):
        raster_map_pgm.append([])
        for x in range(len(raster_map[y])):
            b, g, r = raster_map[y][x]
            raster_map_pgm[y].append(rgb_to_gray(r, g, b))
    return raster_map_pgm


def raster_map_to_ppm(raster_map):
    raster_map_ppm = []
    for y in range(len(raster_map)):
        raster_map_ppm.append([])
        for x in range(len(raster_map[y])):
            c = raster_map[y][x]
            raster_map_ppm[y].append([c, c, c])
    return raster_map_ppm


def get_variate_values(raster_map, x, y, radius):
    variate_values = []
    height = len(raster_map)
    width = len(raster_map[0])
    for j in range(y - radius, y + radius + 1):
        for i in range(x - radius, x + radius + 1):
            if j < 0 or i < 0 or j >= height or i >= width:
                continue
            variate_values.append(raster_map[j][i])
    return sorted(variate_values)


def get_variate_values_ppm(raster_map, x, y, radius):
    hs = []
    ss = []
    vs = []
    height = len(raster_map)
    width = len(raster_map[0])
    for j in range(y - radius, y + radius + 1):
        for i in range(x - radius, x + radius + 1):
            if j < 0 or i < 0 or j >= height or i >= width:
                continue
            h, s, v = Hsv.from_rgb_pixmap([[raster_map[j][i]]])[0][0]
            hs.append(h)
            ss.append(s)
            vs.append(v)
    variate_values = []
    hs = sorted(hs)
    ss = sorted(ss)
    vs = sorted(vs)
    for i in range(len(hs)):
        rgb = Hsv.to_rgb_pixmap([[[hs[i], ss[i], vs[i]]]])[0][0]
        variate_values.append(rgb)
    return variate_values


def gauss(sigma):
    l = 3 * sigma * 2 + 1
    ax = np.linspace(-(l - 1) / 2., (l - 1) / 2., l)
    gauss = np.exp(-0.5 * np.square(ax) / np.square(sigma))
    kernel = np.outer(gauss, gauss)
    return kernel / np.sum(kernel)


def lerp(a, b, t):
    return a + t * (b - a)
