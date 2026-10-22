# MoneyPrinterTurbo reference

MoneyPrinterTurbo (MPT) is the stock-footage engine: it searches Pexels by keyword,
downloads clips, and concatenates them to the length of your narration.

## Install

```bash
git clone --depth 1 https://github.com/harry0703/MoneyPrinterTurbo.git ~/MoneyPrinterTurbo
cd ~/MoneyPrinterTurbo
cp config.example.toml config.toml
uv sync        # installs the right Python + deps into .venv
```

All commands below run from `~/MoneyPrinterTurbo` via `uv run python cli.py ...`.
The CLI runs the pipeline directly — no Redis or web server needed (that's only
for the WebUI/API mode).

## config.toml wiring

Only two things must be set:

```toml
pexels_api_keys = ["YOUR_PEXELS_KEY"]      # https://www.pexels.com/api/ (free)

llm_provider = "openai"                    # any OpenAI-compatible provider works
openai_api_key = "YOUR_KEY"
openai_base_url = "https://api.groq.com/openai/v1"   # Groq free tier is fine
openai_model_name = "openai/gpt-oss-120b"            # or any chat model on the account
```

The LLM only writes/extracts the material search terms, so a free-tier model is fine.

Recommended extras:

```toml
subtitle_provider = "edge"   # irrelevant when subtitles are disabled, but keeps
                             # the heavy Whisper model from ever downloading
```

On an 8 GB machine avoid Whisper entirely — run MPT with `--no-subtitle-enabled`
and add your own captions in post (libass + Noto Naskh Arabic renders Arabic RTL
correctly; plain DejaVu works for Latin scripts).

## The two invocations StoryCast uses

### 1. Download the footage pool (audit these clips — always)

```bash
uv run python cli.py --video-script "$(cat scripts/en.txt)" \
  --video-language en-US \
  --video-terms "sailing ship ocean sunset, tall ship mast rigging, stormy sea waves" \
  --video-source pexels --video-aspect 9:16 --video-clip-duration 3 \
  --voice-name no-voice \
  --custom-audio-file audio/en.wav \
  --no-subtitle-enabled --bgm-type none \
  --stop-at materials
```

The JSON result lists the downloaded `materials` paths. Audit them
(scripts/audit_sheet.py) before anything else.

### 2. Assemble from the approved clips only

```bash
uv run python cli.py --video-script "$(cat scripts/en.txt)" \
  --video-language en-US \
  --video-source local \
  --video-materials "approved1.mp4,approved2.mp4,..." \
  --video-aspect 9:16 --image-motion zoom --video-clip-duration 3 \
  --voice-name no-voice \
  --custom-audio-file audio/en.wav \
  --no-subtitle-enabled --bgm-type none \
  --stop-at video
```

### Flag notes

- `--custom-audio-file` + `--voice-name no-voice`: your finished narration is the
  soundtrack; MPT never generates its own TTS. The video is cut to the audio's length.
- `--no-subtitle-enabled --bgm-type none`: keep music out and captions in your own hands.
- `--video-terms` are English phrases even for non-English episodes — Pexels indexes
  almost nothing else. 3–4 terms, chosen to be people-free by design.
- `--video-clip-duration 3` gives snappy cuts; raise for slower pacing.
- `--stop-at materials|video` bounds the run; `terms` stage needs the LLM, `local`
  source skips it.

## Gotchas learned in production

- A transient `downloaded 0 videos` / materials-stage failure happens; retry once
  before changing anything.
- Loose search terms pull junk: "ghost ship" once returned Halloween costume clips.
  Write literal, visual terms and keep the audit gate.
- MPT's final render is just ffmpeg; expect ~2–4 min per 60s vertical cut on an
  8 GB laptop.
- Output lands in `storage/tasks/<task-id>/final-1.mp4`; the JSON stdout has the path.
