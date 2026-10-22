#!/usr/bin/env python3
"""StoryCast TTS — narrate a script via the provider configured for a language.

Providers:
  groq     -> Groq speech API (Orpheus models; WAV output only)
  deepgram -> Deepgram v2 speak (Flux models)

Usage:
  python3 tts.py --config ~/.storycast/config.json --lang en \
      --script scripts/en.txt --out audio/en.wav [--style plain]

Keys are read from the config's "keys" object or from the environment
(GROQ_API_KEY / DEEPGRAM_API_KEY).
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def load_config(path):
    with open(os.path.expanduser(path), encoding="utf-8") as f:
        return json.load(f)


def key_for(cfg, env_name):
    return cfg.get("keys", {}).get(env_name) or os.environ.get(env_name)


def synth_groq(key, model, voice, text, out):
    payload = json.dumps({
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": "wav",  # Orpheus models only accept wav
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/audio/speech",
        data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "StoryCast/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"Groq TTS failed ({e.code}): {e.read().decode()[:400]}")
    with open(out, "wb") as f:
        f.write(data)


def synth_deepgram(key, model, text, out):
    url = f"https://api.deepgram.com/v2/speak?model={model}"
    payload = json.dumps({"text": text}).encode()
    req = urllib.request.Request(
        url, data=payload,
        headers={"Authorization": f"Token {key}", "Content-Type": "application/json", "User-Agent": "StoryCast/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"Deepgram TTS failed ({e.code}): {e.read().decode()[:400]}")
    with open(out, "wb") as f:
        f.write(data)


def main():
    ap = argparse.ArgumentParser(description="StoryCast TTS")
    ap.add_argument("--config", default="~/.storycast/config.json")
    ap.add_argument("--lang", required=True, help="language code from config, e.g. en, ar")
    ap.add_argument("--script", required=True, help="path to the script text file")
    ap.add_argument("--out", required=True, help="output audio path")
    ap.add_argument("--style", choices=["vocalized", "plain"], default="vocalized",
                    help="vocalized keeps the script as written; plain strips Arabic tashkeel")
    args = ap.parse_args()

    cfg = load_config(args.config)
    lang = next((l for l in cfg["languages"] if l["code"] == args.lang), None)
    if not lang:
        sys.exit(f"language '{args.lang}' not in config — run storycast-setup")

    text = open(os.path.expanduser(args.script), encoding="utf-8").read().strip()
    if args.style == "plain":
        # strip Arabic diacritics (U+064B–U+0652, U+0670)
        text = "".join(ch for ch in text if not (0x064B <= ord(ch) <= 0x0652 or ord(ch) == 0x0670))

    tts = lang["tts"]
    provider = tts["provider"]
    env_name = tts.get("api_key_env", f"{provider.upper()}_API_KEY")
    key = key_for(cfg, env_name)
    if not key:
        sys.exit(f"missing API key: {env_name} not in config or environment")

    if provider == "groq":
        synth_groq(key, tts["model"], tts["voice"], text, args.out)
    elif provider == "deepgram":
        synth_deepgram(key, tts["model"], text, args.out)
    else:
        sys.exit(f"unknown provider: {provider}")

    kb = os.path.getsize(args.out) / 1024
    print(f"OK {args.out} ({kb:.0f} KB) via {provider}:{tts.get('voice', tts['model'])}")


if __name__ == "__main__":
    main()
