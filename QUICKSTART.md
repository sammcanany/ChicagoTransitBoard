# Quick Start Guide

## Two Setup Methods

### Method 1: Web Setup Portal

No config file editing required. The board creates its own WiFi network for setup.

1. Flash MicroPython firmware
2. Upload `main.py` and `setup_portal.py`
3. Connect to "ChicagoTransitBoard" WiFi network
4. Configure via web browser
5. Done!

**[See detailed Web Setup instructions →](#method-1-web-setup-portal)**

### Method 2: Manual Config File

Traditional method - edit config.py on your computer.

1. Flash MicroPython firmware
2. Create and edit config.py
3. Upload all files
4. Done!

**[See Manual Setup instructions →](#method-2-manual-config-file)**

---

## Method 1: Web Setup Portal

### Step 1: Hardware Assembly

1. **Connect Panels**:
   - Plug Panel 1 into Interstate 75 W HUB75 connector
   - Chain Panel 2 to Panel 1 output connector

2. **Connect Power**:
   - Plug 5V power supply into Panel 1 screw terminals
   - Daisy-chain to Panel 2 (or use splitter)

3. **Connect USB**: Plug USB-C cable from Interstate 75 W to computer

### Step 2: Flash MicroPython Firmware

1. **Download Firmware**:
   - Go to: https://github.com/pimoroni/interstate75/releases/latest
   - Download: `pimoroni-interstate75_w_rp2350-vX.X.X.uf2`

2. **Enter Bootloader Mode**:
   - Hold **BOOT** button on Interstate 75 W
   - While holding BOOT, tap **RST** button (or plug in USB)
   - Release BOOT
   - A drive named "RP2350" should appear

3. **Flash Firmware**:
   - Drag the `.uf2` file to the "RP2350" drive
   - Board will reboot automatically

### Step 3: Install Thonny

1. Download from: https://thonny.org/
2. Install and open Thonny
3. Bottom-right corner: Select **"Raspberry Pi Pico"**
4. You should see `>>>` prompt in the Shell window

### Step 4: Upload Setup Files

1. Close Thonny if it's open (it locks the serial port)
2. Run: `python upload.py`
3. All required files upload automatically
4. On first run, required libraries (mDNS) are installed automatically

**Alternative: Using Thonny**
1. In Thonny, open `main.py`
2. **File → Save As → Raspberry Pi Pico** → Save as `main.py`
3. Repeat for `setup_portal.py`, `config_portal.py`, etc.
4. Manually install mDNS library:
   ```python
   import mip
   mip.install("github:cbrand/micropython-mdns")
   ```

### Step 5: Start Setup Portal

1. **Restart the board** (press RST button or unplug/replug power)
2. The board will detect no config.py and automatically:
   - Create a WiFi Access Point
   - Start the web server
   - Show connection info in serial console

You should see in Thonny's shell:
```
==================================================
Access Point Created!
==================================================
Network: ChicagoTransitBoard
Password: setup1234
IP Address: 192.168.4.1

Connect to this network and go to:
http://192.168.4.1
==================================================
```

### Step 6: Initial WiFi Setup

1. **On your phone or computer:**
   - Go to WiFi settings
   - Connect to network: `ChicagoTransitBoard`
   - Password: `setup1234`

2. **Open web browser** and go to:
   - http://192.168.4.1

3. **Configure WiFi only**:
   - **WiFi SSID**: Select your network from dropdown or enter manually
   - **WiFi Password**: Your WiFi password

4. **Click "Save and Restart"**

5. **Wait for restart** (about 5 seconds)
   - The ChicagoTransitBoard network will disappear
   - The board restarts and connects to your WiFi

### Step 7: Complete Configuration Portal

After the board connects to your WiFi, configure everything through the main portal:

1. **On your phone or computer (now connected to your normal WiFi):**
   - Open web browser and go to: **http://board.local**
   - (Or use the board's IP address if mDNS doesn't work)

2. **Fill out the complete configuration:**
   
   **API Settings:**
   - **Metra API Token**: Get from https://metra.com/developers
   - **CTA API Key**: Get from https://www.transitchicago.com/developers/
   
   **Primary Line:**
   - **Transit Type**: Choose Metra or CTA
   - **Line**: Select from dropdown (UP-N, Brown Line, etc.) or enter custom
   - **Station**: Select from filtered dropdown (shows only stations for your transit type)
   
   **Display Mode:**
   - **Direction Rotation**: Show 1-2 lines with inbound/outbound rotation (default)
   - **Station Rotation**: Cycle through 3+ stations, each showing full screen
   
   **Secondary Line (Optional for Direction Rotation Mode):**
   - Check "Enable Secondary Line"
   - **Transit Type**: Choose Metra or CTA (can be different from primary!)
   - **Line**: Select line for second display
   - **Station**: Select station for second line
   
   **Station Rotation (For Station Rotation Mode):**
   - Configure 3+ stations to cycle through
   - Each station shows full screen with inbound/outbound
   - Example: Home station → Work station → Family member's station
   
   **Display Settings:**
   - **Brightness**: 10-100%
   - **Update Interval**: 30-300 seconds
   - **Rotation Time**: 3-30 seconds between views
   - **Trains to Show**: 1-8 trains per direction
   
   **Features (Optional):**
   - **Service Alerts**: Show service disruption warnings
   - **Alert Icons**: Display warning icons next to affected trains
   - **Auto-Update**: Check GitHub for updates (daily/weekly/monthly)
   
   **Weather (Optional):**
   - **Enable Weather**: Show current temperature and conditions
   - **Service**: Weather.gov (free, US-only) or OpenWeatherMap (requires API key)
   - **ZIP Code**: Your location for weather data
   - **Display Mode**: Icon only or icon + temperature
   - **Update Interval**: 15, 30, or 60 minutes
   
   **System Settings:**
   - **Watchdog Timer**: Auto-recovery from crashes (5s, 8s, or 10s timeout)
   - **Sleep Mode**: Dim display at night (configurable start/end hours and brightness)
   - **Adaptive Brightness**: Auto-adjust brightness based on time of day

3. **Click "Save Configuration"**

4. **Board restarts automatically** and starts displaying train data.

### Done!

Your board is now:
- Connected to your WiFi
- Accessible at http://board.local for future config changes
- Fetching train data from Metra and/or CTA
- Displaying arrivals with rotation
- Auto-updating from GitHub (if enabled)

**Pro tip**: You can always access http://board.local to change settings without re-uploading code.

---

## Method 2: Manual Config File

1. **Connect Panels**:
   - Plug Panel 1 into Interstate 75 W HUB75 connector
   - Chain Panel 2 to Panel 1 output connector

2. **Connect Power**:
   - Plug 5V power supply into Panel 1 screw terminals
   - Daisy-chain to Panel 2 (or use splitter)
   - Interstate 75 W can be powered via USB-C or from panel 5V

3. **Connect USB**:
   - Plug USB-C cable from Interstate 75 W to computer

## Step 2: Flash MicroPython Firmware

1. **Download Firmware**:
   - Go to: https://github.com/pimoroni/interstate75/releases/latest
   - Download: `pimoroni-interstate75_w_rp2350-vX.X.X.uf2`

2. **Enter Bootloader Mode**:
   - Hold **BOOT** button on Interstate 75 W
   - While holding BOOT, tap **RST** button
   - Release BOOT
   - A drive named "RP2350" should appear

3. **Flash Firmware**:
   - Drag the `.uf2` file to the "RP2350" drive
   - Board will reboot automatically

## Step 3: Install Thonny

1. Download from: https://thonny.org/
2. Install and open Thonny
3. Bottom-right corner: Select **"Raspberry Pi Pico"**
4. You should see `>>>` prompt in the Shell window

## Step 4: Create Configuration File

1. Open `config.example.py` in Thonny

2. Fill in your settings:
   ```python
   # WiFi
   WIFI_SSID = "Your_Network_Name"
   WIFI_PASSWORD = "Your_Password"
   
   # API Keys
   METRA_API_TOKEN = "your_metra_token_here"  # Get from https://metra.com/developers
   CTA_API_KEY = "your_cta_key_here"          # Get from https://www.transitchicago.com/developers/
   
   # Primary Line Configuration
   STATION_STOP_ID = "RAVENSWOOD"        # Display name for primary station
   PRIMARY_STATION_ID = "RAVENSWOOD"     # API ID for primary station
   LINE_1 = "UP-N"                       # Primary line (UP-N, Brn, etc.)
   
   # Secondary Line (Dual Line Mode)
   LINE_2 = None                         # Secondary line (e.g., "Brn") or None
   SECONDARY_STATION_ID = None           # Station ID for secondary line
   SECONDARY_STATION_NAME = None         # Display name for secondary station
   
   # Display Settings
   DISPLAY_ROTATION_TIME = 5      # Seconds between Inbound/Outbound/Alerts
   UPDATE_INTERVAL = 30           # API refresh interval (seconds)
   BRIGHTNESS = 0.5               # 0.0 to 1.0
   NUM_TRAINS_TO_SHOW = 4         # Number of trains per direction
   
   # Feature Toggles
   ENABLE_AUTO_UPDATE = True           # Check GitHub for updates
   ENABLE_SERVICE_ALERTS = True        # Show service disruption alerts
   ENABLE_ALERT_ICONS = True           # Show warning icons next to affected trains
   ALERTS_UPDATE_INTERVAL = 180        # Check alerts every 3 minutes (less frequent than trains)
   
   # Rotation Mode (v1.4.0)
   ROTATION_MODE = "direction"  # "direction" (1-2 lines) or "station" (3+ stations)
   
   # Station Rotation Configuration (only used when ROTATION_MODE = "station")
   ROTATION_STATIONS = [
       {"name": "Ravenswood", "id": "RAVENSWOOD", "line": "UP-N", "transit_type": "metra"},
       {"name": "Kimball", "id": "30249", "line": "Brown", "transit_type": "cta"},
       {"name": "Clybourn", "id": "CLYBOURN", "line": "UP-NW", "transit_type": "metra"}
   ]
   STATION_ROTATION_TIME = 10  # Seconds per station
   
   # Weather Integration (v1.3.0)
   ENABLE_WEATHER = False                      # Show weather icon and temp
   WEATHER_API_SERVICE = "weathergov"          # "weathergov" (free) or "openweathermap"
   WEATHER_API_KEY = ""                        # Required for OpenWeatherMap only
   WEATHER_ZIP_CODE = "60601"                  # Your ZIP code
   WEATHER_UPDATE_INTERVAL = 1800              # Update every 30 minutes (in seconds)
   WEATHER_DISPLAY_MODE = "icon_only"          # "icon_only" or "icon_and_temp"
   
   # System Settings (v1.3.0)
   ENABLE_WATCHDOG = True                      # Auto-recovery from crashes
   WATCHDOG_TIMEOUT = 8000                     # Watchdog timeout in milliseconds
   ENABLE_SLEEP_MODE = False                   # Dim display at night
   SLEEP_START_HOUR = 23                       # Start dimming at 11 PM
   SLEEP_END_HOUR = 5                          # Resume normal brightness at 5 AM
   SLEEP_BRIGHTNESS = 0.1                      # Brightness during sleep hours (0.0-1.0)
   ENABLE_ADAPTIVE_BRIGHTNESS = False          # Auto-adjust brightness by time of day
   ```

3. **Save as `config.py`** (not config.example.py!)
   - **File → Save As → Raspberry Pi Pico**
   - Name it exactly: `config.py`

## Step 5: Upload All Files

Upload these files to the Pico (File → Save As → Raspberry Pi Pico):

**Required files:**
- `main.py` - Main application
- `config.py` - Your configuration (created in Step 4)
- `setup_portal.py` - WiFi setup portal
- `config_portal.py` - Configuration web portal
- `config_portal_template.html` - Web UI template
- `auto_update.py` - Auto-update system
- `version.txt` - Version tracking

## Step 6: Run and Enjoy!

1. In Thonny, open `main.py`
2. Click **Run** (▶)
3. Watch the display show:
   - WiFi connection status
   - Train arrivals for your station
   - Inbound → Outbound → Alerts rotation

The display will show real train arrivals from Metra GTFS-RT (protobuf format, parsed natively) or CTA Train Tracker API (JSON).

## Troubleshooting

**Display Issues:**
- **No lights**: Check 5V power to panels
- **Garbled display**: Try different brightness (0.1 to 1.0) in `config.py`
- **Wrong colors**: Line colors are built-in (UP-N yellow, ME blue, etc.)
- **Flickering**: Check HUB75 cable connection
- **"ERROR" screen**: Shows specific error (WiFi or API issue)

**WiFi Issues:**
- **"No WiFi Connection" error**: Verify SSID/password in `config.py`
- **Can't connect**: Verify 2.4GHz network (Pico doesn't support 5GHz)
- **Wrong password**: Check for typos, case-sensitive
- **Auto-reconnect**: Board will attempt to reconnect if WiFi drops

**API Issues:**
- **"API Error - Check Token" screen**: Verify Metra API token and/or CTA API key in `config.py`
- **No trains shown**: Check STATION_STOP_ID matches your station
- **Wrong station data**: Verify PRIMARY_STATION_ID is correct for your line

**Code Issues:**
- **Import errors**: Reflash MicroPython firmware
- **File not found**: Ensure `config.py` exists (copy from `config.example.py`)
- **Memory errors**: Reduce UPDATE_INTERVAL in `config.py`

## What's Next?

1. **Customize**:
   - Add a second line (dual split screen)
   - Adjust rotation timing
   - Change brightness for different environments

3. **Monitor**:
   - Service alerts show automatically
   - WiFi reconnects automatically
   - Auto-updates check GitHub periodically

---

## Accessing Configuration Portal Later

You can always reconfigure your board without editing files:

1. Connect to your WiFi network
2. Open browser and go to **http://board.local**
3. Make changes and save
4. Board restarts automatically with new settings

## Next Steps

### Customize Your Display
- Enable dual line mode for split-screen (Metra + CTA!)
- Adjust brightness for your room lighting
- Change rotation timing between views
- Show more or fewer trains per direction

### Monitor Your Board
- Service alerts display automatically when active
- Auto-updates check GitHub periodically
- WiFi reconnects automatically if connection drops
- Access http://board.local to check system status (uptime, memory, IP)

---

**Need help? Check [README.md](README.md) or open a GitHub issue!**