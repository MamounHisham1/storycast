# Voice catalogs

How to pick a narration voice per language, and the exact API contracts.

## Workflow for voice selection

Never pick a voice for the user. Generate a 20-second demo of the same sample
script in every candidate voice (scripts/tts.py), deliver the files, and let the
user listen. One user compared six Arabic voices and rejected four they expected
to like — ears beat descriptions.

## Groq (provider: `groq`)

- Endpoint: `POST https://api.groq.com/openai/v1/audio/speech`
- Key: https://console.groq.com (free tier available)
- **Response format: only `wav`.** Passing mp3 returns 400.
- Arabic model: `canopylabs/orpheus-arabic-saudi`
  - Voices: `fahad`, `sultan`, `abdullah` (male) — `noura`, `lulwa`, `aisha` (female)
  - Voice is required; an unknown voice returns 400 listing all valid names.
  - Arabic handles vocalized (tashkeel) text well; test plain text too — pacing
    differs per voice (one voice read the same script 40% slower than another,
    which suited a calm channel better).
- English model: `canopylabs/orpheus-v1-english`
- Chat models (usable for MPT's LLM stage): `openai/gpt-oss-120b`,
  `openai/gpt-oss-20b`, `qwen/qwen3.8-27b` — model availability varies per account.

## Deepgram (provider: `deepgram`)

- Endpoint: `POST https://api.deepgram.com/v2/speak?model=<model>` (model in the
  **query string**, not the body — this differs from most APIs)
- Auth header: `Authorization: Token <key>` (Token, not Bearer)
- Key: https://console.deepgram.com (free tier available)
- English model: `flux-cliff-en` (voice is baked into the model name; speed and
  expressivity as query params: `&speed=1&expressivity=1`)
- Output: mp3 by default.

## Free fallback (provider: `edge`, optional)

`edge-tts` (Microsoft neural voices, free, no key) works for any language and is
the zero-cost fallback — but the generic voices are recognizably "default TTS".
One produced episode used Deepgram for English and Groq for Arabic; both ran
inside their free tiers for daily production.

## Voice demo pattern (for setup interviews)

1. Take a 2–3 sentence sample in the target language.
2. Generate one file per candidate voice (scripts/tts.py with a temporary config).
3. Deliver all files as clickable links with duration notes.
4. Record the winner in `~/.storycast/config.json`.

Duration note: the same text can render 20–30s depending on voice. Slower voices
suit calm/bedtime channels; check the pacing, not just the timbre.
