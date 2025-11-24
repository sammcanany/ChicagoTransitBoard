# Metra Transit Board
# For Pimoroni Interstate 75 W (RP2350) + 2x 64x32 HUB75 Matrices
# MicroPython code

import time
import network
import os
from machine import WDT
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_128X64

# ===== INITIALIZE DISPLAY FIRST (needed for LED) =====
# Interstate 75 W with 2x 64x32 panels = 128x64 display
i75 = Interstate75(display=DISPLAY_INTERSTATE75_128X64)
display = i75.display

# ===== STATUS LED =====
# Interstate 75 has an onboard RGB LED accessed via i75.set_led(r, g, b)
# Controlled by ENABLE_STATUS_LED config option

def _led_enabled():
    """Check if status LED is enabled in config"""
    try:
        return ENABLE_STATUS_LED
    except NameError:
        return True  # Default to enabled if config not loaded yet

def led_on(r=50, g=50, b=50):
    """Turn status LED on (white by default)"""
    if not _led_enabled():
        return
    try:
        i75.set_led(r, g, b)
    except:
        pass

def led_off():
    """Turn status LED off"""
    try:
        i75.set_led(0, 0, 0)
    except:
        pass

def led_connected():
    """Set LED to dim green to indicate WiFi connected and running"""
    led_on(r=0, g=20, b=0)

def led_set_status(status):
    """Set LED to indicate current status.
    
    Args:
        status: 'connected' (dim green), 'error' (dim red), 'off'
    """
    if status == 'connected':
        led_connected()
    elif status == 'error':
        led_on(r=20, g=0, b=0)  # Dim red - error state
    else:
        led_off()

def led_blink(times=1, on_ms=100, off_ms=100, r=50, g=50, b=50):
    """Blink the status LED a specified number of times"""
    for _ in range(times):
        led_on(r, g, b)
        time.sleep_ms(on_ms)
        led_off()
        time.sleep_ms(off_ms)

def led_pattern_wifi_connecting():
    """Blue blink pattern while connecting to WiFi"""
    led_blink(3, 100, 100, r=0, g=0, b=100)

def led_pattern_updating():
    """Yellow pulse pattern while updating"""
    led_blink(2, 500, 200, r=100, g=100, b=0)

def led_pattern_error():
    """Red rapid blink pattern for errors"""
    led_blink(5, 50, 50, r=100, g=0, b=0)

def led_pattern_success():
    """Green long blink for success, then stay dim green"""
    led_on(r=0, g=100, b=0)
    time.sleep_ms(1000)
    led_set_status('connected')  # Stay dim green

# Check if we need to run setup portal
def needs_setup():
    """Check if config.py exists"""
    try:
        os.stat('config.py')
        return False
    except:
        return True

# ===== IMPORT CONFIGURATION =====
try:
    from config import (
        WIFI_SSID, WIFI_PASSWORD, METRA_API_TOKEN,
        STATION_STOP_ID, LINE_1, LINE_2,
        DISPLAY_ROTATION_TIME, UPDATE_INTERVAL, BRIGHTNESS,
        ENABLE_AUTO_UPDATE, CHECK_UPDATE_INTERVAL,
        ENABLE_SERVICE_ALERTS, ENABLE_ALERT_ICONS
    )

    # Alerts update interval with default
    try:
        from config import ALERTS_UPDATE_INTERVAL
    except ImportError:
        ALERTS_UPDATE_INTERVAL = 180  # Default: 3 minutes

    # Optional fields with defaults
    try:
        from config import CTA_API_KEY
    except ImportError:
        CTA_API_KEY = ""
    
    try:
        from config import PRIMARY_STATION_ID
    except ImportError:
        PRIMARY_STATION_ID = STATION_STOP_ID
    
    try:
        from config import SECONDARY_STATION_ID, SECONDARY_STATION_NAME
    except ImportError:
        SECONDARY_STATION_ID = None
        SECONDARY_STATION_NAME = None
    
    try:
        from config import NUM_TRAINS_TO_SHOW
    except ImportError:
        NUM_TRAINS_TO_SHOW = 4
    
    # Watchdog timer settings
    try:
        from config import ENABLE_WATCHDOG, WATCHDOG_TIMEOUT
    except ImportError:
        ENABLE_WATCHDOG = True
        WATCHDOG_TIMEOUT = 8000  # 8 seconds default
    
    # Weather settings
    try:
        from config import (
            ENABLE_WEATHER, WEATHER_API_SERVICE, WEATHER_API_KEY,
            WEATHER_ZIP_CODE, WEATHER_UPDATE_INTERVAL, WEATHER_DISPLAY_MODE
        )
    except ImportError:
        ENABLE_WEATHER = False
        WEATHER_API_SERVICE = "weathergov"
        WEATHER_API_KEY = ""
        WEATHER_ZIP_CODE = ""
        WEATHER_UPDATE_INTERVAL = 1800  # 30 minutes
        WEATHER_DISPLAY_MODE = "icon_only"
    
    # Sleep mode settings
    try:
        from config import (
            ENABLE_SLEEP_MODE, SLEEP_START_HOUR, SLEEP_END_HOUR, SLEEP_BRIGHTNESS
        )
    except ImportError:
        ENABLE_SLEEP_MODE = False
        SLEEP_START_HOUR = 23  # 11 PM
        SLEEP_END_HOUR = 5     # 5 AM
        SLEEP_BRIGHTNESS = 0.1  # 10%
    
    # Adaptive brightness settings
    try:
        from config import ENABLE_ADAPTIVE_BRIGHTNESS
    except ImportError:
        ENABLE_ADAPTIVE_BRIGHTNESS = False
    
    # Status LED settings
    try:
        from config import ENABLE_STATUS_LED
    except ImportError:
        ENABLE_STATUS_LED = True  # Enabled by default
    
    # Station rotation settings (v1.4.0)
    try:
        from config import ROTATION_MODE, ROTATION_STATIONS, STATION_ROTATION_TIME
    except ImportError:
        ROTATION_MODE = "direction"  # Default to direction mode
        ROTATION_STATIONS = []
        STATION_ROTATION_TIME = 10
        
except ImportError:
    print("\n" + "="*50)
    print("WARNING: config.py not found!")
    print("="*50)
    print("\nStarting setup portal...")
    print("This will create a WiFi network you can connect to")
    print("for configuring the board.\n")
    
    # Run setup portal
    import setup_portal
    setup_portal.run_server()
    # This won't return - server runs until config is saved and board restarts

import urequests

# Import auto-update module
if ENABLE_AUTO_UPDATE:
    try:
        import auto_update
    except ImportError:
        print("Warning: auto_update.py not found - auto-update disabled")
        ENABLE_AUTO_UPDATE = False

# ===== API CONFIGURATION =====
TRIP_UPDATES_URL = "https://gtfspublic.metrarr.com/gtfs/public/tripupdates"
ALERTS_URL = "https://gtfspublic.metrarr.com/gtfs/public/alerts"

# ===== COLORS =====
# Will be created after display initialization
COLOR_METRA_GREEN = None
COLOR_WHITE = None
COLOR_YELLOW = None
COLOR_RED = None
COLOR_BLACK = None

# ===== DISPLAY ALREADY INITIALIZED ABOVE (for LED access) =====
# Global mDNS server instance
mdns_server = None
mdns_client = None

# Set brightness from config (using display.set_backlight for newer firmware)
try:
    i75.set_brightness(BRIGHTNESS)
except AttributeError:
    # Newer firmware uses set_backlight on display
    pass  # Brightness will be handled via display updates

# Create colors
COLOR_METRA_GREEN = display.create_pen(0, 155, 58)
COLOR_WHITE = display.create_pen(255, 255, 255)
COLOR_YELLOW = display.create_pen(255, 255, 0)
COLOR_RED = display.create_pen(255, 0, 0)
COLOR_BLACK = display.create_pen(0, 0, 0)

# Metra Line Colors
LINE_COLORS = {
    # Metra Lines
    "UP-N": display.create_pen(255, 200, 0),    # Yellow/Gold
    "UP-NW": display.create_pen(0, 155, 58),    # Green
    "UP-W": display.create_pen(255, 105, 180),  # Pink
    "MD-N": display.create_pen(255, 140, 0),    # Orange
    "MD-W": display.create_pen(255, 140, 0),    # Orange
    "NCS": display.create_pen(0, 155, 58),      # Green
    "BNSF": display.create_pen(0, 155, 58),     # Green
    "HC": display.create_pen(255, 140, 0),      # Orange
    "ME": display.create_pen(0, 100, 255),      # Electric Blue
    "RI": display.create_pen(0, 0, 200),        # Blue
    "SWS": display.create_pen(255, 140, 0),     # Orange
    # CTA Lines (if using CTA)
    "Red": display.create_pen(200, 0, 0),       # Red
    "Blue": display.create_pen(0, 100, 255),    # Blue
    "Brn": display.create_pen(139, 69, 19),     # Brown
    "G": display.create_pen(0, 155, 58),        # Green
    "Org": display.create_pen(255, 140, 0),     # Orange
    "P": display.create_pen(128, 0, 128),       # Purple
    "Pink": display.create_pen(255, 105, 180),  # Pink
    "Y": display.create_pen(255, 255, 0),       # Yellow
}

