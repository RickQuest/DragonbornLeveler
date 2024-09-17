import os
import subprocess
import platform
import urllib.request
from pathlib import Path
import ctypes
import sys
import json
import tempfile
import time

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart the script with administrator privileges if not already running as admin."""
    if not is_admin():
        print("Requesting admin privileges...")
        # Relaunch the script with administrator rights
        try:
            params = " ".join([f'"{arg}"' for arg in sys.argv])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        except Exception as e:
            print(f"Failed to elevate privileges: {e}")
        sys.exit()  # Exit the current instance to let the elevated one run

def is_tesseract_installed():
    """Check if Tesseract is available in the system and executable."""
    try:
        # Try to execute `tesseract -v` to verify installation
        result = subprocess.run(["tesseract", "-v"], capture_output=True, check=True, text=True)
        print(f"Tesseract is installed and available: {result.stdout.splitlines()[0]}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_latest_tesseract_release_url():
    """Fetch the latest release download URL for Tesseract from GitHub."""
    api_url = "https://api.github.com/repos/UB-Mannheim/tesseract/releases/latest"

    try:
        print("Fetching the latest Tesseract release information...")
        with urllib.request.urlopen(api_url) as response:
            release_data = json.loads(response.read().decode())
            # Look for the asset that is the Windows installer
            for asset in release_data["assets"]:
                if asset["name"].endswith(".exe"):
                    print(f"Latest Tesseract release: {asset['name']}")
                    return asset["browser_download_url"]
        print("No suitable Tesseract installer found.")
        return None
    except Exception as e:
        print(f"Error fetching the latest release: {e}")
        return None

def install_tesseract_windows():
    """Download and install the latest Tesseract release from GitHub."""
    # Fetch the latest release URL dynamically
    tesseract_url = get_latest_tesseract_release_url()
    print(f'Tesseract download link : {tesseract_url}')
    if not tesseract_url:
        print("Failed to get the latest Tesseract release URL.")
        return None

    # Path to save the installer in the system's temporary folder
    installer_path = Path(tempfile.gettempdir()) / "tesseract_installer.exe"

    try:
        print(f"Downloading Tesseract installer from: {tesseract_url}...")
        urllib.request.urlretrieve(tesseract_url, installer_path)

        print("Running Tesseract installer...")
        # Run the installer with elevated privileges
        run_as_admin_command(f'"{installer_path}" /S')

        print("Tesseract installed successfully.")

        # Check if Tesseract is installed after the installer runs
        tesseract_path = wait_for_tesseract_installation()
        return tesseract_path

    except Exception as e:
        print(f"Error during installation: {e}")
        return None

def run_as_admin_command(command):
    """Run a command as an administrator with a UAC prompt."""
    try:
        params = f'/c {command}'
        # Elevate the command and execute it with administrator rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", params, None, 1)
    except Exception as e:
        print(f"Error executing elevated command: {e}")

def wait_for_tesseract_installation(timeout=60, interval=5):
    """Wait for Tesseract installation to complete by checking its default path."""
    tesseract_path = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    start_time = time.time()

    while time.time() - start_time < timeout:
        if tesseract_path.exists():
            print(f"Tesseract installed at: {tesseract_path}")
            return tesseract_path
        print(f"Waiting for Tesseract installation... ({int(time.time() - start_time)} seconds elapsed)")
        time.sleep(interval)

    print("Tesseract installation timed out or not found.")
    return None

def update_system_path(tesseract_dir):
    """Add the Tesseract directory to the system-wide PATH environment variable."""
    try:
        # Get the current system PATH
        result = subprocess.run(r'reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path',
                                capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            system_path = result.stdout.split("REG_SZ")[1].strip()

            if tesseract_dir not in system_path:
                # Create the new path by appending tesseract_dir
                new_path = f"{system_path};{tesseract_dir}"
                # Run the registry update with elevated privileges
                run_as_admin_command(rf'reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path /t REG_SZ /d "{new_path}" /f')
                print(f"Successfully added {tesseract_dir} to the system PATH.")
            else:
                print(f"{tesseract_dir} is already in the system PATH.")
        else:
            print("Failed to retrieve the system PATH.")
    except Exception as e:
        print(f"Error updating system PATH: {str(e)}")

def install_and_set_tesseract_path():
    """Check for Tesseract installation and set the system-wide environment variable."""
    # Check if Tesseract is installed and executable
    if is_tesseract_installed():
        print("Tesseract is already installed and working.")
    else:
        print("Tesseract is not installed or not functional. Proceeding with installation...")
        tesseract_path = install_tesseract_windows()
        if tesseract_path:
            tesseract_dir = str(Path(tesseract_path).parent)
            update_system_path(tesseract_dir)
        else:
            print("Could not install or find Tesseract.")

def main():
    os_name = platform.system()

    if os_name == "Windows":
        install_and_set_tesseract_path()
    else:
        print("This script is designed for Windows installation of Tesseract.")

if __name__ == "__main__":
    main()
