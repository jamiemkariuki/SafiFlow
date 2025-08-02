# SafiFlow Network Access Guide

This guide explains how to access the SafiFlow web dashboard from other devices on your network.

## Network Configuration

### Flask App Changes
The Flask application has been updated to run on all network interfaces:

```python
# Run Flask app on all network interfaces
app.run(host='0.0.0.0', port=5000, debug=False)
```

### What This Means:
- **`host='0.0.0.0'`**: Makes the app accessible from any network interface
- **`port=5000`**: Standard Flask port
- **`debug=False`**: Production mode for network access

## Accessing the Dashboard

### 1. Find Your Raspberry Pi's IP Address

When you start the Flask app, it will display the IP addresses:

```bash
python3 app.py
```

Output:
```
SafiFlow Web Dashboard
Local access: http://localhost:5000
Network access: http://192.168.1.100:5000
Press Ctrl+C to stop the server
```

### 2. Access from Other Devices

#### From Any Device on the Network:
- **URL**: `http://[RASPBERRY_PI_IP]:5000`
- **Example**: `http://192.168.1.100:5000`

#### From Your Computer:
- **Local**: `http://localhost:5000`
- **Network**: `http://192.168.1.100:5000`

#### From Mobile Devices:
- **Phone/Tablet**: `http://192.168.1.100:5000`
- **Same WiFi**: Must be on the same network

## Network Troubleshooting

### 1. Find Raspberry Pi IP Address

#### Method 1: From Raspberry Pi
```bash
hostname -I
```

#### Method 2: From Router
- Log into your router admin panel
- Look for connected devices
- Find your Raspberry Pi by hostname

#### Method 3: Network Scan
```bash
nmap -sn 192.168.1.0/24
```

### 2. Test Network Connectivity

#### From Raspberry Pi:
```bash
# Test if port 5000 is open
netstat -tlnp | grep 5000
```

#### From Another Device:
```bash
# Test connection to Raspberry Pi
ping 192.168.1.100

# Test web server
curl http://192.168.1.100:5000
```

### 3. Common Issues and Solutions

#### Issue: "Connection Refused"
**Solution:**
1. Check if Flask is running: `ps aux | grep python`
2. Verify port 5000 is not blocked
3. Restart Flask app

#### Issue: "Page Not Found"
**Solution:**
1. Check if app is running on correct port
2. Verify URL is correct
3. Check firewall settings

#### Issue: "Cannot Access from Mobile"
**Solution:**
1. Ensure mobile device is on same WiFi
2. Check router firewall settings
3. Try accessing via IP address

## Security Considerations

### 1. Network Security
- **Firewall**: Configure router firewall if needed
- **Port Forwarding**: Only if accessing from internet
- **VPN**: Consider VPN for remote access

### 2. Application Security
- **Change Secret Key**: Update in `app.py`
- **HTTPS**: Consider SSL certificate for production
- **Authentication**: Device ID-based login is basic

### 3. Production Recommendations
```python
# For production, consider:
app.secret_key = os.environ.get('SECRET_KEY', 'your_secure_key')
app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
```

## Advanced Configuration

### 1. Custom Port
```python
# Change port in app.py
app.run(host='0.0.0.0', port=8080, debug=False)
```

### 2. Domain Name
- Set up DNS for your Raspberry Pi
- Use domain instead of IP address
- Example: `http://safiflow.local:5000`

### 3. Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Mobile Access

### 1. QR Code Access
Create a QR code with your dashboard URL:
```
http://192.168.1.100:5000
```

### 2. Mobile Browser
- Open browser on phone/tablet
- Enter the dashboard URL
- Login with Device ID

### 3. Responsive Design
The dashboard is mobile-responsive and works on:
- **Smartphones**: iOS Safari, Android Chrome
- **Tablets**: iPad, Android tablets
- **Desktop**: Chrome, Firefox, Safari, Edge

## Testing Network Access

### 1. From Different Devices
- **Computer**: `http://192.168.1.100:5000`
- **Phone**: Same URL on mobile browser
- **Tablet**: Same URL on tablet browser

### 2. Network Commands
```bash
# Test from Raspberry Pi
curl http://localhost:5000

# Test from another device
curl http://192.168.1.100:5000

# Check if port is open
telnet 192.168.1.100 5000
```

### 3. Troubleshooting Commands
```bash
# Check Flask process
ps aux | grep python

# Check network interfaces
ifconfig

# Check listening ports
netstat -tlnp

# Test database connection
mysql -h 192.168.72.143 -u root -p
```

## Quick Start

1. **Start Flask App**:
   ```bash
   python3 app.py
   ```

2. **Note the IP Address**:
   ```
   Network access: http://192.168.1.100:5000
   ```

3. **Access from Any Device**:
   - Open browser
   - Go to: `http://192.168.1.100:5000`
   - Login with Device ID

4. **Test All Features**:
   - Dashboard view
   - Add measurements
   - View all readings
   - Logout functionality

The SafiFlow dashboard is now accessible from any device on your network! 🚀 