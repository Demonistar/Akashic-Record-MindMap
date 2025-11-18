#!/usr/bin/env python3
"""
Theme Engine for Akashic Record MindMap
Provides visual customization through theme system
All rendering goes through themes to avoid hard-coded visuals
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import tkinter as tk
import math


@dataclass
class NodeStyle:
    """Visual properties for a node"""
    shape: str  # 'gravestone', 'rectangle', 'bubble', 'crypt'
    fill_color: str
    border_color: str
    border_width: int
    text_color: str
    font_family: str
    font_size: int
    width: int
    height: int
    shadow: bool = False


@dataclass
class ConnectionStyle:
    """Visual properties for connections"""
    type: str  # 'web', 'string_lights', 'straight', 'bezier'
    color: str
    width: int
    animated: bool = False
    animation_speed: float = 1.0


@dataclass
class CabinetStyle:
    """Visual properties for file cabinet"""
    type: str  # 'mausoleum', 'filing_cabinet', 'treasure_chest'
    color: str
    width: int
    height: int
    drawer_colors: Dict[str, str]  # drawer_name -> color


class Theme:
    """Base theme class - all themes inherit from this"""

    def __init__(self, name: str):
        self.name = name
        self.node_styles = {}  # tier -> NodeStyle
        self.connection_style = None
        self.cabinet_style = None

    def get_node_style(self, tier: int, completed: bool = False) -> NodeStyle:
        """Get style for node at given tier"""
        raise NotImplementedError

    def get_connection_style(self) -> ConnectionStyle:
        """Get style for connections"""
        return self.connection_style

    def get_cabinet_style(self) -> CabinetStyle:
        """Get style for cabinet"""
        return self.cabinet_style

    def draw_node(self, canvas: tk.Canvas, x: int, y: int,
                  style: NodeStyle, text: str, tags: tuple) -> List[int]:
        """Draw node on canvas - returns list of canvas item IDs"""
        raise NotImplementedError

    def draw_connection(self, canvas: tk.Canvas, x1: int, y1: int,
                       x2: int, y2: int, style: ConnectionStyle, tags: tuple = ('connection',)) -> List[int]:
        """Draw connection line - returns list of canvas item IDs"""
        raise NotImplementedError


class CemeteryTheme(Theme):
    """Cemetery/graveyard theme with tombstones and spider webs"""

    def __init__(self):
        super().__init__("cemetery")

        # Define styles for different tiers (based on number of children)
        self.node_styles = {
            0: NodeStyle(  # Small graves (0-1 children)
                shape='gravestone_small',
                fill_color='#4a4a4a',
                border_color='#2a2a2a',
                border_width=2,
                text_color='#ffffff',
                font_family='Arial',
                font_size=10,
                width=100,
                height=80,
                shadow=True
            ),
            1: NodeStyle(  # Medium graves (2-4 children)
                shape='gravestone_medium',
                fill_color='#5a5a5a',
                border_color='#2a2a2a',
                border_width=2,
                text_color='#ffffff',
                font_family='Arial',
                font_size=12,
                width=120,
                height=100,
                shadow=True
            ),
            2: NodeStyle(  # Large crypts (5+ children)
                shape='crypt',
                fill_color='#6a6a6a',
                border_color='#2a2a2a',
                border_width=3,
                text_color='#ffffff',
                font_family='Arial',
                font_size=14,
                width=150,
                height=120,
                shadow=True
            )
        }

        self.connection_style = ConnectionStyle(
            type='web',
            color='#888888',
            width=1,
            animated=False,
            animation_speed=2.0
        )

        self.cabinet_style = CabinetStyle(
            type='mausoleum',
            color='#3a3a3a',
            width=120,
            height=400,
            drawer_colors={
                'top': '#4a4a4a',
                'middle': '#4a4a4a',
                'bottom': '#4a4a4a'
            }
        )

    def get_node_style(self, tier: int, completed: bool = False) -> NodeStyle:
        """Get style based on tier (more children = higher tier)"""
        if tier >= 2:
            style_dict = self.node_styles[2].__dict__.copy()
        elif tier == 1:
            style_dict = self.node_styles[1].__dict__.copy()
        else:
            style_dict = self.node_styles[0].__dict__.copy()

        # Modify for completed nodes
        if completed:
            style_dict['fill_color'] = '#2d5016'  # Dark green tint
            style_dict['border_color'] = '#1a3009'

        return NodeStyle(**style_dict)

    def draw_node(self, canvas: tk.Canvas, x: int, y: int,
                  style: NodeStyle, text: str, tags: tuple) -> List[int]:
        """Draw gravestone-shaped node"""
        items = []
        w, h = style.width, style.height

        # Shadow if enabled
        if style.shadow:
            shadow = canvas.create_oval(
                x - w//2 + 5, y + h//2 - 5,
                x + w//2 + 5, y + h//2 + 15,
                fill='#000000', outline='', stipple='gray50',
                tags=tags
            )
            items.append(shadow)

        if style.shape == 'gravestone_small':
            # Rectangle base
            rect = canvas.create_rectangle(
                x - w//2, y - h//4,
                x + w//2, y + h//2,
                fill=style.fill_color, outline=style.border_color,
                width=style.border_width, tags=tags
            )
            items.append(rect)

            # Rounded top
            arc = canvas.create_arc(
                x - w//2, y - h//2,
                x + w//2, y,
                start=0, extent=180,
                fill=style.fill_color, outline=style.border_color,
                width=style.border_width, tags=tags
            )
            items.append(arc)

            # Small cross
            cross_v = canvas.create_line(
                x, y - h//3, x, y - h//6,
                fill=style.border_color, width=2, tags=tags
            )
            cross_h = canvas.create_line(
                x - 8, y - h//4, x + 8, y - h//4,
                fill=style.border_color, width=2, tags=tags
            )
            items.extend([cross_v, cross_h])

        elif style.shape == 'gravestone_medium':
            # Taller gravestone
            rect = canvas.create_rectangle(
                x - w//2, y - h//3,
                x + w//2, y + h//2,
                fill=style.fill_color, outline=style.border_color,
                width=style.border_width, tags=tags
            )
            items.append(rect)

            arc = canvas.create_arc(
                x - w//2, y - h//2,
                x + w//2, y + h//6,
                start=0, extent=180,
                fill=style.fill_color, outline=style.border_color,
                width=style.border_width, tags=tags
            )
            items.append(arc)

            # Medium cross
            cross_v = canvas.create_line(
                x, y - h//3, x, y - h//8,
                fill=style.border_color, width=3, tags=tags
            )
            cross_h = canvas.create_line(
                x - 10, y - h//5, x + 10, y - h//5,
                fill=style.border_color, width=3, tags=tags
            )
            items.extend([cross_v, cross_h])

        elif style.shape == 'crypt':
            # Crypt/mausoleum structure
            # Base
            base = canvas.create_rectangle(
                x - w//2, y,
                x + w//2, y + h//2,
                fill=style.fill_color, outline=style.border_color,
                width=style.border_width, tags=tags
            )
            items.append(base)

            # Building
            building = canvas.create_rectangle(
                x - w//2 + 10, y - h//2,
                x + w//2 - 10, y,
                fill=style.fill_color, outline=style.border_color,
                width=style.border_width, tags=tags
            )
            items.append(building)

            # Roof (triangle)
            roof = canvas.create_polygon(
                x - w//2 + 10, y - h//2,
                x, y - h//2 - 20,
                x + w//2 - 10, y - h//2,
                fill=style.fill_color, outline=style.border_color,
                width=style.border_width, tags=tags
            )
            items.append(roof)

            # Door
            door = canvas.create_rectangle(
                x - 15, y - 20,
                x + 15, y,
                fill='#1a1a1a', outline=style.border_color,
                width=1, tags=tags
            )
            items.append(door)
        else:
            # Fallback to simple rectangle
            rect = canvas.create_rectangle(
                x - w//2, y - h//2,
                x + w//2, y + h//2,
                fill=style.fill_color, outline=style.border_color,
                width=style.border_width, tags=tags
            )
            items.append(rect)

        # Text (FIXED: Bug #3 - place INSIDE gravestone, not below)
        # Truncate text if too long
        display_text = text if len(text) <= 15 else text[:12] + "..."

        # Place text INSIDE the gravestone at CENTER for visibility
        text_item = canvas.create_text(
            x, y,  # CENTER of gravestone, not below (was y + h//2 + 15)
            text=display_text,
            fill='#FFFFFF',  # Always white for visibility (was style.text_color)
            font=(style.font_family, style.font_size, 'bold'),
            tags=tags,
            width=w - 20  # Word wrap within gravestone
        )
        items.append(text_item)

        return items

    def draw_connection(self, canvas: tk.Canvas, x1: int, y1: int,
                       x2: int, y2: int, style: ConnectionStyle, tags: tuple = ('connection',)) -> List[int]:
        """Draw spider web connection"""
        items = []

        if style.type == 'web':
            # Main strand
            main = canvas.create_line(
                x1, y1, x2, y2,
                fill=style.color, width=style.width,
                tags=tags
            )
            items.append(main)

            # Add web details (crosshatching)
            distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)

            if distance > 50:  # Only add details if connection is long enough
                # Calculate perpendicular offsets
                angle = math.atan2(y2-y1, x2-x1)
                perp_angle = angle + math.pi/2

                # Add 2-3 cross strands
                num_cross = min(3, int(distance / 50))
                for i in range(1, num_cross + 1):
                    t = i / (num_cross + 1)
                    mid_x = x1 + (x2 - x1) * t
                    mid_y = y1 + (y2 - y1) * t

                    offset = 15
                    cross = canvas.create_line(
                        mid_x + offset * math.cos(perp_angle),
                        mid_y + offset * math.sin(perp_angle),
                        mid_x - offset * math.cos(perp_angle),
                        mid_y - offset * math.sin(perp_angle),
                        fill=style.color, width=style.width,
                        tags=tags
                    )
                    items.append(cross)
        else:
            # Fallback to straight line
            line = canvas.create_line(
                x1, y1, x2, y2,
                fill=style.color, width=style.width,
                tags=tags
            )
            items.append(line)

        return items


class DefaultTheme(Theme):
    """Simple default theme - clean and professional"""

    def __init__(self):
        super().__init__("default")

        base_style = NodeStyle(
            shape='rectangle',
            fill_color='#E3F2FD',
            border_color='#1976D2',
            border_width=2,
            text_color='#000000',
            font_family='Arial',
            font_size=12,
            width=120,
            height=40,
            shadow=False
        )

        # All tiers use same style in default theme
        self.node_styles = {
            0: base_style,
            1: base_style,
            2: base_style
        }

        self.connection_style = ConnectionStyle(
            type='straight',
            color='#1976D2',
            width=2,
            animated=False
        )

        self.cabinet_style = CabinetStyle(
            type='filing_cabinet',
            color='#8D6E63',
            width=80,
            height=150,
            drawer_colors={
                'top': '#A1887F',
                'middle': '#A1887F',
                'bottom': '#A1887F'
            }
        )

    def get_node_style(self, tier: int, completed: bool = False) -> NodeStyle:
        style_dict = self.node_styles[0].__dict__.copy()

        if completed:
            style_dict['fill_color'] = '#C8E6C9'  # Light green
            style_dict['border_color'] = '#4CAF50'  # Green

        return NodeStyle(**style_dict)

    def draw_node(self, canvas: tk.Canvas, x: int, y: int,
                  style: NodeStyle, text: str, tags: tuple) -> List[int]:
        """Draw simple rectangle node"""
        items = []
        w, h = style.width, style.height

        rect = canvas.create_rectangle(
            x - w//2, y - h//2,
            x + w//2, y + h//2,
            fill=style.fill_color, outline=style.border_color,
            width=style.border_width, tags=tags
        )
        items.append(rect)

        # Truncate text if too long
        display_text = text if len(text) <= 15 else text[:12] + "..."

        text_item = canvas.create_text(
            x, y,
            text=display_text, fill=style.text_color,
            font=(style.font_family, style.font_size),
            tags=tags, width=w-10
        )
        items.append(text_item)

        return items

    def draw_connection(self, canvas: tk.Canvas, x1: int, y1: int,
                       x2: int, y2: int, style: ConnectionStyle, tags: tuple = ('connection',)) -> List[int]:
        """Draw simple straight line"""
        item = canvas.create_line(
            x1, y1, x2, y2,
            fill=style.color, width=style.width,
            tags=tags
        )
        return [item]


class ValentineTheme(Theme):
    """Valentine's Day theme - hearts and roses"""

    def __init__(self):
        super().__init__("valentine")

        self.node_styles = {
            0: NodeStyle(
                shape='heart_small',
                fill_color='#FFB6C1',  # Light pink
                border_color='#FF1493',  # Deep pink
                border_width=2,
                text_color='#8B0000',  # Dark red
                font_family='Arial',
                font_size=12,
                width=100,
                height=90,
                shadow=True
            ),
            1: NodeStyle(
                shape='heart_medium',
                fill_color='#FF69B4',  # Hot pink
                border_color='#C71585',  # Medium violet red
                border_width=3,
                text_color='#FFFFFF',
                font_family='Arial',
                font_size=14,
                width=120,
                height=110,
                shadow=True
            ),
            2: NodeStyle(
                shape='heart_large',
                fill_color='#FF1493',  # Deep pink
                border_color='#8B0000',  # Dark red
                border_width=4,
                text_color='#FFFFFF',
                font_family='Arial',
                font_size=16,
                width=150,
                height=140,
                shadow=True
            )
        }

        self.connection_style = ConnectionStyle(
            type='roses',
            color='#FF69B4',
            width=2,
            animated=False
        )

        self.cabinet_style = CabinetStyle(
            type='gift_box',
            color='#FFB6C1',
            width=120,
            height=400,
            drawer_colors={
                'top': '#FF69B4',
                'middle': '#FFB6C1',
                'bottom': '#FF1493'
            }
        )

    def get_node_style(self, tier: int, completed: bool = False) -> NodeStyle:
        if tier >= 2:
            style = self.node_styles[2]
        elif tier == 1:
            style = self.node_styles[1]
        else:
            style = self.node_styles[0]

        if completed:
            import copy
            style = copy.copy(style)
            style.fill_color = '#98FB98'  # Pale green

        return style

    def draw_node(self, canvas: tk.Canvas, x: int, y: int,
                  style: NodeStyle, text: str, tags: tuple) -> List[int]:
        """Draw heart-shaped node"""
        items = []
        w, h = style.width, style.height

        # Shadow
        if style.shadow:
            shadow = canvas.create_oval(
                x - w//2 + 5, y + h//2 - 5,
                x + w//2 + 5, y + h//2 + 15,
                fill='#000000', outline='', stipple='gray50',
                tags=tags
            )
            items.append(shadow)

        # Simplified heart: two circles + triangle
        # Left circle
        left_circle = canvas.create_oval(
            x - w//3, y - h//4,
            x, y + h//8,
            fill=style.fill_color,
            outline=style.border_color,
            width=style.border_width,
            tags=tags
        )
        items.append(left_circle)

        # Right circle
        right_circle = canvas.create_oval(
            x, y - h//4,
            x + w//3, y + h//8,
            fill=style.fill_color,
            outline=style.border_color,
            width=style.border_width,
            tags=tags
        )
        items.append(right_circle)

        # Bottom triangle (forms point of heart)
        triangle = canvas.create_polygon(
            x - w//3, y + h//8,
            x + w//3, y + h//8,
            x, y + h//2,
            fill=style.fill_color,
            outline=style.border_color,
            width=style.border_width,
            tags=tags
        )
        items.append(triangle)

        # Text
        text_item = canvas.create_text(
            x, y + h//8,
            text=text,
            fill=style.text_color,
            font=(style.font_family, style.font_size, 'bold'),
            tags=tags,
            width=w - 20
        )
        items.append(text_item)

        return items

    def draw_connection(self, canvas: tk.Canvas, x1: int, y1: int,
                       x2: int, y2: int, style: ConnectionStyle, tags: tuple = ('connection',)) -> List[int]:
        """Draw rose vine connection with hearts"""
        items = []

        # Main vine
        line = canvas.create_line(
            x1, y1, x2, y2,
            fill=style.color,
            width=style.width,
            smooth=True,
            tags=tags
        )
        items.append(line)

        # Add heart symbol at midpoint
        import math
        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        if distance > 80:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            heart = canvas.create_text(
                mid_x, mid_y,
                text='♥',
                fill=style.color,
                font=('Arial', 12),
                tags=tags
            )
            items.append(heart)

        return items


