# Metra Transit Board Configuration
# Copy this file to 'config.py' and fill in your settings

# WiFi Settings
WIFI_SSID = "Your_WiFi_Network_Name"
WIFI_PASSWORD = "Your_WiFi_Password"

# API Settings
METRA_API_TOKEN = "your_metra_token_here"
# Get your API token from: https://metra.com/developers

CTA_API_KEY = "your_cta_key_here"
# Get your CTA API key from: https://www.transitchicago.com/developers/

# Station Configuration
STATION_STOP_ID = "RAVENSWOOD"
# Display name for primary station
# Examples: RAVENSWOOD, OTC, CLYBOURN, ROGERPK (Metra)
#           Belmont, Fullerton, Chicago (CTA)

PRIMARY_STATION_ID = "RAVENSWOOD"
# API ID for primary station (used for API calls)

# Line Configuration
# Set one or two lines to display
# For one line: set LINE_1, leave LINE_2 as None
# For two lines: set both LINE_1 and LINE_2
LINE_1 = "UP-N"  # Primary line (e.g., UP-N for Union Pacific North)
LINE_2 = None    # Secondary line (e.g., "Brn" for Brown Line, or None)

# Secondary Line Station (only needed if LINE_2 is set)
SECONDARY_STATION_ID = None  # API ID for secondary line station
SECONDARY_STATION_NAME = None  # Display name for secondary station

# Available Metra Lines:
# UP-N   = Union Pacific North
# UP-NW  = Union Pacific Northwest  
# UP-W   = Union Pacific West
# MD-N   = Milwaukee District North
# MD-W   = Milwaukee District West
# NCS    = North Central Service
# BNSF   = BNSF Railway
# HC     = Heritage Corridor
# ME     = Metra Electric
# RI     = Rock Island
# SWS    = SouthWest Service

# CTA Lines:
# Red, Blue, Brn (Brown), G (Green), Org (Orange), 
# Pink, P (Purple), Y (Yellow)

# ========================================
# Display Settings
# ========================================
DISPLAY_ROTATION_TIME = 5  # Seconds to show each direction (inbound/outbound)
UPDATE_INTERVAL = 30       # Seconds between API updates
BRIGHTNESS = 0.5           # Display brightness (0.0 to 1.0)
NUM_TRAINS_TO_SHOW = 4     # Number of trains to display per direction

# ========================================
# Rotation Mode
# ========================================
ROTATION_MODE = "direction"  # "direction" or "station"

# "direction" mode (default):
#   - Shows 1-2 configured lines (LINE_1 and optionally LINE_2)
#   - Rotates between Inbound → Outbound → Alerts
#   - If dual line mode: shows both lines split screen simultaneously
#
# "station" mode:
#   - Cycles through multiple stations one at a time (full screen each)
#   - Each station shows Inbound → Outbound before moving to next
#   - Useful for monitoring home + work stations, or multiple family members' locations

# Station Rotation Configuration (only used when ROTATION_MODE = "station")
ROTATION_STATIONS = [
    # Example configuration - replace with your stations
    {
        "name": "Ravenswood",           # Display name
        "id": "RAVENSWOOD",             # API station ID
        "line": "UP-N",                 # Line name
        "transit_type": "metra"         # "metra" or "cta"
    },
    {
        "name": "Kimball",
        "id": "30249",
        "line": "Brown",
        "transit_type": "cta"
    },
    {
        "name": "Clybourn",
        "id": "CLYBOURN",
        "line": "UP-NW",
        "transit_type": "metra"
    }
]

STATION_ROTATION_TIME = 10  # Seconds per station (shows inbound + outbound before rotating)
# Note: Each direction still uses DISPLAY_ROTATION_TIME, this is the total time per station

# ========================================
# Service Alerts
# ========================================
ENABLE_SERVICE_ALERTS = True  # Show service alerts in rotation
ENABLE_ALERT_ICONS = True     # Show warning icon next to affected trains
ALERTS_UPDATE_INTERVAL = 180  # Seconds between alert updates (3 minutes)

# ========================================
# Auto-Update
# ========================================
ENABLE_AUTO_UPDATE = True  # Check for updates on startup (enabled by default)
CHECK_UPDATE_INTERVAL = 604800  # Check for updates every 7 days/weekly (in seconds)
# Options: 86400 (daily), 604800 (weekly - recommended), 2592000 (monthly)

# ========================================
# System Reliability
# ========================================
ENABLE_WATCHDOG = True       # Enable watchdog timer (recommended)
WATCHDOG_TIMEOUT = 8000      # Timeout in milliseconds (8 seconds default)
# System will auto-reboot if it doesn't respond within this time

# ========================================
# Weather
# ========================================
ENABLE_WEATHER = False                    # Show weather icon/temp on display
WEATHER_API_SERVICE = "weathergov"        # "weathergov" (free, US only) or "openweathermap"
WEATHER_API_KEY = ""                      # API key for OpenWeatherMap (leave empty for weather.gov)
WEATHER_ZIP_CODE = ""                     # Your ZIP code or location (e.g., "60601")
WEATHER_UPDATE_INTERVAL = 1800            # Update weather every 30 minutes (in seconds)
WEATHER_DISPLAY_MODE = "icon_only"        # "icon_only" or "icon_and_temp"
# Get OpenWeatherMap API key from: https://openweathermap.org/api

# ========================================
# Power Management
# ========================================

# Sleep Mode (Dim Display at Night)
ENABLE_SLEEP_MODE = False    # Automatically dim display during sleep hours
SLEEP_START_HOUR = 23        # Start dimming at this hour (0-23, e.g., 23 = 11 PM)
SLEEP_END_HOUR = 5           # Stop dimming at this hour (0-23, e.g., 5 = 5 AM)
SLEEP_BRIGHTNESS = 0.1       # Brightness during sleep hours (0.05-0.3, default 0.1 = 10%)
# Note: Cannot be used simultaneously with Adaptive Brightness

# Adaptive Brightness (Auto-adjust by Time of Day)
ENABLE_ADAPTIVE_BRIGHTNESS = False  # Auto-adjust brightness based on time
# When enabled:
#   6 AM - 6 PM:   100% brightness (uses BRIGHTNESS setting)
#   6 PM - 10 PM:  70% brightness
#   10 PM - 6 AM:  30% brightness
# Note: Cannot be used simultaneously with Sleep Mode
