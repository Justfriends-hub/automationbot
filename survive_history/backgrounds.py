"""
Environment backgrounds per Part C of character-and-style-bible.md.
Kept simple/flat/graphic per the locked art style — gradient sky, silhouette
ground shapes, a flickering campfire, and (for the ice shore) wind-streak lines.
"""

from manim import (
    VGroup, Rectangle, Polygon, Circle, Line, Triangle,
    ORIGIN, UP, DOWN, LEFT, RIGHT, DEGREES, BLACK,
)

FRAME_W = 4.5   # vertical 9:16 canvas at Manim's default frame height ~8
FRAME_H = 8.0


def fire(position=ORIGIN, scale=1.0):
    """A simple layered-triangle campfire, flame color locked to warm orange/yellow."""
    base = Triangle(color="#7A4A2A", fill_color="#7A4A2A", fill_opacity=1).scale(0.25 * scale)
    flame_outer = Triangle(color="#FF7A1A", fill_color="#FF7A1A", fill_opacity=1).scale(0.22 * scale)
    flame_inner = Triangle(color="#FFD23F", fill_color="#FFD23F", fill_opacity=1).scale(0.12 * scale)
    flame_outer.next_to(base, UP, buff=-0.05)
    flame_inner.next_to(base, UP, buff=0.02)
    group = VGroup(base, flame_outer, flame_inner).move_to(position)
    group.flame_parts = VGroup(flame_outer, flame_inner)
    return group


def wind_lines(n=5):
    """Curved streak lines implying blizzard wind, per style bible."""
    lines = VGroup()
    for i in range(n):
        y = 2.5 - i * 1.0
        ln = Line(LEFT * FRAME_W + UP * y, LEFT * (FRAME_W - 1.2) + UP * (y + 0.3),
                  color="#DCE6F0", stroke_width=2, stroke_opacity=0.5)
        lines.add(ln)
    return lines


def open_ice_shore():
    """ENV001 — flat frozen coastline, sunset gradient, campfire center, wind lines."""
    sky = Rectangle(width=FRAME_W * 2, height=FRAME_H, fill_opacity=1, stroke_width=0)
    sky.set_fill(color=["#3A2A5C", "#C9622E"], opacity=1)  # purple-to-orange gradient approx
    sky.set_sheen_direction(UP)

    ground = Polygon(
        LEFT * FRAME_W + DOWN * 1.5, RIGHT * FRAME_W + DOWN * 1.5,
        RIGHT * FRAME_W + DOWN * 4, LEFT * FRAME_W + DOWN * 4,
        fill_color="#DCE6F0", fill_opacity=1, stroke_width=0,
    )

    rocks = VGroup(*[
        Polygon(ORIGIN, RIGHT * 0.4, UP * 0.3 + RIGHT * 0.2, fill_color="#2A2A2A",
                fill_opacity=1, stroke_width=0).move_to(LEFT * 2.8 + DOWN * (1.7 + i * 0.1))
        for i in range(3)
    ])

    camp_fire = fire(position=DOWN * 1.6, scale=1.2)
    wind = wind_lines()

    scene = VGroup(sky, ground, rocks, wind, camp_fire)
    scene.camp_fire = camp_fire
    return scene


def bone_hut_interior():
    """ENV002 — arched mammoth rib/tusk frame, mounted skulls, central fire pit."""
    interior = Rectangle(width=FRAME_W * 2, height=FRAME_H, fill_opacity=1, stroke_width=0)
    interior.set_fill(color="#2A2018", opacity=1)

    ribs = VGroup(*[
        Line(LEFT * (3.5 - i * 1.5) + DOWN * 3, UP * (2.5 - i * 0.3), color="#C9BBA0", stroke_width=8)
        for i in range(3)
    ] + [
        Line(RIGHT * (3.5 - i * 1.5) + DOWN * 3, UP * (2.5 - i * 0.3), color="#C9BBA0", stroke_width=8)
        for i in range(3)
    ])

    skull_l = Circle(radius=0.3, color="#C9BBA0", fill_color="#C9BBA0", fill_opacity=1).move_to(LEFT * 3 + UP * 1)
    skull_r = Circle(radius=0.3, color="#C9BBA0", fill_color="#C9BBA0", fill_opacity=1).move_to(RIGHT * 3 + UP * 1)

    pit_fire = fire(position=DOWN * 1.8, scale=1.4)

    scene = VGroup(interior, ribs, skull_l, skull_r, pit_fire)
    scene.camp_fire = pit_fire
    return scene


