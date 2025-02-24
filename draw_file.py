import asyncio
import sys
import time
from PIL import Image
from bleak import BleakScanner, BleakClient

# Service and characteristic UUIDs as discovered
SERVICE_UUID = "0000ffd0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000ffd1-0000-1000-8000-00805f9b34fb"

def load_and_resize_image(image_path):
    """
    Load an image file (jpg, png, gif) and resize it to 16x16 pixels.
    Returns a list of (r, g, b) tuples in row-major order.
    """
    try:
        # Open the image file
        img = Image.open(image_path)
        
        # Handle GIF animation - just take the first frame
        if img.format == 'GIF' and 'duration' in img.info:
            img = img.convert('RGBA')
        
        # Resize the image to 16x16 pixels
        img = img.resize((16, 16), Image.Resampling.LANCZOS)
        
        # Convert to RGB mode to ensure we have RGB values
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Extract RGB values for each pixel
        picture = []
        for y in range(16):
            for x in range(16):
                r, g, b = img.getpixel((x, y))
                picture.append((r, g, b))
        
        return picture
    
    except Exception as e:
        print(f"Error loading image: {e}")
        sys.exit(1)

def get_full_picture_command(block_index: int, block_pixels: list) -> bytearray:
    """
    Constructs a full-picture update command for a block of pixels.
    """
    if len(block_pixels) != 32:
        raise ValueError("block_pixels must contain exactly 32 pixels.")
    
    header = bytearray(3)
    header[0] = 0xBC
    header[1] = 0x0F
    header[2] = (block_index+1) & 0xFF  # block index (1-8)
    
    pixel_data = bytearray()
    for (r, g, b) in block_pixels:
        pixel_data.extend([r & 0xFF, g & 0xFF, b & 0xFF])
    
    terminator = bytearray([0x55])
    return header + pixel_data + terminator

async def send_command(client, hex_cmd):
    """Send a raw command to the device"""
    data = bytes.fromhex(hex_cmd)
    await client.write_gatt_char(CHARACTERISTIC_UUID, data)
    await asyncio.sleep(0.02)  # Minimal delay

async def send_image_blocks_only(client, picture):
    """
    Send only the image data blocks in rapid succession.
    No initialization or finalization commands.
    """
    for block_index in range(8):
        start = block_index * 32
        end = start + 32
        block_pixels = picture[start:end]
        command = get_full_picture_command(block_index, block_pixels)
        await client.write_gatt_char(CHARACTERISTIC_UUID, command)
        await asyncio.sleep(0.02)  # Minimal delay between blocks

async def continuous_refresh(client, picture):
    """
    Continuously refresh the display with extremely rapid updates.
    This tries to create a persistent display by sending refreshes so
    quickly that the blank period isn't noticeable.
    """
    start_time = time.time()
    count = 0
    
    try:
        print("Starting refresh mode (press Ctrl+C to exit)...")
        
        # Initial setup
        await send_command(client, "bc0ff1080855")  # Start image mode

        while True:
            await send_image_blocks_only(client, picture)
            
            # Very short delay to prevent overwhelming the BLE connection
            await asyncio.sleep(10.0)
            
    
    except KeyboardInterrupt:
        print("\nContinuous mode stopped")
    except Exception as e:
        print(f"\nError in continuous mode: {e}")

async def main():
    # Check if image file path is provided
    if len(sys.argv) != 2:
        print("Usage: python image_to_matrix.py <image_file>")
        print("Supported formats: JPG, PNG, GIF")
        return
    
    image_path = sys.argv[1]
    
    # Load and resize the image
    print(f"Loading and resizing image: {image_path}")
    picture = load_and_resize_image(image_path)
    print(f"Loaded image with {len(picture)} pixels")
    
    # Scan for BLE devices
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
    
    try:
        async with BleakClient(target) as client:
            if client.is_connected:
                print("Connected!")
                
                # Run in continuous refresh mode
                await continuous_refresh(client, picture)
            else:
                print("Failed to connect.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())