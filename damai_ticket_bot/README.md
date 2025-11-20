# Damai Ticket Bot (Android/ADB)

This is an automated tool to assist in booking tickets on the Damai (大麦) app using an Android device via ADB.

## Features

- **Auto-Click**: Automatically detects "Buy Now" buttons.
- **OCR Recognition**: Uses `cnocr` to identify buttons on the screen (Purchase, Confirm, Submit).
- **ADB Integration**: Connects directly to your Android phone.
- **Manual Failover**: Pauses on "Submit" or when captchas might appear to allow manual intervention.

## Prerequisites

1. **Python 3.8+**: Ensure Python is installed.
2. **ADB (Android Debug Bridge)**:
   - Install Android SDK Platform-Tools.
   - Ensure `adb` is in your system PATH.
3. **Android Phone**:
   - USB Debugging enabled (Developer Options).
   - Damai App installed and logged in.

## Installation

1. Open a terminal in this folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: `cnocr` requires PyTorch/ONNX Runtime. If installation fails, check [cnocr documentation](https://github.com/breezedeus/cnocr).*

## Usage

1. Connect your Android phone to PC via USB.
2. Verify connection:
   ```bash
   adb devices
   ```
3. Run the bot:
   ```bash
   python main.py
   ```
4. In the GUI:
   - Click **Check Device** to ensure connection.
   - Open the specific event page on your phone.
   - Click **Start Bot**.

## Logic Flow

1. **Search**: Bot continuously takes screenshots looking for "立即购买" (Buy Now).
2. **Select**: Once clicked, it looks for "确定" (Confirm) to select ticket tier.
3. **Submit**: It looks for "提交订单" (Submit Order).
4. **Pause**: After clicking submit, it pauses for you to handle payment or CAPTCHA.

## Disclaimer

This tool is for educational purposes only. Use at your own risk. The author is not responsible for any account bans or failed orders.
