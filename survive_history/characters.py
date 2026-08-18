"""
Stick-figure characters locked to the Survive History character-and-style-bible.
Simplified chibi/stick-figure hybrid: round head, thick dark outline, flat color fill,
minimal limbs. No detailed hands/faces (per style bible).
"""

from manim import (
    VGroup, Circle, Line, Dot, Arc, Text,
    BLACK, WHITE, UP, DOWN, LEFT, RIGHT, ORIGIN,
    DEGREES,
)

# Color Locks (Part B of character-and-style-bible.md)
CHARACTER_COLORS = {
    "Korr":  {"fill": "#4A3728", "outline": BLACK},   # dark brown/grey fur wrap
    "Nala":  {"fill": "#7A8B9A", "outline": BLACK},   # light grey-blue wrap
    "Tarek": {"fill": "#3E2E22", "outline": BLACK},   # simple dark wrap, no headgear
    "Edda":  {"fill": "#2E241C", "outline": BLACK},   # darkest, most weathered wrap
}

HEAD_RADIUS = 0.35
BODY_LEN = 1.1
LIMB_LEN = 0.55
LINE_WIDTH = 6


def _base_figure(fill_color, height_scale=1.0):
    """Builds a static stick figure: head, torso, two arms, two legs."""
    group = VGroup()

    torso = Line(ORIGIN, DOWN * BODY_LEN * height_scale, color=fill_color, stroke_width=LINE_WIDTH * 3)
    head = Circle(radius=HEAD_RADIUS, color=BLACK, fill_color=fill_color, fill_opacity=1, stroke_width=LINE_WIDTH)
    head.move_to(torso.get_start() + UP * HEAD_RADIUS)

    # minimal face: two dot eyes, no nose (per style bible)
    eye_l = Dot(radius=0.03, color=BLACK).move_to(head.get_center() + LEFT * 0.12 + UP * 0.05)
    eye_r = Dot(radius=0.03, color=BLACK).move_to(head.get_center() + RIGHT * 0.12 + UP * 0.05)

    left_leg = Line(torso.get_end(), torso.get_end() + DOWN * LIMB_LEN + LEFT * 0.2,
                     color=BLACK, stroke_width=LINE_WIDTH)
    right_leg = Line(torso.get_end(), torso.get_end() + DOWN * LIMB_LEN + RIGHT * 0.2,
                      color=BLACK, stroke_width=LINE_WIDTH)

    shoulder = torso.get_start() + DOWN * 0.15
    left_arm = Line(shoulder, shoulder + DOWN * 0.3 + LEFT * 0.4, color=BLACK, stroke_width=LINE_WIDTH)
    right_arm = Line(shoulder, shoulder + DOWN * 0.3 + RIGHT * 0.4, color=BLACK, stroke_width=LINE_WIDTH)

    group.add(head, eye_l, eye_r, torso, left_leg, right_leg, left_arm, right_arm)
    group.arms = VGroup(left_arm, right_arm)
    group.legs = VGroup(left_leg, right_leg)
    group.head = head
    group.torso = torso
    return group


def make_character(name: str, pose: str = "idle"):
    """
    Returns a VGroup stick figure for the named locked character, posed.
    Supported poses: idle, point_right, point_left, sit, gesture_up, lean_forward
    """
    if name not in CHARACTER_COLORS:
        raise ValueError(f"Unknown character '{name}'. Must be one of {list(CHARACTER_COLORS)}")

    colors = CHARACTER_COLORS[name]
    fig = _base_figure(colors["fill"])

    shoulder = fig.torso.get_start() + DOWN * 0.15

    if pose == "point_right":
        fig.arms[1].put_start_and_end_on(shoulder, shoulder + RIGHT * 0.9 + UP * 0.1)
    elif pose == "point_left":
        fig.arms[0].put_start_and_end_on(shoulder, shoulder + LEFT * 0.9 + UP * 0.1)
    elif pose == "sit":
        fig.legs[0].put_start_and_end_on(fig.torso.get_end(), fig.torso.get_end() + RIGHT * 0.45 + DOWN * 0.05)
        fig.legs[1].put_start_and_end_on(fig.torso.get_end(), fig.torso.get_end() + LEFT * 0.45 + DOWN * 0.05)
        fig.shift(DOWN * 0.3)
    elif pose == "gesture_up":
        fig.arms[0].put_start_and_end_on(shoulder, shoulder + UP * 0.5 + LEFT * 0.3)
        fig.arms[1].put_start_and_end_on(shoulder, shoulder + UP * 0.5 + RIGHT * 0.3)
    elif pose == "lean_forward":
        fig.rotate(-8 * DEGREES, about_point=fig.torso.get_end())
    # "idle" = default, no change

    name_tag = Text(name, font_size=14, color=WHITE).next_to(fig, DOWN, buff=0.55)
    fig.add(name_tag)
    return fig
