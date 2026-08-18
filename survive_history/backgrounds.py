"""
Predefined environments for Survive History shorts.
Per character-and-style-bible.md: flat color, thick black outlines, chibi aesthetic.
"""

from manim import (
    VGroup, Rectangle, Circle, Line, Polygon, Text,
    BLACK, WHITE, ORIGIN, UP, DOWN, LEFT, RIGHT,
)


class CampfireEnvironment(VGroup):
    """Base camp at night, campfire glowing, two tents in background."""
    
    def __init__(self):
        super().__init__()
        
        # Night sky background (dark blue)
        sky = Rectangle(width=8, height=6, fill_color="#1a1a2e", fill_opacity=1, stroke_width=0)
        sky.to_edge(UP, buff=0)
        
        # Ground
        ground = Rectangle(width=8, height=2, fill_color="#2d5016", fill_opacity=1, stroke_width=0)
        ground.to_edge(DOWN, buff=0)
        
        # Campfire (simple cone + flame)
        fire_base = Polygon(
            [-0.3, -0.5, 0], [0.3, -0.5, 0], [0.1, 0.3, 0], [-0.1, 0.3, 0],
            fill_color="#d2691e", fill_opacity=1, stroke_width=2, stroke_color=BLACK
        )
        fire_base.move_to(ORIGIN)
        
        # Flame (simple triangle)
        flame = Polygon(
            [-0.15, 0.3, 0], [0.15, 0.3, 0], [0, 0.8, 0],
            fill_color="#ff6b35", fill_opacity=0.9, stroke_width=1, stroke_color="#ff0000"
        )
        flame.move_to(ORIGIN)
        
        self.campfire = VGroup(fire_base, flame)
        self.campfire.flame_parts = flame
        self.campfire.move_to([0, -1.2, 0])
        
        # Two simple tents in background
        tent_left = Polygon(
            [-0.4, 0, 0], [0, 0.6, 0], [0.4, 0, 0],
            fill_color="#8b4513", fill_opacity=1, stroke_width=1, stroke_color=BLACK
        )
        tent_left.move_to([-2.5, 0.5, 0])
        
        tent_right = Polygon(
            [-0.4, 0, 0], [0, 0.6, 0], [0.4, 0, 0],
            fill_color="#a0522d", fill_opacity=1, stroke_width=1, stroke_color=BLACK
        )
        tent_right.move_to([2.5, 0.5, 0])
        
        self.add(sky, ground, self.campfire, tent_left, tent_right)


class DesertEnvironment(VGroup):
    """Desert landscape: sand dunes, sparse vegetation, hot sky."""
    
    def __init__(self):
        super().__init__()
        
        # Hot sky (gradient yellow/orange)
        sky = Rectangle(width=8, height=6, fill_color="#f4a460", fill_opacity=1, stroke_width=0)
        sky.to_edge(UP, buff=0)
        
        # Sand dunes
        dune1 = Polygon(
            [-4, -0.5, 0], [-1, 1.5, 0], [1, 0, 0],
            fill_color="#daa520", fill_opacity=1, stroke_width=0
        )
        dune2 = Polygon(
            [0, 0, 0], [3, 1, 0], [5, -0.5, 0],
            fill_color="#cd853f", fill_opacity=1, stroke_width=0
        )
        
        ground = Rectangle(width=8, height=2, fill_color="#bdb76b", fill_opacity=1, stroke_width=0)
        ground.to_edge(DOWN, buff=0)
        
        # Sparse cactus
        cactus_stem = Rectangle(width=0.15, height=0.8, fill_color="#228b22", fill_opacity=1, stroke_width=1, stroke_color=BLACK)
        cactus_stem.move_to([2, -0.8, 0])
        cactus_arm = Rectangle(width=0.3, height=0.1, fill_color="#228b22", fill_opacity=1, stroke_width=1, stroke_color=BLACK)
        cactus_arm.move_to([2.5, -0.4, 0])
        
        self.add(sky, dune1, dune2, ground, cactus_stem, cactus_arm)


class ForestEnvironment(VGroup):
    """Forest clearing: trees, grass, dappled light."""
    
    def __init__(self):
        super().__init__()
        
        # Forest sky (light green-blue)
        sky = Rectangle(width=8, height=6, fill_color="#87ceeb", fill_opacity=1, stroke_width=0)
        sky.to_edge(UP, buff=0)
        
        # Ground
        ground = Rectangle(width=8, height=2, fill_color="#228b22", fill_opacity=1, stroke_width=0)
        ground.to_edge(DOWN, buff=0)
        
        # Simple trees (brown trunks + green circles for foliage)
        tree_left_trunk = Rectangle(width=0.2, height=1.2, fill_color="#654321", fill_opacity=1, stroke_width=1, stroke_color=BLACK)
        tree_left_trunk.move_to([-2.5, -0.2, 0])
        tree_left_foliage = Circle(radius=0.6, fill_color="#2d5016", fill_opacity=1, stroke_width=1, stroke_color=BLACK)
        tree_left_foliage.move_to([-2.5, 0.8, 0])
        
        tree_right_trunk = Rectangle(width=0.2, height=1.2, fill_color="#654321", fill_opacity=1, stroke_width=1, stroke_color=BLACK)
        tree_right_trunk.move_to([2.5, -0.2, 0])
        tree_right_foliage = Circle(radius=0.6, fill_color="#2d5016", fill_opacity=1, stroke_width=1, stroke_color=BLACK)
        tree_right_foliage.move_to([2.5, 0.8, 0])
        
        self.add(sky, ground, tree_left_trunk, tree_left_foliage, tree_right_trunk, tree_right_foliage)


# Environment registry
ENVIRONMENTS = {
    "ENV001": CampfireEnvironment,
    "ENV002": DesertEnvironment,
    "ENV003": ForestEnvironment,
}
