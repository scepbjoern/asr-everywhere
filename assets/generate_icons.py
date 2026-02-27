"""Generate tray icons for ASR Everywhere."""

from PIL import Image, ImageDraw

# Icon sizes for .ico files (multi-resolution)
SIZES = [16, 32, 48, 64, 256]


def create_microphone_icon(size: int, color: str, bg_color: str | None = None) -> Image.Image:
    """Create a microphone icon.

    Args:
        size: Icon size in pixels
        color: Main color (hex)
        bg_color: Optional background color

    Returns:
        PIL Image
    """
    # Create image with transparency
    mode = "RGBA"
    bg = (0, 0, 0, 0) if bg_color is None else tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5)) + (255,)
    
    image = Image.new(mode, (size, size), bg)
    draw = ImageDraw.Draw(image)

    # Parse color
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    fill = (r, g, b, 255)

    # Scale factor
    s = size / 64.0

    # Draw microphone body (rounded rectangle)
    mic_width = int(20 * s)
    mic_height = int(32 * s)
    mic_x = (size - mic_width) // 2
    mic_y = int(12 * s)
    
    # Microphone body (rounded rectangle approximation)
    draw.rounded_rectangle(
        [mic_x, mic_y, mic_x + mic_width, mic_y + mic_height],
        radius=int(10 * s),
        fill=fill,
    )

    # Microphone stand (horizontal line at bottom)
    stand_y = mic_y + mic_height + int(2 * s)
    stand_width = int(28 * s)
    stand_x = (size - stand_width) // 2
    stand_height = int(3 * s)
    draw.rectangle(
        [stand_x, stand_y, stand_x + stand_width, stand_y + stand_height],
        fill=fill,
    )

    # Microphone base (vertical line)
    base_x = (size) // 2 - int(1.5 * s)
    base_y = stand_y + stand_height
    base_height = int(8 * s)
    draw.rectangle(
        [base_x, base_y, base_x + int(3 * s), base_y + base_height],
        fill=fill,
    )

    # Microphone arc (curved lines on sides)
    arc_y = mic_y + mic_height // 2
    arc_radius = int(14 * s)
    # Left arc
    draw.arc(
        [mic_x - arc_radius + int(4*s), arc_y - arc_radius,
         mic_x - arc_radius + int(4*s) + arc_radius * 2, arc_y + arc_radius],
        start=270, end=90,
        fill=fill,
        width=max(1, int(2 * s)),
    )

    return image


def create_recording_icon(size: int, color: str) -> Image.Image:
    """Create a recording indicator icon (filled circle with pulse effect).

    Args:
        size: Icon size in pixels
        color: Main color (hex)

    Returns:
        PIL Image
    """
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Parse color
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)

    # Scale factor
    s = size / 64.0

    # Outer pulse ring (lighter, larger)
    margin_outer = int(4 * s)
    outer_color = (r, g, b, 100)
    draw.ellipse(
        [margin_outer, margin_outer, size - margin_outer, size - margin_outer],
        fill=outer_color,
    )

    # Inner filled circle
    margin = int(12 * s)
    fill = (r, g, b, 255)
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=fill,
    )

    # Center dot (white)
    center_margin = int(24 * s)
    draw.ellipse(
        [center_margin, center_margin, size - center_margin, size - center_margin],
        fill=(255, 255, 255, 255),
    )

    return image


def create_processing_icon(size: int, color: str) -> Image.Image:
    """Create a processing indicator icon (spinning dots).

    Args:
        size: Icon size in pixels
        color: Main color (hex)

    Returns:
        PIL Image
    """
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Parse color
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)

    # Scale factor
    s = size / 64.0
    center = size // 2
    radius = int(20 * s)
    dot_radius = int(6 * s)

    # Draw 3 dots in a circular pattern with varying opacity
    import math
    for i, angle in enumerate([90, 210, 330]):
        rad = math.radians(angle)
        x = center + int(radius * math.cos(rad))
        y = center - int(radius * math.sin(rad))
        
        # Varying opacity for animation effect
        alpha = 255 - (i * 60)
        fill = (r, g, b, alpha)
        
        draw.ellipse(
            [x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
            fill=fill,
        )

    return image


def save_ico(filename: str, images: list[Image.Image]) -> None:
    """Save images as multi-resolution .ico file.

    Args:
        filename: Output filename
        images: List of images at different sizes
    """
    # PIL's .ico saving requires special handling
    # Save the largest image, and it will include all sizes
    images[0].save(
        filename,
        format="ICO",
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:],
    )


def main():
    """Generate all icons."""
    import os

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Idle icon - green microphone
    print("Creating icon_idle.ico...")
    idle_images = [create_microphone_icon(size, "#4CAF50") for size in SIZES]
    save_ico(os.path.join(script_dir, "icon_idle.ico"), idle_images)

    # Recording icon - red circle with pulse
    print("Creating icon_recording.ico...")
    recording_images = [create_recording_icon(size, "#F44336") for size in SIZES]
    save_ico(os.path.join(script_dir, "icon_recording.ico"), recording_images)

    # Processing icon - orange spinning dots
    print("Creating icon_processing.ico...")
    processing_images = [create_processing_icon(size, "#FF9800") for size in SIZES]
    save_ico(os.path.join(script_dir, "icon_processing.ico"), processing_images)

    print("Icons created successfully!")


if __name__ == "__main__":
    main()