def get_line_color(line_code):
    """Get color for a specific line, default to Metra green"""
    return LINE_COLORS.get(line_code, COLOR_METRA_GREEN)

# ===== WIFI CONNECTION =====
def connect_wifi(silent=False):
    """Connect to WiFi and show status on display. Returns True if successful.
    
    Args:
        silent: If True, don't update display (for background reconnection)
    """
    global wifi_connected

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Set hostname BEFORE connecting (required for mDNS)
    try:
        network.hostname("board")
        if not silent:
            print("Hostname set to 'board' for mDNS")
    except Exception as e:
        if not silent:
            print(f"Could not set hostname: {e}")

    # Check if already connected
    if wlan.isconnected():
        wifi_connected = True
        if not silent:
            print(f"Already connected! IP: {wlan.ifconfig()[0]}")

        # Sync time with NTP server
        try:
            import ntptime
            print("Syncing time with NTP...")
            ntptime.settime()
            print("Time synced successfully")
        except Exception as e:
            print(f"NTP sync failed: {e}")

        # Start mDNS responder using micropython-mdns library
        global mdns_server, mdns_client
        try:
            from mdns_client import Client
            from mdns_client.responder import Responder

            ip = wlan.ifconfig()[0]
            mdns_client = Client(ip)
            mdns_server = Responder(
                mdns_client,
                own_ip=lambda: ip,
                host=lambda: "board"
            )
            mdns_server.advertise("_http", "_tcp", port=80)
            print(f"mDNS ready: http://board.local or http://{ip}")

        except Exception as e:
            print(f"mDNS setup failed: {e}")
            mdns_server = None
            mdns_client = None

        return True
    
    wlan.config(pm=0xa11140)  # Turn WiFi power saving off for some slow APs
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    # Show connecting message and LED pattern
    if not silent:
        display.set_pen(COLOR_BLACK)
        display.clear()
        display.set_pen(COLOR_WHITE)
        display.text("Connecting WiFi...", 5, 5, scale=1)
        i75.update()
    
    max_wait = 20
    while max_wait > 0:
        led_pattern_wifi_connecting()  # Blink LED while connecting
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        time.sleep(0.5)  # Reduced sleep to allow more LED blinks
    
    if wlan.status() != 3:
        wifi_connected = False
        led_pattern_error()  # Error LED pattern
        print("WiFi connection failed")
        return False
    else:
        wifi_connected = True
        ip = wlan.ifconfig()[0]
        led_pattern_success()  # Success LED pattern
        print(f'Connected! IP: {ip}')

        # Sync time with NTP server
        try:
            import ntptime
            print("Syncing time with NTP...")
            ntptime.settime()
            print("Time synced successfully")
        except Exception as e:
            print(f"NTP sync failed: {e}")

        # Start mDNS responder using micropython-mdns library
        global mdns_server, mdns_client
        try:
            from mdns_client import Client
            from mdns_client.responder import Responder

            ip = wlan.ifconfig()[0]
            mdns_client = Client(ip)
            mdns_server = Responder(
                mdns_client,
                own_ip=lambda: ip,
                host=lambda: "board"
            )
            mdns_server.advertise("_http", "_tcp", port=80)
            print(f"mDNS ready: http://board.local or http://{ip}")

        except Exception as e:
            print(f"mDNS setup failed: {e}")
            mdns_server = None
            mdns_client = None

        if not silent:
            display.set_pen(COLOR_BLACK)
            display.clear()
            display.set_pen(COLOR_METRA_GREEN)
            display.text("WiFi OK!", 5, 5, scale=1)
            display.text(ip, 5, 15, scale=1)
            i75.update()
            time.sleep(2)
        led_connected()  # Keep LED green while running
        return True


def check_wifi_and_reconnect():
    """Check WiFi connection and attempt to reconnect if disconnected.
    Returns True if connected, False if reconnection failed."""
    global wifi_connected
    
    wlan = network.WLAN(network.STA_IF)
    
    if wlan.isconnected():
        return True
    
    # WiFi disconnected - attempt to reconnect
    print("WiFi disconnected! Attempting to reconnect...")
    led_pattern_error()
    wifi_connected = False
    
    # Try to reconnect silently (don't update display during normal operation)
    for attempt in range(3):
        print(f"Reconnection attempt {attempt + 1}/3...")
        if connect_wifi(silent=True):
            print("WiFi reconnected successfully!")
            led_connected()  # Keep LED green while running
            return True
        time.sleep(2)
    
    print("Failed to reconnect to WiFi after 3 attempts")
    return False

# ===== TRAIN DATA =====
class TrainArrival:
    def __init__(self, route, direction, minutes, line_num=1):
        self.route = route
        self.direction = direction  # "Inbound" or "Outbound"
        self.minutes = minutes
        self.line_num = line_num  # 1 or 2 (which line this train belongs to)

# Separate lists for each line and direction
line1_inbound = []
line1_outbound = []
line2_inbound = []
line2_outbound = []

# Service alerts
active_alerts = []
line1_has_alerts = False
line2_has_alerts = False

# Weather data
weather_data = {
    "temp": None,
    "condition": None,  # "clear", "cloudy", "rain", "snow"
    "icon": None,
    "last_update": 0
}

# Error states
wifi_connected = False
api_error = False
last_successful_update = 0
cached_trains_available = False

# Track which view we're showing
current_direction = "Inbound"  # "Inbound", "Outbound", or "Alerts"
dual_line_mode = LINE_2 is not None

# Station rotation mode variables (v1.4.0)
current_station_index = 0  # Which station we're currently displaying in rotation mode
station_rotation_enabled = ROTATION_MODE == "station" and len(ROTATION_STATIONS) > 0

