import mysql.connector
from mysql.connector import Error
from DeviceID import get_or_create_device_id

# Database configuration
DB_CONFIG = {
    'host': 'localhost', # Add custom ip/url for db
    'user': 'root',
    'password': 'hello',  # Add your MySQL password here
    'database': 'safiflow'
}

def setup_database():
    """Set up the database and create device ID"""
    try:
        # Create device ID first
        device_id = get_or_create_device_id()
        print(f"Device ID created: {device_id}")
        
        # Connect to database
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Insert device ID into DeviceID table
            query = "INSERT INTO DeviceID (device_id) VALUES (%s)"
            cursor.execute(query, (device_id,))
            connection.commit()
            print("Device ID inserted into database successfully!")
            
            cursor.close()
            connection.close()
            print("Database setup completed!")
            
    except Error as e:
        print(f"Error setting up database: {e}")
        print("Please make sure:")
        print("1. MySQL server is running")
        print("2. Database 'safiflow' exists")
        print("3. Tables are created using safiflow.sql")
        print("4. MySQL credentials are correct in DB_CONFIG")

if __name__ == "__main__":
    setup_database() 