#!/usr/bin/env python3
"""
End-to-end: topic -> script (Gemini) -> voice (edge-tts, free) -> stick-figure
animation (Manim) -> final muxed MP4 with burned-in captions.

Usage:
  python3 generate_episode.py --topic "The night the fire almost went out"

Env vars required:
  GEMINI_API_KEY
Optional:
  GEMINI_MODEL   (default: gemini-3.6-flash)
  TTS_VOICE      (default: en-US-AndrewNeural)
"""

import argparse
import json
import os
import re
import subprocess
import sys

CHARACTER_BIBLE = """
Korr  - the steady hunter-provider. Calm, short sentences, protective.
Nala  - the fire keeper. Quick-witted, blunt, comic timing, fidgets with tools.
Tarek - the curious teenager. Impulsive, asks the question the viewer is thinking.
Edda  - the elder. Warm, unhurried, delivers the "real history" teaching payoff.
"""

POSES = ["idle", "point_right", "point_left", "sit", "gesture_up", "lean_forward"]
ENVIRONMENTS = ["ENV001", "ENV002", "ENV003", "ENV004", "ENV005"]
ENV_NAMES = {
    "ENV001": "Open Ice Shore (outdoor, sunset, wind)",
    "ENV002": "Bone Hut Interior (indoor, fire pit, mammoth ribs)",
    "ENV003": "Forest Camp (dense pine treeline, dusk)",
    "ENV004": "Coastal Cliffs (rocky sea coast, grey overcast)",
    "ENV005": "Blizzard (whiteout storm, no fire, high danger)",
}
LEDGER_PATH = "ledger.json"


def load_ledger() -> dict:
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH) as f:
            return json.load(f)
    raise FileNotFoundError(
        "ledger.json not found in repo root — this is the show's memory. "
        "Add the seed ledger.json before running."
    )


def save_ledger(ledger: dict):
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2)


def call_gemini(ledger: dict) -> dict:
    import time
    import urllib.error
    import urllib.request

    api_key = os.environ["GEMINI_API_KEY"]
    model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    arc_topic = ledger["current_arc"] or ledger["storyline_queue"][0]
    part_number = ledger["next_part"]
    env_options = "\n".join(f"  {k} = {v}" for k, v in ENV_NAMES.items())

    prompt = f"""You are the showrunner for "Survive History," an Ice Age survival stick-figure
Short series. You reason about story continuity — you decide when a Part continues the
current Arc and when an Arc wraps up, exactly like a real showrunner tracking a season.

Locked cast:
{CHARACTER_BIBLE}

Environments available (pick the one that fits this Part's scene):
{env_options}

CURRENT SHOW STATE (this is memory — respect it, don't contradict it):
- Arc topic: "{arc_topic}"
- This is Part {part_number} of a planned {ledger['total_parts_planned']}-part arc
- World state: {json.dumps(ledger['world_state'])}
- Characters: {json.dumps(ledger['characters'])}
- Last cliffhanger to pay off: {ledger['last_cliffhanger'] or "none, this is Part 1"}

Write this next Part: 6-8 short shots (each ~8-15 words, punchy short-form pace),
at least 2 different characters, opens on danger/tension, ends on a cliffhanger UNLESS
this Part number equals the planned total parts, in which case wrap the Arc with a
satisfying resolution + tease the next Arc instead.

Return ONLY valid JSON, no markdown fences, no commentary, in exactly this schema:
{{
  "environment": "one of {ENVIRONMENTS}",
  "shots": [
    {{"character": "Korr|Nala|Tarek|Edda", "pose": "one of {POSES}", "line": "spoken line", "caption": "same or shortened"}}
  ],
  "arc_status": "continuing" or "arc_complete",
  "cliffhanger": "one sentence describing what the NEXT part must pay off (empty string if arc_complete)",
  "world_state_updates": {{"season": "...", "location": "ENV00X", "fire": "...", "weather": "..."}},
  "character_updates": {{"Korr": "...", "Nala": "...", "Tarek": "...", "Edda": "..."}}
}}"""

    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(url, data=body, headers={"content-type": "application/json"})

    last_error = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
            break
        except urllib.error.HTTPError as e:
            last_error = e
            if e.code in (429, 503) and attempt < 4:
                wait = 10 * (attempt + 1)
                print(f"  Gemini returned {e.code}, retrying in {wait}s (attempt {attempt + 1}/5)...")
                time.sleep(wait)
                continue
            raise
    else:
        raise last_error

    text = data["candidates"][0]["content"]["parts"][0]["text"]
    text = re.sub(r"^```json|```$", "", text.strip(), flags=re.M).strip()
    episode = json.loads(text)

    if episode.get("environment") not in ENVIRONMENTS:
        episode["environment"] = ledger["world_state"]["location"]

    episode["_arc_topic"] = arc_topic
    episode["_part_number"] = part_number
    return episode