def parse_gtfs_protobuf(data):
    """Simple GTFS-RT protobuf parser for MicroPython

    Protobuf wire types:
    0 = varint, 1 = 64-bit, 2 = length-delimited, 5 = 32-bit

    GTFS-RT FeedMessage structure:
    - field 1: header (FeedHeader)
    - field 2: entity[] (FeedEntity)

    FeedEntity:
    - field 1: id (string)
    - field 3: trip_update (TripUpdate)

    TripUpdate:
    - field 1: trip (TripDescriptor)
    - field 2: stop_time_update[] (StopTimeUpdate)

    TripDescriptor:
    - field 1: trip_id (string)
    - field 5: route_id (string)

    StopTimeUpdate:
    - field 1: stop_sequence (uint32)
    - field 2: arrival (StopTimeEvent)
    - field 4: stop_id (string)

    StopTimeEvent:
    - field 2: time (int64)
    """
    result = {"entity": []}
    pos = 0

    def read_varint(data, pos):
        """Read a varint from data at position pos"""
        result = 0
        shift = 0
        while pos < len(data):
            b = data[pos]
            pos += 1
            result |= (b & 0x7F) << shift
            if not (b & 0x80):
                break
            shift += 7
        return result, pos

    def read_string(data, pos):
        """Read a length-delimited string"""
        length, pos = read_varint(data, pos)
        s = data[pos:pos+length]
        try:
            return s.decode('utf-8'), pos + length
        except:
            return "", pos + length

    def read_bytes(data, pos):
        """Read length-delimited bytes"""
        length, pos = read_varint(data, pos)
        return data[pos:pos+length], pos + length

    def parse_stop_time_event(data):
        """Parse StopTimeEvent to get time"""
        pos = 0
        time_val = 0
        while pos < len(data):
            if pos >= len(data):
                break
            tag, pos = read_varint(data, pos)
            field_num = tag >> 3
            wire_type = tag & 0x7

            if field_num == 2 and wire_type == 0:  # time (varint)
                time_val, pos = read_varint(data, pos)
            elif wire_type == 0:
                _, pos = read_varint(data, pos)
            elif wire_type == 2:
                _, pos = read_bytes(data, pos)
            elif wire_type == 1:
                pos += 8
            elif wire_type == 5:
                pos += 4
            else:
                break
        return time_val

    def parse_stop_time_update(data):
        """Parse StopTimeUpdate message
        GTFS-RT spec:
        - field 1: stop_sequence (uint32)
        - field 2: arrival (StopTimeEvent)
        - field 3: departure (StopTimeEvent)
        - field 4: stop_id (string)
        """
        pos = 0
        stop = {"stop_sequence": 0, "stop_id": "", "arrival": {"time": 0}}
        while pos < len(data):
            if pos >= len(data):
                break
            tag, pos = read_varint(data, pos)
            field_num = tag >> 3
            wire_type = tag & 0x7

            if field_num == 1 and wire_type == 0:  # stop_sequence
                stop["stop_sequence"], pos = read_varint(data, pos)
            elif field_num == 2 and wire_type == 2:  # arrival
                arrival_data, pos = read_bytes(data, pos)
                stop["arrival"]["time"] = parse_stop_time_event(arrival_data)
            elif field_num == 3 and wire_type == 2:  # departure
                dep_data, pos = read_bytes(data, pos)
                if stop["arrival"]["time"] == 0:
                    stop["arrival"]["time"] = parse_stop_time_event(dep_data)
            elif field_num == 4 and wire_type == 2:  # stop_id
                stop["stop_id"], pos = read_string(data, pos)
            elif wire_type == 0:
                _, pos = read_varint(data, pos)
            elif wire_type == 2:
                _, pos = read_bytes(data, pos)
            elif wire_type == 1:
                pos += 8
            elif wire_type == 5:
                pos += 4
            else:
                break
        return stop

    def parse_trip_descriptor(data):
        """Parse TripDescriptor message"""
        pos = 0
        trip = {"trip_id": "", "route_id": ""}
        while pos < len(data):
            if pos >= len(data):
                break
            tag, pos = read_varint(data, pos)
            field_num = tag >> 3
            wire_type = tag & 0x7

            if field_num == 1 and wire_type == 2:  # trip_id
                trip["trip_id"], pos = read_string(data, pos)
            elif field_num == 5 and wire_type == 2:  # route_id
                trip["route_id"], pos = read_string(data, pos)
            elif wire_type == 0:
                _, pos = read_varint(data, pos)
            elif wire_type == 2:
                _, pos = read_bytes(data, pos)
            elif wire_type == 1:
                pos += 8
            elif wire_type == 5:
                pos += 4
            else:
                break
        return trip

    def parse_trip_update(data):
        """Parse TripUpdate message"""
        pos = 0
        update = {"trip": {}, "stop_time_update": []}
        while pos < len(data):
            if pos >= len(data):
                break
            tag, pos = read_varint(data, pos)
            field_num = tag >> 3
            wire_type = tag & 0x7

            if field_num == 1 and wire_type == 2:  # trip
                trip_data, pos = read_bytes(data, pos)
                update["trip"] = parse_trip_descriptor(trip_data)
            elif field_num == 2 and wire_type == 2:  # stop_time_update
                stu_data, pos = read_bytes(data, pos)
                update["stop_time_update"].append(parse_stop_time_update(stu_data))
            elif wire_type == 0:
                _, pos = read_varint(data, pos)
            elif wire_type == 2:
                _, pos = read_bytes(data, pos)
            elif wire_type == 1:
                pos += 8
            elif wire_type == 5:
                pos += 4
            else:
                break
        return update

    def parse_entity(data):
        """Parse FeedEntity message"""
        pos = 0
        entity = {"id": "", "trip_update": None}
        while pos < len(data):
            if pos >= len(data):
                break
            tag, pos = read_varint(data, pos)
            field_num = tag >> 3
            wire_type = tag & 0x7

            if field_num == 1 and wire_type == 2:  # id
                entity["id"], pos = read_string(data, pos)
            elif field_num == 3 and wire_type == 2:  # trip_update
                tu_data, pos = read_bytes(data, pos)
                entity["trip_update"] = parse_trip_update(tu_data)
            elif wire_type == 0:
                _, pos = read_varint(data, pos)
            elif wire_type == 2:
                _, pos = read_bytes(data, pos)
            elif wire_type == 1:
                pos += 8
            elif wire_type == 5:
                pos += 4
            else:
                break
        return entity

    # Parse top-level FeedMessage
    try:
        while pos < len(data):
            tag, pos = read_varint(data, pos)
            field_num = tag >> 3
            wire_type = tag & 0x7

            if field_num == 2 and wire_type == 2:  # entity
                entity_data, pos = read_bytes(data, pos)
                entity = parse_entity(entity_data)
                if entity.get("trip_update"):
                    result["entity"].append(entity)
            elif wire_type == 0:
                _, pos = read_varint(data, pos)
            elif wire_type == 2:
                _, pos = read_bytes(data, pos)
            elif wire_type == 1:
                pos += 8
            elif wire_type == 5:
                pos += 4
            else:
                pos += 1  # Skip unknown

        print(f"Parsed {len(result['entity'])} entities from protobuf")
        return result
    except Exception as e:
        print(f"Protobuf parse error: {e}")
        return None

def parse_gtfs_alerts_protobuf(data):
    """Parse GTFS-RT alerts protobuf

    Alert structure:
    - field 1: id (string)
    - field 2: alert (Alert)

    Alert:
    - field 1: active_period[] (TimeRange)
    - field 5: informed_entity[] (EntitySelector)
    - field 6: cause (Cause enum)
    - field 7: effect (Effect enum)
    - field 8: url (TranslatedString)
    - field 10: header_text (TranslatedString)
    - field 11: description_text (TranslatedString)

    EntitySelector:
    - field 1: agency_id (string)
    - field 4: route_id (string)

    TranslatedString:
    - field 1: translation[] (Translation)

    Translation:
    - field 1: text (string)
    - field 2: language (string)
    """
    result = {"entity": []}
    pos = 0

    def read_varint(data, pos):
        result = 0
        shift = 0
        while pos < len(data):
            b = data[pos]
            pos += 1
            result |= (b & 0x7F) << shift
            if not (b & 0x80):
                break
            shift += 7
        return result, pos

    def read_string(data, pos):
        length, pos = read_varint(data, pos)
        s = data[pos:pos+length]
        try:
            return s.decode('utf-8'), pos + length
        except:
            return "", pos + length

    def read_bytes(data, pos):
        length, pos = read_varint(data, pos)
        return data[pos:pos+length], pos + length

    def parse_translation(data):
        """Parse Translation message"""
        pos = 0
        text = ""
        while pos < len(data):
            if pos >= len(data):
                break
            tag, pos = read_varint(data, pos)
            field_num = tag >> 3
            wire_type = tag & 0x7

            if field_num == 1 and wire_type == 2:  # text
                text, pos = read_string(data, pos)
            elif wire_type == 0:
                _, pos = read_varint(data, pos)
            elif wire_type == 2:
                _, pos = read_bytes(data, pos)
            else:
                break
        return text

    def parse_translated_string(data):
        """Parse TranslatedString message"""
        pos = 0
        translations = []
        while pos < len(data):
            if pos >= len(data):
                break
            tag, pos = read_varint(data, pos)
            field_num = tag >> 3
            wire_type = tag & 0x7

            if field_num == 1 and wire_type == 2:  # translation
                trans_data, pos = read_bytes(data, pos)
                text = parse_translation(trans_data)
                if text:
                    translations.append(text)
            elif wire_type == 0:
                _, pos = read_varint(data, pos)
            elif wire_type == 2:
                _, pos = read_bytes(data, pos)
            else:
                break
        return translations[0] if translations else ""

    def parse_entity_selector(data):
        """Parse EntitySelector message"""
        pos = 0
        route_id = ""
        while pos < len(data):
            if pos >= len(data):
                break
            tag, pos = read_varint(data, pos)
            field_num = tag >> 3
            wire_type = tag & 0x7

            if field_num == 4 and wire_type == 2:  # route_id
                route_id, pos = read_string(data, pos)
            elif wire_type == 0:
                _, pos = read_varint(data, pos)
            elif wire_type == 2:
                _, pos = read_bytes(data, pos)
            else:
                break
        return route_id

    def parse_alert(data):
        """Parse Alert message"""
        pos = 0
        alert = {"header_text": "", "description_text": "", "informed_entity": []}
        while pos < len(data):
            if pos >= len(data):
                break
            tag, pos = read_varint(data, pos)
            field_num = tag >> 3
            wire_type = tag & 0x7

            if field_num == 5 and wire_type == 2:  # informed_entity
                entity_data, pos = read_bytes(data, pos)
                route_id = parse_entity_selector(entity_data)
                if route_id:
                    alert["informed_entity"].append(route_id)
            elif field_num == 10 and wire_type == 2:  # header_text
                header_data, pos = read_bytes(data, pos)
                alert["header_text"] = parse_translated_string(header_data)
            elif field_num == 11 and wire_type == 2:  # description_text
                desc_data, pos = read_bytes(data, pos)
                alert["description_text"] = parse_translated_string(desc_data)
            elif wire_type == 0:
                _, pos = read_varint(data, pos)
            elif wire_type == 2:
                _, pos = read_bytes(data, pos)
            else:
                break
        return alert

    def parse_entity(data):
        """Parse FeedEntity message"""
        pos = 0
        entity = {"id": "", "alert": None}
        while pos < len(data):
            if pos >= len(data):
                break
            tag, pos = read_varint(data, pos)
            field_num = tag >> 3
            wire_type = tag & 0x7

            if field_num == 1 and wire_type == 2:  # id
                entity["id"], pos = read_string(data, pos)
            elif field_num == 2 and wire_type == 2:  # alert
                alert_data, pos = read_bytes(data, pos)
                entity["alert"] = parse_alert(alert_data)
            elif wire_type == 0:
                _, pos = read_varint(data, pos)
            elif wire_type == 2:
                _, pos = read_bytes(data, pos)
            else:
                break
        return entity

    # Parse top-level FeedMessage
    try:
        while pos < len(data):
            tag, pos = read_varint(data, pos)
            field_num = tag >> 3
            wire_type = tag & 0x7

            if field_num == 2 and wire_type == 2:  # entity
                entity_data, pos = read_bytes(data, pos)
                entity = parse_entity(entity_data)
                if entity.get("alert"):
                    result["entity"].append(entity)
            elif wire_type == 0:
                _, pos = read_varint(data, pos)
            elif wire_type == 2:
                _, pos = read_bytes(data, pos)
            elif wire_type == 1:
                pos += 8
            elif wire_type == 5:
                pos += 4
            else:
                pos += 1

        print(f"Parsed {len(result['entity'])} alerts from protobuf")
        return result
    except Exception as e:
        print(f"Alerts protobuf parse error: {e}")
        return None

