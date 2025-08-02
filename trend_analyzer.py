import mysql.connector
from mysql.connector import Error
import datetime as dt
from datetime import timedelta
import statistics
import json
import os

# Database configuration
DB_CONFIG = {
    'host': '192.168.72.143',
    'user': 'root',
    'password': 'hello',
    'database': 'safiflow'
}

class TrendAnalyzer:
    def __init__(self):
        self.alerts = []
        self.alert_file = "alerts.json"
        self.load_alerts()
    
    def create_database_connection(self):
        """Create and return a database connection"""
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def get_recent_readings(self, device_id, measurement_type, days=7):
        """Get recent readings for trend analysis"""
        connection = self.create_database_connection()
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
                    return []
                
                # Get readings from last N days
                cutoff_date = dt.datetime.now() - timedelta(days=days)
                
                query = f"""
                    SELECT `usage`, recorded_at, period
                    FROM {table_name}
                    WHERE device_id = %s AND recorded_at >= %s
                    ORDER BY recorded_at ASC
                """
                cursor.execute(query, (device_id, cutoff_date))
                return cursor.fetchall()
                
            except Error as e:
                print(f"Error getting readings: {e}")
                return []
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return []
    
    def analyze_trend(self, readings, measurement_type):
        """Analyze trend in readings"""
        if len(readings) < 3:
            return None, "Insufficient data for trend analysis"
        
        # Extract values and timestamps
        values = [reading['usage'] for reading in readings]
        timestamps = [reading['recorded_at'] for reading in readings]
        
        # Calculate basic statistics
        mean_value = statistics.mean(values)
        current_value = values[-1]
        previous_value = values[-2] if len(values) > 1 else current_value
        
        # Calculate trend indicators
        trend_direction = "stable"
        trend_strength = "weak"
        alert_level = "none"
        
        # Determine trend direction
        if current_value > previous_value * 1.1:  # 10% increase
            trend_direction = "rising"
            if current_value > mean_value * 1.2:  # 20% above average
                alert_level = "warning"
            if current_value > mean_value * 1.5:  # 50% above average
                alert_level = "critical"
        elif current_value < previous_value * 0.9:  # 10% decrease
            trend_direction = "falling"
        
        # Calculate trend strength
        if len(values) >= 5:
            recent_values = values[-5:]
            slope = (recent_values[-1] - recent_values[0]) / len(recent_values)
            
            if abs(slope) > mean_value * 0.1:
                trend_strength = "strong"
            elif abs(slope) > mean_value * 0.05:
                trend_strength = "moderate"
        
        # Generate trend message
        trend_message = f"{measurement_type.replace('_', ' ').title()} is {trend_direction}"
        if trend_strength != "weak":
            trend_message += f" ({trend_strength} trend)"
        
        return {
            'direction': trend_direction,
            'strength': trend_strength,
            'alert_level': alert_level,
            'current_value': current_value,
            'previous_value': previous_value,
            'mean_value': mean_value,
            'message': trend_message,
            'readings_count': len(readings)
        }, None
    
    def check_anomalies(self, readings, measurement_type):
        """Check for anomalous readings"""
        if len(readings) < 3:
            return []
        
        values = [reading['usage'] for reading in readings]
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        anomalies = []
        for i, reading in enumerate(readings):
            value = reading['usage']
            z_score = abs((value - mean_value) / std_dev) if std_dev > 0 else 0
            
            if z_score > 2:  # More than 2 standard deviations
                anomaly = {
                    'type': 'anomaly',
                    'measurement_type': measurement_type,
                    'value': value,
                    'timestamp': reading['recorded_at'],
                    'severity': 'high' if z_score > 3 else 'medium',
                    'message': f"Unusual {measurement_type.replace('_', ' ')} reading: {value:.2f}"
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def check_energy_efficiency(self, energy_usage_readings, energy_collected_readings):
        """Check energy efficiency (usage vs collected)"""
        if not energy_usage_readings or not energy_collected_readings:
            return None
        
        # Get most recent readings
        latest_usage = energy_usage_readings[-1]['usage'] if energy_usage_readings else 0
        latest_collected = energy_collected_readings[-1]['usage'] if energy_collected_readings else 0
        
        if latest_collected > 0:
            efficiency_ratio = latest_usage / latest_collected
            
            if efficiency_ratio > 1.5:  # Using 50% more than collecting
                return {
                    'type': 'efficiency',
                    'severity': 'high',
                    'ratio': efficiency_ratio,
                    'message': f"Energy usage ({latest_usage:.2f} kWh) is {efficiency_ratio:.1f}x higher than collection ({latest_collected:.2f} kWh)"
                }
            elif efficiency_ratio > 1.2:  # Using 20% more than collecting
                return {
                    'type': 'efficiency',
                    'severity': 'medium',
                    'ratio': efficiency_ratio,
                    'message': f"Energy usage ({latest_usage:.2f} kWh) is {efficiency_ratio:.1f}x higher than collection ({latest_collected:.2f} kWh)"
                }
        
        return None
    
    def analyze_device(self, device_id):
        """Analyze trends for a specific device"""
        alerts = []
        
        # Analyze each measurement type
        measurement_types = ['energy_usage', 'energy_collected', 'water_purified']
        
        for measurement_type in measurement_types:
            readings = self.get_recent_readings(device_id, measurement_type, days=7)
            
            if readings:
                # Analyze trends
                trend_result, error = self.analyze_trend(readings, measurement_type)
                if trend_result and trend_result['alert_level'] != 'none':
                    alert = {
                        'type': 'trend',
                        'measurement_type': measurement_type,
                        'severity': trend_result['alert_level'],
                        'message': trend_result['message'],
                        'timestamp': dt.datetime.now(),
                        'device_id': device_id
                    }
                    alerts.append(alert)
                
                # Check for anomalies
                anomalies = self.check_anomalies(readings, measurement_type)
                alerts.extend(anomalies)
        
        # Check energy efficiency
        energy_usage_readings = self.get_recent_readings(device_id, 'energy_usage', days=1)
        energy_collected_readings = self.get_recent_readings(device_id, 'energy_collected', days=1)
        
        efficiency_alert = self.check_energy_efficiency(energy_usage_readings, energy_collected_readings)
        if efficiency_alert:
            efficiency_alert['device_id'] = device_id
            efficiency_alert['timestamp'] = dt.datetime.now()
            alerts.append(efficiency_alert)
        
        return alerts
    
    def get_all_devices(self):
        """Get all device IDs from database"""
        connection = self.create_database_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT device_id FROM DeviceID"
                cursor.execute(query)
                devices = [row[0] for row in cursor.fetchall()]
                return devices
            except Error as e:
                print(f"Error getting devices: {e}")
                return []
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return []
    
    def run_analysis(self):
        """Run analysis for all devices"""
        devices = self.get_all_devices()
        all_alerts = []
        
        for device_id in devices:
            device_alerts = self.analyze_device(device_id)
            all_alerts.extend(device_alerts)
        
        # Add new alerts to existing ones
        self.alerts.extend(all_alerts)
        
        # Keep only recent alerts (last 30 days)
        cutoff_date = dt.datetime.now() - timedelta(days=30)
        self.alerts = [alert for alert in self.alerts if alert['timestamp'] > cutoff_date]
        
        # Save alerts
        self.save_alerts()
        
        return all_alerts
    
    def get_alerts_for_device(self, device_id):
        """Get alerts for a specific device"""
        return [alert for alert in self.alerts if alert.get('device_id') == device_id]
    
    def get_active_alerts(self):
        """Get all active alerts"""
        return self.alerts
    
    def clear_alerts(self, device_id=None):
        """Clear alerts for a device or all alerts"""
        if device_id:
            self.alerts = [alert for alert in self.alerts if alert.get('device_id') != device_id]
        else:
            self.alerts = []
        self.save_alerts()
    
    def save_alerts(self):
        """Save alerts to JSON file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            alerts_for_save = []
            for alert in self.alerts:
                alert_copy = alert.copy()
                if 'timestamp' in alert_copy:
                    alert_copy['timestamp'] = alert_copy['timestamp'].isoformat()
                alerts_for_save.append(alert_copy)
            
            with open(self.alert_file, 'w') as f:
                json.dump(alerts_for_save, f, indent=2)
        except Exception as e:
            print(f"Error saving alerts: {e}")
    
    def load_alerts(self):
        """Load alerts from JSON file"""
        try:
            if os.path.exists(self.alert_file):
                with open(self.alert_file, 'r') as f:
                    alerts_data = json.load(f)
                
                # Convert string timestamps back to datetime objects
                self.alerts = []
                for alert in alerts_data:
                    if 'timestamp' in alert:
                        alert['timestamp'] = dt.datetime.fromisoformat(alert['timestamp'])
                    self.alerts.append(alert)
            else:
                self.alerts = []
        except Exception as e:
            print(f"Error loading alerts: {e}")
            self.alerts = []

def main():
    """Main function to run trend analysis"""
    analyzer = TrendAnalyzer()
    
    print("Running SafiFlow Trend Analysis...")
    new_alerts = analyzer.run_analysis()
    
    if new_alerts:
        print(f"\nFound {len(new_alerts)} new alerts:")
        for alert in new_alerts:
            print(f"- [{alert['severity'].upper()}] {alert['message']}")
    else:
        print("No new alerts found.")
    
    # Print summary
    total_alerts = len(analyzer.get_active_alerts())
    print(f"\nTotal active alerts: {total_alerts}")

if __name__ == "__main__":
    main() 