def update_ledger(ledger: dict, episode: dict) -> dict:
    if episode["arc_status"] == "arc_complete":
        finished_topic = episode["_arc_topic"]
        remaining_queue = [t for t in ledger["storyline_queue"] if t != finished_topic]
        ledger["current_arc"] = remaining_queue[0] if remaining_queue else None
        ledger["storyline_queue"] = remaining_queue
        ledger["next_part"] = 1
        ledger["last_cliffhanger"] = None
    else:
        ledger["current_arc"] = episode["_arc_topic"]
        ledger["next_part"] = episode["_part_number"] + 1
        ledger["last_cliffhanger"] = episode.get("cliffhanger", "")

    ledger["world_state"].update(episode.get("world_state_updates", {}))
    ledger["characters"].update(episode.get("character_updates", {}))
    ledger["session_log"].insert(0, {
        "arc": episode["_arc_topic"],
        "part": episode["_part_number"],
        "status": episode["arc_status"],
    })
    return ledger


def synthesize_voice(episode: dict, workdir: str) -> list:
    voice = os.environ.get("TTS_VOICE", "en-US-AndrewNeural")
    timing = []
    clip_paths = []

    for i, shot in enumerate(episode["shots"]):
        mp3_path = os.path.join(workdir, f"shot_{i}.mp3")
        subprocess.run(
            ["edge-tts", "--voice", voice, "--text", shot["line"], "--write-media", mp3_path],
            check=True,
        )
        duration = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", mp3_path],
            check=True, capture_output=True, text=True,
        ).stdout.strip())
        timing.append({"shot_index": i, "duration": round(duration + 0.4, 2)})  # pad for breathing room
        clip_paths.append(mp3_path)

    return timing, clip_paths


def concat_audio(clip_paths: list, workdir: str) -> str:
    list_path = os.path.join(workdir, "concat_list.txt")
    with open(list_path, "w") as f:
        for p in clip_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    out_path = os.path.join(workdir, "narration.mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", out_path],
        check=True, capture_output=True,
    )
    return out_path


def render_manim(config_path: str, timing_path: str, workdir: str) -> str:
    env = os.environ.copy()
    env["EPISODE_CONFIG"] = os.path.abspath(config_path)
    env["EPISODE_TIMING"] = os.path.abspath(timing_path)

    subprocess.run(
        ["manim", "-qm", "survive_history_scene.py", "Episode", "--media_dir", os.path.join(workdir, "media")],
        cwd="survive_history", env=env, check=True,
    )

    media_dir = os.path.join(workdir, "media", "videos", "survive_history_scene", "720p30")
    for f in os.listdir(media_dir):
        if f.endswith(".mp4"):
            return os.path.join(media_dir, f)
    raise FileNotFoundError("Manim did not produce an mp4")


def mux_final(video_path: str, audio_path: str, out_path: str):
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-i", audio_path,
         "-c:v", "copy", "-c:a", "aac", "-shortest", out_path],
        check=True, capture_output=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="output")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    print("→ Reading show ledger (memory)...")
    ledger = load_ledger()
    print(f"  Arc: {ledger['current_arc'] or ledger['storyline_queue'][0]} | Part {ledger['next_part']}")

    print("→ Generating next Part with Gemini (arc-aware)...")
    episode = call_gemini(ledger)
    print(f"  {len(episode['shots'])} shots, environment {episode['environment']}, status: {episode['arc_status']}")

    config_path = os.path.join(args.outdir, "config.json")
    with open(config_path, "w") as f:
        json.dump(episode, f, indent=2)

    print("→ Synthesizing voice (edge-tts)...")
    timing, clip_paths = synthesize_voice(episode, args.outdir)
    timing_path = os.path.join(args.outdir, "audio_timing.json")
    with open(timing_path, "w") as f:
        json.dump(timing, f, indent=2)

    print("→ Concatenating narration track...")
    narration_path = concat_audio(clip_paths, args.outdir)

    print("→ Rendering stick-figure animation with Manim...")
    video_path = render_manim(config_path, timing_path, args.outdir)

    print("→ Muxing final video...")
    final_path = os.path.join(args.outdir, "final_stickman.mp4")
    mux_final(video_path, narration_path, final_path)

    print("→ Updating ledger (show memory) for next run...")
    ledger = update_ledger(ledger, episode)
    save_ledger(ledger)

    print(f"\nDONE: {final_path}")
    print(f"Next run will continue from: {ledger['current_arc']}, Part {ledger['next_part']}")


if __name__ == "__main__":
    sys.exit(main())
