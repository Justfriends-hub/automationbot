#!/usr/bin/env python3
"""
End-to-end: topic -> documentary script + scene breakdown (Gemini) ->
voice (edge-tts, free) -> matching stock clips (Pexels + Pixabay, free APIs) ->
ffmpeg assembly with burned-in captions -> thumbnail.

Enhanced for free cinematic quality:
- Gemini prompt asks for detailed scene descriptions and a unified style.
- Post-processing adds a film look (colour grade, vignette, slight grain).
- Optional background music (if a file called "background_music.mp3" exists).
- Improved TTS voice (default: en-US-ChristopherNeural, set via TTS_VOICE).

Env vars required:
  GEMINI_API_KEY
  PEXELS_API_KEY
  PIXABAY_API_KEY
Optional:
  GEMINI_MODEL   (default: gemini-3.6-flash)
  TTS_VOICE      (default: en-US-ChristopherNeural)
  DOCUMENTARY_STYLE  (e.g. "warm sepia" or "cold blue", default: "cinematic warm")
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

TOPICS_PATH = "topics_queue.json"
BACKGROUND_MUSIC = "background_music.mp3"   # optional, place in the same directory


# ---------- topic queue ----------

def load_topics() -> dict:
    with open(TOPICS_PATH) as f:
        return json.load(f)

def save_topics(state: dict):
    with open(TOPICS_PATH, "w") as f:
        json.dump(state, f, indent=2)

def pick_topic(state: dict) -> str:
    available = [t for t in state["topic_queue"] if t not in state["used_topics"]]
    if not available:
        state["used_topics"] = []
        available = state["topic_queue"]
    return available[0]


# ---------- script + scene breakdown ----------

def call_gemini(topic: str) -> dict:
    api_key = os.environ["GEMINI_API_KEY"]
    model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    # We ask for a unified style and detailed visual descriptions.
    prompt = f"""You are a cinematic historical documentary scriptwriter for a 60‑second YouTube Short. Topic: "{topic}"

Write a documentary‑style voiceover broken into 10–12 short scenes (one sentence each, ~10–16 words).
- Scene 1: hook
- Scenes 2–3: curiosity gap
- Build tension through the middle
- Scene final: resolution

For each scene also provide:
- A SPECIFIC STOCK FOOTAGE SEARCH QUERY (2–6 words) that will return real, relevant clips.
- A DETAILED VISUAL DESCRIPTION (mood, lighting, camera angle, colour palette) to guide post‑processing and to help find matching clips.

Also choose a UNIFIED CINEMATIC STYLE for the whole documentary (e.g. "warm sepia", "cold blue", "high contrast noir") – this will be applied globally.

Return ONLY valid JSON, no markdown, in this exact schema:
{{
  "title": "short YouTube title under 60 chars",
  "style": "one word or short phrase describing the overall look",
  "scenes": [
    {{
      "narration": "one sentence of voiceover",
      "visual_query": "2‑6 word stock search",
      "visual_description": "detailed description of lighting, mood, angle, colours"
    }}
  ]
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
                print(f"  Gemini returned {e.code}, retrying in {wait}s...")
                time.sleep(wait)
                continue
            raise
    else:
        raise last_error

    text = data["candidates"][0]["content"]["parts"][0]["text"]
    text = re.sub(r"^```json|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)


# ---------- voice (edge-tts) ----------

def synthesize_voice(script: dict, workdir: str) -> list:
    voice = os.environ.get("TTS_VOICE", "en-US-ChristopherNeural")  # more natural than Andrew
    timing = []
    clip_paths = []

    for i, scene in enumerate(script["scenes"]):
        mp3_path = os.path.join(workdir, f"scene_{i}.mp3")
        subprocess.run(
            ["edge-tts", "--voice", voice, "--text", scene["narration"], "--write-media", mp3_path],
            check=True,
        )
        duration = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", mp3_path],
            check=True, capture_output=True, text=True,
        ).stdout.strip())
        timing.append(round(duration + 0.3, 2))
        clip_paths.append(mp3_path)

    return timing, clip_paths


# ---------- stock footage ----------

def search_pexels(query: str) -> str | None:
    api_key = os.environ["PEXELS_API_KEY"]
    url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&orientation=portrait&per_page=1"
    req = urllib.request.Request(url, headers={"Authorization": api_key})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"    [Pexels error] {type(e).__name__}: {e}")
        return None
    videos = data.get("videos", [])
    if not videos:
        return None
    files = sorted(videos[0]["video_files"], key=lambda f: f.get("width", 0), reverse=True)
    for f in files:
        if f.get("width", 0) <= 1080:
            return f["link"]
    return files[-1]["link"] if files else None

