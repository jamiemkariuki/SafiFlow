# SafiFlow Hardware Setup Guide

This guide explains how to set up the SafiFlow system with a 4x4 matrix keypad and 16x2 LCD display on a Raspberry Pi.

## Hardware Requirements

### Required Components:
- **Raspberry Pi** (3B+, 4B, or newer)
- **4x4 Matrix Keypad** (16-button membrane or mechanical)
- **16x2 LCD Display** (I2C or direct GPIO)
- **Breadboard and jumper wires**
- **Power supply for Raspberry Pi**

### Optional Components:
- **Case/enclosure** for the device
- **Mounting hardware**
- **LED indicators** for status

## Wiring Diagram

### 4x4 Matrix Keypad Connections

| Keypad Pin | Raspberry Pi GPIO | Function |
|------------|-------------------|----------|
| Row 1      | GPIO 18 (Pin 12) | Row 1    |
| Row 2      | GPIO 23 (Pin 16) | Row 2    |
| Row 3      | GPIO 24 (Pin 18) | Row 3    |
| Row 4      | GPIO 25 (Pin 22) | Row 4    |
| Col 1      | GPIO 17 (Pin 11) | Column 1 |
| Col 2      | GPIO 27 (Pin 13) | Column 2 |
| Col 3      | GPIO 22 (Pin 15) | Column 3 |
| Col 4      | GPIO 10 (Pin 19) | Column 4 |

### 16x2 LCD Connections (I2C)

| LCD Pin | Raspberry Pi | Function |
|---------|--------------|----------|
| VCC     | 3.3V (Pin 1) | Power    |
| GND     | GND (Pin 6)  | Ground   |
| SDA     | GPIO 2 (Pin 3) | I2C Data |
| SCL     | GPIO 3 (Pin 5) | I2C Clock |

## Installation Steps

### 1. Enable I2C Interface
```bash
sudo raspi-config
```
Navigate to: **Interface Options** → **I2C** → **Enable**

### 2. Install System Dependencies
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-dev
sudo apt-get install i2c-tools
```

### 3. Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

### 4. Test I2C Connection
```bash
sudo i2cdetect -y 1
```
Look for your LCD device address (typically 0x27 or 0x3F).

### 5. Test Keypad
```bash
python3 test_keypad.py
```

## Keypad Layout

```
┌─────────┬─────────┬─────────┬─────────┐
│    1    │    2    │    3    │    A    │
├─────────┼─────────┼─────────┼─────────┤
│    4    │    5    │    6    │    B    │
├─────────┼─────────┼─────────┼─────────┤
│    7    │    8    │    9    │    C    │
├─────────┼─────────┼─────────┼─────────┤
│    *    │    0    │    #    │    D    │
└─────────┴─────────┴─────────┴─────────┘
```

### Key Functions:
- **1**: Energy Usage Measurement
- **2**: Energy Collected Measurement  
- **3**: Water Purified Measurement
- **4**: Show Device ID
- **A**: Exit/Shutdown
- **#**: Enter/Confirm
- ***: Clear/Back
- **0-9**: Numeric input
- **B, C, D**: Reserved for future use

## LCD Display Information

### Display Format:
- **Line 1 (16 chars)**: Primary information
- **Line 2 (16 chars)**: Secondary information or input

### Common Messages:
- `"SafiFlow System"` - Startup
- `"Energy Usage"` - Menu option
- `"Enter kWh:"` - Input prompt
- `"Recording: 12.5"` - Data entry
- `"Energy usage saved!"` - Success message

## Troubleshooting

### LCD Not Working:
1. Check I2C address: `sudo i2cdetect -y 1`
2. Verify wiring connections
3. Check power supply (3.3V)
4. Test with: `python3 test_lcd.py`

### Keypad Not Responding:
1. Verify GPIO pin connections
2. Check for loose wires
3. Test individual buttons
4. Run: `python3 test_keypad.py`

### Database Connection Issues:
1. Ensure MySQL is running: `sudo systemctl status mysql`
2. Check database credentials in `script.py`
3. Verify network connectivity

## Test Scripts

### test_lcd.py
```python
from rpi_lcd import LCD
import time

lcd = LCD()
lcd.text("LCD Test", 1)
lcd.text("Working!", 2)
time.sleep(3)
lcd.clear()
```

### test_keypad.py
```python
from pad4pi import rpi_gpio
import time

KEYPAD = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

ROW_PINS = [18, 23, 24, 25]
COL_PINS = [17, 27, 22, 10]

def key_pressed(key):
    print(f"Key pressed: {key}")

factory = rpi_gpio.KeypadFactory()
keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)
keypad.registerKeyPressHandler(key_pressed)

print("Press keys on keypad...")
while True:
    time.sleep(0.1)
```

## Usage Instructions

### Starting the System:
```bash
python3 script.py
```

### Operation Flow:
1. **Startup**: Device ID displayed
2. **Menu**: Options shown on LCD
3. **Input**: Use keypad to select option
4. **Data Entry**: Enter numeric values
5. **Confirmation**: Press '#' to confirm
6. **Save**: Data automatically saved to database

### Emergency Shutdown:
- Press 'A' key to safely shutdown
- Or use Ctrl+C in terminal

## Safety Notes

- **Power**: Use proper 5V power supply
- **GPIO**: Double-check connections before powering on
- **Database**: Ensure MySQL is running before starting
- **Backup**: Regular database backups recommended

## Customization

### Changing GPIO Pins:
Edit the pin assignments in `script.py`:
```python
ROW_PINS = [18, 23, 24, 25]  # Change as needed
COL_PINS = [17, 27, 22, 10]  # Change as needed
```

### LCD Address:
If your LCD uses a different I2C address:
```python
lcd = LCD(address=0x3F)  # Default is 0x27
```

### Keypad Layout:
Modify the KEYPAD matrix for different layouts:
```python
KEYPAD = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]
``` 