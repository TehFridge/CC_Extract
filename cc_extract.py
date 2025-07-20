import sys
import os

def decompress_nes_data(data, verbose=False):
    pos = 0
    out_size_limit = 16 + 768 * 1024  # max decompressed size limit
    
    out = bytearray()
    data_len = len(data)

    while len(out) < out_size_limit and pos < data_len:
        control_byte = data[pos]
        pos += 1

        if control_byte < 0x80:
            length = control_byte + 1
            if pos + length > data_len:
                if verbose:
                    print("Literal run exceeds data length!")
                    break
            out += data[pos:pos+length]
            pos += length
        else:
            signed_ctrl = control_byte - 256
            if pos >= data_len:
                if verbose:
                    print("Missing length byte for backreference!")
                    break
            length_byte = data[pos]
            pos += 1
            length = length_byte + 1
            copy_start = len(out) + signed_ctrl
            if copy_start < 0:
                if verbose:
                    print("Backreference before start of output buffer!")
                    break
            for i in range(length):
                out.append(out[copy_start + i])
    return out

def extract_nes_roms(input_path):
    with open(input_path, "rb") as f:
        data = f.read()

    rom_offsets = []
    pos = 0

  
    while True:
        pos = data.find(b"NES\x1A", pos)
        if pos == -1:
            break
        if pos > 0:
            rom_offsets.append(pos - 1)  
        pos += 1


    print(f"Found {len(rom_offsets)} NES ROM's.")

    
    for i in range(len(rom_offsets)):
        start = rom_offsets[i]
        end = rom_offsets[i + 1] if i + 1 < len(rom_offsets) else len(data)
        rom_data = data[start:end]

        out_filename = f"rom_{i}_compressed.nes"
        with open(out_filename, "wb") as f:
            f.write(rom_data)
        print(f"Extracted ROM {i} ({len(rom_data)} bytes)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cc_extract.py NesHebereke_x64_Release.dll")
        print("For verbose logs add --verbose at the end")
        sys.exit(1)

    extract_nes_roms(sys.argv[1])
    verbose = "--verbose" in sys.argv
    max_files = 1000 
    base_name = "rom_"

    for i in range(max_files):
        input_filename = f"{base_name}{i}_compressed.nes"
        output_filename = f"{base_name}{i}_decompressed.nes"

        if not os.path.isfile(input_filename):
            print(f"Done :)")
            break
        
        with open(input_filename, "rb") as f:
            compressed_data = f.read()
        
        decompressed = decompress_nes_data(compressed_data, verbose=verbose)
        print(f"ROM {i}: Decompressed size: {len(decompressed)} bytes")

        with open(output_filename, "wb") as f:
            f.write(decompressed)
        
        print(f"Saved decompressed ROM to {output_filename}\n")
        os.remove(f"{base_name}{i}_compressed.nes")

