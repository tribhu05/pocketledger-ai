import os
import sys
import asyncio

OUTPUT_DIR = r"E:\week 2\output_video"
os.makedirs(OUTPUT_DIR, exist_ok=True)

VOICEOVER_SEGMENTS = [
    {
        "scene": 1,
        "start": 0.5,
        "text": "Freelancers shouldn't have to risk their financial privacy just to organize receipts. Meet PocketLedger AI."
    },
    {
        "scene": 2,
        "start": 6.5,
        "text": "Powered by open-weight AI through Ollama, PocketLedger is designed to process financial documents with privacy in mind."
    },
    {
        "scene": 3,
        "start": 13.5,
        "text": "Upload a receipt, extract key expense details, and turn unstructured text into organized financial records."
    },
    {
        "scene": 4,
        "start": 22.5,
        "text": "Then, deterministic validation checks the numbers. AI extracts the details, but financial rules verify the calculations—with human approval in the loop."
    },
    {
        "scene": 5,
        "start": 32.5,
        "text": "Approved expenses enter your ledger, ready for reporting and CSV export, with security-conscious handling of financial data."
    },
    {
        "scene": 6,
        "start": 41.5,
        "text": "PocketLedger AI is open-source and built to put freelancers in control. Explore the code on GitHub. Your records, your control."
    }
]

async def generate():
    eleven_key = os.getenv("ELEVENLABS_API_KEY") or os.getenv("ELEVEN_API_KEY")
    used_engine = "edge-tts (en-US-ChristopherNeural)"

    if eleven_key:
        try:
            from elevenlabs.client import ElevenLabs
            client = ElevenLabs(api_key=eleven_key)
            print("ElevenLabs API key detected, generating with ElevenLabs...")
            for i, seg in enumerate(VOICEOVER_SEGMENTS):
                audio = client.text_to_speech.convert(
                    text=seg["text"],
                    voice_id="JBFqnCBsd6RMkjVDRZzb", # George / Founder voice
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128"
                )
                seg_path = os.path.join(OUTPUT_DIR, f"voice_seg_{i+1}.mp3")
                with open(seg_path, "wb") as f:
                    for chunk in audio:
                        f.write(chunk)
                print(f"Generated ElevenLabs segment {i+1}")
            used_engine = "ElevenLabs (official API)"
        except Exception as e:
            print(f"ElevenLabs generation failed ({e}), falling back to Edge Neural TTS...")
            eleven_key = None

    if not eleven_key:
        print("Using high-fidelity Neural TTS voice...")
        import edge_tts
        voice = "en-US-ChristopherNeural"
        for i, seg in enumerate(VOICEOVER_SEGMENTS):
            seg_path = os.path.join(OUTPUT_DIR, f"voice_seg_{i+1}.mp3")
            communicate = edge_tts.Communicate(seg["text"], voice, rate="+18%", pitch="-1Hz")
            await communicate.save(seg_path)
            print(f"Generated segment {i+1} -> {seg_path}")

    # Combine into full narration track PocketLedger_AI_Voiceover.mp3
    full_text = " ".join([s["text"] for s in VOICEOVER_SEGMENTS])
    full_audio_path = os.path.join(OUTPUT_DIR, "PocketLedger_AI_Voiceover.mp3")
    if eleven_key:
        try:
            from elevenlabs.client import ElevenLabs
            client = ElevenLabs(api_key=eleven_key)
            audio = client.text_to_speech.convert(
                text=full_text,
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )
            with open(full_audio_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)
        except Exception:
            pass
    if not os.path.exists(full_audio_path) or os.path.getsize(full_audio_path) == 0:
        import edge_tts
        voice = "en-US-ChristopherNeural"
        comm = edge_tts.Communicate(full_text, voice, rate="+18%", pitch="-1Hz")
        await comm.save(full_audio_path)

    print(f"Full narration exported: {full_audio_path}")
    return used_engine

if __name__ == "__main__":
    engine = asyncio.run(generate())
    print("TTS Engine used:", engine)
