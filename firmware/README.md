# Firmware Directory

This directory contains custom MicroPython firmware builds for the Pimoroni Interstate 75 W (RP2350).

## Custom Firmware Features

The custom firmware in this directory has been modified to support mDNS functionality:

- **LWIP_MDNS_RESPONDER disabled**: The built-in LwIP mDNS responder has been disabled to allow the `micropython-mdns` library to bind to port 5353
- **Interstate75 support**: Includes all Pimoroni libraries (picographics, hub75, etc.)
- **Full WiFi support**: CYW43 driver for WiFi connectivity

## File

- `i75w_rp2350.uf2` - Custom MicroPython firmware for Interstate 75 W (RP2350) with mDNS support

## Installation

1. Hold the **BOOT** button on the Interstate 75 W while connecting it to USB
2. The board will appear as a USB drive (RPI-RP2)
3. Copy `i75w_rp2350.uf2` to the drive
4. The board will automatically reboot with the new firmware

## After Flashing

After flashing the firmware, you'll need to:

1. Install the Interstate75 library (if not already included):
   ```python
   import mip
   mip.install("github:pimoroni/pimoroni-pico/micropython/modules/interstate75")
   ```

2. Install the micropython-mdns library for mDNS support:
   ```python
   import mip
   mip.install("github:cbrand/micropython-mdns")
   ```

## Building Custom Firmware

If you need to rebuild the firmware, see the build instructions in the main repository documentation.

The firmware was built from the [Pimoroni Interstate75 repository](https://github.com/pimoroni/interstate75) with modifications to disable LWIP_MDNS_RESPONDER in:
- `micropython/ports/rp2/lwip_inc/lwipopts.h`
- `micropython/extmod/lwip-include/lwipopts_common.h`
