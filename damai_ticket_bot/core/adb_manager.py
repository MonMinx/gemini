import subprocess
import os
import time
from typing import Optional, Tuple

class ADBManager:
    def __init__(self, device_id: Optional[str] = None):
        """
        Initialize ADB Manager.
        :param device_id: Optional specific device ID. If None, uses the first connected device.
        """
        self.device_id = device_id
        self.adb_path = "adb"  # Assumes adb is in PATH.

    def _run_command(self, cmd: list) -> str:
        """Run an ADB command and return the output."""
        base_cmd = [self.adb_path]
        if self.device_id:
            base_cmd.extend(["-s", self.device_id])

        full_cmd = base_cmd + cmd
        try:
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"ADB Command Error: {e}")
            print(f"Stderr: {e.stderr}")
            return ""
        except FileNotFoundError:
            print("Error: ADB executable not found. Please ensure Android SDK Platform-Tools are installed and in PATH.")
            return ""

    def get_connected_devices(self) -> list:
        """Get a list of connected device IDs."""
        output = self._run_command(["devices"])
        devices = []
        for line in output.split('\n')[1:]:  # Skip header
            if '\tdevice' in line:
                devices.append(line.split('\t')[0])
        return devices

    def connect(self) -> bool:
        """Check connection or connect to the first available device."""
        devices = self.get_connected_devices()
        if not devices:
            print("No devices found.")
            return False

        if not self.device_id:
            self.device_id = devices[0]
            print(f"Connected to default device: {self.device_id}")
        elif self.device_id not in devices:
             print(f"Device {self.device_id} not found in connected devices.")
             return False

        return True

    def take_screenshot(self) -> Optional[bytes]:
        """
        Take a screenshot and return the binary data (PNG).
        Uses `adb exec-out screencap -p` which is faster than saving to file.
        """
        base_cmd = [self.adb_path]
        if self.device_id:
            base_cmd.extend(["-s", self.device_id])

        cmd = base_cmd + ["exec-out", "screencap", "-p"]

        try:
            # Using Popen/communicate to handle binary output properly
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                print(f"Screenshot failed: {stderr.decode('utf-8', errors='ignore')}")
                return None

            return stdout
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None

    def tap(self, x: int, y: int):
        """Simulate a tap at coordinates (x, y)."""
        self._run_command(["shell", "input", "tap", str(x), str(y)])

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int = 300):
        """Simulate a swipe gesture."""
        self._run_command(["shell", "input", "swipe", str(start_x), str(start_y), str(end_x), str(end_y), str(duration_ms)])

    def input_text(self, text: str):
        """Input text (doesn't support special chars well usually)."""
        self._run_command(["shell", "input", "text", text])

    def press_back(self):
        """Press the Back button."""
        self._run_command(["shell", "input", "keyevent", "4"])
