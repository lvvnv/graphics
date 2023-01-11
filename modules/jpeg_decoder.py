from collections import deque, namedtuple
from itertools import product
from math import ceil, cos, pi
from typing import Tuple

import numpy as np
from scipy.interpolate import griddata

from modules.color_spaces.ycbcr601 import YCbCr601

SOI = b'\xFF\xD8'
SOF0 = b'\xFF\xC0'
SOF2 = b'\xFF\xC2'
DHT = b'\xFF\xC4'
DQT = b'\xFF\xDB'
DRI = b'\xFF\xDD'
SOS = b'\xFF\xDA'
DNL = b'\xFF\xDC'
EOI = b'\xFF\xD9'
RST = tuple(bytes.fromhex(hex(marker)[2:]) for marker in range(0xFFD0, 0xFFD8))

inverted_zigzag = (
    (0, 0), (1, 0), (0, 1), (0, 2), (1, 1), (2, 0), (3, 0), (2, 1),
    (1, 2), (0, 3), (0, 4), (1, 3), (2, 2), (3, 1), (4, 0), (5, 0),
    (4, 1), (3, 2), (2, 3), (1, 4), (0, 5), (0, 6), (1, 5), (2, 4),
    (3, 3), (4, 2), (5, 1), (6, 0), (7, 0), (6, 1), (5, 2), (4, 3),
    (3, 4), (2, 5), (1, 6), (0, 7), (1, 7), (2, 6), (3, 5), (4, 4),
    (5, 3), (6, 2), (7, 1), (7, 2), (6, 3), (5, 4), (4, 5), (3, 6),
    (2, 7), (3, 7), (4, 6), (5, 5), (6, 4), (7, 3), (7, 4), (6, 5),
    (5, 6), (4, 7), (5, 7), (6, 6), (7, 5), (7, 6), (6, 7), (7, 7)
)

color_component = namedtuple("color_component", "name order vertical_sampling horizontal_sampling quantization_table_id repeat shape")
huffman_table = namedtuple("huffman_table", "dc ac")


