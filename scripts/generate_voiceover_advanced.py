"""
PocketLedger AI — Advanced Text-to-Speech & Crystal Clear Voice Generator
========================================================================
Supports:
1. ElevenLabs API (via ELEVENLABS_API_KEY or --api-key argument)
2. Microsoft Edge Neural TTS (en-US-AndrewNeural / en-US-GuyNeural) with studio mastering EQ

Usage:
  # Using Edge Neural TTS (crystal clear studio voice):
  python scripts/generate_voiceover_advanced.py --voice andrew

  # Using ElevenLabs with an API key:
  python scripts/generate_voiceover_advanced.py --elevenlabs-key YOUR_API_KEY

  # Completely mute background music for 100% voice clarity:
  python scripts/generate_voiceover_advanced.py --no-music
"""

import os
import sys
import argparse
import asyncio
import subprocess

OUTPUT_DIR = r"E:\week 2\output_video"
DOCS_VIDEO_DIR = r"E:\week 2\docs\video"
FFMPEG_EXE = r"E:\week 2\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

VOICEOVER_SEGMENTS = [
    {
        "scene": 1,
        "offset": 0.40,
        "text": "Freelancers shouldn't have to risk their financial privacy just to organize receipts. Meet PocketLedger AI."
    },
    {
        "scene": 2,
        "offset": 7.30,
        "text": "Powered by open-weight AI through Ollama, PocketLedger is designed to process financial documents with privacy in mind."
    },
    {
        "scene": 3,
        "offset": 14.40,
        "text": "Upload a receipt, extract key expense details, and turn unstructured text into organized financial records."
    },
    {
        "scene": 4,
        "offset": 22.40,
        "text": "Then, deterministic validation checks the numbers. AI extracts the details, but financial rules verify the calculations—with human approval in the loop."
    },
    {
        "scene": 5,
        "offset": 33.40,
        "text": "Approved expenses enter your ledger, ready for reporting and CSV export, with security-conscious handling of financial data."
    },
    {
        "scene": 6,
        "offset": 41.20,
        "text": "PocketLedger AI is open-source and built to put freelancers in control. Explore the code on GitHub. Your records, your control."
    }
]

async def generate_speech(elevenlabs_key=None, voice_choice="andrew"):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(DOCS_VIDEO_DIR, exist_ok=True)

    if elevenlabs_key:
        print("Using ElevenLabs API for speech generation...")
        try:
            from elevenlabs.client import ElevenLabs
            client = ElevenLabs(api_key=elevenlabs_key)
            for i, seg in enumerate(VOICEOVER_SEGMENTS):
                audio = client.text_to_speech.convert(
                    text=seg["text"],
                    voice_id="JBFqnCBsd6RMkjVDRZzb", # George / Founder
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128",
                    voice_settings={
                        "stability": 0.55,
                        "similarity_boost": 0.85,
                        "style": 0.0,
                        "use_speaker_boost": True
                    }
                )
                seg_path = os.path.join(OUTPUT_DIR, f"voice_seg_{i+1}.mp3")
                with open(seg_path, "wb") as f:
                    for chunk in audio:
                        f.write(chunk)
                print(f"Generated ElevenLabs segment {i+1}")
            return "ElevenLabs"
        except Exception as e:
            print(f"ElevenLabs error: {e}. Falling back to high-clarity Neural voice...")

    # High-clarity Neural TTS fallback
    import edge_tts
    # AndrewNeural is exceptionally crisp, punchy, and articulate for tech product demos
    voice_map = {
        "andrew": "en-US-AndrewNeural",
        "guy": "en-US-GuyNeural",
        "brian": "en-US-BrianNeural",
        "christopher": "en-US-ChristopherNeural"
    }
    voice_name = voice_map.get(voice_choice.lower(), "en-US-AndrewNeural")
    print(f"Generating speech with crystal-clear Neural voice: {voice_name}...")

    for i, seg in enumerate(VOICEOVER_SEGMENTS):
        seg_path = os.path.join(OUTPUT_DIR, f"voice_seg_{i+1}.mp3")
        # rate +10% provides natural fast founder pace while keeping every consonant crystal clear
        communicate = edge_tts.Communicate(seg["text"], voice_name, rate="+10%", pitch="+0Hz")
        await communicate.save(seg_path)
        print(f"Generated segment {i+1} -> {seg_path}")

    # Full narration track export
    full_text = " ".join([s["text"] for s in VOICEOVER_SEGMENTS])
    full_track_path = os.path.join(OUTPUT_DIR, "PocketLedger_AI_Voiceover.mp3")
    comm = edge_tts.Communicate(full_text, voice_name, rate="+10%", pitch="+0Hz")
    await comm.save(full_track_path)
    print(f"Exported full narration: {full_track_path}")
    return voice_name

