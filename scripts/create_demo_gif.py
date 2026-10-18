import os
from PIL import Image

screenshot_dir = r"E:\week 2\docs\screenshots"
image_files = [
    "01_dashboard.png",
    "02_inbox.png",
    "04_review_modal.png",
    "03_ledger.png",
    "05_reports_csv.png",
    "06_system_status.png"
]

images = []
target_size = (1080, 675) # 16:10 aspect ratio, crisp and fast to load

durations = [2200, 2000, 2800, 2200, 2000, 2000] # milliseconds per frame

for filename in image_files:
    filepath = os.path.join(screenshot_dir, filename)
    if os.path.exists(filepath):
        img = Image.open(filepath).convert("RGB")
        img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
        # Quantize to 256 colors for clean, compact GIF
        img_quantized = img_resized.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        images.append(img_quantized)
        print(f"Processed {filename} -> {target_size}")

if images:
    gif_path = os.path.join(screenshot_dir, "pocketledger_demo.gif")
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=durations[:len(images)],
        loop=0,
        optimize=True
    )
    file_size_mb = os.path.getsize(gif_path) / (1024 * 1024)
    print(f"Animated GIF created successfully: {gif_path} ({file_size_mb:.2f} MB)")
else:
    print("No images found to create GIF")