class JpegDecoder:

    def __init__(self, image):

        self.raw_file = image.read()
        self.file_size = len(self.raw_file)

        self.handlers = {
            DHT: self.define_huffman_table,
            DQT: self.define_quantization_table,
            DRI: self.define_restart_interval,
            SOF0: self.start_of_frame,
            SOF2: self.start_of_frame,
            SOS: self.start_of_scan,
            EOI: self.end_of_image,
        }

        self.file_header = 2
        self.scan_finished = False
        self.scan_mode = None
        self.image_width = 0
        self.image_height = 0
        self.color_components = {}
        self.sample_shape = ()
        self.huffman_tables = {}
        self.quantization_tables = {}
        self.restart_interval = 0
        self.image_array = None
        self.result_image = None
        self.scan_count = 0

        while not self.scan_finished:
            try:
                current_byte = self.raw_file[self.file_header]
            except IndexError:
                del self.raw_file
                break

            if current_byte == 0xFF:
                my_marker = self.raw_file[self.file_header: self.file_header + 2]
                self.file_header += 2
                if (my_marker != b"\xFF\x00") and (my_marker not in RST):
                    my_handler = self.handlers.get(my_marker)
                    my_size = bytes_to_uint(self.raw_file[self.file_header: self.file_header + 2]) - 2
                    self.file_header += 2
                    if my_handler is not None:
                        my_data = self.raw_file[self.file_header: self.file_header + my_size]
                        my_handler(my_data)
                    else:
                        self.file_header += my_size
            else:
                self.file_header += 1

    def start_of_frame(self, data):
        data_size = len(data)
        data_header = 0
        mode = self.raw_file[self.file_header - 4: self.file_header - 2]
        if mode == SOF0:
            self.scan_mode = "baseline_dct"
            print("Scan mode: baseline")
        elif mode == SOF2:
            self.scan_mode = "progressive_dct"
            print("Scan mode: progressive")

        precision = data[data_header]
        data_header += 1

        self.image_height = bytes_to_uint(data[data_header: data_header + 2])
        data_header += 2

        self.image_width = bytes_to_uint(data[data_header: data_header + 2])
        data_header += 2
        print(f"Image size: {self.image_width}x{self.image_height}")

        components_amount = data[data_header]
        data_header += 1

        if components_amount == 3:
            print("Colorspace: YCbCr")
        else:
            print("Colorspace: greyscale")

        components = ("Y", "Cb", "Cr")

        for count, component in enumerate(components, start=1):
            my_id = data[data_header]
            data_header += 1
            sample = data[data_header]
            horizontal_sample = sample >> 4
            vertical_sample = sample & 0x0F
            data_header += 1
            my_quantization_table = data[data_header]
            data_header += 1

            my_component = color_component(
                name=component,
                order=count - 1,
                horizontal_sampling=horizontal_sample,
                vertical_sampling=vertical_sample,
                quantization_table_id=my_quantization_table,
                repeat=horizontal_sample * vertical_sample,
                shape=(8 * horizontal_sample, 8 * vertical_sample),
            )

            self.color_components.update({my_id: my_component})

            if count == components_amount:
                break

        sample_width = max(component.shape[0] for component in self.color_components.values())
        sample_height = max(component.shape[1] for component in self.color_components.values())
        self.sample_shape = (sample_width, sample_height)

        print(f"Sampling horizontally: {':'.join(str(component.horizontal_sampling) for component in self.color_components.values())}")
        print(f"Sampling vertically: {':'.join(str(component.vertical_sampling) for component in self.color_components.values())}")

        self.file_header += data_size

    def define_huffman_table(self, data):
        data_size = len(data)
        data_header = 0

        while data_header < data_size:
            table_destination = data[data_header]
            data_header += 1

            codes_count = {
                bit_length: count
                for bit_length, count
                in zip(range(1, 17), data[data_header: data_header + 16])
            }
            data_header += 16

            huffval_dict = {}

            for bit_length, count in codes_count.items():
                huffval_dict.update(
                    {bit_length: data[data_header: data_header + count]}
                )
                data_header += count

            huffman_tree = {}

            code = 0
            for bit_length, values_list in huffval_dict.items():
                code <<= 1
                for huffval in values_list:
                    code_string = bin(code)[2:].rjust(bit_length, "0")
                    huffman_tree.update({code_string: huffval})
                    code += 1

            self.huffman_tables.update({table_destination: huffman_tree})
            print(f"Huffman table: {table_destination & 0x0F}, {'DC' if table_destination >> 4 == 0 else 'AC'}")

        self.file_header += data_size

    def define_quantization_table(self, data):
        data_size = len(data)
        data_header = 0
        while (data_header < data_size):
            table_destination = data[data_header]
            data_header += 1

            qt_values = np.array([value for value in data[data_header: data_header + 64]], dtype="int16")
            quantization_table = undo_zigzag(qt_values)
            data_header += 64

            self.quantization_tables.update({table_destination: quantization_table})
            print(f"Quantization table: {table_destination}")
        self.file_header += data_size

    def define_restart_interval(self, data):
        self.restart_interval = bytes_to_uint(data[:2])
        self.file_header += 2

    def start_of_scan(self, data):
        data_size = len(data)
        data_header = 0
        components_amount = data[data_header]
        data_header += 1

        my_huffman_tables = {}
        my_color_components = {}
        for component in range(components_amount):
            component_id = data[data_header]
            data_header += 1
            tables = data[data_header]
            data_header += 1
            dc_table = tables >> 4
            ac_table = (tables & 0x0F) | 0x10
            my_huffman_tables.update({component_id: huffman_table(dc=dc_table, ac=ac_table)})
            my_color_components.update({component_id: self.color_components[component_id]})

        if self.scan_mode == "progressive_dct":
            spectral_selection_start = data[data_header]
            spectral_selection_end = data[data_header + 1]
            bit_position_high = data[data_header + 2] >> 4
            bit_position_low = data[data_header + 2] & 0x0F
            data_header += 3

        self.file_header += data_size

        if self.image_height == 0:
            dnl_index = self.raw_file[self.file_header:].find(DNL)
            if dnl_index != -1:
                dnl_index += self.file_header
                self.image_height = bytes_to_uint(self.raw_file[dnl_index + 4: dnl_index + 6])

        if components_amount > 1:
            self.mcu_width: int = 8 * max(component.horizontal_sampling for component in self.color_components.values())
            self.mcu_height: int = 8 * max(component.vertical_sampling for component in self.color_components.values())
            self.mcu_shape = (self.mcu_width, self.mcu_height)
        else:
            self.mcu_width: int = 8
            self.mcu_height: int = 8
            self.mcu_shape = (8, 8)

        if components_amount > 1:
            self.mcu_count_h = (self.image_width // self.mcu_width) + (
                0 if self.image_width % self.mcu_width == 0 else 1)
            self.mcu_count_v = (self.image_height // self.mcu_height) + (
                0 if self.image_height % self.mcu_height == 0 else 1)
        else:
            component = my_color_components[component_id]
            sample_ratio_h = self.sample_shape[0] / component.shape[0]
            sample_ratio_v = self.sample_shape[1] / component.shape[1]
            layer_width = self.image_width / sample_ratio_h
            layer_height = self.image_height / sample_ratio_v
            self.mcu_count_h = ceil(layer_width / self.mcu_width)
            self.mcu_count_v = ceil(layer_height / self.mcu_height)

        self.mcu_count = self.mcu_count_h * self.mcu_count_v

        if self.image_array is None:
            count_h = (self.image_width // self.sample_shape[0]) + (
                0 if self.image_width % self.sample_shape[0] == 0 else 1)
            count_v = (self.image_height // self.sample_shape[1]) + (
                0 if self.image_height % self.sample_shape[1] == 0 else 1)
            self.array_width = self.sample_shape[0] * count_h
            self.array_height = self.sample_shape[1] * count_v
            self.array_depth = len(self.color_components)
            self.image_array = np.zeros(shape=(self.array_width, self.array_height, self.array_depth), dtype="int16")

        if self.scan_count == 0:
            self.scan_amount = self.raw_file[self.file_header:].count(SOS) + 1
            print(f"Scans amount: {self.scan_amount}")

        if self.scan_mode == "baseline_dct":
            self.baseline_dct_scan(my_huffman_tables, my_color_components)
        elif self.scan_mode == "progressive_dct":
            self.progressive_dct_scan(
                my_huffman_tables,
                my_color_components,
                spectral_selection_start,
                spectral_selection_end,
                bit_position_high,
                bit_position_low
            )

    def bits_generator(self):
        bit_queue = deque()

        def get_bits(amount: int = 1, restart: bool = False) -> str:
            nonlocal bit_queue

            if restart:
                bit_queue.clear()
                self.file_header += 2

            while amount > len(bit_queue):
                next_byte = self.raw_file[self.file_header]
                self.file_header += 1

                if next_byte == 0xFF:
                    self.file_header += 1
                bit_queue.extend(
                    np.unpackbits(
                        bytearray((next_byte,))
                    )
                )

            return "".join(str(bit_queue.popleft()) for _ in range(amount))

        # Return the nested function
        return get_bits

    def baseline_dct_scan(self, huffman_tables_id, my_color_components):
        print(f"Scanning count: {self.scan_count + 1}/{self.scan_amount}")

        next_bits = self.bits_generator()

        def next_huffval() -> int:
            codeword = ""
            huffman_value = None

            while huffman_value is None:
                codeword += next_bits()
                huffman_value = huffman_table.get(codeword)

            return huffman_value

        idct = InverseDCT()
        resize = ResizeGrid()
        components_amount = len(my_color_components)
        current_mcu = 0
        previous_dc = np.zeros(components_amount, dtype="int16")
        while current_mcu < self.mcu_count:
            mcu_y, mcu_x = divmod(current_mcu, self.mcu_count_h)

            for depth, (component_id, component) in enumerate(my_color_components.items()):
                quantization_table = self.quantization_tables[component.quantization_table_id]
                if components_amount > 1:
                    my_mcu = np.zeros(shape=component.shape, dtype="int16")
                    repeat = component.repeat
                else:
                    my_mcu = np.zeros(shape=(8, 8), dtype="int16")
                    repeat = 1
                for block_count in range(repeat):
                    block = np.zeros(64, dtype="int16")

                    # DC value of the block
                    table_id = huffman_tables_id[component_id].dc
                    huffman_table: dict = self.huffman_tables[table_id]
                    huffman_value = next_huffval()

                    dc_value = bin_twos_complement(next_bits(huffman_value)) + previous_dc[depth]
                    previous_dc[depth] = dc_value
                    block[0] = dc_value

                    table_id = huffman_tables_id[component_id].ac
                    huffman_table: dict = self.huffman_tables[table_id]
                    index = 1
                    while index < 64:
                        huffman_value = next_huffval()
                        if huffman_value == 0x00:
                            break
                        zero_run_length = huffman_value >> 4
                        index += zero_run_length
                        if index >= 64:
                            break
                        ac_bit_length = huffman_value & 0x0F

                        if ac_bit_length > 0:
                            ac_value = bin_twos_complement(next_bits(ac_bit_length))
                            block[index] = ac_value
                        index += 1

                    block = undo_zigzag(block) * quantization_table
                    block = idct(block)
                    block_y, block_x = divmod(block_count, component.horizontal_sampling)
                    block_y, block_x = 8 * block_y, 8 * block_x
                    my_mcu[block_x: block_x + 8, block_y: block_y + 8] = block

                if component.shape != self.sample_shape:
                    my_mcu = resize(my_mcu, self.sample_shape)

                x = self.mcu_width * mcu_x
                y = self.mcu_height * mcu_y
                self.image_array[x: x + self.mcu_width, y: y + self.mcu_height, component.order] = my_mcu
            current_mcu += 1

            if (self.restart_interval > 0) and (current_mcu % self.restart_interval == 0) and (
                    current_mcu != self.mcu_count):
                next_bits(amount=0, restart=True)
                previous_dc[:] = 0
        self.scan_count += 1

    def progressive_dct_scan(self,
                             huffman_tables_id,
                             my_color_components,
                             spectral_selection_start,
                             spectral_selection_end,
                             bit_position_high,
                             bit_position_low):

        if (spectral_selection_start == 0) and (spectral_selection_end == 0):
            values = "dc"
        elif (spectral_selection_start > 0) and (spectral_selection_end >= spectral_selection_start):
            values = "ac"

        if bit_position_high == 0:
            refining = False
        elif (bit_position_high - bit_position_low) == 1:
            refining = True

        print(f"\nScanning count: {self.scan_count + 1}/{self.scan_amount}")

        next_bits = self.bits_generator()

        def next_huffval() -> int:
            codeword = ""
            huffman_value = None

            while huffman_value is None:
                codeword += next_bits()
                huffman_value = huffman_table.get(codeword)

            return huffman_value

        current_mcu = 0
        components_amount = len(my_color_components)

        if values == "dc":
            if not refining:
                previous_dc = np.zeros(components_amount, dtype="int16")
            while current_mcu < self.mcu_count:
                for depth, (component_id, component) in enumerate(my_color_components.items()):
                    x = (current_mcu % self.mcu_count_h) * component.shape[0]
                    y = (current_mcu // self.mcu_count_h) * component.shape[1]
                    if components_amount > 1:
                        repeat = component.repeat
                    else:
                        repeat = 1
                    for block_count in range(repeat):
                        block_y, block_x = divmod(block_count, component.horizontal_sampling)
                        delta_y, delta_x = 8 * block_y, 8 * block_x
                        if not refining:
                            table_id = huffman_tables_id[component_id].dc
                            huffman_table: dict = self.huffman_tables[table_id]
                            huffman_value = next_huffval()
                            dc_value = bin_twos_complement(next_bits(huffman_value)) + previous_dc[depth]
                            previous_dc[depth] = dc_value
                            self.image_array[x + delta_x, y + delta_y, component.order] = (dc_value << bit_position_low)
                        else:
                            new_bit = int(next_bits())
                            self.image_array[x + delta_x, y + delta_y, component.order] |= (new_bit << bit_position_low)

                current_mcu += 1
                if (self.restart_interval > 0) and (current_mcu % self.restart_interval == 0) and (current_mcu != self.mcu_count):
                    next_bits(amount=0, restart=True)
                    if not refining:
                        previous_dc[:] = 0

        elif values == "ac":
            spectral_size = (spectral_selection_end + 1) - spectral_selection_start
            (component_id, component), = my_color_components.items()
            table_id = huffman_tables_id[component_id].ac
            huffman_table: dict = self.huffman_tables[table_id]
            eob_run = 0

            def refine_ac():
                nonlocal to_refine, next_bits, bit_position_low, component
                refine_bits = next_bits(len(to_refine))
                ref_index = 0
                while to_refine:
                    ref_x, ref_y = to_refine.popleft()
                    new_bit = int(refine_bits[ref_index], 2)
                    self.image_array[ref_x, ref_y, component.order] |= new_bit << bit_position_low
                    ref_index += 1

            to_refine = deque()

            current_mcu = 0
            while current_mcu < self.mcu_count:
                x = (current_mcu % self.mcu_count_h) * 8
                y = (current_mcu // self.mcu_count_h) * 8

                index = spectral_selection_start
                while index <= spectral_selection_end:
                    huffman_value = next_huffval()
                    run_magnitute = huffman_value >> 4
                    ac_bits_length = huffman_value & 0x0F
                    if huffman_value == 0:
                        eob_run = 1
                        break
                    elif huffman_value == 0xF0:
                        zero_run = 16
                    elif ac_bits_length == 0:
                        eob_bits = next_bits(run_magnitute)
                        eob_run = (1 << run_magnitute) + int(eob_bits, 2)
                        break
                    else:
                        zero_run = run_magnitute
                    if not refining and zero_run:
                        index += zero_run
                        zero_run = 0
                    else:
                        while zero_run > 0:
                            xr, yr = inverted_zigzag[index]
                            current_value = self.image_array[x + xr, y + yr, component.order]
                            if current_value == 0:
                                zero_run -= 1
                            else:
                                to_refine.append((x + xr, y + yr))
                            index += 1

                    if ac_bits_length > 0:
                        ac_bits = next_bits(ac_bits_length)
                        ac_value = bin_twos_complement(ac_bits)
                        ac_x, ac_y = inverted_zigzag[index]
                        if refining:
                            while self.image_array[x + ac_x, y + ac_y, component.order] != 0:
                                to_refine.append((x + ac_x, y + ac_y))
                                index += 1
                                ac_x, ac_y = inverted_zigzag[index]

                        self.image_array[x + ac_x, y + ac_y, component.order] = ac_value << bit_position_low
                        index += 1
                    if refining:
                        refine_ac()

                if index > spectral_selection_end:
                    current_mcu += 1
                    if refining:
                        x = (current_mcu % self.mcu_count_h) * 8
                        y = (current_mcu // self.mcu_count_h) * 8

                if not refining:
                    current_mcu += eob_run
                    eob_run = 0

                else:
                    while eob_run > 0:
                        xr, yr = inverted_zigzag[index]
                        current_value = self.image_array[x + xr, y + yr, component.order]

                        if current_value != 0:
                            to_refine.append((x + xr, y + yr))

                        index += 1
                        if index > spectral_selection_end:
                            eob_run -= 1
                            current_mcu += 1
                            index = spectral_selection_start
                            x = (current_mcu % self.mcu_count_h) * 8
                            y = (current_mcu // self.mcu_count_h) * 8

                if refining:
                    refine_ac()

                if (self.restart_interval > 0) and (current_mcu % self.restart_interval == 0) and (
                        current_mcu != self.mcu_count):
                    next_bits(amount=0, restart=True)

        self.scan_count += 1
        if self.scan_count == self.scan_amount:
            idct = InverseDCT()
            resize = ResizeGrid()
            dct_array = self.image_array.copy()
            for component in self.color_components.values():
                quantization_table = self.quantization_tables[component.quantization_table_id]
                ratio_h = self.sample_shape[0] // component.shape[0]
                ratio_v = self.sample_shape[1] // component.shape[1]
                component_width = self.array_width // ratio_h
                component_height = self.array_height // ratio_v
                mcu_count_h = component_width // 8
                mcu_count_v = component_height // 8
                mcu_count = mcu_count_h * mcu_count_v
                for current_mcu in range(mcu_count):
                    x1 = (current_mcu % mcu_count_h) * 8
                    y1 = (current_mcu // mcu_count_h) * 8
                    x2 = x1 + 8
                    y2 = y1 + 8
                    block = dct_array[x1: x2, y1: y2, component.order]
                    block *= quantization_table
                    block = idct(block.reshape(8, 8))
                    if component.shape != self.sample_shape:
                        block = resize(block, self.sample_shape)
                        x1 *= ratio_h
                        y1 *= ratio_v
                        x2 *= ratio_h
                        y2 *= ratio_v
                    self.image_array[x1: x2, y1: y2, component.order] = block

    def end_of_image(self, data):
        self.image_array = self.image_array[0: self.image_width, 0: self.image_height, :]

        rotated = np.swapaxes(self.image_array, 0, 1)
        divided = rotated / 255.0
        result_image = [[[int(c[0] * 255.0), min(255, int(c[1] * 255.0)), int(c[2] * 255.0)] for c in row] for row in YCbCr601.to_rgb_pixmap(divided)]

        if self.array_depth == 1:
            np.clip(self.image_array, a_min=0, a_max=255, out=self.image_array)
            self.image_array = self.image_array[..., 0].astype("uint8")
            result_image = [[c for c in row] for row in np.swapaxes(self.image_array, 0, 1)]

        self.scan_finished = True
        self.result_image = result_image


class InverseDCT:
    idct_table = np.zeros(shape=(8, 8, 8, 8), dtype="float64")
    xyuv_coordinates = tuple(product(range(8), repeat=4))
    xy_coordinates = tuple(product(range(8), repeat=2))
    for x, y, u, v in xyuv_coordinates:
        Cu = 2 ** (-0.5) if u == 0 else 1.0
        Cv = 2 ** (-0.5) if v == 0 else 1.0
        idct_table[x, y, u, v] = 0.25 * Cu * Cv * cos((2 * x + 1) * pi * u / 16) * cos((2 * y + 1) * pi * v / 16)

    def __call__(self, block: np.ndarray) -> np.ndarray:
        output = np.zeros(shape=(8, 8), dtype="float64")
        for x, y in self.xy_coordinates:
            output[x, y] = np.sum(block * self.idct_table[x, y, ...], dtype="float64")
        return np.round(output).astype(block.dtype) + 128


class ResizeGrid:
    mesh_cache = {}
    indices_cache = {}

    def __call__(self, block: np.ndarray, new_shape: Tuple[int, int]) -> np.ndarray:
        old_width, old_height = block.shape
        new_width, new_height = new_shape
        key = ((old_width, old_height), (new_width, new_height))

        new_xy = self.mesh_cache.get(key)
        if new_xy is None:
            max_x = old_width - 1
            max_y = old_height - 1
            num_points_x = new_width * 1j
            num_points_y = new_height * 1j
            new_x, new_y = np.mgrid[0: max_x: num_points_x, 0: max_y: num_points_y]
            new_xy = (new_x, new_y)
            self.mesh_cache.update({key: new_xy})

        old_xy = self.indices_cache.get(key[0])
        if old_xy is None:
            xx, yy = np.indices(block.shape)
            xx, yy = xx.flatten(), yy.flatten()
            old_xy = (xx, yy)
            self.indices_cache.update({key[0]: old_xy})

        resized_block = griddata(old_xy, block.ravel(), new_xy)

        return np.round(resized_block).astype(block.dtype)


def bytes_to_uint(bytes_obj: bytes) -> int:
    return int.from_bytes(bytes_obj, byteorder="big", signed=False)


def bin_twos_complement(bits: str) -> int:
    if bits == "":
        return 0
    elif bits[0] == "1":
        return int(bits, 2)
    elif bits[0] == "0":
        bit_length = len(bits)
        return int(bits, 2) - (2 ** bit_length - 1)
    else:
        raise ValueError(f"'{bits}' is not a binary number.")


def undo_zigzag(block):
    return np.array(
        [[block[0], block[1], block[5], block[6], block[14], block[15], block[27], block[28]],
         [block[2], block[4], block[7], block[13], block[16], block[26], block[29], block[42]],
         [block[3], block[8], block[12], block[17], block[25], block[30], block[41], block[43]],
         [block[9], block[11], block[18], block[24], block[31], block[40], block[44], block[53]],
         [block[10], block[19], block[23], block[32], block[39], block[45], block[52], block[54]],
         [block[20], block[22], block[33], block[38], block[46], block[51], block[55], block[60]],
         [block[21], block[34], block[37], block[47], block[50], block[56], block[59], block[61]],
         [block[35], block[36], block[48], block[49], block[57], block[58], block[62], block[63]]],
        dtype=block.dtype
    ).T
