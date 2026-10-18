import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = r"E:\week 2\output_video\scenes"
os.makedirs(OUTPUT_DIR, exist_ok=True)
SCREENSHOT_DIR = r"E:\week 2\docs\screenshots"

W, H = 1920, 1080

def get_font(size, bold=False):
    # Try system fonts on Windows
    candidates = [
        "C:\\Windows\\Fonts\\segoeui.ttf" if not bold else "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\arial.ttf" if not bold else "C:\\Windows\\Fonts\\arialbd.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_header_badge(draw, text, y=60, accent="#10B981"):
    font = get_font(22, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pad_x, pad_y = 20, 8
    x1 = (W - tw) // 2 - pad_x
    x2 = (W + tw) // 2 + pad_x
    y1 = y
    y2 = y + th + pad_y * 2
    # Draw rounded pill
    draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill="#0F172A", outline=accent, width=2)
    draw.text(((W - tw) // 2, y1 + pad_y - 2), text, font=font, fill=accent)
    return y2

def draw_footer_bar(draw, text):
    font = get_font(18, bold=False)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.rectangle([0, H - 50, W, H], fill="#020617")
    draw.text(((W - tw) // 2, H - 38), text, font=font, fill="#94A3B8")

# -------------------------------------------------------------
# Scene 1: The Problem
# -------------------------------------------------------------
def make_scene_1():
    img = Image.new("RGB", (W, H), "#070B12")
    draw = ImageDraw.Draw(img)

    # Gradient-like background
    for y in range(H):
        alpha = int(25 * (y / H))
        draw.line([(0, y), (W, y)], fill=(7 + alpha, 11 + alpha, 18 + alpha))

    badge_bot = draw_header_badge(draw, "POCKETLEDGER AI • THE PROBLEM", y=80, accent="#EF4444")

    # Main Headline
    font_hero = get_font(68, bold=True)
    t1 = "Your finances. Your privacy."
    bbox1 = draw.textbbox((0, 0), t1, font=font_hero)
    draw.text(((W - (bbox1[2] - bbox1[0])) // 2, badge_bot + 40), t1, font=font_hero, fill="#FFFFFF")

    # Subtitle
    font_sub = get_font(28, bold=False)
    t2 = "Freelancers shouldn't have to upload confidential client receipts to cloud AI APIs."
    bbox2 = draw.textbbox((0, 0), t2, font=font_sub)
    draw.text(((W - (bbox2[2] - bbox2[0])) // 2, badge_bot + 125), t2, font=font_sub, fill="#94A3B8")

    # Visual Cards: Messy Spreadsheets vs On-Device AI
    card_w, card_h = 760, 480
    # Left: The Cloud Dilemma
    x_l = 160
    y_cards = badge_bot + 200
    draw.rounded_rectangle([x_l, y_cards, x_l + card_w, y_cards + card_h], radius=20, fill="#0F172A", outline="#334155", width=2)
    draw.text((x_l + 40, y_cards + 40), "THE CLOUD AI DILEMMA", font=get_font(20, bold=True), fill="#EF4444")
    draw.text((x_l + 40, y_cards + 80), "• Leaks client billing rates & NDAs to third parties\n• PII & banking numbers stored on external servers\n• High recurring SaaS subscriptions ($30+/mo)\n• Fails completely when working offline or travelling", font=get_font(24, bold=False), fill="#CBD5E1", spacing=18)

    # Right: The PocketLedger Solution
    x_r = 1000
    draw.rounded_rectangle([x_r, y_cards, x_r + card_w, y_cards + card_h], radius=20, fill="#064E3B", outline="#10B981", width=2)
    draw.text((x_r + 40, y_cards + 40), "THE POCKETLEDGER AI SOLUTION", font=get_font(20, bold=True), fill="#34D399")
    draw.text((x_r + 40, y_cards + 80), "• 100% On-Device local Gemma 2B model via Ollama\n• Zero bytes of financial evidence leave your laptop\n• Deterministic math verification: no AI hallucinations\n• One-time purchase, fully open-source (MIT)", font=get_font(24, bold=False), fill="#ECFDF5", spacing=18)

    draw_footer_bar(draw, "Scene 1: The Freelancer's Privacy Dilemma | Hacktoberfest Side Hustle Challenge")
    img.save(os.path.join(OUTPUT_DIR, "scene_1.png"))
    print("Scene 1 created.")

# -------------------------------------------------------------
# Scene 2: Open-Weight AI (System Status & Dashboard)
# -------------------------------------------------------------
def make_scene_2():
    img = Image.new("RGB", (W, H), "#070B12")
    draw = ImageDraw.Draw(img)

    # Embed Screenshot 06 (System Status & Benchmarks) or 01 (Dashboard)
    ss_path = os.path.join(SCREENSHOT_DIR, "06_system_status.png")
    if os.path.exists(ss_path):
        ss = Image.open(ss_path).convert("RGB")
        ss_resized = ss.resize((1500, 750), Image.Resampling.LANCZOS)
        # Paste centered
        img.paste(ss_resized, (210, 200))
        # Draw frame around it
        draw.rounded_rectangle([206, 196, 1714, 954], radius=16, outline="#38BDF8", width=4)

    badge_bot = draw_header_badge(draw, "OPEN-WEIGHT AI • LOCAL INFERENCE", y=40, accent="#38BDF8")
    font_hero = get_font(42, bold=True)
    t = "Google Gemma 2B Instruct Running Locally via Ollama"
    bbox = draw.textbbox((0, 0), t, font=font_hero)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, badge_bot + 18), t, font=font_hero, fill="#FFFFFF")

    draw_footer_bar(draw, "Scene 2: Local Open-Weight AI Architecture | Gemma 2B Instruct on http://localhost:11434")
    img.save(os.path.join(OUTPUT_DIR, "scene_2.png"))
    print("Scene 2 created.")

# -------------------------------------------------------------
# Scene 3: Receipt Extraction
# -------------------------------------------------------------
def make_scene_3():
    img = Image.new("RGB", (W, H), "#070B12")
    draw = ImageDraw.Draw(img)

    ss_path = os.path.join(SCREENSHOT_DIR, "02_inbox.png")
    if os.path.exists(ss_path):
        ss = Image.open(ss_path).convert("RGB")
        ss_resized = ss.resize((1500, 750), Image.Resampling.LANCZOS)
        img.paste(ss_resized, (210, 200))
        draw.rounded_rectangle([206, 196, 1714, 954], radius=16, outline="#818CF8", width=4)

    badge_bot = draw_header_badge(draw, "RECEIPT → STRUCTURED DATA", y=40, accent="#818CF8")
    font_hero = get_font(42, bold=True)
    t = "Unstructured PDFs & Receipts Extracted into Strict Pydantic Schemas"
    bbox = draw.textbbox((0, 0), t, font=font_hero)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, badge_bot + 18), t, font=font_hero, fill="#FFFFFF")

    draw_footer_bar(draw, "Scene 3: Semantic Extraction Pipeline | Local Tesseract OCR + Gemma 2B Structured JSON")
    img.save(os.path.join(OUTPUT_DIR, "scene_3.png"))
    print("Scene 3 created.")

# -------------------------------------------------------------
# Scene 4: Deterministic Validation (Review Modal)
# -------------------------------------------------------------
def make_scene_4():
    img = Image.new("RGB", (W, H), "#070B12")
    draw = ImageDraw.Draw(img)

    ss_path = os.path.join(SCREENSHOT_DIR, "04_review_modal.png")
    if os.path.exists(ss_path):
        ss = Image.open(ss_path).convert("RGB")
        ss_resized = ss.resize((1500, 750), Image.Resampling.LANCZOS)
        img.paste(ss_resized, (210, 200))
        draw.rounded_rectangle([206, 196, 1714, 954], radius=16, outline="#10B981", width=4)

    badge_bot = draw_header_badge(draw, "AI EXTRACTION • DETERMINISTIC VALIDATION", y=40, accent="#10B981")
    font_hero = get_font(40, bold=True)
    t = "Subtotal + Tax - Discount + Charges = Stated Total (Math Verified)"
    bbox = draw.textbbox((0, 0), t, font=font_hero)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, badge_bot + 18), t, font=font_hero, fill="#FFFFFF")

    draw_footer_bar(draw, "Scene 4: Financial Rules & Math Reconciliation | Discrepancy Detection & Human Approval")
    img.save(os.path.join(OUTPUT_DIR, "scene_4.png"))
    print("Scene 4 created.")

# -------------------------------------------------------------
# Scene 5: Ledger and Export
# -------------------------------------------------------------
def make_scene_5():
    img = Image.new("RGB", (W, H), "#070B12")
    draw = ImageDraw.Draw(img)

    ss_path = os.path.join(SCREENSHOT_DIR, "03_ledger.png")
    if os.path.exists(ss_path):
        ss = Image.open(ss_path).convert("RGB")
        ss_resized = ss.resize((1500, 750), Image.Resampling.LANCZOS)
        img.paste(ss_resized, (210, 200))
        draw.rounded_rectangle([206, 196, 1714, 954], radius=16, outline="#F59E0B", width=4)

    badge_bot = draw_header_badge(draw, "REVIEW → APPROVE → EXPORT", y=40, accent="#F59E0B")
    font_hero = get_font(42, bold=True)
    t = "Multi-Currency Audit Ledger & Injection-Safe CSV Export"
    bbox = draw.textbbox((0, 0), t, font=font_hero)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, badge_bot + 18), t, font=font_hero, fill="#FFFFFF")

    draw_footer_bar(draw, "Scene 5: Expense Reporting | Formula-Injection Neutralization ('=, +, -, @) & SQLite Storage")
    img.save(os.path.join(OUTPUT_DIR, "scene_5.png"))
    print("Scene 5 created.")

# -------------------------------------------------------------
# Scene 6: Final Call to Action
# -------------------------------------------------------------
def make_scene_6():
    img = Image.new("RGB", (W, H), "#030712")
    draw = ImageDraw.Draw(img)

    for y in range(H):
        alpha = int(30 * (y / H))
        draw.line([(0, y), (W, y)], fill=(3 + alpha, 7 + alpha, 18 + alpha))

    badge_bot = draw_header_badge(draw, "OPEN SOURCE • HACKTOBERFEST WEEK 2", y=100, accent="#10B981")

    # Project Name
    font_title = get_font(84, bold=True)
    t_name = "PocketLedger AI"
    bbox_n = draw.textbbox((0, 0), t_name, font=font_title)
    draw.text(((W - (bbox_n[2] - bbox_n[0])) // 2, badge_bot + 40), t_name, font=font_title, fill="#FFFFFF")

    # Tagline
    font_tag = get_font(34, bold=False)
    t_tag = '"Your receipts. Your records. Your data stays yours."'
    bbox_t = draw.textbbox((0, 0), t_tag, font=font_tag)
    draw.text(((W - (bbox_t[2] - bbox_t[0])) // 2, badge_bot + 150), t_tag, font=font_tag, fill="#34D399")

    # Links Box
    box_w, box_h = 1000, 280
    box_x = (W - box_w) // 2
    box_y = badge_bot + 240
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=24, fill="#0F172A", outline="#1E293B", width=2)

    font_link = get_font(30, bold=True)
    draw.text((box_x + 60, box_y + 50), "GitHub:", font=font_link, fill="#38BDF8")
    draw.text((box_x + 220, box_y + 50), "https://github.com/tribhu05/pocketledger-ai", font=font_link, fill="#FFFFFF")

    draw.text((box_x + 60, box_y + 120), "Render Demo:", font=font_link, fill="#F43F5E")
    draw.text((box_x + 270, box_y + 120), "https://pocketledger-ai.onrender.com", font=font_link, fill="#FFFFFF")

    draw.text((box_x + 60, box_y + 190), "Stack:", font=font_link, fill="#A855F7")
    draw.text((box_x + 220, box_y + 190), "Gemma 2B • Ollama • FastAPI • React 19 • Docker", font=font_link, fill="#E2E8F0")

    draw_footer_bar(draw, "Built with Google Gemma 2B & Ollama | MIT License | Deployed on Render")
    img.save(os.path.join(OUTPUT_DIR, "scene_6.png"))
    print("Scene 6 created.")

if __name__ == "__main__":
    make_scene_1()
    make_scene_2()
    make_scene_3()
    make_scene_4()
    make_scene_5()
    make_scene_6()
    print("All 6 scene keyframes generated successfully!")
