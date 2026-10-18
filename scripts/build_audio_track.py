import os
import math
import wave
import struct
import subprocess

OUTPUT_DIR = r"E:\week 2\output_video"
FFMPEG_EXE = r"E:\week 2\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

TOTAL_DURATION = 50.0 # Exactly 50.0 seconds
SAMPLE_RATE = 44100

def generate_ambient_music(duration_sec, filename):
    """Generate subtle, cinematic, elegant ambient background pad."""
    num_samples = int(duration_sec * SAMPLE_RATE)
    # Chord frequencies (Hz) - lush, deep warm electronic chord: F - C - Eb - G (F9sus)
    freqs = [87.31, 130.81, 155.56, 196.00, 261.63, 349.23]
    
    with wave.open(filename, "w") as wav:
        wav.setnchannels(2) # Stereo
        wav.setsampwidth(2) # 16-bit
        wav.setframerate(SAMPLE_RATE)
        
        frames = bytearray()
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            # Slow LFO filter modulation
            lfo = 0.6 + 0.4 * math.sin(2 * math.pi * 0.15 * t)
            
            # Fade in over 2s, fade out over 2s
            fade = 1.0
            if t < 2.0:
                fade = t / 2.0
            elif t > duration_sec - 2.5:
                fade = max(0.0, (duration_sec - t) / 2.5)
            
            sample_val = 0.0
            for j, f in enumerate(freqs):
                detune = 1.0 + 0.002 * math.sin(2 * math.pi * 0.3 * t + j)
                sample_val += math.sin(2 * math.pi * f * detune * t) * (1.0 / (j + 1.2))
            
            sample_val = sample_val * lfo * fade * 0.06 # Soft ambient volume (-24dB)
            
            # Clamp to 16-bit PCM
            val_int = int(max(-1.0, min(1.0, sample_val)) * 32767)
            frames.extend(struct.pack("<hh", val_int, val_int))
            
        wav.writeframes(frames)
    print(f"Generated ambient music: {filename}")

def build_master_audio():
    ambient_wav = os.path.join(OUTPUT_DIR, "ambient_pad.wav")
    generate_ambient_music(TOTAL_DURATION, ambient_wav)

    # Offsets in seconds for each voice segment
    offsets = [0.30, 7.30, 14.50, 22.50, 33.50, 41.10]
    
    # Use ffmpeg complex filter to mix all segments with ambient background
    inputs = ["-i", ambient_wav]
    filter_complex = []
    
    for i in range(1, 7):
        seg_file = os.path.join(OUTPUT_DIR, f"voice_seg_{i}.mp3")
        inputs.extend(["-i", seg_file])
    
    # Delay each voice segment to its start offset
    filter_chains = []
    for i, offset_s in enumerate(offsets):
        delay_ms = int(offset_s * 1000)
        filter_complex.append(f"[{i+1}:a]adelay={delay_ms}|{delay_ms},volume=1.4[v{i+1}]")
        filter_chains.append(f"[v{i+1}]")
    
    # Mix ambient (input 0) with delayed voice segments
    all_inputs = "[0:a]" + "".join(filter_chains)
    mix_count = 1 + len(offsets)
    filter_complex.append(f"{all_inputs}amix=inputs={mix_count}:duration=first:dropout_transition=0[aout]")
    
    filter_str = ";".join(filter_complex)
    output_audio = os.path.join(OUTPUT_DIR, "master_audio_50s.wav")
    
    cmd = [
        FFMPEG_EXE, "-y",
        *inputs,
        "-filter_complex", filter_str,
        "-map", "[aout]",
        "-t", "50.00",
        output_audio
    ]
    
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print("Error mixing audio:\n", res.stderr)
        raise RuntimeError("FFmpeg audio mix failed")
    
    print(f"Master 50.0s audio track created successfully: {output_audio}")

if __name__ == "__main__":
    build_master_audio()
