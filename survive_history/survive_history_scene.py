"""
Renders one Survive History Short from:
  - config.json        (shot list: character, pose, caption text, environment)
  - audio_timing.json  (per-shot duration in seconds, produced by the TTS step)

Usage (from repo root, after generate_episode.py has produced both JSON files):
  manim -qm -r 1080,1920 survive_history/survive_history_scene.py Episode
"""

import json
import os

from manim import Scene, Text, RoundedRectangle, VGroup, DOWN, UP, LEFT, RIGHT, ORIGIN, BLACK, WHITE, config

from characters import make_character
from backgrounds import ENVIRONMENTS

config.frame_width = 4.5
config.frame_height = 8.0
config.pixel_width = 1080
config.pixel_height = 1920


class Episode(Scene):
    def construct(self):
        cfg_path = os.environ.get("EPISODE_CONFIG", "config.json")
        timing_path = os.environ.get("EPISODE_TIMING", "audio_timing.json")

        with open(cfg_path) as f:
            episode = json.load(f)
        with open(timing_path) as f:
            timing = json.load(f)  # list of {"shot_index": int, "duration": float}

        env_key = episode.get("environment", "ENV001")
        bg = ENVIRONMENTS[env_key]()
        self.add(bg)

        durations = {t["shot_index"]: t["duration"] for t in timing}

        for i, shot in enumerate(episode["shots"]):
            duration = durations.get(i, 3.0)

            char = make_character(shot["character"], pose=shot.get("pose", "idle"))
            char.move_to(LEFT * 1.0 if i % 2 == 0 else RIGHT * 1.0)
            char.shift(DOWN * 0.5)

            caption_bg = RoundedRectangle(
                width=3.8, height=1.0, corner_radius=0.15,
                fill_color=BLACK, fill_opacity=0.6, stroke_width=0,
            ).to_edge(DOWN, buff=0.4)
            caption_text = Text(
                shot.get("caption", shot.get("line", "")),
                font_size=26, color=WHITE, weight="BOLD",
            ).scale_to_fit_width(3.5).move_to(caption_bg.get_center())
            caption = VGroup(caption_bg, caption_text)

            self.add(char, caption)

            # gentle fire flicker while this shot holds
            flame = bg.camp_fire.flame_parts
            self.play(flame.animate.scale(1.08), run_time=duration / 2, rate_func=lambda t: t)
            self.play(flame.animate.scale(1 / 1.08), run_time=duration / 2, rate_func=lambda t: t)

            self.remove(char, caption)

        self.wait(0.3)
