"""Generate FinanceFlow PWA icons from an emoji."""
from PIL import Image, ImageDraw, ImageFont

def make_icon(size, path, emoji="💰", bg="#10b981"):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Green rounded square
    radius = int(size * 0.22)
    draw.rounded_rectangle(
        [(0, 0), (size, size)],
        radius=radius,
        fill=bg,
    )

    # Emoji centered
    try:
        font = ImageFont.truetype("seguiemj.ttf", int(size * 0.6))
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), emoji, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(
        ((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1]),
        emoji, font=font, embedded_color=True,
    )

    img.save(path, "PNG")
    print(f"✓ {path} ({size}x{size})")

make_icon(192, "static/icons/icon-192.png")
make_icon(512, "static/icons/icon-512.png")
print("Done. Both icons saved to static/icons/")