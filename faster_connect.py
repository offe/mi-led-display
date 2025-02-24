import asyncio
import time
from bleak import BleakScanner

# Target service UUID (the MI Matrix Display service)
TARGET_SERVICE_UUID = "0000ffd0-0000-1000-8000-00805f9b34fb"
found_device = None  # To store the found device

def detection_callback(device, advertisement_data):
    global found_device
    # print(f"Found {device.name}")
    # Check if the service UUID matches
    print(".", end="", flush=True)
    """
    if TARGET_SERVICE_UUID.lower() in [uuid.lower() for uuid in advertisement_data.service_uuids]:
        print(f"Found target device: {device.name} [{device.address}]")
        found_device = device
    """
    if device.name == "MI Matrix Display":
        found_device = device
        print()

async def find_device(timeout=20):
    global found_device
    print("Scanning for BLE devices with the target service UUID...")

    # Create scanner with callback
    scanner = BleakScanner(detection_callback)

    # Start scanning
    await scanner.start()
    start_time = time.time()

    while found_device is None:
        await asyncio.sleep(0.1)  # Check every 100ms
        if time.time() - start_time > timeout:
            print(f"Timeout: Could not find device within {timeout} seconds.")
            break

    await scanner.stop()

    if found_device:
        return found_device
    else:
        return None

# Example usage
async def main():
    device = await find_device(timeout=20)
    if device:
        print(f"Connecting to {device.name} at {device.address}")
    else:
        print("Device not found.")

if __name__ == "__main__":
    asyncio.run(main())
