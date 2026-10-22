---
name: storycast
description: Turn one story into finished, faceless short videos for multiple languages. Use when the user wants to create faceless channel videos, bilingual/multilingual story videos, TTS narration videos, stock-footage story videos, or mentions story channels, bedtime stories, MoneyPrinterTurbo, voice cloning narration, or episode production — even if they just say "make an episode" or "produce this story as a video". Includes a guided setup interview (storycast-setup) that wires every API key and renders one test episode.
---

# StoryCast

One story in. Compliant, narrated, vertical videos out — one per language.

StoryCast is a production pipeline for faceless story channels. You write (or receive) a story, narrate it with premium TTS voices, cut it over real stock footage with MoneyPrinterTurbo, audit every frame against the channel's content rules, and deliver final vertical cuts.

The pipeline in one line:

```
story → scripts (per language) → TTS narration → MoneyPrinterTurbo (stock footage)
      → frame audit → fade + polish → final MP4 per language
```

This workflow produced real published episodes (a two-language Mary Celeste episode, four final cuts, zero compliance violations). Follow it exactly the first time; improvise only after it works.

## Step 0 — Check setup

Read the user's StoryCast config at `~/.storycast/config.json`. If it exists and lists the needed keys, skip to Step 3. If it does not exist, the skill is not set up yet: tell the user you'll run the setup interview, then follow `storycast-setup` below.

## storycast-setup — the interview

Run this as a conversation. Ask the questions in order, wait for answers, validate as you go. Never ask for a key the user already answered. At the end, write `~/.storycast/config.json` and produce one test episode so the user sees a result before the interview is "done".

### Questions

