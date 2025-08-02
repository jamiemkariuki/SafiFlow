from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
import mysql.connector
from mysql.connector import Error
from DeviceID import get_or_create_device_id
from trend_analyzer import TrendAnalyzer
import datetime as dt
import os

app = Flask(__name__)
app.secret_key = 'safiflow_secret_key_2024'  # Change this in production
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Initialize trend analyzer
trend_analyzer = TrendAnalyzer()

# Database configuration
DB_CONFIG = {
    'host': '192.168.72.143',  # Add custom ip/url for db
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
                    SELECT id, 'energy_usage' as type, `usage`, recorded_at, last_updated, period, 'kWh' as unit
                    FROM EnergyUsage WHERE device_id = %s
                    ORDER BY recorded_at DESC
                """, (device_id,))
                readings.extend(cursor.fetchall())
                
                # Energy Collected
                cursor.execute("""
                    SELECT id, 'energy_collected' as type, `usage`, recorded_at, last_updated, period, 'kWh' as unit
                    FROM EnergyCollected WHERE device_id = %s
                    ORDER BY recorded_at DESC
                """, (device_id,))
                readings.extend(cursor.fetchall())
                
                # Water Purified
                cursor.execute("""
                    SELECT id, 'water_purified' as type, `usage`, recorded_at, last_updated, period, 'Litres' as unit
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
                SELECT id, `usage`, recorded_at, last_updated, period
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

def get_device_alerts(device_id):
    """Get alerts for a specific device"""
    try:
        # Run trend analysis for the device
        device_alerts = trend_analyzer.analyze_device(device_id)
        
        # Get existing alerts for the device
        existing_alerts = trend_analyzer.get_alerts_for_device(device_id)
        
        # Combine and sort by timestamp (newest first)
        all_alerts = device_alerts + existing_alerts
        all_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return all_alerts
    except Exception as e:
        print(f"Error getting alerts: {e}")
        return []

def get_measurement_by_id(measurement_id, measurement_type):
    """Get a specific measurement by ID"""
    connection = create_database_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            if measurement_type == 'energy_usage':
                table_name = 'EnergyUsage'
            elif measurement_type == 'energy_collected':
                table_name = 'EnergyCollected'
            elif measurement_type == 'water_purified':
                table_name = 'WaterPurified'
            else:
                return None
            
            query = f"""
                SELECT id, device_id, `usage`, recorded_at, last_updated, period
                FROM {table_name}
                WHERE id = %s
            """
            cursor.execute(query, (measurement_id,))
            return cursor.fetchone()
            
        except Error as e:
            print(f"Error getting measurement: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return None

def update_measurement(measurement_id, measurement_type, new_value, device_id):
    """Update a measurement"""
    connection = create_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            current_time = dt.datetime.now()
            
            if measurement_type == 'energy_usage':
                table_name = 'EnergyUsage'
            elif measurement_type == 'energy_collected':
                table_name = 'EnergyCollected'
            elif measurement_type == 'water_purified':
                table_name = 'WaterPurified'
            else:
                return False
            
            # Get the last updated timestamp for period calculation
            last_updated = get_last_updated(device_id, table_name)
            calculated_period = calculate_period(last_updated, current_time)
            
            query = f"""
                UPDATE {table_name}
                SET `usage` = %s, last_updated = %s, period = %s
                WHERE id = %s AND device_id = %s
            """
            cursor.execute(query, (new_value, last_updated, calculated_period, measurement_id, device_id))
            connection.commit()
            
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"Error updating measurement: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return False

def delete_measurement(measurement_id, measurement_type, device_id):
    """Delete a measurement"""
    connection = create_database_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            if measurement_type == 'energy_usage':
                table_name = 'EnergyUsage'
            elif measurement_type == 'energy_collected':
                table_name = 'EnergyCollected'
            elif measurement_type == 'water_purified':
                table_name = 'WaterPurified'
            else:
                return False
            
            query = f"DELETE FROM {table_name} WHERE id = %s AND device_id = %s"
            cursor.execute(query, (measurement_id, device_id))
            connection.commit()
            
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"Error deleting measurement: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return False

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
    alerts = get_device_alerts(device_id)
    
    return render_template('dashboard.html', 
                         device_id=device_id, 
                         data=device_data,
                         alerts=alerts)

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

@app.route('/alerts')
def alerts():
    if 'device_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    device_id = session['device_id']
    alerts = get_device_alerts(device_id)
    
    return render_template('alerts.html',
                         device_id=device_id,
                         alerts=alerts)

@app.route('/clear_alerts', methods=['POST'])
def clear_alerts():
    if 'device_id' not in session:
        return redirect(url_for('login'))
    
    device_id = session['device_id']
    trend_analyzer.clear_alerts(device_id)
    flash('Alerts cleared successfully!', 'success')
    
    return redirect(url_for('dashboard'))

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

@app.route('/edit_measurement/<measurement_type>/<int:measurement_id>', methods=['GET', 'POST'])
def edit_measurement(measurement_type, measurement_id):
    if 'device_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    device_id = session['device_id']
    
    if request.method == 'GET':
        measurement = get_measurement_by_id(measurement_id, measurement_type)
        if not measurement or measurement['device_id'] != device_id:
            flash('Measurement not found or access denied.', 'error')
            return redirect(url_for('readings'))
        
        return render_template('edit_measurement.html',
                             measurement=measurement,
                             measurement_type=measurement_type,
                             device_id=device_id)
    
    elif request.method == 'POST':
        new_value = request.form.get('value')
        
        if not new_value or not new_value.replace('.', '').replace('-', '').isdigit():
            flash('Please enter a valid numeric value.', 'error')
            return redirect(url_for('edit_measurement', measurement_type=measurement_type, measurement_id=measurement_id))
        
        try:
            new_value = float(new_value)
            if new_value < 0:
                flash('Value cannot be negative.', 'error')
                return redirect(url_for('edit_measurement', measurement_type=measurement_type, measurement_id=measurement_id))
        except ValueError:
            flash('Please enter a valid numeric value.', 'error')
            return redirect(url_for('edit_measurement', measurement_type=measurement_type, measurement_id=measurement_id))
        
        if update_measurement(measurement_id, measurement_type, new_value, device_id):
            flash(f'{measurement_type.replace("_", " ").title()} measurement updated successfully!', 'success')
        else:
            flash('Failed to update measurement. Please try again.', 'error')
        
        return redirect(url_for('readings'))

@app.route('/delete_measurement/<measurement_type>/<int:measurement_id>', methods=['POST'])
def delete_measurement_route(measurement_type, measurement_id):
    if 'device_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    device_id = session['device_id']
    
    if delete_measurement(measurement_id, measurement_type, device_id):
        flash(f'{measurement_type.replace("_", " ").title()} measurement deleted successfully!', 'success')
    else:
        flash('Failed to delete measurement. Please try again.', 'error')
    
    return redirect(url_for('readings'))

if __name__ == '__main__':
    # Get the Raspberry Pi's IP address for network access
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"SafiFlow Web Dashboard")
    print(f"Local access: http://localhost:5000")
    print(f"Network access: http://{local_ip}:5000")
    print(f"Press Ctrl+C to stop the server")
    
    # Run Flask app on all network interfaces
    app.run(host='0.0.0.0', port=5000, debug=False)