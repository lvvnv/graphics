import math


def BSpline_basis(i, k, t, B, C):
    if k == 0:
        return 1 if (i <= t < i + 1) else 0
    weight1 = (t - i) / k
    weight2 = ((i + k) - t) / k

    b1 = (1 - B + C) * (1 - C) * BSpline_basis(i, k - 1, t, B, C)
    b2 = B * C * BSpline_basis(i + 1, k - 1, t, B, C)
    b3 = C * C * BSpline_basis(i + 2, k - 1, t, B, C)
    return weight1 * b1 + weight2 * b2 + weight1 * b3


def generate_BSpline(ctrl_points, lim, B=0, C=0.5):
    points = []
    n = len(ctrl_points)
    if n < 4:
        raise AttributeError("4 pts required for B-spline curve")
    step = 1 / (lim - 1)
    t = 0
    while t <= 1:
        p = [0, 0]
        for i in range(n):
            b = BSpline_basis(i, 3, t, B, C)
            p[0] += b * ctrl_points[i][0]
            p[1] += b * ctrl_points[i][1]

        points.append(p)
        t += step
    return points


def get_weighted_average(raster_map, x, y, _type):
    x1 = int(math.floor(x))
    y1 = int(math.floor(y))
    x2 = x1 + 1
    y2 = y1 + 1
    og_width = len(raster_map[0])
    og_height = len(raster_map)

    if x1 < 0 or x2 >= og_width or y1 < 0 or y2 >= og_height:
        return raster_map[min(max(y1, 0), og_height - 1)][min(max(x1, 0), og_width - 1)]

    c1 = raster_map[y1][x1]
    c2 = raster_map[y1][x2]
    c3 = raster_map[y2][x1]
    c4 = raster_map[y2][x2]

    weight_x = x - x1
    weight_y = y - y1
    weight1 = (1 - weight_x) * (1 - weight_y)
    weight2 = weight_x * (1 - weight_y)
    weight3 = (1 - weight_x) * weight_y
    weight4 = weight_x * weight_y

    if _type == "ppm":
        color = [
            c1[0] * weight1 + c2[0] * weight2 + c3[0] * weight3 + c4[0] * weight4,
            c1[1] * weight1 + c2[1] * weight2 + c3[1] * weight3 + c4[1] * weight4,
            c1[2] * weight1 + c2[2] * weight2 + c3[2] * weight3 + c4[2] * weight4
        ]
        return color
    else:
        color = c1 * weight1 + c2 * weight2 + c3 * weight3 + c4 * weight4
        return color


class BCspline:
    @classmethod
    def convert_image_ppm(cls, raster_map, width, height, b, c):
        if raster_map is None:
            print("No raster map")
            return
        new_raster_map = []
        for y in range(height):
            new_raster_map.append([])
            for x in range(width):
                new_raster_map[y].append([0, 0, 0])
        og_width = len(raster_map[0])
        og_height = len(raster_map)

        x_ctrl_points = []
        y_ctrl_points = []

        for y in range(og_height):
            for x in range(og_width):
                x_ctrl_points.append([x, raster_map[y][x][1]])
                y_ctrl_points.append([y, raster_map[y][x][2]])

        x_points = generate_BSpline(x_ctrl_points, width, b, c)
        y_points = generate_BSpline(y_ctrl_points, height, b, c)

        for y in range(height):
            for x in range(width):
                x0 = x_points[x][1]
                y0 = y_points[y][1]

                color = get_weighted_average(raster_map, x0, y0, "ppm")
                new_raster_map[y][x] = color
        return new_raster_map

    @classmethod
    def convert_image_pgm(cls, raster_map, width, height, b, c):
        if raster_map is None:
            print("No raster map")
            return
        new_raster_map = []
        for y in range(height):
            new_raster_map.append([])
            for x in range(width):
                new_raster_map[y].append(0)
        og_width = len(raster_map[0])
        og_height = len(raster_map)

        x_ctrl_points = []
        y_ctrl_points = []

        for y in range(og_height):
            for x in range(og_width):
                x_ctrl_points.append([x, raster_map[y][x]])
                y_ctrl_points.append([y, raster_map[y][x]])

        x_points = generate_BSpline(x_ctrl_points, width, b, c)
        y_points = generate_BSpline(y_ctrl_points, height, b, c)

        for y in range(height):
            for x in range(width):
                x0 = x_points[x][1]
                y0 = y_points[y][1]

                color = get_weighted_average(raster_map, x0, y0, "pgm")
                new_raster_map[y][x] = color
        return new_raster_map
