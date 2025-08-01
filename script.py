import datetime as dt
import mysql.connector
from mysql.connector import Error
from DeviceID import get_or_create_device_id
from pad4pi import rpi_gpio
import time
import RPi.GPIO as GPIO
from rpi_lcd import LCD

# LCD Configuration
lcd = LCD()

# Keypad Configuration
KEYPAD = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

ROW_PINS = [18, 23, 24, 25]  # BCM numbering
COL_PINS = [17, 27, 22, 10]  # BCM numbering

# Initialize keypad
factory = rpi_gpio.KeypadFactory()
keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

# Database configuration
DB_CONFIG = {
    'host': 'localhost', # Add custom ip/url for db
    'user': 'root',
    'password': 'hello',  # Add your MySQL password here
    'database': 'safiflow'
}

def create_database_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        lcd.text("DB Error: " + str(e)[:16], 1)
        time.sleep(2)
        return None

def get_last_updated(device_id, table_name):
    """Get the last updated timestamp for a device from a specific table"""
    connection = create_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = f"""
            SELECT recorded_at FROM {table_name} 
            WHERE device_id = %s 
            ORDER BY recorded_at DESC LIMIT 1
            """
            cursor.execute(query, (device_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            lcd.text("Error getting last", 1)
            lcd.text("updated time", 2)
            time.sleep(2)
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return None

def calculate_period(last_updated, current_time):
    """Calculate period based on time difference"""
    if last_updated is None:
        return "initial"
    
    time_diff = current_time - last_updated
    hours_diff = time_diff.total_seconds() / 3600
    
    if hours_diff < 1:
        return "hourly"
    elif hours_diff < 24:
        return "daily"
    elif hours_diff < 168:  # 7 days
        return "weekly"
    else:
        return "monthly"

def insert_energy_usage(device_id, usage, period="daily"):
    """Insert energy usage data into database"""
    connection = create_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            current_time = dt.datetime.now()
            last_updated = get_last_updated(device_id, "EnergyUsage")
            calculated_period = calculate_period(last_updated, current_time)
            
            query = """
            INSERT INTO EnergyUsage (device_id, `usage`, last_updated, period) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (device_id, usage, last_updated, calculated_period))
            connection.commit()
            lcd.text("Energy usage saved!", 1)
            lcd.text(f"Period: {calculated_period}", 2)
            time.sleep(2)
        except Error as e:
            lcd.text("Error saving energy", 1)
            lcd.text("usage data", 2)
            time.sleep(2)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def insert_energy_collected(device_id, usage, period="daily"):
    """Insert energy collected data into database"""
    connection = create_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            current_time = dt.datetime.now()
            last_updated = get_last_updated(device_id, "EnergyCollected")
            calculated_period = calculate_period(last_updated, current_time)
            
            query = """
            INSERT INTO EnergyCollected (device_id, `usage`, last_updated, period) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (device_id, usage, last_updated, calculated_period))
            connection.commit()
            lcd.text("Energy collected", 1)
            lcd.text(f"saved! {calculated_period}", 2)
            time.sleep(2)
        except Error as e:
            lcd.text("Error saving energy", 1)
            lcd.text("collected data", 2)
            time.sleep(2)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def insert_water_purified(device_id, usage, period="daily"):
    """Insert water purified data into database"""
    connection = create_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            current_time = dt.datetime.now()
            last_updated = get_last_updated(device_id, "WaterPurified")
            calculated_period = calculate_period(last_updated, current_time)
            
            query = """
            INSERT INTO WaterPurified (device_id, `usage`, last_updated, period) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (device_id, usage, last_updated, calculated_period))
            connection.commit()
            lcd.text("Water purified", 1)
            lcd.text(f"saved! {calculated_period}", 2)
            time.sleep(2)
        except Error as e:
            lcd.text("Error saving water", 1)
            lcd.text("purified data", 2)
            time.sleep(2)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def get_device_id():
    """Get or create device ID"""
    return get_or_create_device_id()

def get_numeric_input(prompt):
    """Get numeric input from keypad"""
    lcd.text(prompt, 1)
    lcd.text("Enter value:", 2)
    
    value = ""
    while True:
        key = keypad.getKey()
        if key:
            if key == '#':  # Enter key
                if value:
                    return float(value)
                else:
                    lcd.text("Invalid input!", 1)
                    lcd.text("Try again", 2)
                    time.sleep(2)
                    return None
            elif key == '*':  # Clear key
                value = ""
                lcd.text(prompt, 1)
                lcd.text("Enter value:", 2)
            elif key in '0123456789.':
                if len(value) < 10:  # Limit input length
                    value += key
                    lcd.text(prompt, 1)
                    lcd.text(f"Value: {value}", 2)
            time.sleep(0.3)  # Debounce

def show_menu():
    """Display main menu on LCD"""
    lcd.text("SafiFlow Menu:", 1)
    lcd.text("1:Energy 2:Collect", 2)
    time.sleep(2)
    lcd.text("3:Water 4:DeviceID", 1)
    lcd.text("A:Exit", 2)
    time.sleep(2)

def show_device_id(device_id):
    """Display device ID on LCD"""
    lcd.text("Device ID:", 1)
    lcd.text(device_id[:16], 2)
    time.sleep(3)

def handle_energy_usage(device_id):
    """Handle energy usage measurement"""
    lcd.text("Energy Usage", 1)
    lcd.text("Enter kWh:", 2)
    time.sleep(1)
    
    value = get_numeric_input("Energy Usage (kWh)")
    if value is not None:
        lcd.text(f"Recording: {value}", 1)
        lcd.text("kWh...", 2)
        insert_energy_usage(device_id, value)
        lcd.text("Energy usage", 1)
        lcd.text("recorded!", 2)
        time.sleep(2)

def handle_energy_collected(device_id):
    """Handle energy collected measurement"""
    lcd.text("Energy Collected", 1)
    lcd.text("Enter kWh:", 2)
    time.sleep(1)
    
    value = get_numeric_input("Energy Collected (kWh)")
    if value is not None:
        lcd.text(f"Recording: {value}", 1)
        lcd.text("kWh...", 2)
        insert_energy_collected(device_id, value)
        lcd.text("Energy collected", 1)
        lcd.text("recorded!", 2)
        time.sleep(2)

def handle_water_purified(device_id):
    """Handle water purified measurement"""
    lcd.text("Water Purified", 1)
    lcd.text("Enter litres:", 2)
    time.sleep(1)
    
    value = get_numeric_input("Water Purified (L)")
    if value is not None:
        lcd.text(f"Recording: {value}", 1)
        lcd.text("litres...", 2)
        insert_water_purified(device_id, value)
        lcd.text("Water purified", 1)
        lcd.text("recorded!", 2)
        time.sleep(2)

def keypad_handler(key):
    """Handle keypad input"""
    global current_menu_state, device_id
    
    if current_menu_state == "menu":
        if key == '1':
            current_menu_state = "energy_usage"
            handle_energy_usage(device_id)
            current_menu_state = "menu"
        elif key == '2':
            current_menu_state = "energy_collected"
            handle_energy_collected(device_id)
            current_menu_state = "menu"
        elif key == '3':
            current_menu_state = "water_purified"
            handle_water_purified(device_id)
            current_menu_state = "menu"
        elif key == '4':
            show_device_id(device_id)
        elif key == 'A':
            lcd.text("Shutting down...", 1)
            lcd.text("Goodbye!", 2)
            time.sleep(2)
            lcd.clear()
            GPIO.cleanup()
            exit(0)

# Initialize device ID
device_id = get_device_id()
current_menu_state = "menu"

# Display startup message
lcd.text("SafiFlow System", 1)
lcd.text("Initializing...", 2)
time.sleep(2)

lcd.text("Device ID:", 1)
lcd.text(device_id[:16], 2)
time.sleep(3)

# Register keypad handler
keypad.registerKeyPressHandler(keypad_handler)

# Main loop
try:
    while True:
        show_menu()
        time.sleep(0.1)  # Small delay to prevent CPU overuse

except KeyboardInterrupt:
    lcd.text("Shutting down...", 1)
    lcd.text("Goodbye!", 2)
    time.sleep(2)
    lcd.clear()
    GPIO.cleanup()