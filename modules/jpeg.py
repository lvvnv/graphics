def read_jpeg(file):
    f = file.read()

    print(f)
    soi_pos = f.find(b'\xff\xd8')
    sof0_pos = f.find(b'\xff\xc0')
    sof1_pos = f.find(b'\xff\xc1')
    sof2_pos = f.find(b'\xff\xc2')
    dht_pos = f.find(b'\xff\xc4')
    dqt_pos = f.find(b'\xff\xdb')
    dri_pos = f.find(b'\xff\xdd')
    sos_pos = f.find(b'\xff\xda')
    com_pos = f.find(b'\xff\xfe')
    eoi_pos = f.find(b'\xff\xd9')

    print(soi_pos)
    print(sof0_pos)
    print(sof1_pos)
    print(sof2_pos)
    print(dht_pos)
    print(dqt_pos)
    print(dri_pos)
    print(sos_pos)
    print(com_pos)
    print(eoi_pos)

    sof_length = int.from_bytes(f[sof2_pos + 2:sof2_pos + 4], "big")
    bits_per_pixel = int.from_bytes(f[sof2_pos + 4:sof2_pos + 5], "big")
    height = int.from_bytes(f[sof2_pos + 5:sof2_pos + 7], "big")
    width = int.from_bytes(f[sof2_pos + 7:sof2_pos + 9], "big")
    components_number = int.from_bytes(f[sof2_pos + 9:sof2_pos + 10], "big")
    y = int.from_bytes(f[sof2_pos + 11:sof2_pos + 12], "big")
    cb = int.from_bytes(f[sof2_pos + 14:sof2_pos + 15], "big")
    cr = int.from_bytes(f[sof2_pos + 17:sof2_pos + 18], "big")

    print(sof_length, bits_per_pixel, height, width, components_number, y, cb, cr)

    print("--- DHT ---")
    huffman_tables = {}
    while dht_pos != -1:
        dht_length = int.from_bytes(f[dht_pos + 2:dht_pos + 4], "big")
        huffman_table_index = int.from_bytes(f[dht_pos + 4:dht_pos + 5], "big")
        entries = []
        for i in range(5, 16 + 5):
            entry = int.from_bytes(f[dht_pos + i:dht_pos + i + 1], "big")
            entries.append(entry)
        entries_sum = sum(entries)
        table_values = []
        for i in range(5 + 16, 5 + 16 + entries_sum):
            table_value = int.from_bytes(f[dht_pos + i:dht_pos + i + 1], "big")
            table_values.append(table_value)
        print(dht_length, huffman_table_index, entries_sum)
        print(f"bits {entries}")
        print(f"haffval {table_values}")

        iter = 0
        c = 0
        i = 0
        huffman_codes = []
        while iter < 16:
            iter += 1
            if entries[iter - 1] == 0:
                i += 1
                continue
            c = (2 ** i) * (c + 1)
            i = 0
            for x in range(entries[iter - 1]):
                huffman_codes.append(c)
                c += 1
        print(f"huffman_codes {huffman_codes}")

        valptr = [None for _ in range(17)]
        maxcode = [-1 for _ in range(17)]
        mincode = [None for _ in range(17)]
        j = 0
        k = -1
        while True:
            k = k + 1
            if k > 15:
                break
            if entries[k] == 0:
                maxcode[k] = -1
                continue
            valptr[k] = j
            mincode[k] = huffman_codes[j]
            j = j + entries[k] - 1
            maxcode[k] = huffman_codes[j]
            j = j + 1

        huffman_tables[huffman_table_index] = {"valptr": valptr, "maxcode": maxcode, "mincode": mincode, "table_values": table_values, "huffman_codes": huffman_codes}
        dht_pos = f.find(b'\xff\xc4', dht_pos + 1)
    print(huffman_tables)

    print("--- DQT ---")
    while dqt_pos != -1:
        dqt_length = int.from_bytes(f[dqt_pos + 2:dqt_pos + 4], "big")
        dqt_number = int.from_bytes(f[dht_pos + 4:dht_pos + 5], "big")
        quantization_table = []
        for i in range(5, 64 + 5):
            entry = int.from_bytes(f[dqt_pos + i:dqt_pos + i + 1], "big")
            quantization_table.append(entry)
        print(dqt_length, dqt_number)
        print(quantization_table)
        dqt_pos = f.find(b'\xff\xdb', dqt_pos + 1)

    print("--- SOS ---")
    while sos_pos != -1:
        sos_length = int.from_bytes(f[sos_pos + 2:sos_pos + 4], "big")
        components_number = int.from_bytes(f[sos_pos + 4:sos_pos + 5], "big")
        components = []
        for c in range(components_number):
            component_value = int.from_bytes(f[sos_pos + 5 + c * 2:sos_pos + 5 + c * 2 + 1], "big")
            component_huffman = int.from_bytes(f[sos_pos + 5 + c * 2 + 1:sos_pos + 5 + c * 2 + 2], "big")
            components.append([component_value, component_huffman])
        data_pos = sos_pos + 5 + components_number * 2 + 3
        end = f.find(b'\xff', data_pos)
        while f.find(b'\x00', end) != end + 1:
            end = f.find(b'\xff', end + 1)
        data = f[data_pos:end]
        print(sos_length, components_number, components)
        print(data)

        print(len(data))
        print(width * height)

        for component in components:
            decoded_data = []
            component_n = component[0]
            table_n = component[1]
            huffman_table = huffman_tables[table_n]

            index = 0
            while index < len(data):
                k = 0
                c = 0
                while c > huffman_table["maxcode"][k]:
                    base = int(index // 8)
                    shift = int(index % 8)
                    bit = (data[base] >> shift) & 0x1
                    index += 1
                    c = 2 * c + bit
                    k = k + 1
                else:
                    index += 1
                res = huffman_table["valptr"][k] + c - huffman_table["mincode"][k]
                val = huffman_table["table_values"][res]
                decoded_data.append(val)
            print(f"decoded_data: {decoded_data}, len: {len(decoded_data)}")
        sos_pos = f.find(b'\xff\xda', sos_pos + 1)
