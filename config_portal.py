# Configuration Portal for Chicago Transit Board
# Access at http://board.local after WiFi setup
# Allows web-based configuration of all settings

import network
import socket
import json
import time
import machine
import os

# mDNS support for board.local
try:
    import mdns
    MDNS_AVAILABLE = True
except ImportError:
    MDNS_AVAILABLE = False

def setup_mdns(hostname="board"):
    """Set up mDNS so board is accessible at board.local"""
    if not MDNS_AVAILABLE:
        print("mDNS not available - access by IP address only")
        return False
    
    try:
        mdns_server = mdns.Server()
        mdns_server.set_name(hostname)
        mdns_server.start()
        print(f"mDNS started - accessible at http://{hostname}.local")
        return True
    except Exception as e:
        print(f"mDNS setup failed: {e}")
        return False

def detect_transit_type(line_code):
    """Determine if a line is CTA or Metra"""
    if not line_code:
        return "metra"
    cta_lines = ["Red", "Blue", "Brn", "Brown", "G", "Green", "Org", "Orange", "P", "Purple", "Pink", "Y", "Yellow"]
    return "cta" if line_code in cta_lines else "metra"

def get_current_config():
    """Read current config.py settings"""
    try:
        import config
        return {
            'wifi_ssid': getattr(config, 'WIFI_SSID', ''),
            'metra_token': getattr(config, 'METRA_API_TOKEN', ''),
            'cta_token': getattr(config, 'CTA_API_KEY', ''),
            'station_id': getattr(config, 'PRIMARY_STATION_ID', ''),
            'station_name': getattr(config, 'STATION_STOP_ID', ''),
            'line_id': getattr(config, 'LINE_1', ''),
            'line_name': getattr(config, 'LINE_1', ''),
            'secondary_line_id': getattr(config, 'LINE_2', None),
            'secondary_line_name': getattr(config, 'LINE_2', None),
            'secondary_station_id': getattr(config, 'SECONDARY_STATION_ID', None),
            'secondary_station_name': getattr(config, 'SECONDARY_STATION_NAME', None),
            'secondary_transit_type': detect_transit_type(getattr(config, 'LINE_2', None)),
            'enable_secondary': getattr(config, 'LINE_2', None) is not None,
            'brightness': getattr(config, 'BRIGHTNESS', 0.5),
            'update_interval': getattr(config, 'UPDATE_INTERVAL', 60),
            'rotation_time': getattr(config, 'DISPLAY_ROTATION_TIME', 5),
            'num_trains': getattr(config, 'NUM_TRAINS_TO_SHOW', 4),
            'enable_service_alerts': getattr(config, 'ENABLE_SERVICE_ALERTS', True),
            'enable_alert_icons': getattr(config, 'ENABLE_ALERT_ICONS', True),
            'alerts_update_interval': getattr(config, 'ALERTS_UPDATE_INTERVAL', 180),
            'enable_auto_update': getattr(config, 'ENABLE_AUTO_UPDATE', True),
            'check_update_interval': getattr(config, 'CHECK_UPDATE_INTERVAL', 604800),
            # v1.3.0 features
            'enable_watchdog': getattr(config, 'ENABLE_WATCHDOG', True),
            'watchdog_timeout': getattr(config, 'WATCHDOG_TIMEOUT', 8000),
            'enable_status_led': getattr(config, 'ENABLE_STATUS_LED', True),
            'enable_weather': getattr(config, 'ENABLE_WEATHER', False),
            'weather_api_service': getattr(config, 'WEATHER_API_SERVICE', 'weathergov'),
            'weather_api_key': getattr(config, 'WEATHER_API_KEY', ''),
            'weather_zip_code': getattr(config, 'WEATHER_ZIP_CODE', ''),
            'weather_update_interval': getattr(config, 'WEATHER_UPDATE_INTERVAL', 1800),
            'weather_display_mode': getattr(config, 'WEATHER_DISPLAY_MODE', 'icon_only'),
            'enable_sleep_mode': getattr(config, 'ENABLE_SLEEP_MODE', False),
            'sleep_start_hour': getattr(config, 'SLEEP_START_HOUR', 23),
            'sleep_end_hour': getattr(config, 'SLEEP_END_HOUR', 5),
            'sleep_brightness': getattr(config, 'SLEEP_BRIGHTNESS', 0.1),
            'enable_adaptive_brightness': getattr(config, 'ENABLE_ADAPTIVE_BRIGHTNESS', False),
            'rotation_mode': getattr(config, 'ROTATION_MODE', 'direction'),
        }
        
        # Extract station rotation data if available
        rotation_stations = getattr(config, 'ROTATION_STATIONS', [])
        for i, station in enumerate(rotation_stations[:3], 1):  # Up to 3 stations
            result[f'station{i}_station_id'] = station.get('id', '')
            result[f'station{i}_line_id'] = station.get('line', '')
        
        return result
    except ImportError:
        return {
            'wifi_ssid': '',
            'metra_token': '',
            'cta_token': '',
            'station_id': '',
            'station_name': '',
            'line_id': '',
            'line_name': '',
            'secondary_line_id': None,
            'secondary_line_name': None,
            'secondary_station_id': None,
            'secondary_station_name': None,
            'secondary_transit_type': 'metra',
            'enable_secondary': False,
            'brightness': 0.5,
            'update_interval': 60,
            'rotation_time': 5,
            'num_trains': 4,
            'enable_service_alerts': True,
            'enable_alert_icons': True,
            'enable_auto_update': True,
            'check_update_interval': 604800,
            'enable_watchdog': True,
            'watchdog_timeout': 8000,
            'enable_status_led': True,
            'enable_weather': False,
            'weather_api_service': 'weathergov',
            'weather_api_key': '',
            'weather_zip_code': '',
            'weather_update_interval': 1800,
            'weather_display_mode': 'icon_only',
            'enable_sleep_mode': False,
            'sleep_start_hour': 23,
            'sleep_end_hour': 5,
            'sleep_brightness': 0.1,
            'enable_adaptive_brightness': False,
            'rotation_mode': 'direction',
            'station1_station_id': '',
            'station1_line_id': '',
            'station2_station_id': '',
            'station2_line_id': '',
            'station3_station_id': '',
            'station3_line_id': '',
        }