def search_pixabay(query: str) -> str | None:
    api_key = os.environ["PIXABAY_API_KEY"]
    url = f"https://pixabay.com/api/videos/?key={api_key}&q={urllib.parse.quote(query)}&per_page=6"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"    [Pixabay error] {type(e).__name__}: {e}")
        return None
    hits = data.get("hits", [])
    if not hits:
        return None
    videos = hits[0]["videos"]
    for size in ("medium", "small", "large", "tiny"):
        if size in videos:
            return videos[size]["url"]
    return None

def download(url: str, out_path: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (DocumentaryBot/1.0)"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(out_path, "wb") as f:
        f.write(resp.read())

def fetch_clip_for_scene(query: str, workdir: str, index: int) -> str:
    out_path = os.path.join(workdir, f"clip_{index}.mp4")

    link = search_pexels(query)
    if not link:
        link = search_pixabay(query)
    if not link:
        # fallback: split query and try first word
        first_word = query.split()[0]
        link = search_pexels(first_word) or search_pixabay(first_word)
        if not link:
            raise RuntimeError(f"No stock clip found for query: '{query}' (tried Pexels + Pixabay)")

    print(f"  scene {index}: '{query}' -> found")
    download(link, out_path)
    return out_path


# ---------- assembly ----------

def normalize_clip(src: str, duration: float, out_path: str):
    """Scale/crop to 1080x1920, trim/loop to duration, strip audio."""
    subprocess.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", src, "-t", str(duration),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-an", out_path,
    ], check=True, capture_output=True)

def build_srt(script: dict, timing: list, out_path: str):
    lines = []
    t = 0.0
    for i, (scene, dur) in enumerate(zip(script["scenes"], timing), start=1):
        start = t
        end = t + dur
        lines.append(str(i))
        lines.append(f"{_srt_ts(start)} --> {_srt_ts(end)}")
        lines.append(scene["narration"])
        lines.append("")
        t = end
    with open(out_path, "w") as f:
        f.write("\n".join(lines))

def _srt_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def concat_clips(clip_paths: list, workdir: str) -> str:
    list_path = os.path.join(workdir, "clips_list.txt")
    with open(list_path, "w") as f:
        for p in clip_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    out_path = os.path.join(workdir, "combined_video.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
        "-c", "copy", out_path,
    ], check=True, capture_output=True)
    return out_path

def concat_audio(clip_paths: list, workdir: str) -> str:
    list_path = os.path.join(workdir, "audio_list.txt")
    with open(list_path, "w") as f:
        for p in clip_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    out_path = os.path.join(workdir, "narration.mp3")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
        "-c", "copy", out_path,
    ], check=True, capture_output=True)
    return out_path


# ---------- cinematic post‑processing ----------

def apply_cinematic_grade(input_video: str, output_video: str, style: str = "warm"):
    """
    Apply colour grading, vignette, and light film grain using ffmpeg.
    style can be "warm", "cold", "vintage", or "high_contrast".
    """
    # Define colour matrix adjustments
    matrices = {
        "warm": "0.9:0.1:0:0:0.1:0.9:0:0:0:0:1:0",  # push reds/greens
        "cold": "0.7:0:0.3:0:0:0.8:0.2:0:0:0:1:0",   # push blues
        "vintage": "0.6:0.2:0.2:0:0.2:0.6:0.2:0:0.2:0.2:0.6:0",
        "high_contrast": "1.2:0:0:0:0:1.2:0:0:0:0:1.2:0.1"
    }
    matrix = matrices.get(style.lower(), matrices["warm"])

    # Vignette: darken edges with a radial gradient
    vignette_filter = (
        "vignette=PI/4"   # simple vignette
    )

    # Film grain: add a small amount of noise
    grain_filter = "noise=alls=2:allf=t+u"

    filter_chain = (
        f"colorchannelmixer={matrix},"
        f"{vignette_filter},"
        f"{grain_filter}"
    )

    cmd = [
        "ffmpeg", "-y", "-i", input_video,
        "-vf", filter_chain,
        "-c:a", "copy",   # keep audio untouched
        output_video
    ]
    subprocess.run(cmd, check=True, capture_output=True)

