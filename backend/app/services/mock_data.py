"""Mock data for YouCam bypass mode - enables testing without consuming API tokens"""

import io

import numpy as np
from PIL import Image, ImageDraw


def generate_mock_scores() -> dict:
    """
    Generate mock skin analysis scores matching YouCam API structure.

    Returns realistic but fake scores for all skin concerns to test
    MediaPipe visualization and AI analysis generation.

    Structure matches real YouCam API response format:
    - Each concern has {"raw_score": float, "ui_score": float}
    - "all" has {"score": float}
    - "skin_age" is just an integer
    """
    return {
        # Individual concerns - match YouCam API structure
        "acne": {"raw_score": 45.2, "ui_score": 45.2},
        "wrinkle": {"raw_score": 62.8, "ui_score": 62.8},
        "pore": {"raw_score": 55.3, "ui_score": 55.3},
        "age_spot": {"raw_score": 71.4, "ui_score": 71.4},
        "oiliness": {"raw_score": 42.1, "ui_score": 42.1},
        "radiance": {"raw_score": 68.9, "ui_score": 68.9},
        "texture": {"raw_score": 59.7, "ui_score": 59.7},
        "redness": {"raw_score": 73.5, "ui_score": 73.5},
        "firmness": {"raw_score": 66.2, "ui_score": 66.2},
        "moisture": {"raw_score": 51.8, "ui_score": 51.8},
        "dark_circle_v2": {"raw_score": 48.3, "ui_score": 48.3},
        "eye_bag": {"raw_score": 70.1, "ui_score": 70.1},

        # Overall metrics
        "all": {"score": 78.0},
        "skin_age": 28,
    }


def create_debug_mask(width: int, height: int, concern_name: str) -> bytes:
    """
    Create a simple debug mask image for visualization testing.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        concern_name: Name of the concern (for labeling)

    Returns:
        PNG bytes of debug mask with simple patterns
    """
    # Create transparent image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Define colors for different concern types
    color_map = {
        "acne": (255, 100, 100, 150),      # Red
        "wrinkle": (200, 150, 255, 150),   # Purple
        "pore": (100, 200, 255, 150),      # Cyan
        "age_spot": (255, 200, 100, 150),  # Orange
        "oiliness": (255, 255, 100, 150),  # Yellow
        "radiance": (255, 200, 200, 150),  # Pink
        "texture": (150, 255, 150, 150),   # Light green
        "redness": (255, 50, 50, 150),     # Bright red
        "firmness": (200, 200, 255, 150),  # Light blue
        "moisture": (100, 255, 255, 150),  # Aqua
        "dark_circle_v2": (150, 100, 200, 150),  # Dark purple
        "eye_bag": (180, 150, 200, 150),   # Lavender
    }

    color = color_map.get(concern_name, (150, 150, 150, 150))

    # Draw some simple patterns to simulate problem areas
    # Pattern 1: Random scattered dots (simulating problem spots)
    np.random.seed(hash(concern_name) % 2**32)  # Consistent random pattern per concern
    for _ in range(30):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        radius = np.random.randint(5, 15)
        draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)], fill=color)

    # Pattern 2: Some lines (for wrinkles, texture, etc.)
    if concern_name in ["wrinkle", "texture", "firmness"]:
        for i in range(5):
            y_pos = int(height * (0.3 + i * 0.1))
            draw.line([(0, y_pos), (width, y_pos)], fill=color, width=2)

    # Add label
    try:
        # Draw label background
        label = f"[MOCK] {concern_name}"
        bbox = draw.textbbox((0, 0), label)
        label_width = bbox[2] - bbox[0] + 20
        label_height = bbox[3] - bbox[1] + 10
        draw.rectangle([(10, 10), (10 + label_width, 10 + label_height)],
                      fill=(0, 0, 0, 180))
        draw.text((20, 15), label, fill=(255, 255, 255, 255))
    except Exception:
        pass  # Font rendering might fail in some environments

    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def generate_mock_masks(image_width: int = 640, image_height: int = 480) -> dict[str, bytes]:
    """
    Generate mock mask images for all skin concerns.

    Args:
        image_width: Width of the original image
        image_height: Height of the original image

    Returns:
        Dictionary mapping concern names to PNG mask bytes
    """
    concerns = [
        "acne", "wrinkle", "pore", "age_spot", "oiliness",
        "radiance", "texture", "redness", "firmness", "moisture",
        "dark_circle_v2", "eye_bag"
    ]

    masks = {}
    for concern in concerns:
        # Create mask with consistent naming pattern
        mask_name = f"sd_{concern}_output_all.png"
        masks[mask_name] = create_debug_mask(image_width, image_height, concern)

    return masks
