# Metra Transit Board - Interstate 75 W

Real-time Metra train arrivals using **Pimoroni Interstate 75 W** and 2x 64x32 HUB75 LED matrices.

![Platform](https://img.shields.io/badge/Platform-RP2350-red) ![MicroPython](https://img.shields.io/badge/MicroPython-1.27-blue) ![License](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-orange)

## Features

- **Web Configuration Portal**: Access http://board.local to manage all settings through a modern web interface
  - Transit type selection (Metra or CTA)
  - Rotation mode: Direction (1-2 lines) or Station (3+ stations)
  - Line and station selection with smart dropdowns
  - Per-line station configuration
  - Dual line mode support
  - Station rotation mode for monitoring multiple locations
  - Display settings (brightness, update intervals)
  - Weather integration (Weather.gov or OpenWeatherMap)
  - System settings (watchdog, sleep mode, adaptive brightness)
  - System status monitoring
- **WiFi Setup Portal**: First-time setup via Access Point mode - no code editing needed!
- **Real-time Train Arrivals**: Displays upcoming trains from Metra GTFS-Realtime API (JSON format) and CTA Train Tracker API (JSON)
- **Weather Integration**: Display current temperature and conditions with icon
- **Single or Dual Line Support**: Show 1 line (full screen) or 2 lines (split screen)
- **Station Rotation Mode**: Cycle through 3+ stations, showing each full-screen before rotating
- **Direction Rotation**: Automatically cycles between Inbound, Outbound, and Service Alerts every 5 seconds
- **Line-Specific Colors**: Each Metra/CTA line displays in its official brand color (UP-N yellow, ME blue, Brown Line brown, etc.)
- **Service Alerts**: Shows active service disruptions with alert icons next to affected trains
- **Smart Power Management**: Sleep mode (dim at night), adaptive brightness based on time of day
- **Watchdog Timer**: Automatic recovery from crashes and hangs
- **Offline Mode**: Gracefully handles WiFi disconnections and API errors with user-friendly error messages
- **Auto-Update**: Automatically checks for and installs updates from GitHub
- **Fully Configurable**: All settings via web portal at http://board.local or `config.py`

## Hardware

- **Controller**: Pimoroni Interstate 75 W (RP2350 / Pico 2 W)
- **Display**: 2x 64x32 RGB LED Matrix (HUB75, any pitch works)
- **Total Resolution**: 128 x 64 pixels (stacked vertically or chained horizontally)
- **Power**: 5V 10A power supply

## What You Have

**Interstate 75 W** - Perfect for HUB75 matrices!
- RP2350 microcontroller (Pico 2 W)
- Built-in WiFi
- HUB75 connector with level shifters
- Supports up to 128x64 displays

## Quick Start

See **[QUICKSTART.md](QUICKSTART.md)** for detailed setup instructions.

### First-Time Setup (Web Portal - Recommended)
1. Flash MicroPython firmware to Interstate 75 W
2. Upload `main.py` and `setup_portal.py` to the board
3. Power on - board creates WiFi network "ChicagoTransitBoard" (password: setup1234)
4. Connect to the WiFi network and open http://192.168.4.1 in your browser
5. Select your WiFi network and enter password
6. Board restarts and connects to your WiFi

### Configuration (Web Interface)
1. Once connected to your WiFi, access http://board.local in your browser
2. Configure all settings through the modern web interface:
   - **API Keys**: Enter your Metra Token and/or CTA API Key
   - **Transit Lines**: Select transit type (Metra or CTA), line, and station
   - **Rotation Mode**: Choose Direction (1-2 lines) or Station (3+ stations)
   - **Dual Line Mode**: Optionally enable secondary line with separate settings
   - **Station Rotation**: Configure 3+ stations to cycle through (each shows full screen)
   - **Display Settings**: Brightness, update intervals, rotation time, train count
   - **Features**: Service alerts, auto-update settings
   - **Weather**: Enable weather display with Weather.gov (free) or OpenWeatherMap
   - **System**: Watchdog timer, sleep mode (auto-dim at night), adaptive brightness
3. Click "Save Configuration"
4. Board restarts with your settings

### Testing Without LED Matrices
**Yes! You can test everything without the LED matrices:**

Run `test_display.py` to verify the Interstate 75 W basics:
- Tests display initialization
- Checks color rendering
- Validates text display
- Simple scrolling test

Test the web portals before connecting matrices:
- **WiFi Setup**: Run `setup_portal.py` to test Access Point mode
- **Configuration Portal**: Run `config_portal.py` to test the settings interface
- Access either via the board's IP address in your browser

All core functionality (WiFi, API calls, configuration, mDNS) works independently of the display hardware.

### Manual Configuration (Alternative)
1. Copy `config.example.py` to `config.py` and edit settings
2. Upload all files to the board
3. Restart and enjoy!

## API Implementation

This project uses **real-time transit APIs** with native MicroPython parsing:

- **Metra**: GTFS-Realtime protobuf feed with custom MicroPython parser (trip updates and service alerts)
- **CTA**: Train Tracker API with native JSON output
- Both APIs work directly on MicroPython without external dependencies

All API calls are fully implemented in [main.py](main.py) with proper error handling, caching, and a lightweight protobuf parser optimized for MicroPython's memory constraints.

## Configuration

Configure all settings through the **web portal** at http://board.local or by editing `config.py`:

### Web Portal (Recommended)
Access http://board.local in your browser for a modern configuration interface:
- **System Status**: View version, uptime, memory, IP address
- **API Settings**: Enter Metra Token and/or CTA API Key
- **Transit & Lines**: Select Metra or CTA, choose lines from dropdowns
- **Rotation Mode**: Direction rotation (1-2 lines) or Station rotation (3+ stations)
- **Stations**: Per-line station selection (auto-filters based on transit type)
- **Dual Line Mode**: Enable secondary line with independent settings (direction mode)
- **Station Rotation**: Configure 3+ stations to cycle through (station mode)
- **Display Settings**: Brightness (10-100%), update intervals, rotation time, train count
- **Actions**: Save, Refresh Status, Restart Board

### Manual Configuration (config.py)
Copy `config.example.py` to `config.py` for manual editing:

### Required Settings
- **WiFi**: SSID and password
- **Metra API Token**: Get from https://www.metrarail.com/developers
- **Station**: Your station stop ID (e.g., "Ravenswood")
- **Lines**: Primary line (e.g., "UP-N") and optional second line

### Display Settings
- **Rotation Time**: Seconds between Inbound/Outbound/Alerts (default: 5)
- **Update Interval**: Seconds between train data API refreshes (default: 30)
- **Alerts Update Interval**: Seconds between service alert checks (default: 180 / 3 minutes)
- **Brightness**: 0.0-1.0 (default: 0.5)

### Feature Toggles
- **Auto-Update**: Automatically install updates from GitHub
- **Service Alerts**: Show service disruption alerts
- **Alert Icons**: Display warning icons next to affected trains
- **Weather**: Display current temperature and weather icon
- **Watchdog Timer**: Auto-recovery from crashes (5s, 8s, or 10s timeout)
- **Sleep Mode**: Dim display at night (configurable hours)
- **Adaptive Brightness**: Auto-adjust brightness based on time of day

### Weather Configuration
- **Service**: Weather.gov (free, US-only) or OpenWeatherMap (requires API key)
- **ZIP Code**: Your location for weather data
- **Display Mode**: Icon only or icon + temperature
- **Update Interval**: 15, 30, or 60 minutes

See `config.example.py` for detailed documentation of all settings.

## Hardware Setup

### Pimoroni Interstate 75 W Specs

- **Microcontroller**: RP2350 (Pico 2 W)
- **WiFi**: 2.4GHz 802.11n
- **Display Support**: Up to 128x64 pixels
- **Power**: USB-C or via HUB75 5V input
- **Buttons**: Boot button, plus 2 user buttons (A, B)
- **Price**: ~$20

### Recommended Matrices

|     Matrix     |   Size   | Pitch | Resolution |   Price  |
|----------------|----------|-------|------------|----------|
| Adafruit 64x32 | 192x96mm | 2.5mm |    64x32   |  $39.99  |

**Total Project Cost: $70-120**

## Display Modes

The Interstate 75 W supports different configurations:

```python
# 128x32 (2 panels side-by-side)
DISPLAY_INTERSTATE75_128X32

# 128x64 (2 panels stacked or 4 panels)
DISPLAY_INTERSTATE75_128X64

# 64x64 (for square panels)
DISPLAY_INTERSTATE75_64X64
```

## Customization

### Adjust Brightness
```python
i75.set_brightness(0.3)  # 0.0 to 1.0
```

### Change Update Interval
```python
UPDATE_INTERVAL = 60  # Update every 60 seconds
```

### Change Colors
```python
COLOR_METRA_GREEN = display.create_pen(0, 155, 58)  # R, G, B
```

## Troubleshooting

### Display doesn't work
- Check HUB75 cable is firmly connected
- Verify 5V power is connected to matrices
- Try different brightness levels
- Check matrix scan rate (most are 1/16)

### WiFi won't connect
- Verify SSID and password
- Pico only supports 2.4GHz WiFi (not 5GHz)
- Check if WiFi is in range

### Code won't run
- Make sure file is named `main.py`
- Check MicroPython firmware is installed
- Look for errors in Thonny's shell window

### "urequests" not found
```python
# Install using Thonny's package manager
# Or copy urequests.py to the Pico
```

## Using Thonny

**Useful shortcuts:**
- **F5**: Run current script
- **Ctrl+D**: Soft reboot
- **Ctrl+C**: Stop running program
- **View > Files**: See Pico's filesystem

**Copy libraries:**
1. Download `urequests.py` (MicroPython requests)
2. Save to Pico as `urequests.py`

## Resources

- **Interstate 75 Guide**: https://learn.pimoroni.com/article/getting-started-with-interstate-75
- **Pimoroni MicroPython**: https://github.com/pimoroni/pimoroni-pico
- **Metra API Docs**: https://metra.com/metra-gtfs-api
- **Quick Start Guide**: [QUICKSTART.md](QUICKSTART.md)
- **Project Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

## Development

### File Structure
- `main.py` - Main application code
- `config.example.py` - Configuration template
- `auto_update.py` - GitHub auto-update system
- `upload.py` - Upload files to board via serial (alternative to Thonny)
- `version.txt` - Current version number
- `test_display.py` - Hardware test script
- `test_wifi.py` - WiFi connectivity test

### Testing
Run test scripts individually to verify hardware and connectivity:
```bash
# Test display
python test_display.py

# Test WiFi
python test_wifi.py
```

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)**.

**You are free to:**
- Use, modify, and share this project for personal use
- Create derivatives for non-commercial purposes

**Under these terms:**
- **Attribution**: Give appropriate credit to the original author
- **NonCommercial**: No commercial use allowed
- **ShareAlike**: Derivatives must use the same license

See [LICENSE](LICENSE) for full details.

