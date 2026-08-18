"""
Stick-figure characters locked to the Survive History character-and-style-bible.
V2: color-blocked clothing silhouette (not a bare line), rounded joints, a
recognizable prop per character, and a simple hair/headwrap shape so each
character reads distinctly even as a simple figure.
"""

from manim import (
    VGroup, Circle, Line, Dot, Polygon, Triangle, Arc,
    Text, BLACK, WHITE, UP, DOWN, LEFT, RIGHT, ORIGIN, DEGREES,
)

# Color Locks (Part B of character-and-style-bible.md)
CHARACTER_COLORS = {
    "Korr":  {"fill": "#4A3728", "outline": BLACK, "prop": "spear"},
    "Nala":  {"fill": "#7A8B9A", "outline": BLACK, "prop": "poker"},
    "Tarek": {"fill": "#8A6A4A", "outline": BLACK, "prop": None},
    "Edda":  {"fill": "#2E241C", "outline": BLACK, "prop": "cane"},
}

HEAD_RADIUS = 0.38
TORSO_H = 1.15
TORSO_TOP_W = 0.62
TORSO_BOT_W = 0.78
LIMB_W = 10  # stroke width
JOINT_R = 0.055


def _rounded_joint(point, color=BLACK):
    return Dot(radius=JOINT_R, color=color, fill_opacity=1).move_to(point)


def _base_figure(fill_color):
    group = VGroup()

    neck = UP * (TORSO_H / 2)
    hip = DOWN * (TORSO_H / 2)

    # color-blocked torso (tunic silhouette, not a bare line)
    torso = Polygon(
        neck + LEFT * TORSO_TOP_W / 2, neck + RIGHT * TORSO_TOP_W / 2,
        hip + RIGHT * TORSO_BOT_W / 2, hip + LEFT * TORSO_BOT_W / 2,
        fill_color=fill_color, fill_opacity=1, stroke_color=BLACK, stroke_width=5,
    )

    head = Circle(radius=HEAD_RADIUS, color=BLACK, fill_color="#D9B08C", fill_opacity=1, stroke_width=5)
    head.move_to(neck + UP * HEAD_RADIUS * 0.9)

    eye_l = Dot(radius=0.035, color=BLACK).move_to(head.get_center() + LEFT * 0.13 + UP * 0.03)
    eye_r = Dot(radius=0.035, color=BLACK).move_to(head.get_center() + RIGHT * 0.13 + UP * 0.03)

    shoulder_l = neck + LEFT * TORSO_TOP_W / 2
    shoulder_r = neck + RIGHT * TORSO_TOP_W / 2
    elbow_l = shoulder_l + DOWN * 0.28 + LEFT * 0.32
    elbow_r = shoulder_r + DOWN * 0.28 + RIGHT * 0.32
    hand_l = elbow_l + DOWN * 0.22 + LEFT * 0.08
    hand_r = elbow_r + DOWN * 0.22 + RIGHT * 0.08

    arm_l = VGroup(
        Line(shoulder_l, elbow_l, color=fill_color, stroke_width=LIMB_W),
        Line(elbow_l, hand_l, color=fill_color, stroke_width=LIMB_W),
        _rounded_joint(shoulder_l), _rounded_joint(elbow_l), _rounded_joint(hand_l),
    )
    arm_r = VGroup(
        Line(shoulder_r, elbow_r, color=fill_color, stroke_width=LIMB_W),
        Line(elbow_r, hand_r, color=fill_color, stroke_width=LIMB_W),
        _rounded_joint(shoulder_r), _rounded_joint(elbow_r), _rounded_joint(hand_r),
    )

    hip_l = hip + LEFT * TORSO_BOT_W / 2
    hip_r = hip + RIGHT * TORSO_BOT_W / 2
    knee_l = hip_l + DOWN * 0.32 + LEFT * 0.06
    knee_r = hip_r + DOWN * 0.32 + RIGHT * 0.06
    foot_l = knee_l + DOWN * 0.30
    foot_r = knee_r + DOWN * 0.30

    leg_l = VGroup(
        Line(hip_l, knee_l, color=BLACK, stroke_width=LIMB_W),
        Line(knee_l, foot_l, color=BLACK, stroke_width=LIMB_W),
        _rounded_joint(hip_l), _rounded_joint(knee_l),
    )
    leg_r = VGroup(
        Line(hip_r, knee_r, color=BLACK, stroke_width=LIMB_W),
        Line(knee_r, foot_r, color=BLACK, stroke_width=LIMB_W),
        _rounded_joint(hip_r), _rounded_joint(knee_r),
    )

    group.add(leg_l, leg_r, torso, arm_l, arm_r, head, eye_l, eye_r)
    group.arm_l, group.arm_r = arm_l, arm_r
    group.leg_l, group.leg_r = leg_l, leg_r
    group.head = head
    group.torso = torso
    group.hand_r = hand_r
    group.hand_l = hand_l
    return group


