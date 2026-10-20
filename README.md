# LazyLore (with Local Open-Weight AI)

A Python FastAPI microservice that fills open caregiver shifts by fanning out SMS (and escalating to voice), accepting the first valid claim, and handling race conditions safely.

**Hacktoberfest 2026 – Week 3 “Slow and Steady”**  
The service now uses a **local open-weight model** (via Ollama) to understand messy real-world replies instead of brittle keyword matching. This means:

- messages never leave your machine
- Zero ongoing LLM API cost
- Works fully offline once the model is pulled
- Handles natural language (“yeah sure”, “nah I’m booked”, “what time again?”) so coordinators can be lazy

## Quick Start (with open-weight model)

### 1. Install & start Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve          # leave this running
ollama pull gemma2:2b # or phi3:mini / llama3.2:1b