def fetch_metra_trains(station_id, line_code):
    """Fetch Metra train arrivals using GTFS-RT JSON API"""
    trains_inbound = []
    trains_outbound = []

    try:
        # Check if API token is set
        if not METRA_API_TOKEN or METRA_API_TOKEN == "your_token_here":
            print("Metra API token not configured - skipping fetch")
            return trains_inbound, trains_outbound

        import time as time_module
        from time import localtime
        lt = localtime()
        print(f"Fetching Metra trains for {station_id} on {line_code}")
        print(f"Current time: {lt[3]:02d}:{lt[4]:02d}:{lt[5]:02d}")

        # Metra GTFS-RT API - pass token as query parameter
        url = f"{TRIP_UPDATES_URL}?api_token={METRA_API_TOKEN}"
        print(f"Requesting Metra API...")

        response = urequests.get(url, timeout=15)
        print(f"Metra API status: {response.status_code}")
        if response.status_code != 200:
            print(f"Metra API error: {response.status_code}")
            response.close()
            return trains_inbound, trains_outbound

        # Read raw content - Metra returns protobuf
        raw_content = response.content
        response.close()
        print(f"Response size: {len(raw_content)} bytes")

        # Parse GTFS-RT protobuf manually (simplified parser)
        data = parse_gtfs_protobuf(raw_content)
        if not data or "entity" not in data:
            print("Failed to parse Metra protobuf response")
            return trains_inbound, trains_outbound

        # GTFS-RT timestamps are in UTC
        # After NTP sync, time.time() returns UTC
        current_time = time.time()

        upn_trips_checked = 0
        ravenswood_trains_before_filter = 0

        for entity in data["entity"]:
            # Skip entities without trip_update
            if "trip_update" not in entity:
                continue

            trip_update = entity["trip_update"]
            trip = trip_update.get("trip", {})

            # Filter by route (line code)
            if trip.get("route_id") != line_code:
                continue

            upn_trips_checked += 1
            # Look for our station in the stop_time_updates
            arrival_time = None
            stop_sequence = None

            for stop_update in trip_update.get("stop_time_update", []):
                if stop_update.get("stop_id") == station_id:
                    stop_sequence = stop_update.get("stop_sequence", 0)

                    # Get arrival or departure time (POSIX timestamp)
                    if "arrival" in stop_update:
                        arrival_time = stop_update["arrival"].get("time")
                    elif "departure" in stop_update:
                        arrival_time = stop_update["departure"].get("time")
                    break

            # Skip if this trip doesn't stop at our station
            if arrival_time is None:
                continue

            ravenswood_trains_before_filter += 1

            # Calculate minutes until arrival
            minutes = int((arrival_time - current_time) / 60)

            # Filter out old trains
            if minutes < -5:
                continue  # Train already passed

            if minutes < 0:
                minutes = 0  # Train arriving now

            # Filter trains too far in the future (limit to 2 hours)
            if minutes > 120:
                continue

            # Determine direction based on stop sequence
            # Lower sequence = Outbound (away from Chicago)
            # Higher sequence = Inbound (toward Chicago)
            direction = "Inbound" if stop_sequence > 15 else "Outbound"

            train = TrainArrival(line_code, direction, minutes, 1)

            if direction == "Inbound":
                trains_inbound.append(train)
            else:
                trains_outbound.append(train)

        # Sort by arrival time
        trains_inbound.sort(key=lambda t: t.minutes)
        trains_outbound.sort(key=lambda t: t.minutes)

        print(f"Found {len(trains_inbound)} inbound, {len(trains_outbound)} outbound trains")

    except Exception as e:
        import sys
        print(f"Error fetching Metra trains: {type(e).__name__}: {e}")
        sys.print_exception(e)

    return trains_inbound, trains_outbound

def fetch_cta_trains(station_id, line_code=None):
    """Fetch CTA train arrivals using Train Tracker API"""
    trains_inbound = []
    trains_outbound = []
    
    try:
        print(f"Fetching CTA trains for station {station_id}")
        
        # CTA Train Tracker API
        # http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key=KEY&stpid=STATION_ID&outputType=JSON
        url = f"http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key={CTA_API_KEY}&stpid={station_id}&outputType=JSON"
        
        if line_code:
            # Filter by route/line if specified
            url += f"&rt={line_code}"
        
        response = urequests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"CTA API error: {response.status_code}")
            response.close()
            return trains_inbound, trains_outbound
        
        data = response.json()
        response.close()
        
        # Check for API errors
        if "ctatt" not in data:
            print("Invalid CTA API response")
            return trains_inbound, trains_outbound
        
        if "errCd" in data["ctatt"] and data["ctatt"]["errCd"] != "0":
            print(f"CTA API error: {data['ctatt'].get('errNm', 'Unknown error')}")
            return trains_inbound, trains_outbound
        
        # Parse train arrivals
        if "eta" in data["ctatt"]:
            for arrival in data["ctatt"]["eta"]:
                # CTA provides predicted minutes directly in some cases
                # Or we parse from arrT (arrival time)

                # Try to get predicted minutes if available
                # Some CTA responses include this directly
                if "prdt" in arrival and "arrT" in arrival:
                    # Both prediction time and arrival time available
                    # Parse times: Format is "YYYYMMDD HH:MM:SS"
                    try:
                        pred_str = arrival["prdt"]  # When prediction was made
                        arr_str = arrival["arrT"]   # Predicted arrival time

                        # Extract just time portions (HH:MM:SS)
                        pred_parts = pred_str.split(" ")[1].split(":")
                        arr_parts = arr_str.split(" ")[1].split(":")

                        pred_mins = int(pred_parts[0]) * 60 + int(pred_parts[1])
                        arr_mins = int(arr_parts[0]) * 60 + int(arr_parts[1])

                        # Calculate difference
                        minutes = arr_mins - pred_mins

                        # Handle midnight crossover
                        if minutes < 0:
                            minutes += 1440  # Add 24 hours (1440 minutes)

                        # Limit to reasonable range
                        if minutes < 0:
                            minutes = 0
                        if minutes > 60:
                            continue  # Skip trains more than 60 min away

                    except (ValueError, IndexError, KeyError):
                        # Fallback: assume arriving soon
                        minutes = 5
                else:
                    # No time info, skip this arrival
                    continue

                # Get route and direction
                route = arrival.get("rt", line_code or "Unknown")
                destination = arrival.get("destNm", "")

                # Direction determination based on destination
                # Inbound = toward downtown/Loop
                # Outbound = away from downtown
                inbound_keywords = ["Loop", "Howard", "95th/Dan Ryan", "Kimball", "UIC", "Forest Park", "Harlem", "downtown"]
                is_inbound = any(keyword in destination for keyword in inbound_keywords)

                direction = "Inbound" if is_inbound else "Outbound"

                train = TrainArrival(route, direction, minutes, 1)

                if is_inbound:
                    trains_inbound.append(train)
                else:
                    trains_outbound.append(train)
        
        # Sort by arrival time
        trains_inbound.sort(key=lambda t: t.minutes)
        trains_outbound.sort(key=lambda t: t.minutes)
        
        print(f"Found {len(trains_inbound)} inbound, {len(trains_outbound)} outbound trains")
        
    except Exception as e:
        print(f"Error fetching CTA trains: {e}")
    
    return trains_inbound, trains_outbound

def fetch_trains_for_station(station_index):
    """Fetch train arrivals for a specific station in rotation mode"""
    global line1_inbound, line1_outbound, line2_inbound, line2_outbound
    global api_error, last_successful_update, cached_trains_available
    
    if station_index >= len(ROTATION_STATIONS):
        print(f"Invalid station index: {station_index}")
        return
    
    station = ROTATION_STATIONS[station_index]
    print(f"Fetching trains for: {station['name']} ({station['line']})")
    
    try:
        # Clear line2 data (not used in rotation mode)
        line2_inbound = []
        line2_outbound = []
        
        # Call appropriate API based on transit type
        transit_type = station.get("transit_type", "metra").lower()
        
        if transit_type == "cta":
            line1_inbound, line1_outbound = fetch_cta_trains(station["id"], station["line"])
        else:  # metra
            line1_inbound, line1_outbound = fetch_metra_trains(station["id"], station["line"])
        
        # Update status
        if len(line1_inbound) > 0 or len(line1_outbound) > 0:
            api_error = False
            last_successful_update = time.time()
            cached_trains_available = True
            print(f"Found trains for {station['name']}")
        else:
            print(f"No trains found for {station['name']}")
            # Don't set api_error - empty response is valid
        
    except Exception as e:
        print(f"Error fetching trains for station {station_index}: {e}")
        api_error = True

