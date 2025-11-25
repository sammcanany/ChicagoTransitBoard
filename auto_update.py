# Auto-Update Module for Metra Transit Board
# Checks GitHub for updates and downloads new version if available

import urequests
import time

# GitHub Configuration - Two URL patterns to check (CDN caching varies)
GITHUB_RAW_URLS = [
    "https://raw.githubusercontent.com/sammcanany/ChicagoTransitBoard/main",
    "https://raw.githubusercontent.com/sammcanany/ChicagoTransitBoard/refs/heads/main"
]

# Files to update
UPDATE_FILES = [
    "main.py",
    "auto_update.py",
    "setup_portal.py",
    "config_portal.py",
    "version.txt"
]

# Files to NEVER update (user configuration)
PROTECTED_FILES = [
    "config.py"  # User's configuration - never overwrite
]

# Track which URL base worked best for downloads
_working_url_base = None

def get_github_raw_url(filename):
    """Get the raw GitHub URL for a file."""
    global _working_url_base
    base = _working_url_base or GITHUB_RAW_URLS[0]
    return f"{base}/{filename}"
    return url

def get_local_version():
    """Read local version from version.txt"""
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except:
        return "0.0.0"

def parse_version(version_str):
    """Parse version string into tuple of integers for comparison.
    Handles versions like '1.7.0', '1.7.1', '2.0.0', etc.
    Returns (major, minor, patch) tuple."""
    try:
        parts = version_str.strip().split('.')
        # Pad with zeros if needed (e.g., "1.7" becomes (1, 7, 0))
        while len(parts) < 3:
            parts.append('0')
        return tuple(int(p) for p in parts[:3])
    except:
        return (0, 0, 0)

def is_newer_version(remote, local):
    """Check if remote version is newer than local version.
    Returns True if remote > local."""
    remote_tuple = parse_version(remote)
    local_tuple = parse_version(local)
    return remote_tuple > local_tuple

def get_remote_version():
    """Fetch version from GitHub, checking both URL patterns.
    Returns the newest version found across all URLs."""
    global _working_url_base
    
    best_version = None
    best_version_tuple = (0, 0, 0)
    best_url_base = None
    
    for url_base in GITHUB_RAW_URLS:
        try:
            url = f"{url_base}/version.txt"
            response = urequests.get(url, timeout=10)
            if response.status_code == 200:
                version = response.text.strip()
                version_tuple = parse_version(version)
                response.close()
                
                # Keep the newest version found
                if version_tuple > best_version_tuple:
                    best_version = version
                    best_version_tuple = version_tuple
                    best_url_base = url_base
            else:
                response.close()
        except Exception as e:
            print(f"Error fetching from {url_base}: {e}")
    
    # Remember which URL had the newest version for downloads
    if best_url_base:
        _working_url_base = best_url_base
    
    return best_version

def download_file(filename, temp=False):
    """Download a file from GitHub

    Args:
        filename: File to download
        temp: If True, save to .tmp file for atomic replacement
    """
    try:
        url = get_github_raw_url(filename)
        print(f"Downloading {filename}...")

        response = urequests.get(url, timeout=30)
        if response.status_code == 200:
            # Save to temporary file first for atomic update
            target = f"{filename}.tmp" if temp else filename

            with open(target, "w") as f:
                f.write(response.text)
            response.close()
            print(f"Downloaded {filename}")
            return True
        else:
            print(f"Failed to download {filename}: HTTP {response.status_code}")
            response.close()
            return False
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return False

def check_for_updates():
    """Check if updates are available and download them"""
    import os

    print("\n=== Checking for updates ===")

    local_version = get_local_version()
    print(f"Local version: {local_version}")

    remote_version = get_remote_version()
    if remote_version is None:
        print("Could not fetch remote version")
        return False

    print(f"Remote version: {remote_version}")

    if is_newer_version(remote_version, local_version):
        print(f"Update available: {local_version} -> {remote_version}")
        print("Downloading updates to temporary files...")

        # Step 1: Download all files to .tmp first (atomic update)
        download_success = True
        for filename in UPDATE_FILES:
            if not download_file(filename, temp=True):
                download_success = False
                print(f"Failed to download {filename}")
                break

        if not download_success:
            print("\n*** UPDATE FAILED ***")
            print("Cleaning up temporary files...")
            # Clean up any .tmp files
            for filename in UPDATE_FILES:
                try:
                    os.remove(f"{filename}.tmp")
                except:
                    pass
            return False

        # Step 2: All files downloaded successfully - now replace originals
        print("All files downloaded. Applying update...")
        for filename in UPDATE_FILES:
            try:
                # Remove old file
                try:
                    os.remove(filename)
                except:
                    pass  # File might not exist

                # Rename .tmp to actual file
                os.rename(f"{filename}.tmp", filename)
                print(f"Updated {filename}")
            except Exception as e:
                print(f"Error replacing {filename}: {e}")
                # At this point, some files are updated - best to continue

        print("\n*** UPDATE COMPLETE ***")
        print("Rebooting in 3 seconds...")
        time.sleep(3)

        try:
            import machine
            machine.reset()
        except ImportError:
            print("Error: machine module not available")
            print("Please manually restart the board")
            return True
    else:
        print("Already up to date!")
        return False

    return True

def auto_update_on_startup():
    """Check for updates on startup (called from main.py)"""
    try:
        check_for_updates()
    except Exception as e:
        print(f"Auto-update error: {e}")
        print("Continuing with current version...")
