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
