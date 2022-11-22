import array

image_paint_path = "../images/paint.ppm"
image_sample_path = "../images/sample_640×426.ppm"


# P6
def read_ppm(file):
    header = file.readline()
    assert header[:2] == b'P6'
    width, height = [int(i) for i in file.readline().split()]
    depth = file.readline(3)
    return [[[ord(file.read(1)) for _ in range(3)] for _ in range(width)] for _ in range(height)], width, height


def create_ppm(pixel_map, path=image_paint_path):
    header = b'P6\n'
    size = bytes(f"{len(pixel_map[0])} {len(pixel_map)}\n", encoding='utf-8')
    depth = b'255\n'
    f = open(path, 'wb')
    f.write(header)
    f.write(size)
    f.write(depth)
    buff = array.array('B')
    for row in pixel_map:
        for c in row:
            for k in c:
                buff.append(int(k))
    buff.tofile(f)
    f.close()

