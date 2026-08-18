"""
Generate a Survive History episode configuration and audio timing.
This script:
  1. Takes a history topic/prompt
  2. Uses an LLM to generate a story outline with character dialogue
  3. Generates TTS audio for each line
  4. Produces config.json and audio_timing.json for the Manim renderer
"""

import json
import os
import sys
from pathlib import Path

# Placeholder: in production, integrate with:
# - LLM API (e.g., Gemini, GPT) to generate story
# - TTS API (e.g., Google Cloud TTS, ElevenLabs) to generate audio

def generate_episode(topic: str, output_dir: str = "."):
    """
    Generate a Survive History episode from a history topic.
    
    Args:
        topic: The historical topic/prompt (e.g., "The Fall of Rome")
        output_dir: Directory to save config.json and audio_timing.json
    
    Returns:
        dict: The generated episode config
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # PLACEHOLDER: Replace with real LLM call
    # This is a dummy structure showing what the output should look like
    episode_config = {
        "title": f"Survive History: {topic}",
        "environment": "ENV001",  # Campfire setting
        "shots": [
            {
                "character": "Korr",
                "pose": "idle",
                "caption": f"Long ago, {topic} changed everything...",
                "line": f"Long ago, {topic} changed everything...",
            },
            {
                "character": "Nala",
                "pose": "gesture_up",
                "caption": "But how did it really happen?",
                "line": "But how did it really happen?",
            },
            {
                "character": "Tarek",
                "pose": "point_right",
                "caption": "Let me tell you the real story.",
                "line": "Let me tell you the real story.",
            },
            {
                "character": "Edda",
                "pose": "lean_forward",
                "caption": "It all started with one decision...",
                "line": "It all started with one decision...",
            },
        ],
    }
    
    # PLACEHOLDER: Replace with real TTS calls
    # This generates dummy timing (3 seconds per shot)
    audio_timing = [
        {"shot_index": i, "duration": 3.0}
        for i in range(len(episode_config["shots"]))
    ]
    
    # Save configs
    config_path = output_dir / "config.json"
    timing_path = output_dir / "audio_timing.json"
    
    with open(config_path, "w") as f:
        json.dump(episode_config, f, indent=2)
    
    with open(timing_path, "w") as f:
        json.dump(audio_timing, f, indent=2)
    
    print(f"✓ Generated config.json with {len(episode_config['shots'])} shots")
    print(f"✓ Generated audio_timing.json")
    print(f"✓ Next: Run 'manim -qm -r 1080,1920 survive_history/survive_history_scene.py Episode'")
    
    return episode_config


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_episode.py '<topic>'")
        print("Example: python generate_episode.py 'The Fall of Rome'")
        sys.exit(1)
    
    topic = sys.argv[1]
    generate_episode(topic)