class ChristmasTheme(Theme):
    """Christmas theme - presents and ornaments"""

    def __init__(self):
        super().__init__("christmas")

        self.node_styles = {
            0: NodeStyle(
                shape='present_small',
                fill_color='#FF0000',  # Red
                border_color='#FFD700',  # Gold
                border_width=2,
                text_color='#FFFFFF',
                font_family='Arial',
                font_size=12,
                width=100,
                height=80,
                shadow=True
            ),
            1: NodeStyle(
                shape='present_medium',
                fill_color='#228B22',  # Forest green
                border_color='#FFD700',
                border_width=3,
                text_color='#FFFFFF',
                font_family='Arial',
                font_size=14,
                width=120,
                height=100,
                shadow=True
            ),
            2: NodeStyle(
                shape='ornament',
                fill_color='#FFD700',  # Gold
                border_color='#8B0000',  # Dark red
                border_width=4,
                text_color='#8B0000',
                font_family='Arial',
                font_size=16,
                width=140,
                height=140,
                shadow=True
            )
        }

        self.connection_style = ConnectionStyle(
            type='garland',
            color='#FFD700',
            width=2,
            animated=False
        )

        self.cabinet_style = CabinetStyle(
            type='christmas_tree',
            color='#228B22',
            width=120,
            height=400,
            drawer_colors={
                'top': '#FF0000',
                'middle': '#FFD700',
                'bottom': '#228B22'
            }
        )

    def get_node_style(self, tier: int, completed: bool = False) -> NodeStyle:
        if tier >= 2:
            style = self.node_styles[2]
        elif tier == 1:
            style = self.node_styles[1]
        else:
            style = self.node_styles[0]

        if completed:
            import copy
            style = copy.copy(style)
            style.fill_color = '#C8E6C9'  # Light green for completed

        return style

    def draw_node(self, canvas: tk.Canvas, x: int, y: int,
                  style: NodeStyle, text: str, tags: tuple) -> List[int]:
        """Draw present box or ornament"""
        items = []
        w, h = style.width, style.height

        if 'present' in style.shape:
            # Draw present box
            box = canvas.create_rectangle(
                x - w//2, y - h//2,
                x + w//2, y + h//2,
                fill=style.fill_color,
                outline=style.border_color,
                width=style.border_width,
                tags=tags
            )
            items.append(box)

            # Ribbon vertical
            ribbon_v = canvas.create_rectangle(
                x - 5, y - h//2,
                x + 5, y + h//2,
                fill=style.border_color,
                outline='',
                tags=tags
            )
            items.append(ribbon_v)

            # Ribbon horizontal
            ribbon_h = canvas.create_rectangle(
                x - w//2, y - 5,
                x + w//2, y + 5,
                fill=style.border_color,
                outline='',
                tags=tags
            )
            items.append(ribbon_h)

            # Bow on top
            bow = canvas.create_oval(
                x - 15, y - h//2 - 10,
                x + 15, y - h//2 + 10,
                fill=style.border_color,
                outline='',
                tags=tags
            )
            items.append(bow)

        elif 'ornament' in style.shape:
            # Cap/hook
            cap = canvas.create_rectangle(
                x - 8, y - h//2 - 10,
                x + 8, y - h//2,
                fill='#C0C0C0',
                outline=style.border_color,
                width=2,
                tags=tags
            )
            items.append(cap)

            # Ball
            ball = canvas.create_oval(
                x - w//2, y - h//2,
                x + w//2, y + h//2,
                fill=style.fill_color,
                outline=style.border_color,
                width=style.border_width,
                tags=tags
            )
            items.append(ball)

            # Shine effect
            shine = canvas.create_oval(
                x - w//4, y - h//4,
                x - w//8, y - h//8,
                fill='#FFFFFF',
                outline='',
                tags=tags
            )
            items.append(shine)

        # Text
        text_item = canvas.create_text(
            x, y,
            text=text,
            fill=style.text_color,
            font=(style.font_family, style.font_size, 'bold'),
            tags=tags,
            width=w - 20
        )
        items.append(text_item)

        return items

    def draw_connection(self, canvas: tk.Canvas, x1: int, y1: int,
                       x2: int, y2: int, style: ConnectionStyle, tags: tuple = ('connection',)) -> List[int]:
        """Draw garland with colored lights"""
        items = []

        # Main wire
        wire = canvas.create_line(
            x1, y1, x2, y2,
            fill='#2F4F2F',  # Dark green wire
            width=2,
            tags=tags
        )
        items.append(wire)

        # Add light bulbs along the wire
        import math
        distance = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        num_lights = int(distance / 60)  # One light every 60 pixels

        for i in range(1, num_lights + 1):
            t = i / (num_lights + 1)
            light_x = x1 + (x2 - x1) * t
            light_y = y1 + (y2 - y1) * t

            # Alternate colors
            colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00']
            color = colors[i % len(colors)]

            # Draw bulb
            bulb = canvas.create_oval(
                light_x - 4, light_y - 4,
                light_x + 4, light_y + 4,
                fill=color,
                outline='#FFFFFF',
                tags=tags
            )
            items.append(bulb)

        return items


class ThemeRegistry:
    """Manages available themes"""

    def __init__(self):
        self.themes = {}
        self.current_theme_name = 'default'

        # Register built-in themes
        self.register(CemeteryTheme())
        self.register(DefaultTheme())

        # Register holiday themes
        self.register(ValentineTheme())
        self.register(ChristmasTheme())

    def register(self, theme: Theme):
        """Register a theme"""
        self.themes[theme.name] = theme

    def get_current(self) -> Theme:
        """Get currently active theme"""
        return self.themes.get(self.current_theme_name, self.themes['default'])

    def set_current(self, theme_name: str) -> bool:
        """Switch to a different theme"""
        if theme_name in self.themes:
            self.current_theme_name = theme_name
            return True
        return False

    def list_themes(self) -> List[str]:
        """Get list of available theme names"""
        return list(self.themes.keys())