def detect_transit_type(line_code):
    """Determine if a line is CTA or Metra based on line code"""
    if not line_code:
        return "metra"  # Default to Metra
    
    # CTA line codes
    cta_lines = ["Red", "Blue", "Brn", "G", "Org", "P", "Pink", "Y"]
    
    if line_code in cta_lines:
        return "cta"
    else:
        return "metra"

def fetch_trains():
    """Fetch train arrivals from transit APIs"""
    global line1_inbound, line1_outbound, line2_inbound, line2_outbound
    global api_error, last_successful_update, cached_trains_available, wifi_connected
    
    if not wifi_connected:
        print("No WiFi connection")
        return
    
    # In station rotation mode, fetch for current station
    if station_rotation_enabled:
        fetch_trains_for_station(current_station_index)
        return
    
    try:
        print("Fetching train data...")
        
        # Detect transit type for LINE_1
        line1_type = detect_transit_type(LINE_1)
        
        # Fetch LINE_1 data
        if line1_type == "cta":
            line1_inbound, line1_outbound = fetch_cta_trains(PRIMARY_STATION_ID, LINE_1)
        else:  # metra
            line1_inbound, line1_outbound = fetch_metra_trains(PRIMARY_STATION_ID, LINE_1)
        
        # Fetch LINE_2 data if dual line mode
        if dual_line_mode:
            line2_type = detect_transit_type(LINE_2)
            
            if line2_type == "cta":
                line2_inbound, line2_outbound = fetch_cta_trains(SECONDARY_STATION_ID, LINE_2)
            else:  # metra
                line2_inbound, line2_outbound = fetch_metra_trains(SECONDARY_STATION_ID, LINE_2)
                
            # Update line numbers for line 2 trains
            for train in line2_inbound + line2_outbound:
                train.line_num = 2
        else:
            line2_inbound = []
            line2_outbound = []
        
        # Update status
        if len(line1_inbound) > 0 or len(line1_outbound) > 0:
            api_error = False
            last_successful_update = time.time()
            cached_trains_available = True
            print(f"Found trains for {LINE_1}")
        else:
            print(f"No trains found for {LINE_1}")
        
        if dual_line_mode:
            if len(line2_inbound) > 0 or len(line2_outbound) > 0:
                print(f"Found trains for {LINE_2}")
            else:
                print(f"No trains found for {LINE_2}")

    except Exception as e:
        api_error = True
        print(f"Error fetching trains: {e}")
        # Keep cached data if available
        if not cached_trains_available:
            line1_inbound = []
            line1_outbound = []
        line2_inbound = []
        line2_outbound = []

def fetch_alerts():
    """Fetch service alerts from Metra/CTA APIs"""
    global active_alerts, line1_has_alerts, line2_has_alerts

    active_alerts = []
    line1_has_alerts = False
    line2_has_alerts = False

    try:
        print("Fetching service alerts...")

        # Determine which transit system(s) we're using
        line1_type = detect_transit_type(LINE_1) if LINE_1 else "metra"
        line2_type = detect_transit_type(LINE_2) if dual_line_mode and LINE_2 else None

        # Fetch Metra alerts if using any Metra lines
        if line1_type == "metra" or (line2_type and line2_type == "metra"):
            metra_alerts = fetch_metra_alerts()
            active_alerts.extend(metra_alerts)

            # Check if our lines are affected
            for alert in metra_alerts:
                affected_routes = alert.get("routes", [])
                if LINE_1 in affected_routes:
                    line1_has_alerts = True
                if dual_line_mode and LINE_2 in affected_routes:
                    line2_has_alerts = True

        # Fetch CTA alerts if using any CTA lines
        if line1_type == "cta" or (line2_type and line2_type == "cta"):
            cta_alerts = fetch_cta_alerts()
            active_alerts.extend(cta_alerts)

            # Check if our lines are affected
            for alert in cta_alerts:
                affected_routes = alert.get("routes", [])
                if LINE_1 in affected_routes:
                    line1_has_alerts = True
                if dual_line_mode and LINE_2 in affected_routes:
                    line2_has_alerts = True

        if len(active_alerts) > 0:
            print(f"Found {len(active_alerts)} active alerts")
        else:
            print("No active service alerts")

    except Exception as e:
        print(f"Error fetching alerts: {e}")
        active_alerts = []

def fetch_metra_alerts():
    """Fetch service alerts from Metra GTFS-RT alerts feed"""
    alerts = []

    try:
        # Metra alerts API returns protobuf (same as trip updates)
        url = f"{ALERTS_URL}?api_token={METRA_API_TOKEN}"

        response = urequests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Metra alerts API error: {response.status_code}")
            response.close()
            return alerts

        # Read protobuf and parse alerts
        raw_content = response.content
        response.close()

        # Parse GTFS-RT alerts protobuf
        data = parse_gtfs_alerts_protobuf(raw_content)
        if not data or "entity" not in data:
            return alerts

        # Extract alerts
        for entity in data["entity"]:
            if "alert" not in entity:
                continue

            alert_data = entity["alert"]
            header = alert_data.get("header_text", "")
            description = alert_data.get("description_text", "")
            affected_routes = alert_data.get("informed_entity", [])

            # Only add if we have meaningful content
            if header or description:
                alerts.append({
                    "header": header,
                    "description": description,
                    "routes": affected_routes
                })

        print(f"Metra: Found {len(alerts)} alerts")


    except Exception as e:
        print(f"Error fetching Metra alerts: {e}")

    return alerts

def fetch_cta_alerts():
    """Fetch service alerts from CTA alerts API"""
    alerts = []

    try:
        # CTA doesn't have a dedicated alerts API in Train Tracker
        # Alerts are typically shown on their website or via Twitter
        # For now, return empty list
        # In the future, could scrape CTA alerts page or use their general transit feed

        print("CTA: No alerts API available in Train Tracker")

    except Exception as e:
        print(f"Error fetching CTA alerts: {e}")

    return alerts

def fetch_weather():
    """Fetch weather data from configured API service"""
    global weather_data
    
    if not ENABLE_WEATHER or not wifi_connected:
        return
    
    try:
        print("Fetching weather...")
        
        if WEATHER_API_SERVICE == "weathergov":
            # Weather.gov API (free, no key needed, US only)
            # Note: Weather.gov requires lat/lon coordinates, not ZIP codes
            # This is a simplified implementation using hardcoded Chicago coordinates
            # For production, you'd need to convert WEATHER_ZIP_CODE to lat/lon first

            # Chicago coordinates as default
            lat, lon = 41.8781, -87.6298

            # Step 1: Get grid point metadata
            points_url = f"https://api.weather.gov/points/{lat},{lon}"
            headers = {"User-Agent": "ChicagoTransitBoard/1.5.0"}

            response = urequests.get(points_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"Weather.gov points error: {response.status_code}")
                response.close()
                return

            points_data = response.json()
            response.close()

            forecast_url = points_data["properties"]["forecast"]

            # Step 2: Get forecast
            response = urequests.get(forecast_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"Weather.gov forecast error: {response.status_code}")
                response.close()
                return

            forecast_data = response.json()
            response.close()

            # Get current period (first entry)
            current = forecast_data["properties"]["periods"][0]
            weather_data["temp"] = current["temperature"]

            # Parse condition from shortForecast
            forecast_lower = current["shortForecast"].lower()
            if "rain" in forecast_lower or "storm" in forecast_lower:
                weather_data["condition"] = "rain"
                weather_data["icon"] = "rain"
            elif "snow" in forecast_lower:
                weather_data["condition"] = "snow"
                weather_data["icon"] = "snow"
            elif "cloud" in forecast_lower or "overcast" in forecast_lower:
                weather_data["condition"] = "cloudy"
                weather_data["icon"] = "cloud"
            elif "clear" in forecast_lower or "sunny" in forecast_lower:
                weather_data["condition"] = "clear"
                weather_data["icon"] = "sun"
            else:
                weather_data["condition"] = "clear"
                weather_data["icon"] = "sun"
            
        elif WEATHER_API_SERVICE == "openweathermap":
            # OpenWeatherMap API
            if not WEATHER_API_KEY:
                print("OpenWeatherMap requires API key")
                return
            
            url = f"https://api.openweathermap.org/data/2.5/weather?zip={WEATHER_ZIP_CODE},us&appid={WEATHER_API_KEY}&units=imperial"
            response = urequests.get(url)
            data = response.json()
            response.close()
            
            weather_data["temp"] = int(data["main"]["temp"])
            weather_code = data["weather"][0]["id"]
            
            # Map weather codes to simple conditions
            if weather_code < 300:  # Thunderstorm
                weather_data["condition"] = "rain"
                weather_data["icon"] = "rain"
            elif weather_code < 600:  # Rain/Drizzle
                weather_data["condition"] = "rain"
                weather_data["icon"] = "rain"
            elif weather_code < 700:  # Snow
                weather_data["condition"] = "snow"
                weather_data["icon"] = "snow"
            elif weather_code < 800:  # Atmosphere (fog, etc)
                weather_data["condition"] = "cloudy"
                weather_data["icon"] = "cloud"
            elif weather_code == 800:  # Clear
                weather_data["condition"] = "clear"
                weather_data["icon"] = "sun"
            else:  # Clouds
                weather_data["condition"] = "cloudy"
                weather_data["icon"] = "cloud"
        
        weather_data["last_update"] = time.time()
        print(f"Weather: {weather_data['temp']}°F, {weather_data['condition']}")
        
    except Exception as e:
        print(f"Error fetching weather: {e}")

