
# Merkury Innovations Matrix LED Display SDK

This project provides a set of Python scripts to interface with the Merkury Innovations Multicolor Matrix LED Display. This product is available at [Walmart](https://www.walmart.com/ip/Merkury-Innovations-Bluetooth-Matrix-LED-Pixel-Display/5150283693). The purpose of this project is to reverse engineer the communication protocol to allow developers to create custom applications for this device. The model number of the display is MI-LNL62-999W.

## Repository Contents

- `draw_picture.py`: Script to draw a static picture on the display.
- `draw_pixels.py`: Script to send color data to individual pixels on the display.
- `index.html`: Web-based attempt to connect to the display (note: does not work due to service listing issues in browsers for this hardware).

## Getting Started

### Prerequisites

Ensure you have Python 3.7 or higher installed on your system. You can verify this by running:
```bash
python3 --version
```

### Installation

Clone this repository locally and navigate into the project directory:
```bash
git clone https://github.com/yourusername/mi-led-display.git
cd mi-led-display
```

Install the required Python libraries using pip:
```bash
python3 -m venv venv
python3 -m pip install bleak
```

### Running the Scripts

To run the scripts, use the following commands:

```bash
python3 draw_picture.py
python3 draw_pixels.py
```

## Collecting Bluetooth Snoop Logs

Instructions for collecting Bluetooth snoop logs are also provided to assist with further development and debugging. See `snoop_instructions.md` for details.

## License

This project is licensed under the MIT License 
