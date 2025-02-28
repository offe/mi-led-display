import asyncio
import sys
from bleak import BleakScanner, BleakClient

# Service and characteristic UUIDs for MI Matrix Display
SERVICE_UUID = "0000ffd0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000ffd1-0000-1000-8000-00805f9b34fb"

def parse_hex_input(hex_str: str) -> bytearray:
    """
    Converts a hex string input into a bytearray.
    """
    hex_str = hex_str.strip().replace(" ", "")  # Remove spaces and newlines
    try:
        return bytearray.fromhex(hex_str)
    except ValueError:
        print("Invalid hex input. Please enter a valid hex string.")
        return None

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

async def main():
    """
    Main function that connects to the device and sends user input.
    """
    device = await find_device()
    if not device:
        print("MI Matrix Display not found.")
        return
    
    print(f"Connecting to {device.name} at {device.address}...")
    async with BleakClient(device) as client:
        if client.is_connected:
            print("Connected to MI Matrix Display!")
            
            print("Device is ready. Enter hex commands to send (q or Ctrl+C to exit).")
            
            while True:
                try:
                    user_input = input("Enter hex command: ")
                    if (user_input.startswith("q")):
                        print("Exiting")
                        break
                    data = parse_hex_input(user_input)
                    if data:
                        await client.write_gatt_char(CHARACTERISTIC_UUID, data)
                        print(f"Sent: {data.hex()}")
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break
        else:
            print("Failed to connect.")

if __name__ == "__main__":
    asyncio.run(main())
