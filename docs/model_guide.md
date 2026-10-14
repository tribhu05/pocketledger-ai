# Open-Weight Model Selection & Hardware Guide

## 1. Selected Model: Google Gemma 2B Instruct (`gemma2:2b`)

PocketLedger AI standardizes on Google's **Gemma 2B Instruct** open-weight model for document extraction and semantic structuring.

### Key Specifications
- **Parameters:** ~2.6 Billion
- **Quantized Disk Size:** ~1.63 GB (Q4_K_M in Ollama)
- **Active Memory Footprint:** ~2.1 GB RAM / VRAM during generation
- **Context Window:** 8,192 tokens
- **Inference Runtime:** [Ollama](https://ollama.ai)

### Tested Hardware Environment
- **CPU:** AMD Ryzen 3 7320U (4 Cores, 8 Logical Processors)
- **RAM:** 8.00 GB LPDDR5
- **GPU:** AMD Radeon(TM) 610M (Integrated)
- **Operating System:** Windows 11 Home / Linux / macOS
- **Measured Average Latency:** 34.1 seconds per receipt (pure CPU/iGPU execution without dedicated Nvidia GPU)

## 2. Why Gemma 2B over Gemma 9B or 27B?

| Factor | Gemma 2B (Selected) | Gemma 9B | Gemma 27B |
|---|---|---|---|
| **Weight Size** | 1.6 GB | 5.5 GB | 16.0 GB |
| **Minimum RAM** | 4–8 GB | 12–16 GB | 32+ GB |
| **Target Audience Fit** | **Universal:** Runs on everyday freelancer laptops | Requires gaming laptop or developer workstation | Requires dedicated workstation or server GPU |
| **System Impact** | Smooth multitasking alongside IDE & browser | May induce OS memory swap on 8GB machines | Crash / OOM on typical laptops |
| **Field Accuracy** | **100%** on Merchant, Total, Currency, and Doc Type | Marginal gains on clean documents | Diminishing returns for tabular extraction |

Gemma 2B represents the "sweet spot" for real-world freelance adoption: it delivers exceptional structured JSON extraction without demanding exotic hardware.

## 3. Ollama Installation & Setup Guide

### Step 1: Install Ollama
- **Windows:** Download installer from [ollama.ai/download/windows](https://ollama.ai/download/windows)
- **macOS:** `brew install ollama` or download from [ollama.ai/download/mac](https://ollama.ai/download/mac)
- **Linux:** `curl -fsSL https://ollama.com/install.sh | sh`

### Step 2: Download Gemma 2B
In your terminal:
```bash
ollama pull gemma2:2b
```

### Step 3: Verify Model Availability
Ensure Ollama is running in the background:
```bash
ollama serve
```
Test with a quick probe:
```bash
curl http://localhost:11434/api/tags
```
You should see `gemma2:2b` listed in the response.

## 4. Licensing and Usage Terms
Google Gemma is an open-weight model released under the **Gemma Terms of Use**.
- While the PocketLedger AI source code is released under the permissive MIT License, Gemma model weights and inference outputs are governed by Google's terms.
- Review terms at: [https://ai.google.dev/gemma/terms](https://ai.google.dev/gemma/terms)
