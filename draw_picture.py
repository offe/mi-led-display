import asyncio
from bleak import BleakScanner, BleakClient

# Service and characteristic UUIDs as discovered
SERVICE_UUID = "0000ffd0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000ffd1-0000-1000-8000-00805f9b34fb"

def create_picture(n : int) -> list:
    """
    Generates a 16x16 image as a list of (r, g, b) tuples.
    For each pixel at (x, y) with x,y in [0,15],
    the color is defined as (x*16, y*16, 0).
    The result is a list of 256 tuples in row-major order.
    """
    picture = []
    for y in range(16):
        for x in range(16):
            r = x * 16
            g = y * 16
            b = n * 255
            picture.append((r, g, b))
    return picture

def get_full_picture_command(block_index: int, block_pixels: list) -> bytearray:
    """
    Constructs a full-picture update command for a block of pixels.
    
    The command is 113 bytes in total:
      - Header (16 bytes):
          Byte 0: 0xBC (command identifier)
          Byte 1: 0x0F (full-picture update indicator)
          Byte 2: block_index (0 to 7)
          Byte 3: 0x00
          Bytes 4-15: Reserved (set to 0x00)
      - Pixel Data (96 bytes): 32 pixels × 3 bytes per pixel (RGB)
      - Terminator (1 byte): 0x55
       
    `block_pixels` should be a list of exactly 32 (r, g, b) tuples.
    """
    if len(block_pixels) != 32:
        raise ValueError("block_pixels must contain exactly 32 pixels.")
    
    header = bytearray(3)
    header[0] = 0xBC
    header[1] = 0x0F
    header[2] = (block_index+1) & 0xFF  # block index (0-7)
    
    pixel_data = bytearray()
    for (r, g, b) in block_pixels:
        pixel_data.extend([r & 0xFF, g & 0xFF, b & 0xFF])
    # Ensure pixel_data is 96 bytes (32 pixels * 3 bytes)
    if len(pixel_data) != 96:
        raise ValueError("Pixel data length is not 96 bytes.")

    terminator = bytearray([0x55])
    return header + pixel_data + terminator

async def send_picture(client: BleakClient, picture: list):
    """
    Sends a full 16x16 picture to the display.
    The picture is a list of 256 (r, g, b) tuples in row-major order.
    The display is updated in 8 blocks (2 rows each, i.e. 32 pixels per block).
    """
    # Send initialization commands (if required)
    init_commands = [
        #"bc00121255",
        #"bc00010155",
        #"bc000d0d55",
        #"bc000d0d55",
        #"bc00131355",
        "bc0ff1080855"
    ]
    #print("\nSending initialization commands...")
    for cmd in init_commands:
        data = bytes.fromhex(cmd)
        #print(f"Sending init command: {cmd}")
        await client.write_gatt_char(CHARACTERISTIC_UUID, data)
        await asyncio.sleep(0.02)
    #print("Initialization complete.\n")
    print("Sending full-picture update...")

    # For a 16x16 image, we have 16 rows.
    # Each block covers 2 rows = 32 pixels.
    num_blocks = 8  # 16 rows / 2 rows per block = 8 blocks
    for block_index in range(num_blocks):
        start = block_index * 32
        end = start + 32
        block_pixels = picture[start:end]
        command = get_full_picture_command(block_index, block_pixels)
        #print(f"Block {block_index}: Command {command.hex()}")
        await client.write_gatt_char(CHARACTERISTIC_UUID, command)
        # Delay between blocks (adjust as needed)
        await asyncio.sleep(0.02)
    #print("Full picture update sent!")
    # Send end commands (if required)
    end_commands = [
        "bc0ff2080955",
        "bc00010155"
    ]
    #print("\nSending end commands...")
    for cmd in end_commands:
        data = bytes.fromhex(cmd)
        #print(f"Sending end command: {cmd}")
        await client.write_gatt_char(CHARACTERISTIC_UUID, data)
        await asyncio.sleep(0.02)
    #print("End complete.\n")

async def main():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()
    target = None

    for d in devices:
        print(f"Found: {d.name} [{d.address}]")
        if d.name and "MI Matrix Display" in d.name:
            target = d
            break

    if target is None:
        print("MI Matrix Display not found.")
        return

    print(f"\nConnecting to {target.name} ({target.address})...")
    async with BleakClient(target) as client:
        if client.is_connected:
            print("Connected!")
            # Optionally, list services for debugging:
            for service in client.services:
                print(f"Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"  Characteristic: {char.uuid}")


            # Create the 16x16 image
            picture0 = create_picture(0)
            picture1 = create_picture(1)

            #await send_picture(client, picture0)
            while True:
                # Send the full picture update in 8 blocks
                await send_picture(client, picture0)
                await asyncio.sleep(0.1)
                await send_picture(client, picture1)
                await asyncio.sleep(0.1)

        else:
            print("Failed to connect.")

if __name__ == "__main__":
    asyncio.run(main())
