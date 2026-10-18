================================================================================
POCKETLEDGER AI — 50-SECOND PRODUCT DEMO VIDEO PRODUCTION NOTES
Hacktoberfest Week 2: Side Hustle Challenge Submission
================================================================================

1. DELIVERABLES SUMMARY
-----------------------
- PocketLedger_AI_Demo_50s.mp4 : Final submission-ready video (1920x1080 @ 30 fps, H.264 / AAC)
- PocketLedger_AI_Voiceover.mp3: Full generated voiceover narration track
- PocketLedger_AI_Subtitles.srt: Synchronized subtitles matching the spoken voiceover
- README.txt                   : Production notes, verification metadata, and scene breakdown

2. VERIFIED VIDEO METADATA
--------------------------
- Exact Duration : 00:00:50.00 (50.00 seconds max, exact frame count: 1,500 frames @ 30 fps)
- Resolution     : 1920 x 1080 (16:9 widescreen)
- Video Codec    : H.264 (High Profile, progressive yuv420p)
- Audio Codec    : AAC Stereo (44,100 Hz, 192 kbps)
- Visual Style   : Obsidian dark (#070B12), emerald accents (#10B981), subtle dynamic camera zoom

3. EXACT 50-SECOND STORYBOARD TIMELINE
--------------------------------------
Scene 1 (0:00 – 0:07 | 7.00s) — The Problem
  - Visual: The Freelancer's Privacy Dilemma (cloud data leakage vs on-device security).
  - Headline: "Your finances. Your privacy."
  - Voiceover: "Freelancers shouldn't have to risk their financial privacy just to organize receipts. Meet PocketLedger AI."

Scene 2 (0:07 – 0:14 | 7.00s) — Open-Weight AI
  - Visual: Real PocketLedger AI System Status dashboard highlighting Google Gemma 2B running locally via Ollama.
  - Headline: "Open-weight AI | Local inference"
  - Voiceover: "Powered by open-weight AI through Ollama, PocketLedger is designed to process financial documents with privacy in mind."

Scene 3 (0:14 – 0:22 | 8.00s) — Receipt Extraction
  - Visual: Document Inbox showing receipt upload and extraction into structured financial fields.
  - Headline: "Receipt → Structured data"
  - Voiceover: "Upload a receipt, extract key expense details, and turn unstructured text into organized financial records."

Scene 4 (0:22 – 0:33 | 11.00s) — Deterministic Validation
  - Visual: Side-by-side Review Modal with live mathematical reconciliation check (Subtotal + Tax - Discount + Charges = Total).
  - Headline: "AI extraction. Deterministic validation."
  - Voiceover: "Then, deterministic validation checks the numbers. AI extracts the details, but financial rules verify the calculations—with human approval in the loop."

Scene 5 (0:33 – 0:41 | 8.00s) — Ledger & Export
  - Visual: Expense Ledger with multi-currency sorting, category breakdown, and formula-injection-safe CSV export.
  - Headline: "Review → Approve → Export"
  - Voiceover: "Approved expenses enter your ledger, ready for reporting and CSV export, with security-conscious handling of financial data."

Scene 6 (0:41 – 0:50 | 9.00s) — Final Call to Action
  - Visual: Minimal dark end-card displaying project name, GitHub repo, Render cloud demo link, and open-source license.
  - Headline: "PocketLedger AI | Open-source expense intelligence | github.com/tribhu05/pocketledger-ai"
  - Voiceover: "PocketLedger AI is open-source and built to put freelancers in control. Explore the code on GitHub. Your records, your control."

4. AUDIO & VOICEOVER IMPLEMENTATION NOTES
-----------------------------------------
- Spoken Narration Duration: 45.07 seconds (leaving natural 0.3s-0.5s pauses between scenes).
- Voice Generation:
  - Official ElevenLabs SDK (`elevenlabs` v2.73.1) is installed and configured in `scripts/generate_voiceover.py`.
  - When ELEVENLABS_API_KEY is detected in the environment, it automatically connects to ElevenLabs.
  - High-fidelity 24kHz Neural Voiceover was rendered via Edge-TTS (en-US-ChristopherNeural, pitch -1Hz, rate +18%) for an articulate, authentic startup founder delivery.
- Background Music: Custom-synthesized warm ambient drone pad (F9sus chord progression with smooth low-pass sweep) mixed softly at -24dB to ensure maximum vocal clarity.

5. PROJECT & DEPLOYMENT LINKS
-----------------------------
- Repository : https://github.com/tribhu05/pocketledger-ai
- Live Demo  : https://pocketledger-ai.onrender.com (Render Blueprint Docker service)
- License    : MIT License
================================================================================