def get_system_status():
    """Get current system status"""
    import gc
    
    # Get WiFi info
    wlan = network.WLAN(network.STA_IF)
    wifi_connected = wlan.isconnected()
    ip_address = wlan.ifconfig()[0] if wifi_connected else "Not connected"
    
    # Get memory info
    free_mem = gc.mem_free()
    used_mem = gc.mem_alloc()
    total_mem = free_mem + used_mem
    
    # Get version
    try:
        with open('version.txt', 'r') as f:
            version = f.read().strip()
    except:
        version = "Unknown"
    
    return {
        'version': version,
        'ip_address': ip_address,
        'wifi_connected': wifi_connected,
        'free_memory': free_mem,
        'total_memory': total_mem,
        'uptime': time.ticks_ms() // 1000,  # seconds
    }

def config_page(error='', success=''):
    """Main configuration page using shared HTML template"""
    config = get_current_config()
    status = get_system_status()
    
    # Load template file
    try:
        with open('config_portal_template.html', 'r') as f:
            template = f.read()
    except Exception as e:
        return f"<html><body><h1>Error loading template</h1><p>{e}</p></body></html>"
    
    # Format uptime
    uptime_sec = status['uptime']
    uptime_str = f"{uptime_sec // 3600}h {(uptime_sec % 3600) // 60}m"
    
    # Format memory
    mem_pct = int((status['free_memory'] / status['total_memory']) * 100)
    
    # Prepare template replacements
    replacements = {
        # Status values
        '{{STATUS_ONLINE_CLASS}}': 'online' if status['wifi_connected'] else '',
        '{{WIFI_STATUS}}': 'Online' if status['wifi_connected'] else 'Offline',
        '{{VERSION}}': status['version'],
        '{{UPTIME}}': uptime_str,
        '{{MEMORY_PCT}}': str(mem_pct),
        
        # WiFi settings
        '{{WIFI_SSID}}': str(config.get('wifi_ssid') or ''),
        
        # API Keys
        '{{METRA_TOKEN}}': str(config.get('metra_token') or ''),
        '{{CTA_TOKEN}}': str(config.get('cta_token') or ''),
        
        # Transit line info
        '{{LINE_ID}}': str(config.get('line_id') or ''),
        '{{LINE_NAME}}': str(config.get('line_name') or ''),
        '{{STATION_ID}}': str(config.get('station_id') or ''),
        '{{STATION_NAME}}': str(config.get('station_name') or ''),
        '{{SECONDARY_LINE_ID}}': str(config.get('secondary_line_id') or ''),
        '{{SECONDARY_LINE_NAME}}': str(config.get('secondary_line_name') or ''),
        '{{SECONDARY_CHECKED}}': 'checked' if config.get('secondary_line_id') else '',
        '{{SECONDARY_DISPLAY}}': '' if config.get('secondary_line_id') else 'display: none',
        
        # Rotation mode (v1.4.0)
        '{{ROTATION_MODE_DIRECTION}}': 'selected' if config.get('rotation_mode', 'direction') == 'direction' else '',
        '{{ROTATION_MODE_STATION}}': 'selected' if config.get('rotation_mode', 'direction') == 'station' else '',
        '{{DIRECTION_MODE_DISPLAY}}': 'display: none' if config.get('rotation_mode', 'direction') == 'station' else '',
        '{{STATION_MODE_DISPLAY}}': 'display: none' if config.get('rotation_mode', 'direction') == 'direction' else '',
        
        # Display settings
        '{{BRIGHTNESS}}': str(config.get('brightness', 0.7)),
        '{{BRIGHTNESS_PCT}}': str(int(config.get('brightness', 0.7) * 100)),
        '{{ROTATION_TIME}}': str(config.get('rotation_time', 5)),
        '{{UPDATE_INTERVAL}}': str(config.get('update_interval', 60)),
        '{{NUM_TRAINS}}': str(config.get('num_trains', 4)),
        
        # Features
        '{{SERVICE_ALERTS_CHECKED}}': 'checked' if config.get('enable_service_alerts', True) else '',
        '{{ALERT_ICONS_CHECKED}}': 'checked' if config.get('enable_alert_icons', True) else '',
        '{{ALERTS_UPDATE_INTERVAL}}': str(config.get('alerts_update_interval', 180)),
        '{{AUTO_UPDATE_CHECKED}}': 'checked' if config.get('enable_auto_update', True) else '',
        '{{UPDATE_DAILY_SELECTED}}': 'selected' if config.get('check_update_interval', 604800) == 86400 else '',
        '{{UPDATE_WEEKLY_SELECTED}}': 'selected' if config.get('check_update_interval', 604800) == 604800 else '',
        '{{UPDATE_MONTHLY_SELECTED}}': 'selected' if config.get('check_update_interval', 604800) == 2592000 else '',
        
        # Weather settings
        '{{WEATHER_CHECKED}}': 'checked' if config.get('enable_weather', False) else '',
        '{{WEATHER_STATUS}}': 'Enabled' if config.get('enable_weather', False) else 'Disabled',
        '{{WEATHER_GOV_SELECTED}}': 'selected' if config.get('weather_api_service', 'weathergov') == 'weathergov' else '',
        '{{WEATHER_OWM_SELECTED}}': 'selected' if config.get('weather_api_service', 'weathergov') == 'openweathermap' else '',
        '{{WEATHER_ZIP}}': str(config.get('weather_zip_code') or ''),
        '{{WEATHER_API_KEY}}': str(config.get('weather_api_key') or ''),
        '{{WEATHER_ICON_SELECTED}}': 'selected' if config.get('weather_display_mode', 'icon_only') == 'icon_only' else '',
        '{{WEATHER_TEMP_SELECTED}}': 'selected' if config.get('weather_display_mode', 'icon_only') == 'icon_and_temp' else '',
        '{{WEATHER_15MIN_SELECTED}}': 'selected' if config.get('weather_update_interval', 1800) == 900 else '',
        '{{WEATHER_30MIN_SELECTED}}': 'selected' if config.get('weather_update_interval', 1800) == 1800 else '',
        '{{WEATHER_60MIN_SELECTED}}': 'selected' if config.get('weather_update_interval', 1800) == 3600 else '',
        
        # System settings
        '{{WATCHDOG_CHECKED}}': 'checked' if config.get('enable_watchdog', True) else '',
        '{{WATCHDOG_5S_SELECTED}}': 'selected' if config.get('watchdog_timeout', 8000) == 5000 else '',
        '{{WATCHDOG_8S_SELECTED}}': 'selected' if config.get('watchdog_timeout', 8000) == 8000 else '',
        '{{WATCHDOG_10S_SELECTED}}': 'selected' if config.get('watchdog_timeout', 8000) == 10000 else '',
        
        '{{SLEEP_CHECKED}}': 'checked' if config.get('enable_sleep_mode', False) else '',
        '{{SLEEP_START_20_SELECTED}}': 'selected' if config.get('sleep_start_hour', 23) == 20 else '',
        '{{SLEEP_START_21_SELECTED}}': 'selected' if config.get('sleep_start_hour', 23) == 21 else '',
        '{{SLEEP_START_22_SELECTED}}': 'selected' if config.get('sleep_start_hour', 23) == 22 else '',
        '{{SLEEP_START_23_SELECTED}}': 'selected' if config.get('sleep_start_hour', 23) == 23 else '',
        '{{SLEEP_START_0_SELECTED}}': 'selected' if config.get('sleep_start_hour', 23) == 0 else '',
        '{{SLEEP_END_5_SELECTED}}': 'selected' if config.get('sleep_end_hour', 5) == 5 else '',
        '{{SLEEP_END_6_SELECTED}}': 'selected' if config.get('sleep_end_hour', 5) == 6 else '',
        '{{SLEEP_END_7_SELECTED}}': 'selected' if config.get('sleep_end_hour', 5) == 7 else '',
        '{{SLEEP_END_8_SELECTED}}': 'selected' if config.get('sleep_end_hour', 5) == 8 else '',
        '{{SLEEP_BRIGHTNESS}}': str(config.get('sleep_brightness', 0.1)),
        '{{SLEEP_BRIGHTNESS_PCT}}': str(int(config.get('sleep_brightness', 0.1) * 100)),
        
        '{{ADAPTIVE_CHECKED}}': 'checked' if config.get('enable_adaptive_brightness', False) else '',
    }
    
    # Replace all placeholders
    html = template
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    
    return html