def forest_camp():
    """ENV003 — dense pine treeline, dusk, campfire clearing."""
    sky = Rectangle(width=FRAME_W * 2, height=FRAME_H, fill_opacity=1, stroke_width=0)
    sky.set_fill(color=["#1E2A3A", "#4A3B2A"], opacity=1)
    ground = Polygon(
        LEFT * FRAME_W + DOWN * 1.5, RIGHT * FRAME_W + DOWN * 1.5,
        RIGHT * FRAME_W + DOWN * 4, LEFT * FRAME_W + DOWN * 4,
        fill_color="#22301F", fill_opacity=1, stroke_width=0,
    )
    trees = VGroup(*[
        Triangle(fill_color="#0F1A10", fill_opacity=1, stroke_width=0)
        .scale(0.9 + (i % 3) * 0.2)
        .move_to(LEFT * FRAME_W + RIGHT * i * 1.1 + UP * (1.5 + (i % 2) * 0.3))
        for i in range(9)
    ])
    camp_fire = fire(position=DOWN * 1.6, scale=1.1)
    scene = VGroup(sky, trees, ground, camp_fire)
    scene.camp_fire = camp_fire
    return scene


def coastal_cliffs():
    """ENV004 — rocky sea coast, grey overcast, waves implied by streak lines."""
    sky = Rectangle(width=FRAME_W * 2, height=FRAME_H, fill_opacity=1, stroke_width=0)
    sky.set_fill(color=["#5C6B7A", "#8FA3B0"], opacity=1)
    sea = Polygon(
        LEFT * FRAME_W + DOWN * 0.5, RIGHT * FRAME_W + DOWN * 0.5,
        RIGHT * FRAME_W + DOWN * 4, LEFT * FRAME_W + DOWN * 4,
        fill_color="#2E4A5C", fill_opacity=1, stroke_width=0,
    )
    wave_lines = VGroup(*[
        Line(LEFT * FRAME_W + DOWN * (0.7 + i * 0.5), RIGHT * FRAME_W + DOWN * (0.7 + i * 0.5),
             color="#AFC4CE", stroke_width=2, stroke_opacity=0.4)
        for i in range(4)
    ])
    cliff = Polygon(LEFT * FRAME_W, LEFT * 1.5, LEFT * 1.0 + DOWN * 2, LEFT * FRAME_W + DOWN * 2,
                     fill_color="#3A3A3A", fill_opacity=1, stroke_width=0)
    camp_fire = fire(position=DOWN * 1.4 + RIGHT * 0.5, scale=1.0)
    scene = VGroup(sky, sea, wave_lines, cliff, camp_fire)
    scene.camp_fire = camp_fire
    return scene


def blizzard_open():
    """ENV005 — whiteout storm, heavy wind lines, low visibility, no fire (danger state)."""
    sky = Rectangle(width=FRAME_W * 2, height=FRAME_H, fill_opacity=1, stroke_width=0)
    sky.set_fill(color="#C7D2DB", opacity=1)
    ground = Rectangle(width=FRAME_W * 2, height=3, fill_color="#DCE6F0", fill_opacity=1, stroke_width=0)
    ground.to_edge(DOWN, buff=-1)
    heavy_wind = wind_lines(n=9)
    scene = VGroup(sky, ground, heavy_wind)
    scene.camp_fire = fire(position=DOWN * 10, scale=0.01)  # off-screen placeholder, no fire in a storm
    scene.add(scene.camp_fire)
    return scene


ENVIRONMENTS = {
    "ENV001": open_ice_shore,
    "ENV002": bone_hut_interior,
    "ENV003": forest_camp,
    "ENV004": coastal_cliffs,
    "ENV005": blizzard_open,
}
