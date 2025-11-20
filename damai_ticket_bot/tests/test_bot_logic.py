import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Adjust path to import core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.bot_engine import DamaiBot, BotState
from core.adb_manager import ADBManager
from core.ocr_manager import OCRManager

class TestDamaiBot(unittest.TestCase):

    def setUp(self):
        self.mock_adb = MagicMock(spec=ADBManager)
        self.mock_ocr = MagicMock(spec=OCRManager)
        self.bot = DamaiBot(self.mock_adb, self.mock_ocr)
        # Disable threading for testing logic step-by-step
        self.bot.refresh_interval = 0

    def test_initial_state(self):
        self.assertEqual(self.bot.state, BotState.IDLE)

    def test_start_fails_if_no_device(self):
        self.mock_adb.connect.return_value = False
        self.bot.start()
        self.assertFalse(self.bot.running)

    def test_search_buy_button_found(self):
        # Setup
        self.bot.state = BotState.SEARCHING
        self.mock_adb.take_screenshot.return_value = b'fake_image_data'
        # Mock OCR finding "立即购买" at (100, 200)
        self.mock_ocr.find_any_text_center.return_value = (100, 200)

        # Act
        self.bot._step_search()

        # Assert
        self.mock_adb.tap.assert_called_with(100, 200)
        self.assertEqual(self.bot.state, BotState.SELECTING)

    def test_search_buy_button_not_found(self):
        # Setup
        self.bot.state = BotState.SEARCHING
        self.mock_adb.take_screenshot.return_value = b'fake_image_data'
        self.mock_ocr.find_any_text_center.return_value = None

        # Act
        self.bot._step_search()

        # Assert
        self.mock_adb.tap.assert_not_called()
        self.assertEqual(self.bot.state, BotState.SEARCHING)

    def test_select_confirm_button_found(self):
        # Setup
        self.bot.state = BotState.SELECTING
        self.mock_adb.take_screenshot.return_value = b'fake_image_data'
        # Mock OCR finding "确定" at (300, 400)
        self.mock_ocr.find_any_text_center.return_value = (300, 400)

        # Act
        self.bot._step_select()

        # Assert
        self.mock_adb.tap.assert_called_with(300, 400)
        self.assertEqual(self.bot.state, BotState.SUBMITTING)

    def test_submit_order_found(self):
        # Setup
        self.bot.state = BotState.SUBMITTING
        self.mock_adb.take_screenshot.return_value = b'fake_image_data'
        # Mock OCR finding "提交订单" at (500, 600)
        self.mock_ocr.find_any_text_center.return_value = (500, 600)

        # Act
        self.bot._step_submit()

        # Assert
        self.mock_adb.tap.assert_called_with(500, 600)
        self.assertEqual(self.bot.state, BotState.PAUSED)

if __name__ == '__main__':
    unittest.main()