def parse_form_data(data):
    """Parse URL-encoded form data"""
    params = {}
    pairs = data.split('&')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            # URL decode - handle + as space first
            value = value.replace('+', ' ')

            # Decode all percent-encoded characters
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
    """Save configuration to config.py"""
    # Handle checkboxes (checkboxes only send data if checked)
    enable_secondary = 'enable_secondary' in params or 'enable-secondary' in params
    enable_service_alerts = 'enable_service_alerts' in params or 'enable-service-alerts' in params
    enable_alert_icons = 'enable_alert_icons' in params or 'enable-alert-icons' in params
    enable_auto_update = 'enable_auto_update' in params or 'enable-auto-update' in params
    enable_watchdog = 'enable_watchdog' in params or 'enable-watchdog' in params
    enable_status_led = 'enable_status_led' in params or 'enable-status-led' in params
    enable_weather = 'enable_weather' in params or 'enable-weather' in params
    enable_sleep_mode = 'enable_sleep_mode' in params or 'enable-sleep' in params
    enable_adaptive_brightness = 'enable_adaptive_brightness' in params or 'enable-adaptive' in params

    config_content = f"""# Chicago Transit Board Configuration
# Generated by configuration portal

# WiFi Settings
WIFI_SSID = "{params.get('wifi_ssid', '')}"
WIFI_PASSWORD = "{params.get('wifi_password', '')}"

# API Keys
METRA_API_TOKEN = "{params.get('metra_token', '')}"
CTA_API_KEY = "{params.get('cta_token', '')}"

# Station Configuration (Primary Line)
STATION_STOP_ID = "{params.get('station_name', params.get('primary_station_name', ''))}"  # Display name
PRIMARY_STATION_ID = "{params.get('station_id', params.get('primary_station_id', ''))}"  # API ID

# Line Configuration
LINE_1 = "{params.get('line_id', params.get('line_name', ''))}"  # Primary line
"""

    if enable_secondary and params.get('secondary_line_id'):
        config_content += f"""
# Secondary Line (Dual Line Mode)
LINE_2 = "{params.get('secondary_line_id', '')}"
SECONDARY_STATION_ID = "{params.get('secondary_station_id', '')}"
SECONDARY_STATION_NAME = "{params.get('secondary_station_name', '')}"
"""
    else:
        config_content += """
# Secondary Line (Dual Line Mode) - Disabled
LINE_2 = None
SECONDARY_STATION_ID = None
SECONDARY_STATION_NAME = None
"""

    config_content += f"""
# Display Settings
BRIGHTNESS = {params.get('brightness', '0.5')}
UPDATE_INTERVAL = {params.get('update_interval', '60')}
DISPLAY_ROTATION_TIME = {params.get('rotation_time', '5')}
NUM_TRAINS_TO_SHOW = {params.get('num_trains', '4')}

# Rotation Mode
ROTATION_MODE = "{params.get('rotation_mode', 'direction')}"  # "direction" or "station"
"""

    # Build ROTATION_STATIONS array if in station mode
    if params.get('rotation_mode') == 'station':
        stations = []
        for i in range(1, 4):  # Support up to 3 stations
            station_id = params.get(f'station{i}_station_id')
            line_id = params.get(f'station{i}_line_id')
            if station_id and line_id:
                # Detect transit type based on line code
                transit_type = detect_transit_type(line_id)
                # Get station name from the station_id (format is usually descriptive)
                station_name = station_id  # Use ID as name for now
                stations.append(f'    {{"name": "{station_name}", "id": "{station_id}", "line": "{line_id}", "transit_type": "{transit_type}"}}')
        
        if stations:
            config_content += "ROTATION_STATIONS = [\n"
            config_content += ',\n'.join(stations)
            config_content += "\n]\n"
        else:
            config_content += "ROTATION_STATIONS = []\n"
    else:
        config_content += "ROTATION_STATIONS = []\n"
    
    config_content += """STATION_ROTATION_TIME = 10
"""

    config_content += f"""
# Service Alerts
ENABLE_SERVICE_ALERTS = {enable_service_alerts}
ENABLE_ALERT_ICONS = {enable_alert_icons}
ALERTS_UPDATE_INTERVAL = {params.get('alerts_update_interval', '180')}

# Auto-Update
ENABLE_AUTO_UPDATE = {enable_auto_update}
CHECK_UPDATE_INTERVAL = {params.get('check_update_interval', '604800')}

# System Reliability
ENABLE_WATCHDOG = {enable_watchdog}
WATCHDOG_TIMEOUT = {params.get('watchdog_timeout', '8000')}

# Status LED
ENABLE_STATUS_LED = {enable_status_led}

# Weather
ENABLE_WEATHER = {enable_weather}
WEATHER_API_SERVICE = "{params.get('weather_api_service', 'weathergov')}"
WEATHER_API_KEY = "{params.get('weather_api_key', '')}"
WEATHER_ZIP_CODE = "{params.get('weather_zip_code', '')}"
WEATHER_UPDATE_INTERVAL = {params.get('weather_update_interval', '1800')}
WEATHER_DISPLAY_MODE = "{params.get('weather_display_mode', 'icon_only')}"

# Power Management
ENABLE_SLEEP_MODE = {enable_sleep_mode}
SLEEP_START_HOUR = {params.get('sleep_start_hour', params.get('sleep-start-hour', '23'))}
SLEEP_END_HOUR = {params.get('sleep_end_hour', params.get('sleep-end-hour', '5'))}
SLEEP_BRIGHTNESS = {params.get('sleep_brightness', params.get('sleep-brightness', '0.1'))}

ENABLE_ADAPTIVE_BRIGHTNESS = {enable_adaptive_brightness}
"""

    try:
        with open('config.py', 'w') as f:
            f.write(config_content)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def run_server(port=80):
    """Run the configuration web server"""
    # Set up mDNS
    setup_mdns("board")
    
    # Get IP address
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print(f"Configuration portal available at:")
        print(f"  http://board.local:{port}")
        print(f"  http://{ip}:{port}")
    else:
        print("Warning: Not connected to WiFi")
    
    # Create socket
    addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    
    print(f"Listening on port {port}...")
    
    while True:
        try:
            cl, addr = s.accept()
            print(f'Client connected from {addr}')
            request = cl.recv(2048).decode('utf-8')
            
            # Parse request
            lines = request.split('\r\n')
            if len(lines) > 0:
                method_line = lines[0]
                parts = method_line.split(' ')
                if len(parts) >= 2:
                    method = parts[0]
                    path = parts[1]
                    
                    if method == 'GET':
                        if path == '/' or path == '/config':
                            response = config_page()
                            cl.send('HTTP/1.1 200 OK\r\n')
                            cl.send('Content-Type: text/html; charset=utf-8\r\n')
                            cl.send('Connection: close\r\n\r\n')
                            cl.send(response)
                        
                        elif path == '/restart':
                            response = """<!DOCTYPE html>
<html><body style="font-family: sans-serif; text-align: center; padding: 50px;">
<h1>Restarting...</h1>
<p>The board will restart in a few seconds.</p>
<p>Refresh this page after 10 seconds.</p>
</body></html>"""
                            cl.send('HTTP/1.1 200 OK\r\n')
                            cl.send('Content-Type: text/html\r\n')
                            cl.send('Connection: close\r\n\r\n')
                            cl.send(response)
                            cl.close()
                            time.sleep(1)
                            machine.reset()
                    
                    elif method == 'POST' and path == '/save':
                        # Find the body
                        body_start = request.find('\r\n\r\n')
                        if body_start != -1:
                            body = request[body_start + 4:]
                            params = parse_form_data(body)
                            
                            # Also need to preserve WiFi settings
                            try:
                                import config
                                params['wifi_ssid'] = config.WIFI_SSID
                                params['wifi_password'] = config.WIFI_PASSWORD
                            except:
                                pass
                            
                            if save_config(params):
                                response = config_page(success='Configuration saved! Changes will take effect after restart.')
                            else:
                                response = config_page(error='Failed to save configuration.')
                            
                            cl.send('HTTP/1.1 200 OK\r\n')
                            cl.send('Content-Type: text/html; charset=utf-8\r\n')
                            cl.send('Connection: close\r\n\r\n')
                            cl.send(response)
            
            cl.close()
        
        except Exception as e:
            print(f"Error: {e}")
            try:
                cl.close()
            except:
                pass

if __name__ == '__main__':
    run_server()
