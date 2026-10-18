import os
import subprocess

OUTPUT_DIR = r"E:\week 2\output_video"
SCENES_DIR = os.path.join(OUTPUT_DIR, "scenes")
FFMPEG_EXE = r"E:\week 2\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

SCENE_CONFIGS = [
    {"index": 1, "duration": 7.0, "frames": 210, "zoom": "min(zoom+0.0004,1.04)"},
    {"index": 2, "duration": 7.0, "frames": 210, "zoom": "min(zoom+0.0004,1.04)"},
    {"index": 3, "duration": 8.0, "frames": 240, "zoom": "min(zoom+0.0003,1.04)"},
    {"index": 4, "duration": 11.0, "frames": 330, "zoom": "min(zoom+0.00025,1.04)"},
    {"index": 5, "duration": 8.0, "frames": 240, "zoom": "min(zoom+0.0003,1.04)"},
    {"index": 6, "duration": 9.0, "frames": 270, "zoom": "min(zoom+0.0003,1.03)"},
]

def render_scenes():
    clip_files = []
    for cfg in SCENE_CONFIGS:
        idx = cfg["index"]
        img_path = os.path.join(SCENES_DIR, f"scene_{idx}.png")
        clip_path = os.path.join(OUTPUT_DIR, f"clip_{idx}.mp4")
        clip_files.append(clip_path)

        # Generate smooth 1920x1080 30fps clip with subtle motion
        cmd = [
            FFMPEG_EXE, "-y",
            "-loop", "1",
            "-i", img_path,
            "-vf", f"zoompan=z='{cfg['zoom']}':d={cfg['frames']}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30",
            "-t", str(cfg["duration"]),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-r", "30",
            clip_path
        ]
        print(f"Rendering Scene {idx} ({cfg['duration']}s)...")
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            print(f"Error rendering clip {idx}:\n", res.stderr)
            raise RuntimeError(f"Rendering clip {idx} failed")
        print(f"Scene {idx} rendered.")

    # Concat file list
    concat_list = os.path.join(OUTPUT_DIR, "concat_list.txt")
    with open(concat_list, "w") as f:
        for c in clip_files:
            clean_path = c.replace("\\", "/")
            f.write(f"file '{clean_path}'\n")

    # Final video without audio
    merged_video = os.path.join(OUTPUT_DIR, "video_merged.mp4")
    concat_cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        merged_video
    ]
    print("Concatenating scene clips...")
    res = subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print("Error concatenating:\n", res.stderr)
        raise RuntimeError("Concat failed")

    # Mux with master audio track (50.0s)
    audio_track = os.path.join(OUTPUT_DIR, "master_audio_50s.wav")
    final_output = os.path.join(OUTPUT_DIR, "PocketLedger_AI_Demo_50s.mp4")

    # Burning in styled subtitles or embedding them
    srt_path = os.path.join(OUTPUT_DIR, "PocketLedger_AI_Subtitles.srt").replace("\\", "/")
    # Note: On Windows ffmpeg subtitles filter requires escaped colons
    escaped_srt = srt_path.replace(":", "\\:")

    mux_cmd = [
        FFMPEG_EXE, "-y",
        "-i", merged_video,
        "-i", audio_track,
        "-vf", f"subtitles='{escaped_srt}':force_style='FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,BorderStyle=4,Outline=1,Shadow=1,MarginV=35,Alignment=2'",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", "50.00",
        final_output
    ]

    print("Muxing final video with audio and subtitles...")
    res = subprocess.run(mux_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print("Warning: Subtitle burn-in had issue, muxing without burn-in...")
        fallback_mux = [
            FFMPEG_EXE, "-y",
            "-i", merged_video,
            "-i", audio_track,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", "50.00",
            final_output
        ]
        res = subprocess.run(fallback_mux, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            print("Error in fallback mux:\n", res.stderr)
            raise RuntimeError("Final mux failed")

    print(f"Final 50.0s Hackathon Demo Video exported successfully:\n{final_output}")

if __name__ == "__main__":
    render_scenes()
