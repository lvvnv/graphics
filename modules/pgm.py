import array

image_paint_path = "../images/paint.pgm"
image_sample_path = "../images/sample_640×426.pgm"


# P5
def read_pgm(file):
    header = file.readline()
    assert header[:2] == b'P5'
    width, height = [int(x) for x in file.readline().split()]
    depth = file.readline(3)
    return [[ord(file.read(1)) for _ in range(width)] for _ in range(height)], width, height


def create_pgm(pixel_map, path=image_paint_path):
    header = b'P5\n'
    size = bytes(f"{len(pixel_map[0])} {len(pixel_map)}\n", encoding='utf-8')
    depth = b'255'
    f = open(path, 'wb')
    f.write(header)
    f.write(size)
    f.write(depth)
    buff = array.array('B')
    for row in pixel_map:
        for c in row:
            buff.append(int(c))
    buff.tofile(f)
    f.close()
