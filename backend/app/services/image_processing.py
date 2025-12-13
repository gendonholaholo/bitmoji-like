"""Image processing utilities for creating composite skin analysis visualizations"""

import io

from PIL import Image, ImageEnhance, ImageFilter


def create_composite_visualization(
    original_image_bytes: bytes,
    masks: dict[str, bytes],
    scores: dict,
) -> bytes:
    """
    Create a composite visualization combining original image with mask overlays

    Args:
        original_image_bytes: Original uploaded image
        masks: Dictionary of mask_name -> PNG bytes
        scores: Score information from YouCam API

    Returns:
        PNG image bytes with composite visualization
    """
    # Load original image
    original = Image.open(io.BytesIO(original_image_bytes)).convert("RGB")

    # Get dimensions
    width, height = original.size

    # Create composite with original as base
    composite = original.copy()

    # Create overlay layer
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Priority masks to overlay (in order of visibility)
    mask_priorities = [
        ("acne", (255, 59, 48, 180)),      # Red - high visibility
        ("pore", (255, 149, 0, 150)),      # Orange
        ("wrinkle", (255, 204, 0, 140)),   # Yellow
        ("texture", (175, 82, 222, 130)),  # Purple
        ("age_spot", (162, 132, 94, 150)), # Brown
        ("eye_bag", (88, 86, 214, 140)),   # Indigo
        ("dark_circle", (94, 92, 230, 140)), # Blue
    ]

    # Apply each mask with appropriate color
    for concern_name, color in mask_priorities:
        # Find matching mask files
        matching_masks = [name for name in masks.keys() if concern_name in name.lower()]

        for mask_name in matching_masks:
            try:
                # Load mask
                mask_img = Image.open(io.BytesIO(masks[mask_name]))

                # Resize if needed
                if mask_img.size != (width, height):
                    mask_img = mask_img.resize((width, height), Image.Resampling.LANCZOS)

                # Convert to grayscale to use as intensity map
                if mask_img.mode != 'L':
                    if mask_img.mode == 'RGBA':
                        # Use alpha channel if available
                        mask_intensity = mask_img.split()[3]
                    else:
                        mask_intensity = mask_img.convert('L')
                else:
                    mask_intensity = mask_img

                # Create colored overlay from mask
                colored_overlay = Image.new("RGBA", (width, height), color)

                # Apply mask intensity to alpha
                colored_overlay.putalpha(mask_intensity)

                # Enhance opacity for better visibility
                alpha = colored_overlay.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(0.8)  # Increase visibility
                colored_overlay.putalpha(alpha)

                # Composite onto overlay layer
                overlay = Image.alpha_composite(overlay, colored_overlay)

            except Exception as e:
                print(f"Warning: Failed to process mask {mask_name}: {e}")
                continue

    # Convert composite to RGBA for blending
    composite = composite.convert("RGBA")

    # Blend overlay with original (additive blend for heatmap effect)
    final = Image.alpha_composite(composite, overlay)

    # Convert to RGB for output
    final_rgb = final.convert("RGB")

    # Apply slight sharpening for better detail
    final_rgb = final_rgb.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))

    # Save to bytes
    output = io.BytesIO()
    final_rgb.save(output, format="JPEG", quality=95)
    return output.getvalue()


def create_simple_composite(
    original_image_bytes: bytes,
    scores: dict,
) -> bytes:
    """
    Create simple composite without masks - just original image
    Fallback when no masks available

    Args:
        original_image_bytes: Original uploaded image
        scores: Score information

    Returns:
        JPEG image bytes
    """
    original = Image.open(io.BytesIO(original_image_bytes)).convert("RGB")

    # Optionally add score text overlay here
    # For now, just return original

    output = io.BytesIO()
    original.save(output, format="JPEG", quality=95)
    return output.getvalue()


# Color configuration for each concern type
CONCERN_COLORS = {
    "acne": (255, 59, 48, 180),       # Red
    "pore": (255, 149, 0, 160),       # Orange
    "wrinkle": (0, 212, 255, 150),    # Cyan
    "texture": (175, 82, 222, 140),   # Purple
    "age_spot": (255, 204, 0, 160),   # Yellow/Gold
    "eye_bag": (88, 86, 214, 150),    # Indigo
    "dark_circle": (94, 92, 230, 150), # Blue
    "oiliness": (255, 215, 0, 140),   # Gold
    "redness": (255, 100, 100, 160),  # Light red
    "firmness": (0, 255, 200, 130),   # Teal
    "radiance": (255, 255, 100, 130), # Light yellow
    "moisture": (100, 200, 255, 130), # Light blue
}


def create_concern_overlay(
    original_image_bytes: bytes,
    masks: dict[str, bytes],
    concern_key: str,
) -> bytes:
    """
    Create an overlay image for a specific concern.

    Args:
        original_image_bytes: Original uploaded image
        masks: Dictionary of mask_name -> PNG bytes
        concern_key: The concern type to visualize (e.g., 'acne', 'pore')

    Returns:
        JPEG image bytes with the concern overlay
    """
    # Load original image
    original = Image.open(io.BytesIO(original_image_bytes)).convert("RGB")
    width, height = original.size

    # Get color for this concern
    color = CONCERN_COLORS.get(concern_key, (0, 212, 255, 150))

    # Create overlay layer
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Find matching mask files for this concern
    matching_masks = [
        name for name in masks.keys()
        if concern_key.lower() in name.lower()
    ]

    for mask_name in matching_masks:
        try:
            # Load mask
            mask_img = Image.open(io.BytesIO(masks[mask_name]))

            # Resize if needed
            if mask_img.size != (width, height):
                mask_img = mask_img.resize((width, height), Image.Resampling.LANCZOS)

            # Convert to grayscale for intensity
            if mask_img.mode != 'L':
                if mask_img.mode == 'RGBA':
                    mask_intensity = mask_img.split()[3]
                else:
                    mask_intensity = mask_img.convert('L')
            else:
                mask_intensity = mask_img

            # Create colored overlay
            colored_overlay = Image.new("RGBA", (width, height), color)
            colored_overlay.putalpha(mask_intensity)

            # Enhance visibility
            alpha = colored_overlay.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(1.0)
            colored_overlay.putalpha(alpha)

            # Composite
            overlay = Image.alpha_composite(overlay, colored_overlay)

        except Exception as e:
            print(f"Warning: Failed to process mask {mask_name}: {e}")
            continue

    # Blend with original
    composite = original.convert("RGBA")
    final = Image.alpha_composite(composite, overlay)
    final_rgb = final.convert("RGB")

    # Save to bytes
    output = io.BytesIO()
    final_rgb.save(output, format="JPEG", quality=95)
    return output.getvalue()


def create_all_concern_overlays(
    original_image_bytes: bytes,
    masks: dict[str, bytes],
) -> dict[str, bytes]:
    """
    Create overlay images for all concerns.

    Args:
        original_image_bytes: Original uploaded image
        masks: Dictionary of mask_name -> PNG bytes

    Returns:
        Dictionary of concern_key -> JPEG image bytes
    """
    result = {}

    # List of concerns to generate overlays for
    concerns = [
        "acne", "pore", "wrinkle", "age_spot",
        "dark_circle", "oiliness", "redness",
        "firmness", "radiance", "texture"
    ]

    for concern in concerns:
        try:
            overlay_bytes = create_concern_overlay(
                original_image_bytes, masks, concern
            )
            result[concern] = overlay_bytes
        except Exception as e:
            print(f"Warning: Failed to create overlay for {concern}: {e}")

    return result
