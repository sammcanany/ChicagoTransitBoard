# Chicago Transit Board

Real-time Metra and CTA train arrivals on a **Pimoroni Interstate 75 W** with HUB75 LED matrices.

![Platform](https://img.shields.io/badge/Platform-RP2350-red) ![MicroPython](https://img.shields.io/badge/MicroPython-1.27-blue) ![License](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-orange)

## Features

- **Web Configuration Portal** at http://board.local - no code editing needed
- **WiFi Setup Portal** - creates its own network for first-time setup
- **Real-time Arrivals** - Metra GTFS-RT and CTA Train Tracker APIs
- **Line Colors** - Official brand colors for each transit line
- **Service Alerts** - Shows disruptions with warning icons
- **Weather Display** - Temperature and conditions (Weather.gov or OpenWeatherMap)
- **Auto-Update** - Downloads updates from GitHub automatically
- **PWA Support** - Add to home screen on iOS for app-like experience

### Display Modes
- **Single Line** - Full screen for one transit line
- **Dual Line** - Split screen for two lines (mix Metra + CTA!)
- **Station Rotation** - Cycle through 3+ stations

## Hardware

| Component | Description | Price |
|-----------|-------------|-------|
| [Pimoroni Interstate 75 W](https://shop.pimoroni.com/products/interstate-75-w) | RP2350 controller with WiFi | ~$20 |
| 2x HUB75 64x32 LED Matrix | Any pitch (P2.5, P3, P4, etc.) | ~$40 each |
| 5V 10A Power Supply | Powers the LED panels | ~$15 |

**Total: ~$115**

## Quick Start

See **[QUICKSTART.md](QUICKSTART.md)** for detailed instructions.

### TL;DR
1. Flash [Pimoroni MicroPython firmware](https://github.com/pimoroni/interstate75/releases/latest)
2. Run `python upload.py` to upload files and install libraries
3. Connect to "ChicagoTransitBoard" WiFi (password: `setup1234`)
4. Open http://192.168.4.1 and enter your WiFi credentials
5. Access http://board.local to configure transit lines, API keys, and settings

## Configuration

All settings are managed through the web portal at **http://board.local**:

- **API Keys** - Metra token and/or CTA API key
- **Transit Lines** - Select lines and stations from dropdowns
- **Display Settings** - Brightness, update intervals, rotation timing
- **Weather** - Enable with ZIP code (Weather.gov is free)
- **System** - Watchdog timer, sleep mode, auto-update frequency

Alternatively, copy `config.example.py` to `config.py` and edit manually.

## API Keys

| Service | Get Key From |
|---------|--------------|
| Metra | https://metra.com/developers |
| CTA | https://www.transitchicago.com/developers/ |
| OpenWeatherMap (optional) | https://openweathermap.org/api |

## File Structure

```
main.py                    # Main application
config.example.py          # Configuration template
config_portal.py           # Web configuration server
config_portal_template.html # Web UI
setup_portal.py            # WiFi setup AP mode
auto_update.py             # GitHub auto-updater
upload.py                  # Serial upload tool
version.txt                # Version number
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Display blank | Check 5V power to panels, verify HUB75 cable |
| WiFi won't connect | Must be 2.4GHz network (not 5GHz) |
| board.local not working | Use IP address, or install Bonjour (Windows) |
| API errors | Verify API keys in config portal |
| Memory errors | Reduce update interval or number of trains |

## Resources

- [Interstate 75 Guide](https://learn.pimoroni.com/article/getting-started-with-interstate-75)
- [Pimoroni MicroPython](https://github.com/pimoroni/pimoroni-pico)
- [Metra GTFS API](https://metra.com/metra-gtfs-api)
- [CTA Train Tracker API](https://www.transitchicago.com/developers/traintracker/)

## License

**CC BY-NC-SA 4.0** - Free for personal, non-commercial use with attribution.

See [LICENSE](LICENSE) for details.