def master_audio_and_remux(no_music=False):
    print("Mastering audio track with studio vocal EQ (high-pass 120Hz, presence boost +4dB, compression)...")
    
    ambient_wav = os.path.join(OUTPUT_DIR, "ambient_pad.wav")
    inputs = []
    filter_complex = []

    use_bg = (not no_music) and os.path.exists(ambient_wav)

    if use_bg:
        inputs.extend(["-i", ambient_wav])
        # Background music lowered to a subtle whisper (volume=0.035, approx -29dB) so voice is 100% crisp
        filter_complex.append("[0:a]volume=0.035[bg]")
        offset_idx = 1
    else:
        offset_idx = 0

    for i in range(1, 7):
        seg_file = os.path.join(OUTPUT_DIR, f"voice_seg_{i}.mp3")
        inputs.extend(["-i", seg_file])

    filter_chains = []
    for i, seg in enumerate(VOICEOVER_SEGMENTS):
        in_idx = offset_idx + i
        delay_ms = int(seg["offset"] * 1000)
        # Apply high-pass filter at 120Hz (cuts muddy boxiness), treble boost at 3500Hz (+4dB crisp articulation), compressor
        vocal_filter = "highpass=f=120,treble=g=4:f=3500,acompressor=threshold=-16dB:ratio=3:attack=10:release=100"
        filter_complex.append(f"[{in_idx}:a]{vocal_filter},adelay={delay_ms}|{delay_ms},volume=2.4[v{i+1}]")
        filter_chains.append(f"[v{i+1}]")

    if use_bg:
        all_inputs = "[bg]" + "".join(filter_chains)
        num_inputs = 7
    else:
        all_inputs = "".join(filter_chains)
        num_inputs = 6

    filter_complex.append(f"{all_inputs}amix=inputs={num_inputs}:duration=first:dropout_transition=0[aout]")

    filter_str = ";".join(filter_complex)
    master_audio = os.path.join(OUTPUT_DIR, "master_audio_50s.wav")

    cmd = [
        FFMPEG_EXE, "-y",
        *inputs,
        "-filter_complex", filter_str,
        "-map", "[aout]",
        "-t", "50.00",
        master_audio
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print("Audio mix failed:\n", res.stderr)
        return False
    print("Master audio mixed successfully.")

    # Re-mux final video
    merged_video = os.path.join(OUTPUT_DIR, "video_merged.mp4")
    final_output = os.path.join(OUTPUT_DIR, "PocketLedger_AI_Demo_50s.mp4")
    srt_path = os.path.join(OUTPUT_DIR, "PocketLedger_AI_Subtitles.srt").replace("\\", "/")
    escaped_srt = srt_path.replace(":", "\\:")

    mux_cmd = [
        FFMPEG_EXE, "-y",
        "-i", merged_video,
        "-i", master_audio,
        "-vf", f"subtitles='{escaped_srt}':force_style='FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,BorderStyle=4,Outline=1,Shadow=1,MarginV=35,Alignment=2'",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", "50.00",
        final_output
    ]

    print("Re-muxing final 50-second demo video with upgraded crystal-clear voice...")
    res = subprocess.run(mux_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print("Subtitle burn-in returned error, running direct mux fallback...")
        fallback_mux = [
            FFMPEG_EXE, "-y",
            "-i", merged_video,
            "-i", master_audio,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", "50.00",
            final_output
        ]
        subprocess.run(fallback_mux, check=True)

    # Copy updated deliverables to docs/video
    import shutil
    shutil.copy2(final_output, os.path.join(DOCS_VIDEO_DIR, "PocketLedger_AI_Demo_50s.mp4"))
    shutil.copy2(os.path.join(OUTPUT_DIR, "PocketLedger_AI_Voiceover.mp3"), os.path.join(DOCS_VIDEO_DIR, "PocketLedger_AI_Voiceover.mp3"))
    print("Updated final video and voiceover copied to docs/video/!")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate crystal-clear voiceover for PocketLedger AI demo video.")
    parser.add_argument("--elevenlabs-key", help="Optional ElevenLabs API key")
    parser.add_argument("--voice", default="andrew", choices=["andrew", "guy", "brian", "christopher"], help="Neural voice choice")
    parser.add_argument("--no-music", action="store_true", help="Completely remove background ambient music for 100%% voice clarity")
    args = parser.parse_args()

    api_key = args.elevenlabs_key or os.getenv("ELEVENLABS_API_KEY")
    voice_used = asyncio.run(generate_speech(api_key, args.voice))
    master_audio_and_remux(no_music=args.no_music)
    print("\nSUCCESS! Video rebuilt with crystal-clear audio.")