def add_background_music(video_path: str, music_path: str, output_path: str, volume: float = 0.12):
    """
    Mix background music at low volume (12%) with the existing audio.
    """
    cmd = [
        "ffmpeg", "-y", "-i", video_path, "-i", music_path,
        "-filter_complex", f"[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2,volume={volume}[a]",
        "-map", "0:v", "-map", "[a]", "-c:v", "copy",
        output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)


# ---------- final mux with captions ----------

def mux_final(video_path: str, audio_path: str, srt_path: str, out_path: str):
    style = "FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2,Alignment=2,MarginV=80"
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
        "-vf", f"subtitles={srt_path}:force_style='{style}'",
        "-c:v", "libx264", "-c:a", "aac", "-shortest", out_path,
    ], check=True, capture_output=True)


# ---------- thumbnail ----------

def make_thumbnail(video_path: str, title: str, out_path: str):
    frame_path = out_path.replace(".jpg", "_frame.jpg")
    subprocess.run([
        "ffmpeg", "-y", "-ss", "1", "-i", video_path, "-vframes", "1", "-update", "1", frame_path,
    ], check=True, capture_output=True)

    escaped = title.replace(":", "\\:").replace("'", "")
    subprocess.run([
        "ffmpeg", "-y", "-i", frame_path,
        "-vf", (f"drawtext=text='{escaped}':fontcolor=white:fontsize=60:"
                f"box=1:boxcolor=black@0.55:boxborderw=20:x=(w-text_w)/2:y=h-th-120:"
                f"line_spacing=10"),
        out_path,
    ], check=True, capture_output=True)


# ---------- main ----------

def main():
    outdir = "output"
    os.makedirs(outdir, exist_ok=True)

    print("→ Picking next topic...")
    state = load_topics()
    topic = pick_topic(state)
    print(f"  Topic: {topic}")

    print("→ Generating script + scene breakdown with Gemini...")
    script = call_gemini(topic)
    style = script.get("style", "warm")
    print(f"  Title: {script['title']} | {len(script['scenes'])} scenes | style: {style}")

    print("→ Synthesizing voice (edge-tts)...")
    timing, voice_clips = synthesize_voice(script, outdir)

    print("→ Fetching stock footage (Pexels + Pixabay)...")
    raw_clips = [fetch_clip_for_scene(scene["visual_query"], outdir, i)
                 for i, scene in enumerate(script["scenes"])]

    print("→ Normalizing clips to scene durations...")
    norm_clips = []
    for i, (raw, dur) in enumerate(zip(raw_clips, timing)):
        norm_path = os.path.join(outdir, f"norm_{i}.mp4")
        normalize_clip(raw, dur, norm_path)
        norm_clips.append(norm_path)

    print("→ Building captions (SRT)...")
    srt_path = os.path.join(outdir, "captions.srt")
    build_srt(script, timing, srt_path)

    print("→ Concatenating video + audio tracks...")
    video_path = concat_clips(norm_clips, outdir)
    audio_path = concat_audio(voice_clips, outdir)

    print("→ Muxing final video with burned-in captions...")
    temp_mux = os.path.join(outdir, "temp_mux.mp4")
    mux_final(video_path, audio_path, srt_path, temp_mux)

    # --- Post-processing: cinematic look ---
    print(f"→ Applying cinematic grade (style: {style})...")
    graded_video = os.path.join(outdir, "graded.mp4")
    apply_cinematic_grade(temp_mux, graded_video, style)

    # --- Optional background music ---
    final_path = os.path.join(outdir, "final_documentary.mp4")
    if os.path.exists(BACKGROUND_MUSIC):
        print("→ Mixing in background music...")
        add_background_music(graded_video, BACKGROUND_MUSIC, final_path)
    else:
        # just rename graded to final
        os.rename(graded_video, final_path)

    print("→ Making thumbnail...")
    thumb_path = os.path.join(outdir, "thumbnail.jpg")
    make_thumbnail(final_path, script["title"], thumb_path)

    print("→ Updating topic queue...")
    state["used_topics"].append(topic)
    save_topics(state)

    print(f"\nDONE: {final_path}")
    print(f"Thumbnail: {thumb_path}")
    print(f"Title: {script['title']}")

if __name__ == "__main__":
    sys.exit(main())
