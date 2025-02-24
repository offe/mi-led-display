
import asyncio
import random
from bleak import BleakScanner, BleakClient
from plasma import update_plasma, update_error, update_display, top_error_positions, display_pixels, UPDATE_PIXEL_COUNT, WIDTH

# Service and characteristic UUIDs as discovered
SERVICE_UUID = "0000ffd0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000ffd1-0000-1000-8000-00805f9b34fb"

def get_set_pixel_command(pixel_index: int, r: int, g: int, b: int) -> bytearray:
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

            # Send initialization commands before starting pixel updates.
            init_commands = [
                "bc00010155",
                "bc000d0d55"
            ]
            print("\nSending initialization commands...")
            for cmd in init_commands:
                data = bytes.fromhex(cmd)
                print(f"Sending init command: {cmd}")
                await client.write_gatt_char(CHARACTERISTIC_UUID, data)
                await asyncio.sleep(0.2)

            print("\nInitialization complete. Starting plasma effect...")

            t = random.randrange(0, 1000000)
            while True:
                # Update plasma state
                update_plasma(t)
                update_error()
                update_display()

                # Send the UPDATE_PIXEL_COUNT last positions from top_error_positions
                for idx in top_error_positions[-UPDATE_PIXEL_COUNT:]:
                    y, x = divmod(idx, WIDTH)  # Assuming a 16x16 grid
                    r, g, b = [int(c * 255) for c in display_pixels[y][x]]
                    command = get_set_pixel_command(idx, r, g, b)
                    await client.write_gatt_char(CHARACTERISTIC_UUID, command)

                t += 0.01
                await asyncio.sleep(0.033)  # Roughly 30 FPS
        else:
            print("Failed to connect.")

if __name__ == "__main__":
    asyncio.run(main())
