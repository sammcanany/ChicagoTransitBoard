# WiFi Setup Portal for Chicago Transit Board
# Creates an Access Point and web server for initial configuration

import network
import socket
import time
import machine

# AP Configuration
AP_SSID = "ChicagoTransitBoard"
AP_PASSWORD = "setup1234"  # Change this for security

def create_ap():
    """Create Access Point for setup"""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD)
    
    while not ap.active():
        time.sleep(0.1)
    
    print(f"\n{'='*50}")
    print(f"Access Point Created!")
    print(f"{'='*50}")
    print(f"Network: {AP_SSID}")
    print(f"Password: {AP_PASSWORD}")
    print(f"IP Address: {ap.ifconfig()[0]}")
    print(f"\nConnect to this network and go to:")
    print(f"http://{ap.ifconfig()[0]}")
    print(f"{'='*50}\n")
    
    return ap

def html_page(error="", networks=[]):
    """Generate setup HTML page"""
    error_html = f'<div class="error">{error}</div>' if error else ""
    
    # Generate network options
    network_options = ""
    if networks:
        for ssid, rssi, _security in networks:
            # Signal strength indicator (using ASCII for compatibility)
            if rssi > -50:
                signal = "****"
            elif rssi > -60:
                signal = "*** "
            elif rssi > -70:
                signal = "**  "
            else:
                signal = "*   "

            network_options += f'<option value="{ssid}">{ssid} ({signal})</option>\n'
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Chicago Transit Board - WiFi Setup</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .container {{
            background: white;
            max-width: 500px;
            width: 100%;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .logo {{
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #009B3A 0%, #007A2E 100%);
            border-radius: 20px;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            color: white;
            font-weight: bold;
        }}
        
        h1 {{
            color: #2d3748;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        
        .subtitle {{
            color: #718096;
            font-size: 14px;
        }}
        
        .info {{
            background: #EBF8FF;
            border-left: 4px solid #3182CE;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 25px;
            font-size: 14px;
            color: #2C5282;
        }}
        
        .error {{
            background: #FFF5F5;
            border-left: 4px solid #E53E3E;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 25px;
            font-size: 14px;
            color: #C53030;
        }}
        
        .form-group {{
            margin-bottom: 25px;
        }}
        
        label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2d3748;
            font-size: 14px;
        }}
        
        input, select {{
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 15px;
            transition: all 0.3s;
            background: white;
        }}
        
        input:focus, select:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        
        .help {{
            font-size: 12px;
            color: #718096;
            margin-top: 6px;
        }}
        
        button {{
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-bottom: 12px;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }}
        
        .btn-secondary {{
            background: #edf2f7;
            color: #4a5568;
        }}
        
        .btn-secondary:hover {{
            background: #e2e8f0;
        }}
        
        .signal {{
            font-size: 12px;
            margin-left: 5px;
        }}
        
        .excellent {{ color: #38a169; }}
        .good {{ color: #48bb78; }}
        .fair {{ color: #ecc94b; }}
        .weak {{ color: #f56565; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">CTB</div>
            <h1>Chicago Transit Board</h1>
            <div class="subtitle">WiFi Configuration</div>
        </div>
        
        <div class="info">
            <strong>Step 1: Connect to WiFi</strong><br>
            Select your network and enter the password. You can configure Metra settings later by editing config.py on the board.
        </div>
        
        {error_html}
        
        <form method="POST" action="/save">
            <div class="form-group">
                <label>WiFi Network</label>
                <select name="ssid" id="ssid" required onchange="checkManual()">
                    <option value="">-- Select Network --</option>
                    {network_options}
                    <option value="__manual__">Enter Manually...</option>
                </select>
                <input type="text" name="ssid_manual" id="ssid_manual" placeholder="Network Name" style="display:none; margin-top:10px;">
                <div class="help">2.4GHz networks only (5GHz not supported)</div>
            </div>
            
            <div class="form-group">
                <label>WiFi Password</label>
                <input type="password" name="password" required placeholder="Enter your WiFi password">
            </div>
            
            <button type="submit" class="btn-primary">Connect and Save</button>
            <button type="button" class="btn-secondary" onclick="location.reload()">Rescan Networks</button>
        </form>
    </div>
    
    <script>
        function checkManual() {{
            var select = document.getElementById('ssid');
            var manual = document.getElementById('ssid_manual');
            if (select.value === '__manual__') {{
                manual.style.display = 'block';
                manual.required = true;
                select.required = false;
            }} else {{
                manual.style.display = 'none';
                manual.required = false;
                select.required = true;
            }}
        }}
    </script>
</body>
</html>"""

def success_page():
    """Page shown after successful save"""
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>WiFi Connected!</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            max-width: 500px;
            width: 100%;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }
        
        .checkmark {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            border-radius: 50%;
            margin: 0 auto 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 50px;
            color: white;
        }
        
        h1 {
            color: #2d3748;
            font-size: 28px;
            margin-bottom: 20px;
        }
        
        .success-box {
            background: #F0FFF4;
            border: 2px solid #9AE6B4;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 30px;
        }
        
        .success-box h2 {
            color: #22543D;
            font-size: 20px;
            margin-bottom: 10px;
        }
        
        .success-box p {
            color: #2F855A;
            line-height: 1.6;
        }
        
        .next-steps {
            text-align: left;
            background: #f7fafc;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .next-steps h3 {
            color: #2d3748;
            font-size: 16px;
            margin-bottom: 15px;
        }
        
        .next-steps ol {
            margin-left: 20px;
            color: #4a5568;
            line-height: 1.8;
        }
        
        .next-steps code {
            background: #edf2f7;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 13px;
        }
        
        .countdown {
            color: #718096;
            font-size: 14px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="checkmark">&#10003;</div>
        <h1>WiFi Connected!</h1>
        
        <div class="success-box">
            <h2>Setup Complete</h2>
            <p>Your Chicago Transit Board is now connected to WiFi.</p>
        </div>
        
        <div class="next-steps">
            <h3>Next Steps:</h3>
            <ol>
                <li>Edit <code>config.py</code> on the board to add your Metra API token and station settings</li>
                <li>Or see <code>config.example.py</code> for all available options</li>
                <li>Restart the board to start showing train data</li>
            </ol>
        </div>
        
        <div class="countdown">This setup network will shut down in 5 seconds...</div>
    </div>
</body>
</html>"""

def scan_networks():
    """Scan for available WiFi networks"""
    import network
    
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    
    print("Scanning for WiFi networks...")
    networks = sta.scan()
    
    # Sort by signal strength (RSSI)
    networks = sorted(networks, key=lambda x: x[3], reverse=True)
    
    # Format: (ssid, bssid, channel, RSSI, security, hidden)
    # Convert to (ssid_string, rssi, has_security)
    result = []
    seen_ssids = set()
    
    for net in networks:
        ssid = net[0].decode('utf-8') if net[0] else ""
        rssi = net[3]
        security = net[4] != 0  # 0 = open, anything else = secured
        
        # Skip hidden networks and duplicates
        if ssid and ssid not in seen_ssids:
            result.append((ssid, rssi, security))
            seen_ssids.add(ssid)
    
    sta.active(False)
    print(f"Found {len(result)} networks")
    return result

def parse_form_data(data):
    """Parse URL-encoded form data"""
    params = {}
    pairs = data.split('&')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            # URL decode - handle common characters
            value = value.replace('+', ' ')

            # Decode percent-encoded characters
            i = 0
            decoded = ""
            while i < len(value):
                if value[i] == '%' and i + 2 < len(value):
                    try:
                        hex_chars = value[i+1:i+3]
                        decoded += chr(int(hex_chars, 16))
                        i += 3
                    except ValueError:
                        decoded += value[i]
                        i += 1
                else:
                    decoded += value[i]
                    i += 1

            params[key] = decoded
    return params

def save_config(params):
    """Save WiFi configuration to config.py"""
    
    # Get SSID - either from dropdown or manual entry
    ssid = params.get('ssid', '')
    if ssid == '__manual__':
        ssid = params.get('ssid_manual', '')
    
    config_content = f"""# Chicago Transit Board Configuration
# WiFi configured via setup portal
# Edit this file to add your Metra API settings

# ===== WIFI SETTINGS =====
WIFI_SSID = "{ssid}"
WIFI_PASSWORD = "{params.get('password', '')}"

# ===== METRA API =====
# Get your token from https://www.metrarail.com/developers
METRA_API_TOKEN = "your_token_here"

# ===== STATION AND LINES =====
STATION_STOP_ID = "Ravenswood"  # Change to your station
LINE_1 = "UP-N"  # Primary line
LINE_2 = None  # Optional second line for dual display

# ===== DISPLAY SETTINGS =====
DISPLAY_ROTATION_TIME = 5  # Seconds between Inbound/Outbound/Alerts
UPDATE_INTERVAL = 60  # Seconds between API updates
BRIGHTNESS = 0.5  # 0.0 to 1.0

# ===== FEATURE TOGGLES =====
ENABLE_AUTO_UPDATE = True
CHECK_UPDATE_INTERVAL = 3600  # Check for updates every hour
ENABLE_SERVICE_ALERTS = True
ENABLE_ALERT_ICONS = True
"""
    
    try:
        with open('config.py', 'w') as f:
            f.write(config_content)
        print("WiFi configuration saved to config.py")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def run_server():
    """Run the web server"""
    ap = create_ap()
    
    # Scan for networks once at startup
    print("\nScanning for available networks...")
    available_networks = scan_networks()
    
    # Create socket
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    
    print("Web server running...")
    
    while True:
        try:
            cl, addr = s.accept()
            print(f'\nClient connected from {addr}')

            # Read headers first
            cl.settimeout(5.0)
            request = b''
            while b'\r\n\r\n' not in request:
                chunk = cl.recv(1024)
                if not chunk:
                    break
                request += chunk

            # Check for Content-Length and read body if present
            headers_end = request.find(b'\r\n\r\n')
            if headers_end > 0:
                headers = request[:headers_end].decode('utf-8')
                body_start = request[headers_end + 4:]

                # Find Content-Length
                content_length = 0
                for line in headers.split('\r\n'):
                    if line.lower().startswith('content-length:'):
                        content_length = int(line.split(':')[1].strip())
                        break

                # Read remaining body if needed
                while len(body_start) < content_length:
                    chunk = cl.recv(1024)
                    if not chunk:
                        break
                    body_start += chunk

                request = (request[:headers_end + 4] + body_start)

            request = request.decode('utf-8')
            
            # Parse request
            lines = request.split('\r\n')
            if len(lines) > 0:
                method_line = lines[0]
                print(f"Request: {method_line}")
                
                if 'GET / ' in method_line or 'GET /setup' in method_line:
                    # Rescan networks on page load
                    networks = scan_networks()
                    response = html_page(networks=networks)
                    cl.send('HTTP/1.1 200 OK\r\n')
                    cl.send('Content-Type: text/html\r\n')
                    cl.send('Connection: close\r\n\r\n')
                    cl.sendall(response)
                
                elif 'POST /save' in method_line:
                    # Extract form data
                    body = request.split('\r\n\r\n', 1)[1] if '\r\n\r\n' in request else ''
                    print(f"Form body: {body}")  # Debug
                    params = parse_form_data(body)
                    print(f"Parsed params: {params}")  # Debug

                    ssid = params.get('ssid', '')
                    if ssid == '__manual__':
                        ssid = params.get('ssid_manual', 'N/A')
                    password = params.get('password', '')
                    print(f"Received WiFi config: SSID={ssid}, Password={'*' * len(password)}")
                    
                    # Save configuration
                    if save_config(params):
                        response = success_page()
                        cl.send('HTTP/1.1 200 OK\r\n')
                        cl.send('Content-Type: text/html\r\n')
                        cl.send('Connection: close\r\n\r\n')
                        cl.sendall(response)
                        cl.close()
                        
                        print("\n⏳ Restarting in 5 seconds...")
                        time.sleep(5)
                        
                        # Shutdown AP and restart
                        ap.active(False)
                        s.close()
                        machine.reset()
                    else:
                        response = html_page(error="Failed to save WiFi configuration. Please try again.", networks=available_networks)
                        cl.send('HTTP/1.1 500 Internal Server Error\r\n')
                        cl.send('Content-Type: text/html\r\n')
                        cl.send('Connection: close\r\n\r\n')
                        cl.sendall(response)
                
                else:
                    # 404
                    cl.send('HTTP/1.1 404 Not Found\r\n')
                    cl.send('Connection: close\r\n\r\n')
            
            cl.close()
            
        except Exception as e:
            print(f"Error handling request: {e}")
            try:
                cl.close()
            except:
                pass

if __name__ == "__main__":
    print("Starting setup portal...")
    run_server()
