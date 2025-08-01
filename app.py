from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
import mysql.connector
from mysql.connector import Error
from DeviceID import get_or_create_device_id
import datetime as dt
import os

app = Flask(__name__)
app.secret_key = 'safiflow_secret_key_2024'  # Change this in production
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

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
        print(f"Error connecting to MySQL: {e}")
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
            print(f"Error getting last updated: {e}")
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

def get_all_readings(device_id, measurement_type=None, page=1, per_page=20):
    """Get all readings for a device with optional filtering and pagination"""
    connection = create_database_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Determine which table to query
            if measurement_type == 'energy_usage':
                table_name = 'EnergyUsage'
                unit = 'kWh'
            elif measurement_type == 'energy_collected':
                table_name = 'EnergyCollected'
                unit = 'kWh'
            elif measurement_type == 'water_purified':
                table_name = 'WaterPurified'
                unit = 'Litres'
            else:
                # Get all readings from all tables
                readings = []
                
                # Energy Usage
                cursor.execute("""
                    SELECT 'energy_usage' as type, `usage`, recorded_at, last_updated, period, 'kWh' as unit
                    FROM EnergyUsage WHERE device_id = %s
                    ORDER BY recorded_at DESC
                """, (device_id,))
                readings.extend(cursor.fetchall())
                
                # Energy Collected
                cursor.execute("""
                    SELECT 'energy_collected' as type, `usage`, recorded_at, last_updated, period, 'kWh' as unit
                    FROM EnergyCollected WHERE device_id = %s
                    ORDER BY recorded_at DESC
                """, (device_id,))
                readings.extend(cursor.fetchall())
                
                # Water Purified
                cursor.execute("""
                    SELECT 'water_purified' as type, `usage`, recorded_at, last_updated, period, 'Litres' as unit
                    FROM WaterPurified WHERE device_id = %s
                    ORDER BY recorded_at DESC
                """, (device_id,))
                readings.extend(cursor.fetchall())
                
                # Sort all readings by recorded_at
                readings.sort(key=lambda x: x['recorded_at'], reverse=True)
                
                # Pagination
                total = len(readings)
                start = (page - 1) * per_page
                end = start + per_page
                paginated_readings = readings[start:end]
                
                return {
                    'readings': paginated_readings,
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'pages': (total + per_page - 1) // per_page
                }
            
            # Single table query
            offset = (page - 1) * per_page
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) as total FROM {table_name} WHERE device_id = %s", (device_id,))
            total = cursor.fetchone()['total']
            
            # Get paginated readings
            query = f"""
                SELECT `usage`, recorded_at, last_updated, period
                FROM {table_name}
                WHERE device_id = %s
                ORDER BY recorded_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (device_id, per_page, offset))
            readings = cursor.fetchall()
            
            # Add type and unit to each reading
            for reading in readings:
                reading['type'] = measurement_type
                reading['unit'] = unit
            
            return {
                'readings': readings,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
            
        except Error as e:
            print(f"Error getting readings: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return None

def verify_device_id(device_id):
    """Verify if device ID exists in database"""
    connection = create_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT device_id FROM DeviceID WHERE device_id = %s"
            cursor.execute(query, (device_id,))
            result = cursor.fetchone()
            return result is not None
        except Error as e:
            print(f"Error verifying device ID: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return False

def get_device_data(device_id):
    """Get all data for a specific device"""
    connection = create_database_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get latest energy usage
            cursor.execute("""
                SELECT `usage`, recorded_at, last_updated, period FROM EnergyUsage 
                WHERE device_id = %s 
                ORDER BY recorded_at DESC LIMIT 1
            """, (device_id,))
            latest_energy_usage = cursor.fetchone()
            
            # Get latest energy collected
            cursor.execute("""
                SELECT `usage`, recorded_at, last_updated, period FROM EnergyCollected 
                WHERE device_id = %s 
                ORDER BY recorded_at DESC LIMIT 1
            """, (device_id,))
            latest_energy_collected = cursor.fetchone()
            
            # Get latest water purified
            cursor.execute("""
                SELECT `usage`, recorded_at, last_updated, period FROM WaterPurified 
                WHERE device_id = %s 
                ORDER BY recorded_at DESC LIMIT 1
            """, (device_id,))
            latest_water_purified = cursor.fetchone()
            
            # Get summary statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_energy_readings,
                    AVG(`usage`) as avg_energy_usage
                FROM EnergyUsage 
                WHERE device_id = %s
            """, (device_id,))
            energy_stats = cursor.fetchone()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_energy_collected_readings,
                    AVG(`usage`) as avg_energy_collected
                FROM EnergyCollected 
                WHERE device_id = %s
            """, (device_id,))
            energy_collected_stats = cursor.fetchone()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_water_readings,
                    AVG(`usage`) as avg_water_purified
                FROM WaterPurified 
                WHERE device_id = %s
            """, (device_id,))
            water_stats = cursor.fetchone()
            
            return {
                'latest_energy_usage': latest_energy_usage,
                'latest_energy_collected': latest_energy_collected,
                'latest_water_purified': latest_water_purified,
                'energy_stats': energy_stats,
                'energy_collected_stats': energy_collected_stats,
                'water_stats': water_stats
            }
            
        except Error as e:
            print(f"Error getting device data: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return None

@app.route('/')
def index():
    if 'device_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        device_id = request.form['device_id'].strip()
        if verify_device_id(device_id):
            session['device_id'] = device_id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Device ID. Please try again.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('device_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'device_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    device_id = session['device_id']
    device_data = get_device_data(device_id)
    
    return render_template('dashboard.html', 
                         device_id=device_id, 
                         data=device_data)

@app.route('/readings')
def readings():
    if 'device_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    device_id = session['device_id']
    measurement_type = request.args.get('type', 'all')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    readings_data = get_all_readings(device_id, measurement_type, page, per_page)
    
    return render_template('readings.html',
                         device_id=device_id,
                         readings_data=readings_data,
                         measurement_type=measurement_type)

@app.route('/add_measurement', methods=['POST'])
def add_measurement():
    if 'device_id' not in session:
        return redirect(url_for('login'))
    
    device_id = session['device_id']
    measurement_type = request.form['type']
    value = request.form['value']
    
    connection = create_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            current_time = dt.datetime.now()
            
            if measurement_type == 'energy_usage':
                last_updated = get_last_updated(device_id, "EnergyUsage")
                calculated_period = calculate_period(last_updated, current_time)
                query = "INSERT INTO EnergyUsage (device_id, `usage`, last_updated, period) VALUES (%s, %s, %s, %s)"
            elif measurement_type == 'energy_collected':
                last_updated = get_last_updated(device_id, "EnergyCollected")
                calculated_period = calculate_period(last_updated, current_time)
                query = "INSERT INTO EnergyCollected (device_id, `usage`, last_updated, period) VALUES (%s, %s, %s, %s)"
            elif measurement_type == 'water_purified':
                last_updated = get_last_updated(device_id, "WaterPurified")
                calculated_period = calculate_period(last_updated, current_time)
                query = "INSERT INTO WaterPurified (device_id, `usage`, last_updated, period) VALUES (%s, %s, %s, %s)"
            else:
                flash('Invalid measurement type.', 'error')
                return redirect(url_for('dashboard'))
            
            cursor.execute(query, (device_id, float(value), last_updated, calculated_period))
            connection.commit()
            flash(f'{measurement_type.replace("_", " ").title()} measurement added successfully! Period: {calculated_period}', 'success')
            
        except Error as e:
            flash(f'Error adding measurement: {e}', 'error')
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)