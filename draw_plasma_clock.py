
import asyncio
import random
from bleak import BleakScanner, BleakClient, BleakError
from plasma import update_plasma, update_clock, update_error, update_display, top_error_positions, display_pixels, UPDATE_PIXEL_COUNT, WIDTH

# Service and characteristic UUIDs as discovered
SERVICE_UUID = "0000ffd0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000ffd1-0000-1000-8000-00805f9b34fb"

async def find_device(name="MI Matrix Display", timeout=20):
    """
    Scans for the MI Matrix Display device.
    """
    print("Scanning for BLE devices...")
    scanner = BleakScanner()
    await scanner.start()
    
    target_device = None
    start_time = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time() - start_time) < timeout:
        for device in scanner.discovered_devices:
            if device.name == name:
                target_device = device
                break
        if target_device:
            break
        await asyncio.sleep(1)
    
    await scanner.stop()
    return target_device

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
    while True:
        try:
            device = await find_device()
            if not device:
                print("MI Matrix Display not found.")
                return

            print(f"\nConnecting to {device.name} ({device.address})...")
            async with BleakClient(device) as client:
                if client.is_connected:
                    print("Connected!")

                    # Send initialization commands before starting pixel updates.
                    init_commands = [
                        "bc00010155",
                        "bc000d0d55"
                    ]
                    for cmd in init_commands:
                        data = bytes.fromhex(cmd)
                        await client.write_gatt_char(CHARACTERISTIC_UUID, data)
                        await asyncio.sleep(0.2)

                    print("\nInitialization complete. Starting plasma effect...")

                    t = random.randrange(0, 1000000)
                    while True:
                        # Update plasma state
                        update_plasma(t)
                        update_clock()
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
        except BleakError as e:
            print("Lost connection")

if __name__ == "__main__":
    asyncio.run(main())