def _add_prop(fig, prop_name, fill_color):
    if prop_name == "spear":
        shaft = Line(fig.hand_r, fig.hand_r + UP * 1.3 + RIGHT * 0.1, color="#5A4530", stroke_width=6)
        tip = Triangle(fill_color="#B0B0B0", fill_opacity=1, stroke_width=2, color=BLACK)
        tip.scale(0.12).move_to(shaft.get_end() + UP * 0.08)
        fig.add(shaft, tip)
    elif prop_name == "poker":
        stick = Line(fig.hand_r, fig.hand_r + UP * 0.9 + RIGHT * 0.15, color="#5A4530", stroke_width=6)
        fig.add(stick)
    elif prop_name == "cane":
        cane = Line(fig.hand_r, fig.hand_r + DOWN * 0.7, color="#3A2E22", stroke_width=6)
        fig.add(cane)


def _add_headwrap(fig, name):
    """Small distinguishing headwrap/hair shape so silhouettes differ at a glance."""
    if name == "Korr":
        wrap = Arc(radius=HEAD_RADIUS * 1.05, angle=200 * DEGREES, start_angle=160 * DEGREES,
                   color="#3A2E22", stroke_width=8).move_to(fig.head.get_center())
        fig.add(wrap)
    elif name == "Nala":
        tie = Dot(radius=0.06, color="#2A2A2A").move_to(fig.head.get_center() + UP * HEAD_RADIUS * 0.9 + RIGHT * 0.15)
        fig.add(tie)
    elif name == "Edda":
        shawl = Arc(radius=HEAD_RADIUS * 1.15, angle=260 * DEGREES, start_angle=140 * DEGREES,
                    color="#2E241C", stroke_width=10).move_to(fig.head.get_center())
        fig.add(shawl)
    # Tarek: no headgear (per style bible), left plain


def make_character(name: str, pose: str = "idle"):
    """
    Returns a VGroup stick figure for the named locked character, posed.
    Supported poses: idle, point_right, point_left, sit, gesture_up, lean_forward
    """
    if name not in CHARACTER_COLORS:
        raise ValueError(f"Unknown character '{name}'. Must be one of {list(CHARACTER_COLORS)}")

    colors = CHARACTER_COLORS[name]
    fig = _base_figure(colors["fill"])

    shoulder_r = fig.torso.get_vertices()[1]
    shoulder_l = fig.torso.get_vertices()[0]

    if pose == "point_right":
        fig.arm_r[1].put_start_and_end_on(fig.arm_r[0].get_end(), fig.arm_r[0].get_end() + RIGHT * 0.75)
    elif pose == "point_left":
        fig.arm_l[1].put_start_and_end_on(fig.arm_l[0].get_end(), fig.arm_l[0].get_end() + LEFT * 0.75)
    elif pose == "sit":
        fig.shift(DOWN * 0.35)
    elif pose == "gesture_up":
        fig.arm_l[0].put_start_and_end_on(shoulder_l, shoulder_l + UP * 0.4 + LEFT * 0.2)
        fig.arm_r[0].put_start_and_end_on(shoulder_r, shoulder_r + UP * 0.4 + RIGHT * 0.2)
    elif pose == "lean_forward":
        fig.rotate(-7 * DEGREES, about_point=fig.torso.get_bottom())
    # "idle" = default, no change

    _add_headwrap(fig, name)
    if colors["prop"] and pose not in ("sit",):
        _add_prop(fig, colors["prop"], colors["fill"])

    name_tag = Text(name, font_size=14, color=WHITE).next_to(fig, DOWN, buff=0.55)
    fig.add(name_tag)
    return fig
