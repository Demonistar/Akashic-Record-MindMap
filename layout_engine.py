#!/usr/bin/env python3
"""
Layout Engine for Akashic Record MindMap
Provides multiple layout algorithms for auto-arranging nodes
"""

from typing import List, Dict, Tuple
import math


class Layout:
    """Base class for layout algorithms"""

    def arrange(self, parent_node, children_nodes: list, canvas_width: int, canvas_height: int) -> Dict[str, Tuple[int, int]]:
        """
        Calculate positions for children nodes
        Returns: {node_id: (x, y)}
        """
        raise NotImplementedError


class TreeLayout(Layout):
    """Hierarchical tree layout - parent at top, children below"""

    def __init__(self, horizontal_spacing=150, vertical_spacing=120):
        self.h_spacing = horizontal_spacing
        self.v_spacing = vertical_spacing

    def arrange(self, parent_node, children_nodes: list, canvas_width: int, canvas_height: int) -> Dict[str, Tuple[int, int]]:
        positions = {}

        if not children_nodes:
            return positions

        # Parent position
        parent_x = parent_node.x
        parent_y = parent_node.y

        # Calculate total width needed
        total_width = len(children_nodes) * self.h_spacing
        start_x = parent_x - total_width // 2 + self.h_spacing // 2

        # Position children in a row below parent
        for i, child in enumerate(children_nodes):
            child_x = start_x + i * self.h_spacing
            child_y = parent_y + self.v_spacing
            positions[child.id] = (child_x, child_y)

        return positions


class GridLayout(Layout):
    """Grid layout - children arranged in rows and columns"""

    def __init__(self, columns=3, spacing=120):
        self.columns = columns
        self.spacing = spacing

    def arrange(self, parent_node, children_nodes: list, canvas_width: int, canvas_height: int) -> Dict[str, Tuple[int, int]]:
        positions = {}

        if not children_nodes:
            return positions

        parent_x = parent_node.x
        parent_y = parent_node.y

        rows = math.ceil(len(children_nodes) / self.columns)

        # Center the grid around parent
        grid_width = self.columns * self.spacing
        grid_height = rows * self.spacing
        start_x = parent_x - grid_width // 2 + self.spacing // 2
        start_y = parent_y + self.spacing

        for i, child in enumerate(children_nodes):
            row = i // self.columns
            col = i % self.columns

            child_x = start_x + col * self.spacing
            child_y = start_y + row * self.spacing
            positions[child.id] = (child_x, child_y)

        return positions


class HorizontalLayout(Layout):
    """Horizontal layout - children in a row beside parent"""

    def __init__(self, spacing=150):
        self.spacing = spacing

    def arrange(self, parent_node, children_nodes: list, canvas_width: int, canvas_height: int) -> Dict[str, Tuple[int, int]]:
        positions = {}

        if not children_nodes:
            return positions

        parent_x = parent_node.x
        parent_y = parent_node.y

        total_width = len(children_nodes) * self.spacing
        start_x = parent_x + self.spacing
        start_y = parent_y - total_width // 2 + self.spacing // 2

        for i, child in enumerate(children_nodes):
            child_x = start_x
            child_y = start_y + i * self.spacing
            positions[child.id] = (child_x, child_y)

        return positions


class VerticalLayout(Layout):
    """Vertical layout - children in a column below parent"""

    def __init__(self, spacing=100):
        self.spacing = spacing

    def arrange(self, parent_node, children_nodes: list, canvas_width: int, canvas_height: int) -> Dict[str, Tuple[int, int]]:
        positions = {}

        if not children_nodes:
            return positions

        parent_x = parent_node.x
        parent_y = parent_node.y

        start_y = parent_y + self.spacing

        for i, child in enumerate(children_nodes):
            child_x = parent_x
            child_y = start_y + i * self.spacing
            positions[child.id] = (child_x, child_y)

        return positions


class RadialLayout(Layout):
    """Radial layout - children arranged in a circle around parent"""

    def __init__(self, radius=150):
        self.radius = radius

    def arrange(self, parent_node, children_nodes: list, canvas_width: int, canvas_height: int) -> Dict[str, Tuple[int, int]]:
        positions = {}

        if not children_nodes:
            return positions

        parent_x = parent_node.x
        parent_y = parent_node.y

        angle_step = 2 * math.pi / len(children_nodes)

        for i, child in enumerate(children_nodes):
            angle = i * angle_step - math.pi / 2  # Start at top
            child_x = parent_x + int(self.radius * math.cos(angle))
            child_y = parent_y + int(self.radius * math.sin(angle))
            positions[child.id] = (child_x, child_y)

        return positions


class LayoutEngine:
    """Manages layout algorithms"""

    def __init__(self):
        self.layouts = {
            'tree': TreeLayout(),
            'grid': GridLayout(),
            'horizontal': HorizontalLayout(),
            'vertical': VerticalLayout(),
            'radial': RadialLayout()
        }

    def apply_layout(self, layout_name: str, parent_node, children_nodes: list,
                    canvas_width: int, canvas_height: int) -> Dict[str, Tuple[int, int]]:
        """Apply a layout algorithm and return new positions"""
        if layout_name not in self.layouts:
            layout_name = 'tree'  # Default

        layout = self.layouts[layout_name]
        return layout.arrange(parent_node, children_nodes, canvas_width, canvas_height)

    def get_available_layouts(self) -> List[str]:
        """Get list of available layout names"""
        return list(self.layouts.keys())
