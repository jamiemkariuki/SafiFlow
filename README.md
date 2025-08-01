# SafiFlow Data Collection System

A comprehensive IoT data collection system for monitoring energy usage, energy collection, and water purification metrics with both console and web interfaces.

## Features

- **Unique device ID generation and management**
- **MySQL database integration**
- **Energy usage tracking**
- **Energy collection monitoring**
- **Water purification measurement**
- **Data persistence and retrieval**
- **Modern web dashboard with authentication**
- **Real-time data visualization**
- **Responsive design for mobile devices**

## System Architecture

### Console Application (`script.py`)
- Command-line interface for data collection
- Direct database interaction
- Device ID management

### Web Dashboard (`app.py`)
- Modern web interface with authentication
- Real-time data visualization
- Responsive design
- Session management

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Setup

1. **Start MySQL server**
2. **Create the database and tables:**
   ```bash
   mysql -u root -p < safiflow.sql
   ```
3. **Update database configuration** in `app.py`, `script.py`, and `setup_database.py`:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': 'your_mysql_password',  # Update this
       'database': 'safiflow'
   }
   ```

### 3. Initialize Device ID

Run the setup script to create and register the device ID:

```bash
python setup_database.py
```

This will:
- Generate a unique device ID
- Save it to `device_id.txt`
- Insert it into the database

### 4. Run the Applications

#### Console Application
```bash
python script.py
```

#### Web Dashboard
```bash
python app.py
```

Then open your browser and navigate to: `http://localhost:5000`

## Usage

### Console Application

The console application provides a menu-driven interface:

1. **Device ID** - Display the current device ID
2. **Measure energy usage** - Record energy consumption in kWh
3. **Measure energy collected** - Record energy generation in kWh
4. **Measure water purified** - Record water purification in litres
5. **Exit** - Close the application

### Web Dashboard

1. **Login** - Enter your Device ID to access the dashboard
2. **View Data** - See real-time metrics and statistics
3. **Add Measurements** - Input new data through the web interface
4. **Logout** - Secure session management

## File Structure

```
SafiFlow/
├── app.py                 # Flask web application
├── script.py              # Console application
├── DeviceID.py            # Device ID management
├── setup_database.py      # Database initialization
├── safiflow.sql          # Database schema
├── requirements.txt       # Python dependencies
├── device_id.txt         # Stored device ID (auto-generated)
├── templates/
│   ├── index.html        # Landing page
│   ├── login.html        # Login page
│   └── dashboard.html    # Main dashboard
└── README.md            # This file
```

## Database Schema

The system uses the following tables:

- **`DeviceID`** - Stores unique device identifiers
- **`EnergyUsage`** - Records energy consumption data
- **`EnergyCollected`** - Records energy generation data
- **`WaterPurified`** - Records water purification data
- **`Users`** - User management (for future use)

## Web Dashboard Features

### Authentication
- Device ID-based login system
- Session management with Flask-Session
- Secure logout functionality

### Dashboard Components
- **Real-time Metrics Display**
  - Latest energy usage, collection, and water purification data
  - Historical statistics and averages
  - Timestamp information

- **Data Input Forms**
  - Add new energy usage measurements
  - Record energy collection data
  - Input water purification metrics

- **Responsive Design**
  - Mobile-friendly interface
  - Modern gradient backgrounds
  - Interactive hover effects

### Visual Design
- **Modern UI/UX**
  - Glassmorphism design elements
  - Gradient color schemes
  - Font Awesome icons
  - Smooth animations and transitions

- **Data Visualization**
  - Card-based layout for metrics
  - Color-coded categories
  - Statistical summaries
  - Time-based information

## Troubleshooting

### Common Issues

1. **MySQL Connection Error**
   - Ensure MySQL server is running
   - Verify credentials in DB_CONFIG
   - Check database and table existence

2. **Device ID Issues**
   - Delete `device_id.txt` and run `setup_database.py` again
   - Verify device ID exists in database

3. **Web Dashboard Not Loading**
   - Check if Flask is installed: `pip install Flask Flask-Session`
   - Ensure port 5000 is available
   - Check console for error messages

4. **Session Issues**
   - Clear browser cookies
   - Restart the Flask application
   - Check session configuration

### Database Issues

1. **Tables Not Found**
   ```bash
   mysql -u root -p < safiflow.sql
   ```

2. **Connection Refused**
   - Start MySQL service
   - Check firewall settings
   - Verify host and port configuration

## Security Considerations

- Change the Flask secret key in production
- Use environment variables for database credentials
- Implement proper user authentication for production
- Add HTTPS for production deployment
- Regular database backups

## Development

### Adding New Features

1. **New Data Types**
   - Add table to `safiflow.sql`
   - Update database functions in `app.py`
   - Add form fields to dashboard template

2. **New Dashboard Features**
   - Extend `get_device_data()` function
   - Add new routes in `app.py`
   - Create new template sections

3. **API Endpoints**
   - Add new routes with proper authentication
   - Implement JSON responses for AJAX calls
   - Add error handling and validation

## Production Deployment

1. **Environment Setup**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your_secure_secret_key
   ```

2. **Database Security**
   - Use dedicated database user
   - Implement connection pooling
   - Regular backups

3. **Web Server**
   - Use Gunicorn or uWSGI
   - Configure Nginx reverse proxy
   - Enable HTTPS

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review database logs
3. Check Flask application logs
4. Verify all dependencies are installed 