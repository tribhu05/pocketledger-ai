"""
PocketLedger AI — Hero Banner Generator
Aspect Ratio: 100:53 (1200 x 636)
Matches DEV.to cover guidelines and Master Prompt requirements.
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_BANNER = r"E:\week 2\docs\screenshots\hero_banner.png"
MODAL_SCREENSHOT = r"E:\week 2\docs\screenshots\04_review_modal.png"
DASH_SCREENSHOT = r"E:\week 2\docs\screenshots\01_dashboard.png"

WIDTH = 1200
HEIGHT = 636

# Create dark charcoal canvas
img = Image.new("RGBA", (WIDTH, HEIGHT), (15, 23, 42, 255)) # Dark slate/charcoal #0F172A
draw = ImageDraw.Draw(img)

# Background subtle ambient glow in emerald
glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
glow_draw = ImageDraw.Draw(glow)
glow_draw.ellipse([800, -100, 1400, 500], fill=(16, 185, 129, 35)) # Emerald ambient glow
glow_draw.ellipse([-100, 300, 500, 900], fill=(30, 41, 59, 80)) # Subtle cool shadow
glow = glow.filter(ImageFilter.GaussianBlur(80))
img = Image.alpha_composite(img, glow)
draw = ImageDraw.Draw(img)

# Try loading standard Windows fonts
try:
    font_badge = ImageFont.truetype("arialbd.ttf", 16)
    font_title = ImageFont.truetype("arialbd.ttf", 52)
    font_subtitle = ImageFont.truetype("arialbd.ttf", 26)
    font_supporting = ImageFont.truetype("arialbd.ttf", 18)
    font_quote = ImageFont.truetype("arial.ttf", 18)
    font_card_head = ImageFont.truetype("arialbd.ttf", 18)
    font_card_body = ImageFont.truetype("arial.ttf", 15)
    font_pill = ImageFont.truetype("arialbd.ttf", 14)
except Exception:
    font_badge = ImageFont.load_default()
    font_title = ImageFont.load_default()
    font_subtitle = ImageFont.load_default()
    font_supporting = ImageFont.load_default()
    font_quote = ImageFont.load_default()
    font_card_head = ImageFont.load_default()
    font_card_body = ImageFont.load_default()
    font_pill = ImageFont.load_default()

# --- Left Column: Typography & Positioning ---
# 1. Challenge Badge
draw.rounded_rectangle([70, 75, 430, 110], radius=18, fill=(6, 78, 59, 200), outline=(16, 185, 129, 255), width=1)
draw.text((85, 84), "HACKTOBERFEST 2026 • SIDE HUSTLE", fill=(52, 211, 153, 255), font=font_badge)

# 2. Exact Title: "PocketLedger AI"
draw.text((70, 130), "PocketLedger AI", fill=(248, 250, 252, 255), font=font_title)

# 3. Exact Subtitle: "Your receipts. Your rules."
draw.text((72, 198), "Your receipts. Your rules.", fill=(16, 185, 129, 255), font=font_subtitle)

# 4. Exact Supporting text: "OPEN-WEIGHT AI • LOCAL-FIRST • VERIFIED MATH"
draw.rounded_rectangle([70, 245, 530, 285], radius=8, fill=(30, 41, 59, 220), outline=(51, 65, 85, 255), width=1)
draw.text((82, 253), "OPEN-WEIGHT AI • LOCAL-FIRST • VERIFIED MATH", fill=(148, 163, 184, 255), font=font_supporting)

# 5. Core Architectural Principle
draw.text((72, 315), "The Architectural Contract:", fill=(203, 213, 225, 255), font=font_card_head)

principle_lines = [
    "• AI reads the document.",
    "• Deterministic code checks the numbers.",
    "• Humans approve the record."
]
y_offset = 345
for line in principle_lines:
    draw.text((72, y_offset), line, fill=(241, 245, 249, 255), font=font_quote)
    y_offset += 28

# 6. Trust Badges at bottom left
draw.rounded_rectangle([70, 460, 230, 500], radius=6, fill=(15, 23, 42, 240), outline=(16, 185, 129, 200), width=1)
draw.text((85, 470), "🛡️ 100% On-Device", fill=(16, 185, 129, 255), font=font_pill)

draw.rounded_rectangle([245, 460, 395, 500], radius=6, fill=(15, 23, 42, 240), outline=(59, 130, 246, 200), width=1)
draw.text((260, 470), "⚡ Gemma 2B (Ollama)", fill=(96, 165, 250, 255), font=font_pill)

draw.rounded_rectangle([410, 460, 540, 500], radius=6, fill=(15, 23, 42, 240), outline=(168, 85, 247, 200), width=1)
draw.text((425, 470), "📁 Local SQLite", fill=(192, 132, 252, 255), font=font_pill)

draw.text((72, 540), "Tested on 4-Core Ryzen 3 (8GB RAM) • MIT Licensed Open Source", fill=(100, 116, 139, 255), font=font_pill)


# --- Right Column: Realistic Application UI Showcase ---
# We composite a crisp, perspective-framed snippet of the actual review modal / dashboard
card_x = 590
card_y = 65
card_w = 540
card_h = 505

# Card Outer Container with Border & Drop Shadow
card_shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
card_shadow_draw = ImageDraw.Draw(card_shadow)
card_shadow_draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=16, fill=(0, 0, 0, 140))
card_shadow = card_shadow.filter(ImageFilter.GaussianBlur(15))
img = Image.alpha_composite(img, card_shadow)
draw = ImageDraw.Draw(img)

# Main Card Body
draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=16, fill=(17, 24, 39, 255), outline=(55, 65, 81, 255), width=2)

# Card Header Bar
draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + 48], radius=16, fill=(31, 41, 55, 255))
draw.rectangle([card_x, card_y + 30, card_x + card_w, card_y + 48], fill=(31, 41, 55, 255))
draw.line([card_x, card_y + 48, card_x + card_w, card_y + 48], fill=(55, 65, 81, 255), width=1)

# Window dots
draw.ellipse([card_x + 18, card_y + 18, card_x + 28, card_y + 28], fill=(239, 68, 68, 255))
draw.ellipse([card_x + 36, card_y + 18, card_x + 46, card_y + 28], fill=(245, 158, 11, 255))
draw.ellipse([card_x + 54, card_y + 18, card_x + 64, card_y + 28], fill=(16, 185, 129, 255))
draw.text((card_x + 78, card_y + 14), "PocketLedger AI — Review & Deterministic Validation", fill=(209, 213, 219, 255), font=font_pill)

# Embed actual application screenshot inside the card window
if os.path.exists(MODAL_SCREENSHOT):
    try:
        ss_img = Image.open(MODAL_SCREENSHOT).convert("RGBA")
        # Crop into the most illustrative middle area (receipt preview + extracted numbers)
        w_orig, h_orig = ss_img.size
        # Crop the center modal dialog
        crop_box = (int(w_orig * 0.15), int(h_orig * 0.12), int(w_orig * 0.85), int(h_orig * 0.88))
        ss_cropped = ss_img.crop(crop_box)
        target_preview_w = card_w - 24
        target_preview_h = card_h - 70
        ss_resized = ss_cropped.resize((target_preview_w, target_preview_h), Image.Resampling.LANCZOS)
        
        # Paste inside card
        img.paste(ss_resized, (card_x + 12, card_y + 58), ss_resized)
        draw = ImageDraw.Draw(img)
    except Exception as e:
        print(f"Error loading screenshot: {e}")

# Add floating verification pill overlay on bottom-right of card
pill_x = card_x + 20
pill_y = card_y + card_h - 60
draw.rounded_rectangle([pill_x, pill_y, pill_x + 290, pill_y + 42], radius=10, fill=(6, 78, 59, 240), outline=(52, 211, 153, 255), width=2)
draw.text((pill_x + 14, pill_y + 11), "✓ Reconciliation Balanced (Δ $0.00)", fill=(240, 253, 244, 255), font=font_pill)

# Save final image
img = img.convert("RGB")
img.save(OUTPUT_BANNER, "PNG", quality=95)
print(f"Hero banner generated successfully at: {OUTPUT_BANNER} (Size: {WIDTH}x{HEIGHT})")