def draw_weather_icon(x, y):
    """Draw a simple weather icon at the given position"""
    if not ENABLE_WEATHER or weather_data["icon"] is None:
        return
    
    icon = weather_data["icon"]
    
    # Simple 5x5 pixel icons
    display.set_pen(COLOR_YELLOW)
    
    if icon == "sun":
        # Draw sun (circle with rays)
        display.pixel(x+2, y+2)
        display.pixel(x+1, y+2)
        display.pixel(x+3, y+2)
        display.pixel(x+2, y+1)
        display.pixel(x+2, y+3)
    elif icon == "cloud":
        # Draw cloud
        display.set_pen(COLOR_WHITE)
        display.pixel(x+1, y+2)
        display.pixel(x+2, y+2)
        display.pixel(x+3, y+2)
        display.pixel(x+2, y+1)
    elif icon == "rain":
        # Draw cloud with rain
        display.set_pen(COLOR_WHITE)
        display.pixel(x+1, y+1)
        display.pixel(x+2, y+1)
        display.pixel(x+3, y+1)
        display.set_pen(COLOR_YELLOW)
        display.pixel(x+1, y+3)
        display.pixel(x+3, y+3)
    elif icon == "snow":
        # Draw snowflake
        display.set_pen(COLOR_WHITE)
        display.pixel(x+2, y+1)
        display.pixel(x+2, y+2)
        display.pixel(x+2, y+3)
        display.pixel(x+1, y+2)
        display.pixel(x+3, y+2)

def get_current_hour():
    """Get current hour (0-23) from RTC or system time"""
    # Note: You may need to sync time via NTP first
    # For now, using system time (seconds since epoch)
    # This assumes time is set correctly
    current_time = time.localtime()
    return current_time[3]  # Hour component

def adjust_brightness():
    """Adjust display brightness based on sleep mode or adaptive brightness"""
    if not ENABLE_SLEEP_MODE and not ENABLE_ADAPTIVE_BRIGHTNESS:
        return BRIGHTNESS
    
    hour = get_current_hour()
    
    # Sleep mode takes priority over adaptive brightness
    if ENABLE_SLEEP_MODE:
        # Check if we're in sleep hours
        if SLEEP_START_HOUR > SLEEP_END_HOUR:
            # Sleep period crosses midnight (e.g., 23:00 to 5:00)
            if hour >= SLEEP_START_HOUR or hour < SLEEP_END_HOUR:
                return SLEEP_BRIGHTNESS
        else:
            # Sleep period same day (e.g., 1:00 to 5:00)
            if SLEEP_START_HOUR <= hour < SLEEP_END_HOUR:
                return SLEEP_BRIGHTNESS
    
    # Adaptive brightness (if enabled and not in sleep mode)
    if ENABLE_ADAPTIVE_BRIGHTNESS:
        if 6 <= hour < 18:  # 6 AM - 6 PM
            return BRIGHTNESS  # 100% (use config value)
        elif 18 <= hour < 22:  # 6 PM - 10 PM
            return BRIGHTNESS * 0.7  # 70%
        else:  # 10 PM - 6 AM
            return BRIGHTNESS * 0.3  # 30%
    
    return BRIGHTNESS

def draw_display():
    """Update the LED display based on mode and direction"""
    # Adjust brightness based on time
    current_brightness = adjust_brightness()
    try:
        i75.set_brightness(current_brightness)
    except AttributeError:
        pass  # Newer firmware doesn't have this method
    
    # Check if we should show error screen
    if not wifi_connected or (api_error and not cached_trains_available):
        draw_error_screen()
        return
    
    display.set_pen(COLOR_BLACK)
    display.clear()
    
    if current_direction == "Alerts" and ENABLE_SERVICE_ALERTS and len(active_alerts) > 0:
        # Show alerts screen
        draw_alerts_screen()
    elif dual_line_mode:
        # DUAL LINE MODE: Split screen - top and bottom
        draw_dual_line_display()
    else:
        # SINGLE LINE MODE: Full screen
        draw_single_line_display()
    
    # Draw weather icon in top-right corner if enabled
    if ENABLE_WEATHER and WEATHER_DISPLAY_MODE == "icon_only" and weather_data["temp"] is not None:
        draw_weather_icon(120, 2)
    elif ENABLE_WEATHER and WEATHER_DISPLAY_MODE == "icon_and_temp" and weather_data["temp"] is not None:
        draw_weather_icon(115, 2)
        display.set_pen(COLOR_WHITE)
        display.text(f"{weather_data['temp']}", 100, 2, scale=1)
    
    i75.update()

def draw_single_line_display():
    """Draw display for single line (full screen 128x64)"""
    # Header - Station name with line color
    line_color = get_line_color(LINE_1)
    display.set_pen(line_color)
    display.text(STATION_STOP_ID, 5, 2, scale=2)
    
    # Get trains for current direction
    trains = line1_inbound if current_direction == "Inbound" else line1_outbound
    
    if len(trains) == 0:
        display.set_pen(COLOR_WHITE)
        display.text("No trains", 30, 30, scale=2)
        return
    
    # Show up to 2 trains
    y_start = 25
    for i, train in enumerate(trains[:2]):
        y = y_start + (i * 18)
        
        # Format: "UP-N, Inbound" or "UP-N, Outbound"
        train_text = f"{train.route}, {train.direction}"
        
        # Show alert icon if this line has alerts
        if ENABLE_ALERT_ICONS and line1_has_alerts:
            display.set_pen(COLOR_RED)
            display.text("!", 2, y, scale=1)
            display.set_pen(COLOR_WHITE)
            display.text(train_text, 10, y, scale=1)
        else:
            display.set_pen(COLOR_WHITE)
            display.text(train_text, 2, y, scale=1)
        
        # Time on the right
        time_text = format_time(train.minutes)
        time_color = get_time_color(train.minutes)
        
        display.set_pen(time_color)
        time_x = 128 - (len(time_text) * 6) - 5
        display.text(time_text, time_x, y, scale=1)

def draw_dual_line_display():
    """Draw display for two lines (split screen: 128x32 each)"""
    # TOP HALF - Line 1
    line1_color = get_line_color(LINE_1)
    display.set_pen(line1_color)
    display.text(LINE_1, 2, 1, scale=1)
    
    trains1 = line1_inbound if current_direction == "Inbound" else line1_outbound
    if len(trains1) > 0:
        train = trains1[0]  # Show first train only
        train_text = f"{train.route}, {train.direction}"
        
        # Show alert icon if line has alerts
        if ENABLE_ALERT_ICONS and line1_has_alerts:
            display.set_pen(COLOR_RED)
            display.text("!", 2, 10, scale=1)
            display.set_pen(COLOR_WHITE)
            display.text(train_text, 10, 10, scale=1)
        else:
            display.set_pen(COLOR_WHITE)
            display.text(train_text, 2, 10, scale=1)
        
        time_text = format_time(train.minutes)
        time_color = get_time_color(train.minutes)
        display.set_pen(time_color)
        time_x = 128 - (len(time_text) * 6) - 5
        display.text(time_text, time_x, 10, scale=1)
    else:
        display.set_pen(COLOR_WHITE)
        display.text("No trains", 20, 10, scale=1)
    
    # Divider line
    for x in range(0, 128, 4):
        display.set_pen(line1_color)
        display.pixel(x, 32)
    
    # BOTTOM HALF - Line 2
    line2_color = get_line_color(LINE_2)
    display.set_pen(line2_color)
    display.text(LINE_2, 2, 34, scale=1)
    
    trains2 = line2_inbound if current_direction == "Inbound" else line2_outbound
    if len(trains2) > 0:
        train = trains2[0]  # Show first train only
        train_text = f"{train.route}, {train.direction}"
        
        # Show alert icon if line has alerts
        if ENABLE_ALERT_ICONS and line2_has_alerts:
            display.set_pen(COLOR_RED)
            display.text("!", 2, 43, scale=1)
            display.set_pen(COLOR_WHITE)
            display.text(train_text, 10, 43, scale=1)
        else:
            display.set_pen(COLOR_WHITE)
            display.text(train_text, 2, 43, scale=1)
        
        time_text = format_time(train.minutes)
        time_color = get_time_color(train.minutes)
        display.set_pen(time_color)
        time_x = 128 - (len(time_text) * 6) - 5
        display.text(time_text, time_x, 43, scale=1)
    else:
        display.set_pen(COLOR_WHITE)
        display.text("No trains", 20, 43, scale=1)

