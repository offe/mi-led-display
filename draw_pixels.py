import asyncio
import random
from bleak import BleakScanner, BleakClient

# Service and characteristic UUIDs as discovered
SERVICE_UUID = "0000ffd0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000ffd1-0000-1000-8000-00805f9b34fb"

def get_set_pixel_command(pixel_index: int, r: int, g: int, b: int) -> bytearray:
    """
    Constructs a command to set a pixel on the MI Matrix Display.
    
    Command structure (10 bytes):
      Byte 0: 0xBC            -> Command identifier.
      Byte 1: 0x01            -> Fixed parameter.
      Byte 2: 0x01            -> Fixed parameter.
      Byte 3: 0x00            -> Fixed parameter.
      Byte 4: pixel_index     -> Pixel index (0-255).
      Byte 5: r               -> Red (0-255).
      Byte 6: g               -> Green (0-255).
      Byte 7: b               -> Blue (0-255).
      Byte 8: end_index       -> Typically pixel_index + 1 (special-case for 255).
      Byte 9: 0x55            -> Terminator.
    """
    # Compute the "end" parameter
    end_index = (pixel_index + 1) % 256
    if pixel_index == 0:
        end_index = 0xFF

    return bytearray([
        0xBC, 0x01, 0x01, 0x00,
        pixel_index,
        r, g, b,
        end_index,
        0x55
    ])

async def main():
    retries_left = 10
    target = None
    while target is None:
        print("Scanning for BLE devices...")
        devices = await BleakScanner.discover()

        for d in devices:
            print(f"Found: {d.name} [{d.address}]")
            if d.name and "MI Matrix Display" in d.name:
                target = d
                break

        if target is None:
            print("MI Matrix Display not found.")
            retries_left -= 1

        if retries_left == 0:
            return

    print(f"\nConnecting to {target.name} ({target.address})...")
    async with BleakClient(target) as client:
        if client.is_connected:
            print("Connected!")
            # Optional: list services for debugging
            for service in client.services:
                print(f"Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"  Characteristic: {char.uuid}")

            # Send initialization commands before starting pixel updates.
            init_commands = [
                #"bc00011255",
                "bc00010155",
                "bc000d0d55"
            ]
            print("\nSending initialization commands...")
            for cmd in init_commands:
                data = bytes.fromhex(cmd)
                print(f"Sending init command: {cmd}")
                await client.write_gatt_char(CHARACTERISTIC_UUID, data)
                await asyncio.sleep(0.2)  # Short delay between commands

            print("\nInitialization complete. Starting pixel updates...")

            # Now continuously update pixels with random colors.
            pixel_index = 0
            screen = 0
            while True:
                r = random.randint(0, 255)
                g = random.randint(0, 31) + (screen % 2) * (255 - 31)
                b = random.randint(0, 255)

                command = get_set_pixel_command(pixel_index, r, g, b)
                # print(f"Pixel {pixel_index:3}: Color ({r:02X} {g:02X} {b:02X}), Command: {command.hex()}")
                await client.write_gatt_char(CHARACTERISTIC_UUID, command)

                pixel_index = (pixel_index + 1) % 256
                if pixel_index == 0:
                    screen += 1
                await asyncio.sleep(0.002)
        else:
            print("Failed to connect.")

if __name__ == "__main__":
    asyncio.run(main())
