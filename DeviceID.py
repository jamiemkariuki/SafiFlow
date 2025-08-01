import random
import os
import string

def generate_device_id():
    """Generate a short, memorable device ID"""
    # Generate a 6-character alphanumeric ID
    # Format: 3 letters + 3 numbers (e.g., ABC123)
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    numbers = ''.join(random.choices(string.digits, k=3))
    return f"{letters}{numbers}"

def save_device_id(device_id, filename="device_id.txt"):
    """Save device ID to a text file"""
    try:
        with open(filename, 'w') as f:
            f.write(device_id)
        print(f"Device ID saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving device ID: {e}")
        return False

def read_device_id(filename="device_id.txt"):
    """Read device ID from text file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                device_id = f.read().strip()
            return device_id
        else:
            return None
    except Exception as e:
        print(f"Error reading device ID: {e}")
        return None

def get_or_create_device_id():
    """Get existing device ID or create a new one"""
    device_id = read_device_id()
    if device_id is None:
        device_id = generate_device_id()
        save_device_id(device_id)
    return device_id

if __name__ == "__main__":
    # Create device ID if it doesn't exist
    device_id = get_or_create_device_id()
    print(f"Device ID: {device_id}")