def format_time(minutes):
    """Format minutes into display string"""
    if minutes == 0:
        return "ARR"
    elif minutes == 1:
        return "1 min"
    else:
        return f"{minutes} min"

def get_time_color(minutes):
    """Get color based on time until arrival"""
    if minutes == 0:
        return COLOR_RED
    elif minutes <= 2:
        return COLOR_YELLOW
    else:
        return COLOR_WHITE

def draw_alerts_screen():
    """Draw full-screen alerts display"""
    display.set_pen(COLOR_RED)
    display.text("SERVICE ALERTS", 10, 2, scale=1)
    
    if len(active_alerts) == 0:
        display.set_pen(COLOR_WHITE)
        display.text("No active alerts", 10, 25, scale=1)
        return
    
    # Show first alert (could scroll through multiple)
    alert = active_alerts[0]
    
    y = 15
    display.set_pen(COLOR_YELLOW)
    
    # Display header (truncate if too long)
    header = alert.get('header', 'Alert')
    if len(header) > 20:
        header = header[:20] + "..."
    display.text(header, 2, y, scale=1)
    
    # Show affected routes
    y += 12
    display.set_pen(COLOR_WHITE)
    routes = alert.get('routes', [])
    if routes:
        routes_text = "Lines: " + ", ".join(routes[:3])
        display.text(routes_text, 2, y, scale=1)
    
    # Show description (first line only)
    y += 12
    desc = alert.get('description', '')
    if desc and len(desc) > 0:
        # Take first 40 chars
        desc_line = desc[:40]
        if len(desc) > 40:
            desc_line += "..."
        display.text(desc_line, 2, y, scale=1)

def draw_error_screen():
    """Display error messages when WiFi or API fails"""
    display.set_pen(COLOR_BLACK)
    display.clear()
    
    # Error header in red
    display.set_pen(COLOR_RED)
    display.text("ERROR", 35, 5, scale=2)
    
    # Specific error message
    display.set_pen(COLOR_WHITE)
    if not wifi_connected:
        display.text("No WiFi", 30, 25, scale=1)
        display.text("Connection", 20, 35, scale=1)
        display.set_pen(COLOR_YELLOW)
        display.text("Check SSID/", 15, 50, scale=1)
        display.text("Password", 25, 57, scale=1)
    elif api_error:
        display.text("API Error", 25, 25, scale=1)
        display.set_pen(COLOR_YELLOW)
        display.text("Check Token", 15, 40, scale=1)
        display.text("in config.py", 10, 50, scale=1)

