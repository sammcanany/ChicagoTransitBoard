#!/usr/bin/env python3
"""
Upload files to MicroPython board via serial connection
Requires: pip install pyserial
"""

import serial
import serial.tools.list_ports
import time
import os
import sys
import hashlib
import json

# Files to upload
FILES_TO_UPLOAD = [
    "main.py",
    "setup_portal.py",
    "config_portal.py",
    "config_portal_template.html",
    "auto_update.py",
    "version.txt",
]

# Cache file to store file hashes
CACHE_FILE = ".upload_cache.json"

# Required MicroPython libraries to install via mip
REQUIRED_LIBS = [
    "github:cbrand/micropython-mdns",
]

def install_libraries(ser):
    """Install required MicroPython libraries via mip"""
    print("\nInstalling required libraries...")
    print("-" * 50)
    
    for lib in REQUIRED_LIBS:
        print(f"Installing {lib}...", end=" ", flush=True)
        try:
            # Enter raw REPL mode
            ser.write(b'\x01')  # Ctrl-A
            time.sleep(0.1)
            ser.reset_input_buffer()
            
            # Run mip install
            cmd = f'import mip; mip.install("{lib}")\r\n'
            ser.write(cmd.encode('utf-8'))
            ser.write(b'\x04')  # Execute
            
            # Wait for install to complete (can take a while)
            time.sleep(10)
            
            # Read output
            output = ser.read(ser.in_waiting or 1).decode('utf-8', errors='ignore')
            
            # Exit raw REPL
            ser.write(b'\x02')
            time.sleep(0.1)
            ser.reset_input_buffer()
            
            if "Error" in output or "error" in output:
                print(f"\u2717 (may already be installed)")
            else:
                print("\u2713")
                
        except Exception as e:
            print(f"\u2717 Error: {e}")
            # Try to recover
            ser.write(b'\x03\x03\x02')
            time.sleep(0.1)
    
    print("-" * 50)

def calculate_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None

def load_cache():
    """Load the upload cache"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache):
    """Save the upload cache"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass

def file_needs_upload(filepath, cache):
    """Check if file needs to be uploaded"""
    if not os.path.exists(filepath):
        return False

    current_hash = calculate_file_hash(filepath)
    if current_hash is None:
        return True

    cached_hash = cache.get(filepath)
    return cached_hash != current_hash

def find_board():
    """Find the MicroPython board serial port"""
    ports = serial.tools.list_ports.comports()

    # Look for common MicroPython device descriptions
    for port in ports:
        # Raspberry Pi Pico shows up as "USB Serial Device" on Windows
        if "USB Serial" in port.description or "Pico" in port.description:
            return port.device

    # If not found, print available ports
    print("Available ports:")
    for port in ports:
        print(f"  {port.device}: {port.description}")

    return None

def upload_file(ser, local_path, remote_path=None):
    """Upload a single file to the board using chunked binary writes"""
    if remote_path is None:
        remote_path = os.path.basename(local_path)

    print(f"Uploading {local_path} -> {remote_path}...", end=" ", flush=True)

    try:
        with open(local_path, 'rb') as f:
            content = f.read()

        # Enter raw REPL mode
        ser.write(b'\x01')  # Ctrl-A: raw REPL mode
        time.sleep(0.1)
        ser.reset_input_buffer()

        # Open file for writing
        cmd = f'f=open("{remote_path}","wb")\r\n'
        ser.write(cmd.encode('utf-8'))
        ser.write(b'\x04')  # Execute
        time.sleep(0.1)
        ser.reset_input_buffer()

        # Write in small chunks to avoid memory issues
        chunk_size = 256  # Small chunks to avoid memory pressure
        total_chunks = (len(content) + chunk_size - 1) // chunk_size
        
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            # Convert chunk to hex representation for safe transmission
            hex_data = chunk.hex()
            
            ser.write(b'\x01')  # Enter raw REPL
            time.sleep(0.02)
            
            cmd = f'f.write(bytes.fromhex("{hex_data}"))\r\n'
            ser.write(cmd.encode('utf-8'))
            ser.write(b'\x04')  # Execute
            time.sleep(0.02)
            ser.reset_input_buffer()

        # Close file
        ser.write(b'\x01')
        time.sleep(0.02)
        ser.write(b'f.close()\r\n')
        ser.write(b'\x04')
        time.sleep(0.1)

        # Exit raw REPL mode
        ser.write(b'\x02')  # Ctrl-B: exit raw REPL
        time.sleep(0.1)
        ser.reset_input_buffer()

        print("✓")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        # Try to clean up
        try:
            ser.write(b'\x03\x03')  # Ctrl-C
            ser.write(b'\x02')  # Ctrl-B
        except:
            pass
        return False

def main():
    print("MicroPython File Uploader (Sync Mode)")
    print("=" * 50)

    # Load cache
    cache = load_cache()
    
    # Check if this is first upload (no cache exists)
    first_upload = len(cache) == 0

    # Check which files need uploading
    files_to_upload = []
    skipped_files = []

    for filename in FILES_TO_UPLOAD:
        if not os.path.exists(filename):
            print(f"Missing: {filename}")
            continue

        if file_needs_upload(filename, cache):
            files_to_upload.append(filename)
        else:
            skipped_files.append(filename)

    if not files_to_upload:
        print("\n All files up to date - nothing to upload")
        print("\nTo force upload all files, delete .upload_cache.json")
        # Even if nothing changed, still open serial monitor
        files_to_upload = []

    print(f"\nFiles to upload: {len(files_to_upload)}")
    for f in files_to_upload:
        print(f"  • {f}")

    if skipped_files:
        print(f"\nSkipping {len(skipped_files)} unchanged file(s)")

    # Find the board
    port = find_board()
    if not port:
        print("\nError: Could not find MicroPython board")
        print("Please check that:")
        print("  1. The board is connected via USB")
        print("  2. Drivers are installed")
        sys.exit(1)

    print(f"\nFound board on {port}")

    # Connect to board
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(0.5)

        # Send Ctrl-C to interrupt any running program
        ser.write(b'\x03\x03')  # Ctrl-C twice
        time.sleep(0.5)

        # Clear any pending input
        ser.reset_input_buffer()
        
        # Install libraries on first upload
        if first_upload:
            install_libraries(ser)

        if files_to_upload:
            print("\nUploading files...")
            print("-" * 50)

            success_count = 0
            fail_count = 0
            new_cache = cache.copy()

            for filename in files_to_upload:
                if upload_file(ser, filename):
                    success_count += 1
                    # Update cache with new hash
                    new_cache[filename] = calculate_file_hash(filename)
                else:
                    fail_count += 1

            print("-" * 50)
            print(f"\nUpload complete: {success_count} succeeded, {fail_count} failed")

            # Save updated cache
            if success_count > 0:
                save_cache(new_cache)

        # Always soft reset the board before serial monitor
        print("\nResetting board...")
        ser.write(b'\x04')  # Ctrl-D: soft reset
        time.sleep(1)

        # Read and print initial output
        output = ser.read(ser.in_waiting or 1).decode('utf-8', errors='ignore')
        if output:
            print("\nBoard output:")
            print(output)

        # Enter serial monitor mode
        print("\n" + "=" * 50)
        print("Serial Monitor (Press Ctrl+C to exit)")
        print("=" * 50)

        try:
            while True:
                # Check for data from board
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    print(data, end='', flush=True)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\nExiting serial monitor...")

        ser.close()

    except serial.SerialException as e:
        print(f"\nError: Could not connect to {port}")
        print(f"Details: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