1. **Languages?** Any set works (e.g. Arabic + English, English only, Spanish + English). Each language needs a narration voice later. Record the language codes (`ar`, `en`, ...).
2. **Channel names and handles?** One per language (e.g. "قصص قبل النوم" @qasasqablalnawm / "Nightfall Tales" @NightfallTales). Used for watermarks.
3. **Narration voice per language?** Offer the catalogs from `references/voices.md`. The proven pair: Groq Orpheus `fahad` for Arabic, Deepgram Flux `cliff` for English. Users can ask for demos — generate a short sample per candidate voice (scripts/tts.py) and let them listen before choosing.
4. **API keys?** Ask for each, then validate with a real test call before saving:
   - Groq (key + https://api.groq.com/openai/v1) — Arabic TTS and/or LLM. Validate: `curl -s https://api.groq.com/openai/v1/models -H "Authorization: Bearer $KEY"`.
   - Deepgram — English (or any language) TTS. Validate: a 1-word synthesis call to `https://api.deepgram.com/v2/speak?model=<voice>`.
   - Pexels — stock footage. Validate: `curl -s -H "Authorization: $KEY" "https://api.pexels.com/videos/search?query=ocean&per_page=1"`.
   Keys live only in the user's local config. Never print them back in full after saving.
5. **MoneyPrinterTurbo installed?** If not: `git clone --depth 1 https://github.com/harry0703/MoneyPrinterTurbo.git ~/MoneyPrinterTurbo` then `cd ~/MoneyPrinterTurbo && uv sync`. Wire its `config.toml`: paste the Pexels key into `pexels_api_keys`, and point the LLM at any OpenAI-compatible provider the user has (Groq works: `llm_provider = "openai"`, `openai_base_url = "https://api.groq.com/openai/v1"`, `openai_model_name = "openai/gpt-oss-120b"`). See `references/moneyprinterturbo.md`.
6. **Content rules?** Ask directly: "Any content rules I should enforce on every frame?" Common ones (all supported natively): no music, no alcohol, no women on screen, no people at all, religious sensitivities. Record the list — the audit in Step 5 enforces exactly these, nothing more.
7. **Output folder?** Where episodes land (default `~/Videos/StoryCast/`).

### After the interview

Save the config, then produce a **test episode** from a one-paragraph story the user picks, following Steps 1–6 below, and show the result. Setup is not done until one real video plays.

Config shape:

```json
{
  "languages": [
    {"code": "ar", "channel": "قصص قبل النوم", "handle": "@qasasqablalnawm",
     "tts": {"provider": "groq", "model": "canopylabs/orpheus-arabic-saudi", "voice": "fahad", "api_key_env": "GROQ_API_KEY"}},
    {"code": "en", "channel": "Nightfall Tales", "handle": "@NightfallTales",
     "tts": {"provider": "deepgram", "model": "flux-cliff-en", "voice": "cliff", "api_key_env": "DEEPGRAM_API_KEY"}}
  ],
  "keys": {"GROQ_API_KEY": "...", "DEEPGRAM_API_KEY": "...", "PEXELS_API_KEY": "..."},
  "mpt_path": "~/MoneyPrinterTurbo",
  "content_rules": ["no_music", "no_women_on_screen"],
  "output_dir": "~/Videos/StoryCast"
}
```

API keys belong in this file (chmod 600 it) or in environment variables — never in the repo, never in chat logs.

## Step 1 — Write the scripts

One story becomes one script file per language. Rules that made the produced episodes work:

- 120–150 words per language ≈ 50–70s of narration. Vertical shorts live in that range.
- Hook in the first sentence: a cold-open fact, not a greeting ("In 1872, a ship was found sailing alone across the Atlantic." — not "Today I'll tell you about...").
- End with the channel's call-to-action line ("Follow for a new true story, every night.").
- **Arabic (and other scripts with optional diacritics): write fully vocalized** — with tashkeel. TTS pronunciation of bare Arabic is unreliable; vocalized text fixed mispronunciations in testing. If a voice sounds over-articulated, test a plain-text variant before abandoning vocalization.
- Save as `<episode-dir>/scripts/<lang>.txt`.

## Step 2 — Narrate

Use `scripts/tts.py`:

```bash
python3 scripts/tts.py --config ~/.storycast/config.json --lang en \
  --script <episode>/scripts/en.txt --out <episode>/audio/en.wav
```

It dispatches per language to the configured provider (Groq OpenAI-compatible speech endpoint, or Deepgram v2 speak) and writes audio. Sanity-check: duration should be 45–75s for a 120–150-word script; if a call fails, read the error — Groq Orpheus only outputs WAV and requires a listed voice; Deepgram v2 takes the model as a query parameter.

## Step 3 — Stock footage pool

MoneyPrinterTurbo downloads the pool. From its directory:

```bash
uv run python cli.py --video-script "$(cat <episode>/scripts/en.txt)" \
  --video-language en-US \
  --video-terms "sailing ship ocean sunset, tall ship mast rigging, stormy sea waves" \
  --video-source pexels --video-aspect 9:16 --video-clip-duration 3 \
  --voice-name no-voice \
  --custom-audio-file <episode>/audio/en.wav \
  --no-subtitle-enabled --bgm-type none \
  --stop-at materials
```

Notes that matter:

- `--video-terms` are English search phrases even for non-English episodes (Pexels indexes little else). 3–4 terms, all people-free by design (see Step 4).
- `--custom-audio-file` feeds your finished narration straight in; `--voice-name no-voice` stops MPT from generating its own robotic voice.
- MPT's LLM stage (script/terms) runs on any OpenAI-compatible provider — Groq's free tier works well.
- A transient "downloaded 0 videos" failure happens; retry once before debugging.
- Same footage pool can serve every language of the episode — assemble per language from the same audited clips for brand consistency.

## Step 4 — The frame audit (mandatory, never skip)

MPT picks clips automatically. Automatic picks will eventually include something the channel must not show. The audit is the fix, and it is a hard gate:

1. Build a contact sheet — 3 frames per clip, tiled into one image. Use `scripts/audit_sheet.py`:

```bash
python3 scripts/audit_sheet.py --clips <clip1.mp4> <clip2.mp4> ... --out sheet.jpg
```

2. Read the sheet. Check every clip against the channel's content rules from config (default rules include: no women anywhere in frame — including background extras — no music, plus anything else the user listed). When a person appears and the rule set requires certainty, and the frames are too small to be certain, the clip fails — ambiguous fails, always.
3. Drop failing clips from the list. If more than a third fail, rewrite the search terms (people-free nouns: "sailing ship ocean sunset, storm waves, empty deck") and re-download.
4. Only approved clips continue to Step 5.

Real-world rate from the produced episode: 1 in 18 clips failed the audit. It happens on every batch. That is why this step exists.

## Step 5 — Assemble

Feed only the approved clips back to MPT as local materials:

```bash
uv run python cli.py --video-script "$(cat <episode>/scripts/<lang>.txt)" \
  --video-language <lang> \
  --video-source local \
  --video-materials "<approved1.mp4>,<approved2.mp4>,..." \
  --video-aspect 9:16 --image-motion zoom --video-clip-duration 3 \
  --voice-name no-voice \
  --custom-audio-file <episode>/audio/<lang>.wav \
  --no-subtitle-enabled --bgm-type none \
  --stop-at video
```

`--no-subtitle-enabled` and `--bgm-type none` are deliberate: MPT's subtitles need a heavy Whisper model and its music library violates no-music rules. Burn your own captions (ASS subtitles with a proper RTL font for Arabic — Noto Naskh Arabic renders correctly via libass) and skip music entirely.

## Step 6 — Polish and deliver

Post-process every cut with an end fade:

```bash
ffmpeg -i final.mp4 -vf "fade=t=out:st=$((DUR-1.3)):d=1.3" -af "afade=t=out:st=$((DUR-1.3)):d=1.3" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart final-faded.mp4
```

(On an 8 GB laptop a 70s 1080×1920 re-encode takes ~2 minutes; don't go heavier than crf 20.)

Deliver every language cut as a clickable file link, in a table with language, length, and size. Then ask for the style/format verdict before producing the next episode.

## If something breaks

| Symptom | Cause → fix |
|---|---|
| TTS 400 "voice is required" | Provider needs a listed voice — see `references/voices.md` |
| Groq TTS 400 on mp3 | Orpheus models only output `wav` |
| MPT "downloaded 0 videos" | Transient Pexels failure — retry once |
| MPT cut contains rule-breaking frames | Skipped audit. Go back to Step 4; never ship unaudited footage |
| Captions garbled in Arabic | Missing RTL font — install `noto-fonts` Arabic variants; libass shapes via HarfBuzz |
| MPT cut ends abruptly | Skipped the Step 6 fade |

## Deeper references

- `references/moneyprinterturbo.md` — full MPT setup, config.toml wiring, CLI flags, pipeline stages
- `references/voices.md` — voice catalogs per provider, demo-generation workflow for voice selection
- `references/compliance.md` — content-rule patterns, audit workflow details, caption/watermark placement
- `references/recipes.md` — script structures that work (cold-open hooks, pacing per language, CTA patterns)
