import io
from typing import List, Dict, Optional, Tuple
import numpy as np
from PIL import Image

# Try importing cnocr, handle failure for development/mocking environments
try:
    from cnocr import CnOcr
    CNOCR_AVAILABLE = True
except ImportError:
    CNOCR_AVAILABLE = False
    print("Warning: cnocr not found. OCR features will require a mock or installation.")

class OCRManager:
    def __init__(self):
        self.ocr = None
        if CNOCR_AVAILABLE:
            # Initialize cnocr with a lightweight model if possible
            # 'densenet_lite_136-fc' is a common lightweight model for cnocr
            try:
                self.ocr = CnOcr()
            except Exception as e:
                print(f"Failed to initialize CnOcr: {e}")

    def analyze_screen(self, image_bytes: bytes) -> List[Dict]:
        """
        Analyze the screen image and return a list of recognized text blocks.
        :param image_bytes: PNG binary data from ADB.
        :return: List of dicts like {'text': 'Buy', 'position': box_coords, 'score': 0.9}
        """
        if not self.ocr:
            print("OCR engine not available.")
            return []

        try:
            # Convert bytes to PIL Image then to numpy array
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            img_np = np.array(image)

            # cnocr expects numpy array or path
            results = self.ocr.ocr(img_np)
            return results
        except Exception as e:
            print(f"OCR Analysis failed: {e}")
            return []

    def find_text_center(self, image_bytes: bytes, target_text: str, partial_match: bool = True) -> Optional[Tuple[int, int]]:
        """
        Find the center coordinates of the given text.
        :param image_bytes: PNG binary data.
        :param target_text: The text to look for.
        :param partial_match: If True, matches if target_text is a substring.
        :return: (x, y) or None if not found.
        """
        results = self.analyze_screen(image_bytes)

        for item in results:
            text = item['text']
            # item['position'] is usually [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]

            found = False
            if partial_match:
                if target_text in text:
                    found = True
            else:
                if target_text == text:
                    found = True

            if found:
                box = item['position']
                # Calculate center
                # box is a numpy array of shape (4, 2)
                center_x = int(np.mean(box[:, 0]))
                center_y = int(np.mean(box[:, 1]))
                return (center_x, center_y)

        return None

    def find_any_text_center(self, image_bytes: bytes, target_texts: List[str]) -> Optional[Tuple[int, int]]:
        """Find center of first matching text from a list."""
        results = self.analyze_screen(image_bytes)

        for item in results:
            text = item['text']
            for target in target_texts:
                if target in text:
                    box = item['position']
                    center_x = int(np.mean(box[:, 0]))
                    center_y = int(np.mean(box[:, 1]))
                    return (center_x, center_y)
        return None
