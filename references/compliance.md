# Compliance — the frame audit and channel rules

Stock footage is chosen by a machine from a public library. If the channel has
content rules, a machine-picked pool **will** eventually break them. In one real
production batch, 1 of 18 clips had to be dropped; in another, "ghost ship" as a
search term returned Halloween costume clips. The audit is not optional.

## Configuring rules

`~/.storycast/config.json` → `content_rules` is a list of free-form strings, e.g.:

```json
"content_rules": ["no_music", "no_women_on_screen", "no_alcohol", "no_children"]
```

Common patterns seen in the wild: no music at all; no women anywhere in frame
(including background extras and unverifiable figures); no alcohol; no children;
nothing mocking religious figures. Enforce exactly what the user listed — no
more, no less — and keep the list in config so every future episode inherits it.

## The audit gate

1. After MPT's materials stage, run scripts/audit_sheet.py over the pool.
2. **Read the sheet yourself** as images — every tile, every clip.
3. A clip fails if it breaks any rule, or if you cannot verify it doesn't
   (e.g. a distant figure you can't identify). **Ambiguous fails.**
4. Assemble only from passing clips (`--video-source local --video-materials ...`).
5. After assembly, optionally re-verify the final cut with a second contact
   sheet (frames every ~3s) for episodes with strict rules.

If more than a third of the pool fails, the search terms are the problem.
Rewrite them as literal visual nouns ("sailing ship ocean sunset", "storm waves,
empty deck") instead of thematic words ("mystery", "ghost", "crew") that pull
costume and stock-footage junk.

## Music

`--bgm-type none` in every MPT call. The custom-pipeline alternative is a
synthesized ambience bed (pink noise low-passed) — that is noise, not music, but
if the channel's rules say "no music at all" and the user is strict, ask once
whether ambient nature sound counts, and record the answer in config.

## Captions and watermarks

MPT cuts ship without captions or watermarks (deliberately — see SKILL.md).
To add them:

- Captions: sentence-timed ASS (proportional to character count is fine for v1;
  word-synced via Whisper timestamps if the user wants more). Arabic: libass +
  HarfBuzz shapes RTL correctly with Noto Naskh Arabic.
- Watermark: a second ASS dialogue event, top-center (`Alignment: 8`), small and
  semi-transparent. Bottom placement collides with captions — put it at the top.
- Watermark text = the channel handle per language from config.

## End fade

Every cut gets an end fade-to-black + audio fade (scripts/fade.py, default
1.3s). Cuts that stop abruptly feel unfinished; the fade also gives shorts a
clean loop point back to the hook.
