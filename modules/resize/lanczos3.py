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
                new_raster_map.append([0, 0, 0])
