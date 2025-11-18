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


class ThemeRegistry:
    """Manages available themes"""

    def __init__(self):
        self.themes = {}
        self.current_theme_name = 'default'

        # Register built-in themes
        self.register(CemeteryTheme())
        self.register(DefaultTheme())

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
