# StoryCast

One story in. Finished, faceless videos out — one per language, narrated with premium TTS voices, cut over real stock footage, audited frame by frame against your content rules.

StoryCast is an agent skill that runs a complete faceless-channel production pipeline: you hand your agent a story (or just a topic), it writes the scripts in every language you publish, narrates them with voices you picked by ear, cuts them over Pexels stock footage with [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo), audits every frame against your content rules, and delivers final vertical cuts with fade-outs — ready to upload.

It exists because running a faceless channel is 90% repetitive production: the same story written twice, narrated twice, cut twice, checked twice, every day, forever. StoryCast turns that into one conversation with your agent.

## What it produced

This skill is a field report, not a theory. It was extracted from a real two-channel operation — an Arabic channel (قصص قبل النوم) and its English sister (Nightfall Tales) — where it produced its first full episode end to end: the Mary Celeste, written natively in both languages, narrated in Fahad (Groq Orpheus) and cliff (Deepgram Flux), cut twice — once over public-domain maritime paintings, once over real ocean stock footage — frame-audited against the channel's content rules, and delivered as four final vertical cuts. The first stock-footage assembly was rejected by its own audit (Halloween costumes from a loose search term); the workflow caught it, rebuilt the clip pool, and re-rendered clean. That audit loop is a permanent part of the skill.

## Install

```
npx skills add MamounHisham1/storycast
```

or clone it into your agent's skills folder:

```
git clone https://github.com/MamounHisham1/storycast ~/.agents/skills/storycast
```

Works with any agent that reads SKILL.md files (Claude Code, Cursor, Codex, Copilot, Windsurf, Gemini, ZCode, and more).

## The setup interview

After installing, tell your agent:

```
storycast-setup
```

and it interviews you, in order:

1. Which languages do you publish in?
2. Channel names and handles (used for watermarks)?
3. Narration voices — it generates audible demos of every candidate voice and lets you choose by ear, not by description
4. API keys — Groq (Arabic TTS and/or the LLM stage), Deepgram (English TTS), Pexels (footage) — each validated with a real test call before saving
5. MoneyPrinterTurbo — cloned, installed, and its config wired automatically
6. Content rules — "no music", "no women on screen", "no alcohol", anything you want enforced on every frame
7. Output folder

Then it produces one full test episode from a story you pick. Setup isn't done until you've watched a real video.

Everything lands in `~/.storycast/config.json` (chmod 600). Keys never leave your machine.

## What it does

Per episode, per language:

1. **Script** — written natively per language (not translated), with a cold-open hook and a one-line call to action. Arabic is written fully vocalized (tashkeel) because TTS mispronounces bare Arabic — one of several things this workflow learned by breaking it first.
2. **Narration** — your locked voice per language via Groq speech or Deepgram. The same text rendered in different voices can differ 40% in pacing; the skill checks duration, not just audio.
3. **Footage pool** — MoneyPrinterTurbo downloads 15–20 vertical clips from Pexels using people-safe search terms. Your narration is fed in as the finished soundtrack; the engine never generates its own voice.
4. **The audit** — every clip rendered as frames on a contact sheet, every tile inspected against your rules. A clip that can't be verified fails. Ambiguous fails. This gate exists because in real production, 1 of 18 clips failed and "ghost ship" as a search term once returned Halloween costumes.
5. **Assembly** — only approved clips, cut to the narration's length, zoom motion, no engine music, no engine subtitles.
6. **Polish** — fade-to-black with audio fade, your channel watermark, optional burned captions (correct RTL Arabic shaping via libass).

## What you need

- An agent that reads SKILL.md files
- [uv](https://docs.astral.sh/uv/) (MoneyPrinterTurbo's dependency manager) and ffmpeg
- Free API keys: [Groq](https://console.groq.com) (TTS + LLM stage), [Deepgram](https://console.deepgram.com) (TTS alternative), [Pexels](https://www.pexels.com/api/) (footage)
- ~2 GB disk for MoneyPrinterTurbo and its clip cache

No paid tier is required for any of it at daily-production volume.

## Structure

```
storycast/
├── SKILL.md                    the pipeline + the setup interview
├── scripts/
│   ├── tts.py                  unified narration (Groq / Deepgram, per-language config)
│   ├── audit_sheet.py          frame contact sheets for the compliance audit
│   └── fade.py                 end fade-to-black + audio fade
└── references/
    ├── moneyprinterturbo.md    install, config wiring, CLI flags, production gotchas
    ├── voices.md               voice catalogs and API contracts per provider
    ├── compliance.md           content rules, the audit gate, captions, watermarks
    └── recipes.md              script structures: hooks, pacing, multi-language rules
```

## Content rules are first-class

Faceless channels live and die by platform policy and personal standards. StoryCast treats content rules as configuration, not vibes: whatever you list at setup is enforced as a hard gate on every episode. Ambiguous clips fail by default. The stock-footage pool is re-audited every single time, because a machine picking clips from a public library will eventually pick something you can't publish.

## Notes

- MoneyPrinterTurbo does the footage work; StoryCast tells it exactly what to do and vets what it brings back. Keep your MPT clone updated.
- Pexels' free tier comfortably covers daily production; Groq and Deepgram free tiers cover narration for a daily cadence.
- The audit is your agent reading frames, so it's only as strict as the rules you gave it. Write them honestly at setup.

MIT. Use it, fork it, ship it.