# ===== MAIN LOOP =====
async def main_loop():
    """Async main loop that runs alongside mDNS"""
    global current_direction, current_station_index
    import uasyncio

    print("Metra Transit Board - Interstate 75 W")
    
    # Read version
    try:
        with open("version.txt", "r") as f:
            version = f.read().strip()
            print(f"Version: {version}")
    except:
        print("Version: unknown")
    
    if station_rotation_enabled:
        print(f"Mode: Station Rotation ({len(ROTATION_STATIONS)} stations)")
        for i, station in enumerate(ROTATION_STATIONS):
            print(f"  {i+1}. {station['name']} - {station['line']} ({station['transit_type']})")
    else:
        print(f"Mode: Direction Rotation")
        print(f"Station: {STATION_STOP_ID}")
        print(f"Line(s): {LINE_1}" + (f" and {LINE_2}" if dual_line_mode else ""))
    
    # Initialize watchdog timer if enabled
    wdt = None
    if False:  # DISABLED FOR TESTING - was: if ENABLE_WATCHDOG:
        try:
            wdt = WDT(timeout=WATCHDOG_TIMEOUT)
            print(f"Watchdog enabled: {WATCHDOG_TIMEOUT}ms timeout")
        except Exception as e:
            print(f"Warning: Could not enable watchdog: {e}")
            wdt = None
    
    # Connect to WiFi
    if not connect_wifi():
        # WiFi failed - show error and halt
        draw_error_screen()
        print("Cannot start without WiFi")
        return
    
    # Check for updates if enabled
    if ENABLE_AUTO_UPDATE:
        print("\nChecking for updates...")
        led_pattern_updating()  # LED pattern while checking
        try:
            auto_update.auto_update_on_startup()
        except Exception as e:
            print(f"Update check failed: {e}")
            led_pattern_error()
    
    # Fetch initial train data
    fetch_trains()

    # Fetch initial weather data if enabled
    if ENABLE_WEATHER:
        fetch_weather()

    # Start config portal web server (non-blocking)
    config_server = None
    try:
        import socket
        config_server = socket.socket()
        config_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        config_server.bind(('0.0.0.0', 80))
        config_server.listen(1)
        config_server.setblocking(False)
        wlan = network.WLAN(network.STA_IF)
        print(f"\nConfig portal available at http://{wlan.ifconfig()[0]}")
    except Exception as e:
        print(f"Could not start config portal: {e}")
        config_server = None

    last_update = time.time()
    last_rotation = time.time()
    last_update_check = time.time()
    last_weather_update = time.time()
    last_alerts_update = time.time()
    last_wifi_check = time.time()
    wifi_check_interval = 30  # Check WiFi every 30 seconds
    
    while True:
        try:
            # Feed the watchdog
            if wdt is not None:
                wdt.feed()

            current_time = time.time()
            
            # Check WiFi connection periodically and reconnect if needed
            if current_time - last_wifi_check >= wifi_check_interval:
                last_wifi_check = current_time
                if not check_wifi_and_reconnect():
                    # WiFi is down and couldn't reconnect
                    # Continue loop but skip network operations
                    led_blink(1, 200, 100, r=100, g=0, b=0)  # Red blink to indicate offline
                    continue

            # Handle config portal web requests (non-blocking)
            if config_server:
                try:
                    cl, addr = config_server.accept()
                    cl.settimeout(5.0)
                    try:
                        # Read headers first
                        request = b''
                        while b'\r\n\r\n' not in request:
                            chunk = cl.recv(1024)
                            if not chunk:
                                break
                            request += chunk

                        # Find Content-Length in headers
                        headers_end = request.find(b'\r\n\r\n')
                        headers_part = request[:headers_end].decode('utf-8')
                        print(f"Headers: {headers_part[:200]}")
                        content_length = 0
                        for line in headers_part.split('\r\n'):
                            if 'content-length' in line.lower():
                                print(f"CL header: {line}")
                                content_length = int(line.split(':')[1].strip())
                                break
                        print(f"Content-Length parsed: {content_length}")

                        # Read remaining body based on Content-Length
                        if content_length > 0:
                            body_start_idx = headers_end + 4
                            body = request[body_start_idx:]
                            # Keep reading until we have full body
                            while len(body) < content_length:
                                remaining = content_length - len(body)
                                chunk = cl.recv(min(4096, remaining))
                                if not chunk:
                                    break
                                body += chunk
                            request = request[:body_start_idx] + body
                            print(f"Body received: {len(body)} bytes")

                        request = request.decode('utf-8')
                        print(f"Web request: {request[:50]}...")

                        if 'GET / ' in request or 'GET /config' in request:
                            # Stream template file in larger chunks to avoid splitting placeholders
                            import config_portal
                            import gc
                            gc.collect()  # Free memory first
                            config = config_portal.get_current_config()
                            status = config_portal.get_system_status()
                            cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n')

                            # Stream file in 4KB chunks with line-based reading
                            with open('config_portal_template.html', 'r') as f:
                                buffer = ''
                                for line in f:
                                    # Apply common replacements
                                    line = line.replace('{{METRA_TOKEN}}', str(config.get('metra_token') or ''))
                                    line = line.replace('{{STATION_NAME}}', str(config.get('station_name') or ''))
                                    line = line.replace('{{STATION_ID}}', str(config.get('station_id') or ''))
                                    line = line.replace('{{LINE_ID}}', str(config.get('line_id') or ''))
                                    line = line.replace('{{LINE_NAME}}', str(config.get('line_name') or ''))
                                    line = line.replace('{{BRIGHTNESS}}', str(config.get('brightness', 0.5)))
                                    line = line.replace('{{BRIGHTNESS_PCT}}', str(int(config.get('brightness', 0.5) * 100)))
                                    line = line.replace('{{UPDATE_INTERVAL}}', str(config.get('update_interval', 60)))
                                    line = line.replace('{{ROTATION_TIME}}', str(config.get('rotation_time', 5)))
                                    line = line.replace('{{NUM_TRAINS}}', str(config.get('num_trains', 4)))
                                    line = line.replace('{{VERSION}}', status['version'])
                                    line = line.replace('{{WIFI_SSID}}', str(config.get('wifi_ssid') or ''))
                                    line = line.replace('{{CTA_TOKEN}}', str(config.get('cta_token') or ''))
                                    line = line.replace('{{STATUS_ONLINE_CLASS}}', 'online' if status['wifi_connected'] else '')
                                    line = line.replace('{{WIFI_STATUS}}', 'Online' if status['wifi_connected'] else 'Offline')
                                    line = line.replace('{{UPTIME}}', f"{status['uptime'] // 3600}h {(status['uptime'] % 3600) // 60}m")
                                    line = line.replace('{{MEMORY_PCT}}', str(int((status['free_memory'] / status['total_memory']) * 100)))
                                    # Checkboxes and selects - use empty string for unchecked
                                    line = line.replace('{{SERVICE_ALERTS_CHECKED}}', 'checked' if config.get('enable_service_alerts', True) else '')
                                    line = line.replace('{{ALERT_ICONS_CHECKED}}', 'checked' if config.get('enable_alert_icons', True) else '')
                                    line = line.replace('{{ALERTS_UPDATE_INTERVAL}}', str(config.get('alerts_update_interval', 180)))
                                    line = line.replace('{{AUTO_UPDATE_CHECKED}}', 'checked' if config.get('enable_auto_update', True) else '')
                                    line = line.replace('{{WATCHDOG_CHECKED}}', 'checked' if config.get('enable_watchdog', True) else '')
                                    line = line.replace('{{WEATHER_CHECKED}}', 'checked' if config.get('enable_weather', False) else '')
                                    line = line.replace('{{WEATHER_STATUS}}', 'Enabled' if config.get('enable_weather', False) else 'Disabled')
                                    line = line.replace('{{WEATHER_ZIP}}', str(config.get('weather_zip_code', '')))
                                    line = line.replace('{{WEATHER_API_KEY}}', str(config.get('weather_api_key', '')))
                                    line = line.replace('{{SECONDARY_CHECKED}}', 'checked' if config.get('secondary_line_id') else '')
                                    line = line.replace('{{SECONDARY_DISPLAY}}', '' if config.get('secondary_line_id') else 'display: none')
                                    line = line.replace('{{SECONDARY_LINE_ID}}', str(config.get('secondary_line_id') or ''))
                                    line = line.replace('{{SECONDARY_LINE_NAME}}', str(config.get('secondary_line_name') or ''))
                                    line = line.replace('{{ROTATION_MODE_DIRECTION}}', 'selected')
                                    line = line.replace('{{ROTATION_MODE_STATION}}', '')
                                    line = line.replace('{{DIRECTION_MODE_DISPLAY}}', '')
                                    line = line.replace('{{STATION_MODE_DISPLAY}}', 'display: none')
                                    buffer += line
                                    if len(buffer) > 2048:
                                        cl.send(buffer)
                                        buffer = ''
                                        gc.collect()
                                if buffer:
                                    cl.send(buffer)
                        elif 'GET /restart' in request:
                            cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Restarting...</h1>')
                            cl.close()
                            import machine
                            machine.reset()
                        elif 'POST /save' in request:
                            import config_portal
                            body = request.split('\r\n\r\n', 1)[1] if '\r\n\r\n' in request else ''
                            print(f"POST body length: {len(body)}")
                            print(f"POST body: {body[:200]}")
                            params = config_portal.parse_form_data(body)
                            print(f"Parsed station: {params.get('primary_station_id', 'NOT FOUND')}")
                            # Preserve WiFi settings
                            params['wifi_ssid'] = WIFI_SSID
                            params['wifi_password'] = WIFI_PASSWORD
                            if config_portal.save_config(params):
                                # Send success page and soft restart
                                cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
                                cl.send('<!DOCTYPE html><html><head><title>Saved</title>')
                                cl.send('<meta name="viewport" content="width=device-width,initial-scale=1">')
                                cl.send('<style>body{font-family:sans-serif;text-align:center;padding:50px;background:#1a1a2e;color:#fff}')
                                cl.send('.success{background:#28a745;padding:20px;border-radius:8px;margin:20px auto;max-width:400px}')
                                cl.send('</style></head><body>')
                                cl.send('<div class="success"><h2>Configuration Saved!</h2>')
                                cl.send('<p>Restarting...</p></div>')
                                cl.send('</body></html>')
                                cl.close()
                                # Soft restart - re-execute main.py
                                import sys
                                sys.exit()
                            else:
                                cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
                                cl.send('<!DOCTYPE html><html><body style="font-family:sans-serif;text-align:center;padding:50px">')
                                cl.send('<h2 style="color:red">Failed to save configuration</h2>')
                                cl.send('<p><a href="/">Try Again</a></p></body></html>')
                        else:
                            # Handle favicon and other requests
                            cl.send('HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n')
                    except Exception as e:
                        print(f"Web request error: {e}")
                        try:
                            cl.send('HTTP/1.1 500 Error\r\n\r\n')
                        except:
                            pass
                    finally:
                        try:
                            cl.close()
                        except:
                            pass
                except OSError:
                    pass  # No connection waiting

            # Check WiFi connection periodically
            wlan = network.WLAN(network.STA_IF)
            if not wlan.isconnected():
                print("WiFi disconnected, attempting reconnect...")
                connect_wifi()
            
            # Update train data from API
            if current_time - last_update >= UPDATE_INTERVAL:
                if wifi_connected:
                    fetch_trains()
                last_update = current_time
            
            # Update service alerts periodically (less frequent than trains)
            if ENABLE_SERVICE_ALERTS and wifi_connected and (current_time - last_alerts_update >= ALERTS_UPDATE_INTERVAL):
                fetch_alerts()
                last_alerts_update = current_time

            # Update weather data periodically
            if ENABLE_WEATHER and wifi_connected and (current_time - last_weather_update >= WEATHER_UPDATE_INTERVAL):
                fetch_weather()
                last_weather_update = current_time

            # Check for software updates periodically
            if ENABLE_AUTO_UPDATE and wifi_connected and (current_time - last_update_check >= CHECK_UPDATE_INTERVAL):
                print("\nPeriodic update check...")
                try:
                    auto_update.check_for_updates()
                except Exception as e:
                    print(f"Update check failed: {e}")
                last_update_check = current_time
            
            # Rotate between views based on mode
            if current_time - last_rotation >= DISPLAY_ROTATION_TIME:
                if station_rotation_enabled:
                    # Station rotation mode: cycle through stations
                    # Each station shows Inbound → Outbound before moving to next station
                    if ENABLE_SERVICE_ALERTS and len(active_alerts) > 0:
                        # With alerts: Inbound -> Outbound -> Alerts -> next station
                        if current_direction == "Inbound":
                            current_direction = "Outbound"
                        elif current_direction == "Outbound":
                            current_direction = "Alerts"
                        else:
                            # After alerts, move to next station
                            current_direction = "Inbound"
                            current_station_index = (current_station_index + 1) % len(ROTATION_STATIONS)
                            fetch_trains_for_station(current_station_index)
                    else:
                        # No alerts: Inbound -> Outbound -> next station
                        if current_direction == "Inbound":
                            current_direction = "Outbound"
                        else:
                            # After outbound, move to next station
                            current_direction = "Inbound"
                            current_station_index = (current_station_index + 1) % len(ROTATION_STATIONS)
                            fetch_trains_for_station(current_station_index)
                    
                    station = ROTATION_STATIONS[current_station_index]
                    print(f"Station: {station['name']} - {current_direction}")
                else:
                    # Direction rotation mode (original behavior)
                    if ENABLE_SERVICE_ALERTS and len(active_alerts) > 0:
                        # Cycle: Inbound -> Outbound -> Alerts -> Inbound
                        if current_direction == "Inbound":
                            current_direction = "Outbound"
                        elif current_direction == "Outbound":
                            current_direction = "Alerts"
                        else:
                            current_direction = "Inbound"
                    else:
                        # No alerts: just toggle Inbound <-> Outbound
                        current_direction = "Outbound" if current_direction == "Inbound" else "Inbound"
                    
                    print(f"Switched to {current_direction}")
                
                last_rotation = current_time
            
            # Update display
            draw_display()

            await uasyncio.sleep_ms(500)

        except KeyboardInterrupt:
            print("Stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            await uasyncio.sleep(5)

async def main():
    """Main entry point"""
    await main_loop()

if __name__ == "__main__":
    # Check for setup mode (hold BOOT button on startup)
    # Or if config.py doesn't exist
    if needs_setup():
        print("\n" + "="*50)
        print("SETUP MODE")
        print("="*50)
        print("No configuration found. Starting setup portal...")
        import setup_portal
        setup_portal.run_server()
    else:
        # Normal operation - run async main
        import uasyncio
        uasyncio.run(main())
