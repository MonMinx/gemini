import time
import threading
from enum import Enum
from typing import Callable, Optional
from .adb_manager import ADBManager
from .ocr_manager import OCRManager

class BotState(Enum):
    IDLE = 0
    SEARCHING = 1    # Searching for "Buy" button
    SELECTING = 2    # Selecting ticket/seat
    SUBMITTING = 3   # Submitting order
    PAUSED = 99      # Paused (e.g., for manual captcha)

class DamaiBot:
    def __init__(self, adb: ADBManager, ocr: OCRManager):
        self.adb = adb
        self.ocr = ocr
        self.state = BotState.IDLE
        self.running = False
        self.thread = None
        self.log_callback: Optional[Callable[[str], None]] = None

        # Configuration
        self.refresh_interval = 0.1  # Time between checks in seconds
        self.keywords = {
            "buy": ["立即购买", "立即预订", "特惠购买", "缺货登记"], # "缺货登记" triggers refresh
            "confirm": ["确定", "选座购买"], # Popup confirmation
            "submit": ["提交订单"]
        }

        # Internal tracking
        self.target_seat_index = 0 # Default to first option if needed

    def set_logger(self, callback):
        self.log_callback = callback

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(f"[BOT] {message}")

    def start(self):
        if self.running:
            return

        # Check connection first
        if not self.adb.connect():
            self.log("Error: Could not connect to device.")
            return

        self.running = True
        self.state = BotState.SEARCHING
        self.thread = threading.Thread(target=self._run_loop)
        self.thread.daemon = True # Kill if main exits
        self.thread.start()
        self.log("Bot started.")

    def stop(self):
        self.running = False
        self.state = BotState.IDLE
        self.log("Bot stopped.")

    def _run_loop(self):
        while self.running:
            try:
                if self.state == BotState.SEARCHING:
                    self._step_search()
                elif self.state == BotState.SELECTING:
                    self._step_select()
                elif self.state == BotState.SUBMITTING:
                    self._step_submit()
                elif self.state == BotState.PAUSED:
                    time.sleep(1)

                time.sleep(self.refresh_interval)
            except Exception as e:
                self.log(f"Error in loop: {e}")
                time.sleep(1)

    def _capture_and_find(self, targets):
        screenshot = self.adb.take_screenshot()
        if not screenshot:
            return None, None

        # OCR analysis
        coords = self.ocr.find_any_text_center(screenshot, targets)
        return coords, screenshot

    def _step_search(self):
        """
        Look for "Buy" button.
        If "缺货登记" (Out of stock) is found, we might need to refresh logic
        (simulated by just clicking it or refreshing page - simplistic for now).
        """
        self.log("Searching for buy button...")
        coords, _ = self._capture_and_find(self.keywords["buy"])

        if coords:
            self.log(f"Found buy button at {coords}. Clicking...")
            self.adb.tap(coords[0], coords[1])
            self.state = BotState.SELECTING
            # Give UI time to transition
            time.sleep(0.5)
        else:
            # self.log("Buy button not found.")
            pass

    def _step_select(self):
        """
        On the selection screen (Ticket tiers, dates).
        Usually need to click "Confirm" or specific tier.
        """
        self.log("In selection screen...")

        # Try to find "Confirm" button first (if selections are already default)
        coords, _ = self._capture_and_find(self.keywords["confirm"])

        if coords:
            self.log(f"Found confirm/select button at {coords}. Clicking...")
            self.adb.tap(coords[0], coords[1])
            self.state = BotState.SUBMITTING
            time.sleep(0.5)
            return

        # TODO: Add logic to select specific ticket tier if "Confirm" isn't active
        # For now, we assume user pre-selected or default is fine,
        # or we blindly tap a common area if OCR fails?
        # Better to stick to OCR for "Confirm" for safety.

    def _step_submit(self):
        """
        Final screen: Submit Order.
        """
        self.log("In submit screen...")
        coords, _ = self._capture_and_find(self.keywords["submit"])

        if coords:
            self.log(f"Found Submit button at {coords}. CLICKING!!!")
            self.adb.tap(coords[0], coords[1])

            # After submit, we might hit a captcha or success.
            # We can pause here or keep clicking if it didn't register.
            # Let's pause to allow manual check
            self.log("Order submitted (hopefully). Pausing for manual check.")
            self.state = BotState.PAUSED
        else:
            # If we don't see submit, maybe we are still in previous screen?
            # Or maybe we need to scroll?
            pass
