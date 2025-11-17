#!/usr/bin/env python3
"""
Desktop MindMap Application - Production Ready
A comprehensive mindmap application with desktop overlay, file cabinet interface,
and advanced node management features.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
import datetime
import time
import math
import difflib
from collections import deque

# Optional imports with graceful fallbacks
try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available - advanced graphics disabled")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("NumPy not available - advanced physics disabled")

try:
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.pagesizes import letter
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not available - PDF export disabled")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("python-docx not available - DOCX export disabled")

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    print("openpyxl not available - XLSX export disabled")


# ============================================================================
# CORE CLASSES
# ============================================================================

class MindMapNode:
    """Stores node data with full metadata"""

    def __init__(self, node_id, content="New Node", tier=1, x=100, y=100, parent_id=None):
        self.id = node_id
        self.content = content
        self.tier = max(1, min(5, tier))  # Clamp between 1-5
        self.x = x
        self.y = y
        self.parent_id = parent_id
        self.children_ids = []
        self.collapsed = False
        self.timestamp = datetime.datetime.now().isoformat()
        self.type = "mindmap-node"
        self.source = "user"
        self.tags = []
        self.emotion = "neutral"
        self.linked_node_ids = []
        self.meta = {}

    def get_size(self):
        """Calculate node size based on tier"""
        base_width = 120
        base_height = 40
        scale = 1.0 - (self.tier - 1) * 0.15
        return int(base_width * scale), int(base_height * scale)

    def get_display_text(self):
        """Get truncated text for display"""
        max_chars = 15
        if len(self.content) <= max_chars:
            return self.content
        return self.content[:max_chars] + "..."

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "content": self.content,
            "tier": self.tier,
            "x": self.x,
            "y": self.y,
            "parent_id": self.parent_id,
            "children_ids": self.children_ids,
            "collapsed": self.collapsed,
            "timestamp": self.timestamp,
            "type": self.type,
            "source": self.source,
            "tags": self.tags,
            "emotion": self.emotion,
            "linked_node_ids": self.linked_node_ids,
            "meta": self.meta
        }

    @staticmethod
    def from_dict(data):
        """Create node from dictionary"""
        node = MindMapNode(
            data["id"],
            data.get("content", "New Node"),
            data.get("tier", 1),
            data.get("x", 100),
            data.get("y", 100),
            data.get("parent_id")
        )
        node.children_ids = data.get("children_ids", [])
        node.collapsed = data.get("collapsed", False)
        node.timestamp = data.get("timestamp", datetime.datetime.now().isoformat())
        node.type = data.get("type", "mindmap-node")
        node.source = data.get("source", "user")
        node.tags = data.get("tags", [])
        node.emotion = data.get("emotion", "neutral")
        node.linked_node_ids = data.get("linked_node_ids", [])
        node.meta = data.get("meta", {})
        return node


class Connection:
    """Manages connections between nodes with physics"""

    def __init__(self, conn_id, from_node_id, to_node_id, conn_type="hierarchical", weight=5):
        self.id = conn_id
        self.from_node_id = from_node_id
        self.to_node_id = to_node_id
        self.type = conn_type  # "hierarchical" or "reference"
        self.weight = max(1, min(10, weight))  # Clamp 1-10

    def get_color(self):
        """Get connection color based on type"""
        if self.type == "hierarchical":
            return "#1976D2"  # Blue
        else:
            return "#FF9800"  # Orange

    def get_width(self):
        """Get line width based on weight"""
        return 2 + (self.weight - 1) * 0.2

    def is_slack(self):
        """Check if connection should have slack/sag"""
        return self.weight <= 5

    def get_sag_amount(self):
        """Calculate sag amount for slack connections"""
        if not self.is_slack():
            return 0
        # Weight 1 = max sag (50px), weight 5 = slight sag (10px)
        return 50 - (self.weight - 1) * 10

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "from_node_id": self.from_node_id,
            "to_node_id": self.to_node_id,
            "type": self.type,
            "weight": self.weight
        }

    @staticmethod
    def from_dict(data):
        """Create connection from dictionary"""
        return Connection(
            data["id"],
            data["from_node_id"],
            data["to_node_id"],
            data.get("type", "hierarchical"),
            data.get("weight", 5)
        )


class FileCabinet:
    """Handles the 3-drawer cabinet interface"""

    def __init__(self, x=50, y=50):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 150
        self.locked = False
        self.orientation = "right"  # "right" or "left"

        # Drawer states
        self.top_drawer_open = False
        self.middle_drawer_open = False
        self.bottom_drawer_open = False

        self.drawer_height = 40
        self.drawer_slide_amount = 25

    def get_bounds(self):
        """Get cabinet boundary rectangle"""
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def get_drawer_bounds(self, drawer_name):
        """Get specific drawer boundary rectangle"""
        drawer_y = {
            "top": self.y + 10,
            "middle": self.y + 55,
            "bottom": self.y + 100
        }

        y = drawer_y.get(drawer_name, self.y)
        slide = self.drawer_slide_amount if self.is_drawer_open(drawer_name) else 0

        if self.orientation == "right":
            return (self.x, y, self.x + self.width + slide, y + self.drawer_height)
        else:
            return (self.x - slide, y, self.x + self.width, y + self.drawer_height)

    def is_drawer_open(self, drawer_name):
        """Check if a drawer is open"""
        if drawer_name == "top":
            return self.top_drawer_open
        elif drawer_name == "middle":
            return self.middle_drawer_open
        elif drawer_name == "bottom":
            return self.bottom_drawer_open
        return False

    def toggle_drawer(self, drawer_name):
        """Toggle drawer open/close state"""
        if drawer_name == "top":
            self.top_drawer_open = not self.top_drawer_open
        elif drawer_name == "middle":
            self.middle_drawer_open = not self.middle_drawer_open
        elif drawer_name == "bottom":
            self.bottom_drawer_open = not self.bottom_drawer_open

    def close_all_drawers(self):
        """Close all drawers"""
        self.top_drawer_open = False
        self.middle_drawer_open = False
        self.bottom_drawer_open = False

    def point_in_cabinet(self, x, y):
        """Check if point is inside cabinet body (not drawers)"""
        bounds = self.get_bounds()
        return bounds[0] <= x <= bounds[2] and bounds[1] <= y <= bounds[3]

    def point_in_drawer(self, x, y, drawer_name):
        """Check if point is inside specific drawer"""
        bounds = self.get_drawer_bounds(drawer_name)
        return bounds[0] <= x <= bounds[2] and bounds[1] <= y <= bounds[3]

    def update_orientation(self, screen_width):
        """Update orientation based on screen position"""
        center_x = screen_width / 2
        if self.x < center_x:
            self.orientation = "right"
        else:
            self.orientation = "left"

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "x": self.x,
            "y": self.y,
            "orientation": self.orientation,
            "locked": self.locked
        }

    @staticmethod
    def from_dict(data):
        """Create cabinet from dictionary"""
        cabinet = FileCabinet(data.get("x", 50), data.get("y", 50))
        cabinet.orientation = data.get("orientation", "right")
        cabinet.locked = data.get("locked", False)
        return cabinet


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class MindMapApp:
    """Main application controller"""

    def __init__(self, root):
        self.root = root
        self.root.title("Akashic Record MindMap")

        # Window setup
        self.setup_window()

        # Data structures
        self.nodes = {}  # node_id -> MindMapNode
        self.connections = {}  # conn_id -> Connection
        self.selected_nodes = []
        self.cabinet = FileCabinet(50, 50)

        # State variables
        self.drag_data = {"x": 0, "y": 0, "item": None, "type": None}
        self.linking_mode = False
        self.linking_from_node = None
        self.canvas_offset = {"x": 0, "y": 0}
        self.zoom_factor = 1.0
        self.current_file = None
        self.auto_save_enabled = True
        self.theme = "default"

        # Manila folder state
        self.manila_folder_open = None  # None, "projects", or "settings"
        self.manila_folder_items = []

        # Undo/redo
        self.undo_stack = deque(maxlen=50)
        self.redo_stack = deque(maxlen=50)

        # UI setup
        self.setup_canvas()
        self.setup_menu()
        self.setup_bindings()

        # Start auto-save timer
        self.auto_save_timer()

        # Initial draw
        self.redraw_all()

        print("MindMap Desktop Application started successfully")
        print("Press Ctrl+N to create your first node")

    def setup_window(self):
        """Setup fullscreen transparent window"""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Fullscreen without forcing always-on-top
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Don't use -fullscreen as it blocks alt-tab
        # Instead use overrideredirect for borderless window
        self.root.overrideredirect(False)  # Keep window decorations for now

        # Transparency (0.9 alpha) - makes window see-through
        self.root.attributes("-alpha", 0.9)

        # DON'T keep on top - allow alt-tab and switching to other apps
        # Window will come to front when clicked due to normal window behavior
        # self.root.attributes("-topmost", True)  # REMOVED

        # Light gray background - with 90% transparency, desktop shows through
        # Using systemTransparent for better platform compatibility
        try:
            self.root.configure(bg='systemTransparent')
        except:
            # Fallback for systems that don't support systemTransparent
            self.root.configure(bg='#F0F0F0')

    def setup_canvas(self):
        """Initialize canvas"""
        # Canvas with light background - combined with window alpha, desktop shows through
        # Light gray that becomes mostly transparent with the window's alpha setting
        self.canvas = tk.Canvas(
            self.root,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Status text
        self.status_text = self.canvas.create_text(
            10, self.root.winfo_screenheight() - 20,
            anchor="sw",
            text="Nodes: 0/0 | Zoom: 100%",
            font=("Arial", 10),
            fill="#424242"
        )

    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Project", command=self.open_project, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Project", command=self.save_project, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy", command=self.copy_nodes, accelerator="Ctrl+C")
        edit_menu.add_command(label="Cut", command=self.cut_nodes, accelerator="Ctrl+X")
        edit_menu.add_command(label="Paste", command=self.paste_nodes, accelerator="Ctrl+V")
        edit_menu.add_command(label="Delete", command=self.delete_selected_nodes, accelerator="Del")

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Minimap", command=self.toggle_minimap, accelerator="Ctrl+M")
        view_menu.add_command(label="Expand All", command=self.expand_all, accelerator="Ctrl+E")

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_help, accelerator="F1")

    def show_dialog_topmost(self, dialog_func, *args, **kwargs):
        """Helper to show dialogs properly - ensures dialogs appear in front"""
        # No need to toggle topmost since we're not using it anymore
        # Just call the dialog function directly
        result = dialog_func(*args, **kwargs)
        return result

    def setup_bindings(self):
        """Setup event bindings"""
        # Mouse events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)

        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.create_node())
        self.root.bind("<Control-s>", lambda e: self.save_project())
        self.root.bind("<Control-o>", lambda e: self.open_project())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<Control-c>", lambda e: self.copy_nodes())
        self.root.bind("<Control-x>", lambda e: self.cut_nodes())
        self.root.bind("<Control-v>", lambda e: self.paste_nodes())
        self.root.bind("<Delete>", lambda e: self.delete_selected_nodes())
        self.root.bind("<Control-l>", lambda e: self.start_linking_mode())
        self.root.bind("<Control-t>", lambda e: self.adjust_connection_tension())
        self.root.bind("<Control-f>", lambda e: self.search_nodes())
        self.root.bind("<Control-m>", lambda e: self.toggle_minimap())
        self.root.bind("<Control-k>", lambda e: self.toggle_cabinet_lock())
        self.root.bind("<Control-e>", lambda e: self.expand_all())
        self.root.bind("<Control-r>", lambda e: self.collapse_selected())
        self.root.bind("<F1>", lambda e: self.show_help())
        self.root.bind("<F5>", lambda e: self.refresh_auto_links())
        self.root.bind("<Escape>", lambda e: self.clear_selection())
        self.root.bind("<Control-q>", lambda e: self.exit_app())
        self.root.bind("<Control-w>", lambda e: self.minimize_window())

    # ========================================================================
    # DRAWING METHODS
    # ========================================================================

    def redraw_all(self):
        """Redraw entire canvas"""
        self.canvas.delete("all")

        # Draw connections first (behind nodes)
        for conn in self.connections.values():
            self.draw_connection(conn)

        # Draw nodes
        for node in self.nodes.values():
            self.draw_node(node)

        # Draw file cabinet
        self.draw_cabinet()

        # Draw manila folder if open
        if self.manila_folder_open:
            self.draw_manila_folder()

        # Update status
        self.update_status()

    def draw_node(self, node):
        """Draw a single node"""
        if node.collapsed and node.parent_id:
            return  # Don't draw collapsed child nodes

        width, height = node.get_size()
        x1 = node.x - width // 2
        y1 = node.y - height // 2
        x2 = node.x + width // 2
        y2 = node.y + height // 2

        # Color scheme based on theme
        if self.theme == "dark":
            fill_color = self.get_gradient_color("#424242", "#BDBDBD", node.tier / 5.0)
        else:
            fill_color = self.get_gradient_color("#E3F2FD", "#42A5F5", node.tier / 5.0)

        # Draw node rectangle
        outline_color = "#FF9800" if node.id in self.selected_nodes else "#1976D2"
        outline_width = 3 if node.id in self.selected_nodes else 1

        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=fill_color,
            outline=outline_color,
            width=outline_width,
            tags=(f"node_{node.id}", "node")
        )

        # Draw text
        self.canvas.create_text(
            node.x, node.y,
            text=node.get_display_text(),
            font=("Arial", 10, "bold"),
            fill="#212121",
            tags=(f"node_{node.id}", "node")
        )

        # Draw tier badge
        badge_size = 16
        badge_x = x2 - badge_size - 2
        badge_y = y1 + 2

        self.canvas.create_oval(
            badge_x, badge_y,
            badge_x + badge_size, badge_y + badge_size,
            fill="#FFC107",
            outline="#F57C00",
            tags=(f"node_{node.id}", "node")
        )

        self.canvas.create_text(
            badge_x + badge_size // 2, badge_y + badge_size // 2,
            text=str(node.tier),
            font=("Arial", 8, "bold"),
            fill="#212121",
            tags=(f"node_{node.id}", "node")
        )

    def draw_connection(self, conn):
        """Draw a connection between nodes"""
        # Get nodes
        from_node = self.nodes.get(conn.from_node_id)
        to_node = self.nodes.get(conn.to_node_id)

        if not from_node or not to_node:
            return

        # Calculate line points
        x1, y1 = from_node.x, from_node.y
        x2, y2 = to_node.x, to_node.y

        # Line style
        color = conn.get_color()
        width = int(conn.get_width())
        dash = (5, 5) if conn.type == "reference" else ()

        # Draw with sag if applicable
        if conn.is_slack():
            sag = conn.get_sag_amount()
            # Calculate midpoint with sag (catenary approximation)
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2 + sag

            # Draw curved line using multiple segments
            self.canvas.create_line(
                x1, y1, mid_x, mid_y,
                fill=color,
                width=width,
                dash=dash,
                smooth=True,
                tags=(f"conn_{conn.id}", "connection")
            )
            self.canvas.create_line(
                mid_x, mid_y, x2, y2,
                fill=color,
                width=width,
                dash=dash,
                smooth=True,
                tags=(f"conn_{conn.id}", "connection")
            )
        else:
            # Straight line
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill=color,
                width=width,
                dash=dash,
                tags=(f"conn_{conn.id}", "connection")
            )

    def draw_cabinet(self):
        """Draw file cabinet"""
        x, y = self.cabinet.x, self.cabinet.y
        w, h = self.cabinet.width, self.cabinet.height

        # Cabinet body - wooden brown
        self.canvas.create_rectangle(
            x, y, x + w, y + h,
            fill="#8D6E63",
            outline="#5D4037",
            width=2,
            tags=("cabinet_body", "cabinet")
        )

        # 3D depth effect (shadow)
        shadow_offset = 3
        self.canvas.create_rectangle(
            x + shadow_offset, y + shadow_offset,
            x + w + shadow_offset, y + h + shadow_offset,
            fill="#424242",
            outline="",
            tags=("cabinet_shadow", "cabinet")
        )
        # Lower shadow
        self.canvas.tag_lower("cabinet_shadow")

        # Draw drawers
        self.draw_drawer("top", "Nodes")
        self.draw_drawer("middle", "Projects")
        self.draw_drawer("bottom", "Settings")

        # Draw lock icon if locked
        if self.cabinet.locked:
            lock_x = x + w - 20
            lock_y = y + 5
            self.canvas.create_text(
                lock_x, lock_y,
                text="🔒",
                font=("Arial", 12),
                tags=("cabinet_lock", "cabinet")
            )

    def draw_drawer(self, drawer_name, label):
        """Draw a single drawer"""
        bounds = self.cabinet.get_drawer_bounds(drawer_name)
        x1, y1, x2, y2 = bounds

        # Drawer color (slightly lighter than cabinet)
        drawer_color = "#A1887F"

        # Draw drawer
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=drawer_color,
            outline="#5D4037",
            width=2,
            tags=(f"drawer_{drawer_name}", "drawer", "cabinet")
        )

        # Draw handle
        handle_size = 10
        handle_x = (x1 + x2) / 2
        handle_y = (y1 + y2) / 2

        self.canvas.create_oval(
            handle_x - handle_size // 2, handle_y - handle_size // 2,
            handle_x + handle_size // 2, handle_y + handle_size // 2,
            fill="#5D4037",
            outline="#3E2723",
            tags=(f"drawer_{drawer_name}", "drawer", "cabinet")
        )

        # Draw label
        label_y = y1 - 8
        self.canvas.create_text(
            (x1 + x2) / 2, label_y,
            text=label,
            font=("Arial", 8, "bold"),
            fill="#424242",
            tags=("cabinet_label", "cabinet")
        )

    def draw_manila_folder(self):
        """Draw manila folder interface"""
        # Folder dimensions
        folder_width = 400
        folder_height = 500
        folder_x = (self.root.winfo_screenwidth() - folder_width) // 2
        folder_y = (self.root.winfo_screenheight() - folder_height) // 2

        # Shadow
        shadow_offset = 5
        self.canvas.create_rectangle(
            folder_x + shadow_offset, folder_y + shadow_offset,
            folder_x + folder_width + shadow_offset,
            folder_y + folder_height + shadow_offset,
            fill="#424242",
            outline="",
            tags=("manila_shadow", "manila")
        )

        # Folder background - tan color
        self.canvas.create_rectangle(
            folder_x, folder_y,
            folder_x + folder_width, folder_y + folder_height,
            fill="#F5DEB3",
            outline="#8B7355",
            width=3,
            tags=("manila_bg", "manila")
        )

        # Tab
        tab_width = 120
        tab_height = 30
        self.canvas.create_polygon(
            folder_x + 20, folder_y,
            folder_x + 20, folder_y - tab_height,
            folder_x + 20 + tab_width, folder_y - tab_height,
            folder_x + 20 + tab_width, folder_y,
            fill="#F5DEB3",
            outline="#8B7355",
            width=2,
            tags=("manila_tab", "manila")
        )

        # Tab label
        tab_label = "Projects" if self.manila_folder_open == "projects" else "Settings"
        self.canvas.create_text(
            folder_x + 20 + tab_width // 2,
            folder_y - tab_height // 2,
            text=tab_label,
            font=("Arial", 10, "bold"),
            fill="#424242",
            tags=("manila_tab_label", "manila")
        )

        # Close button
        close_x = folder_x + folder_width - 30
        close_y = folder_y + 10
        self.canvas.create_oval(
            close_x, close_y, close_x + 20, close_y + 20,
            fill="#F44336",
            outline="#C62828",
            width=2,
            tags=("manila_close", "manila")
        )
        self.canvas.create_text(
            close_x + 10, close_y + 10,
            text="X",
            font=("Arial", 12, "bold"),
            fill="white",
            tags=("manila_close", "manila")
        )

        # Content
        if self.manila_folder_open == "projects":
            self.draw_projects_folder_content(folder_x, folder_y, folder_width, folder_height)
        elif self.manila_folder_open == "settings":
            self.draw_settings_folder_content(folder_x, folder_y, folder_width, folder_height)

    def draw_projects_folder_content(self, x, y, width, height):
        """Draw projects folder content"""
        # Title
        self.canvas.create_text(
            x + width // 2, y + 40,
            text="Recent Projects",
            font=("Arial", 16, "bold"),
            fill="#424242",
            tags=("manila_content", "manila")
        )

        # Find recent .json files
        import glob
        json_files = glob.glob("*.json")
        json_files.sort(key=os.path.getmtime, reverse=True)
        recent_files = json_files[:4]

        # Draw file list
        start_y = y + 80
        self.manila_folder_items = []

        for i, filename in enumerate(recent_files):
            item_y = start_y + i * 60

            # File item background
            self.canvas.create_rectangle(
                x + 20, item_y,
                x + width - 20, item_y + 50,
                fill="white",
                outline="#BDBDBD",
                width=1,
                tags=("manila_content", "manila")
            )

            # Filename
            self.canvas.create_text(
                x + 30, item_y + 15,
                text=filename,
                anchor="w",
                font=("Arial", 11),
                fill="#424242",
                tags=("manila_content", "manila")
            )

            # Open button
            btn_x = x + width - 100
            btn_y = item_y + 15
            btn_id = self.canvas.create_rectangle(
                btn_x, btn_y,
                btn_x + 70, btn_y + 25,
                fill="#4CAF50",
                outline="#2E7D32",
                width=2,
                tags=(f"manila_open_{i}", "manila_button", "manila")
            )

            self.canvas.create_text(
                btn_x + 35, btn_y + 12,
                text="Open",
                font=("Arial", 10, "bold"),
                fill="white",
                tags=(f"manila_open_{i}", "manila_button", "manila")
            )

            self.manila_folder_items.append(filename)

    def draw_settings_folder_content(self, x, y, width, height):
        """Draw settings folder content"""
        # Title
        self.canvas.create_text(
            x + width // 2, y + 40,
            text="Settings",
            font=("Arial", 16, "bold"),
            fill="#424242",
            tags=("manila_content", "manila")
        )

        start_y = y + 80

        # Auto-save toggle
        self.canvas.create_text(
            x + 30, start_y,
            text="Auto-Save:",
            anchor="w",
            font=("Arial", 12, "bold"),
            fill="#424242",
            tags=("manila_content", "manila")
        )

        toggle_color = "#4CAF50" if self.auto_save_enabled else "#F44336"
        toggle_text = "ON" if self.auto_save_enabled else "OFF"

        self.canvas.create_rectangle(
            x + 150, start_y - 10,
            x + 220, start_y + 15,
            fill=toggle_color,
            outline="#424242",
            width=2,
            tags=("manila_autosave_toggle", "manila_button", "manila")
        )

        self.canvas.create_text(
            x + 185, start_y + 2,
            text=toggle_text,
            font=("Arial", 11, "bold"),
            fill="white",
            tags=("manila_autosave_toggle", "manila_button", "manila")
        )

        # Theme selector
        start_y += 60
        self.canvas.create_text(
            x + 30, start_y,
            text="Theme:",
            anchor="w",
            font=("Arial", 12, "bold"),
            fill="#424242",
            tags=("manila_content", "manila")
        )

        theme_text = "Default" if self.theme == "default" else "Dark"
        self.canvas.create_rectangle(
            x + 150, start_y - 10,
            x + 250, start_y + 15,
            fill="#2196F3",
            outline="#424242",
            width=2,
            tags=("manila_theme_toggle", "manila_button", "manila")
        )

        self.canvas.create_text(
            x + 200, start_y + 2,
            text=theme_text,
            font=("Arial", 11, "bold"),
            fill="white",
            tags=("manila_theme_toggle", "manila_button", "manila")
        )

        # Export section
        start_y += 60
        self.canvas.create_text(
            x + 30, start_y,
            text="Export:",
            anchor="w",
            font=("Arial", 12, "bold"),
            fill="#424242",
            tags=("manila_content", "manila")
        )

        # Export buttons
        export_formats = [
            ("CSV", True),
            ("PDF", REPORTLAB_AVAILABLE),
            ("DOCX", DOCX_AVAILABLE),
            ("XLSX", OPENPYXL_AVAILABLE)
        ]

        btn_y = start_y + 30
        for i, (fmt, available) in enumerate(export_formats):
            btn_x = x + 30 + i * 90

            btn_color = "#FF9800" if available else "#BDBDBD"

            self.canvas.create_rectangle(
                btn_x, btn_y,
                btn_x + 80, btn_y + 30,
                fill=btn_color,
                outline="#424242",
                width=2,
                tags=(f"manila_export_{fmt.lower()}", "manila_button", "manila")
            )

            self.canvas.create_text(
                btn_x + 40, btn_y + 15,
                text=fmt,
                font=("Arial", 10, "bold"),
                fill="white" if available else "#757575",
                tags=(f"manila_export_{fmt.lower()}", "manila_button", "manila")
            )

    def get_gradient_color(self, color1, color2, ratio):
        """Get intermediate color between two colors"""
        # Simple hex color interpolation
        c1 = color1.lstrip('#')
        c2 = color2.lstrip('#')

        r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
        r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)

        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)

        return f"#{r:02x}{g:02x}{b:02x}"

    def update_status(self):
        """Update status text"""
        total_nodes = len(self.nodes)
        selected_count = len(self.selected_nodes)
        zoom_pct = int(self.zoom_factor * 100)

        status = f"Nodes: {selected_count}/{total_nodes} | Zoom: {zoom_pct}%"

        if self.linking_mode:
            status += " | LINKING MODE (Select target node)"

        self.canvas.itemconfig(self.status_text, text=status)

        # Recreate status text (it may have been deleted)
        if not self.canvas.coords(self.status_text):
            self.status_text = self.canvas.create_text(
                10, self.root.winfo_screenheight() - 20,
                anchor="sw",
                text=status,
                font=("Arial", 10),
                fill="#424242"
            )

    # ========================================================================
    # EVENT HANDLERS - CRITICAL BUG FIXES APPLIED
    # ========================================================================

    def on_canvas_click(self, event):
        """Handle canvas click - CRITICAL: Fixed node ID parsing and click priority"""
        x, y = event.x, event.y

        # PRIORITY 1: Check manila folder clicks
        if self.manila_folder_open:
            if self.handle_manila_folder_click(x, y):
                return

        # PRIORITY 2: Check DRAWER clicks (must be before cabinet body)
        for drawer_name in ["top", "middle", "bottom"]:
            if self.cabinet.point_in_drawer(x, y, drawer_name):
                self.handle_drawer_click(drawer_name)
                return

        # PRIORITY 3: Check NODE clicks
        clicked_items = self.canvas.find_overlapping(x, y, x, y)

        for item in clicked_items:
            tags = self.canvas.gettags(item)

            # FIXED: Correct node ID parsing using slicing
            node_tags = [tag for tag in tags if tag.startswith("node_")]
            if node_tags:
                node_tag = node_tags[0]
                node_id = node_tag[5:]  # Remove "node_" prefix - CRITICAL FIX

                if node_id in self.nodes:
                    self.handle_node_click(node_id, event)
                    return

        # PRIORITY 4: Check CABINET BODY clicks (only if unlocked)
        if not self.cabinet.locked and self.cabinet.point_in_cabinet(x, y):
            self.start_cabinet_drag(x, y)
            return

        # PRIORITY 5: Empty space - deselect
        self.clear_selection()
        self.redraw_all()

    def on_canvas_right_click(self, event):
        """Handle right click - CRITICAL: Fixed node ID parsing"""
        x, y = event.x, event.y

        clicked_items = self.canvas.find_overlapping(x, y, x, y)

        for item in clicked_items:
            tags = self.canvas.gettags(item)

            # FIXED: Correct node ID parsing using slicing
            node_tags = [tag for tag in tags if tag.startswith("node_")]
            if node_tags:
                node_tag = node_tags[0]
                node_id = node_tag[5:]  # Remove "node_" prefix - CRITICAL FIX

                if node_id in self.nodes:
                    self.show_node_context_menu(node_id, event)
                    return

    def on_canvas_double_click(self, event):
        """Handle double click - CRITICAL: Fixed node ID parsing"""
        x, y = event.x, event.y

        clicked_items = self.canvas.find_overlapping(x, y, x, y)

        for item in clicked_items:
            tags = self.canvas.gettags(item)

            # FIXED: Correct node ID parsing using slicing
            node_tags = [tag for tag in tags if tag.startswith("node_")]
            if node_tags:
                node_tag = node_tags[0]
                node_id = node_tag[5:]  # Remove "node_" prefix - CRITICAL FIX

                if node_id in self.nodes:
                    self.edit_node(node_id)
                    return

    def on_canvas_drag(self, event):
        """Handle canvas drag"""
        if self.drag_data["item"] is None:
            return

        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]

        if self.drag_data["type"] == "node":
            # Move node
            node_id = self.drag_data["item"]
            if node_id in self.nodes:
                self.nodes[node_id].x += dx
                self.nodes[node_id].y += dy
                self.redraw_all()

        elif self.drag_data["type"] == "cabinet":
            # Move cabinet
            self.cabinet.x += dx
            self.cabinet.y += dy
            self.cabinet.update_orientation(self.root.winfo_screenwidth())
            self.redraw_all()

        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_canvas_release(self, event):
        """Handle mouse release"""
        self.drag_data = {"x": 0, "y": 0, "item": None, "type": None}

    # ========================================================================
    # INTERACTION HANDLERS
    # ========================================================================

    def handle_node_click(self, node_id, event):
        """Handle node click"""
        # Linking mode
        if self.linking_mode:
            if self.linking_from_node and self.linking_from_node != node_id:
                self.create_reference_link(self.linking_from_node, node_id)
            self.linking_mode = False
            self.linking_from_node = None
            self.redraw_all()
            return

        # Ctrl+click for multi-select
        if event.state & 0x4:  # Ctrl key
            if node_id in self.selected_nodes:
                self.selected_nodes.remove(node_id)
            else:
                self.selected_nodes.append(node_id)
        else:
            self.selected_nodes = [node_id]

        # Start dragging
        self.drag_data = {
            "x": event.x,
            "y": event.y,
            "item": node_id,
            "type": "node"
        }

        self.redraw_all()

    def handle_drawer_click(self, drawer_name):
        """Handle drawer click"""
        if drawer_name == "top":
            # Top drawer: Create top-tier node
            self.cabinet.toggle_drawer("top")
            if self.cabinet.top_drawer_open:
                self.create_node(tier=1)

        elif drawer_name == "middle":
            # Middle drawer: Open projects folder
            self.cabinet.toggle_drawer("middle")
            if self.cabinet.middle_drawer_open:
                self.manila_folder_open = "projects"
            else:
                self.manila_folder_open = None

        elif drawer_name == "bottom":
            # Bottom drawer: Open settings folder
            self.cabinet.toggle_drawer("bottom")
            if self.cabinet.bottom_drawer_open:
                self.manila_folder_open = "settings"
            else:
                self.manila_folder_open = None

        self.redraw_all()

    def handle_manila_folder_click(self, x, y):
        """Handle manila folder clicks"""
        clicked_items = self.canvas.find_overlapping(x, y, x, y)

        for item in clicked_items:
            tags = self.canvas.gettags(item)

            # Close button
            if "manila_close" in tags:
                self.manila_folder_open = None
                self.cabinet.close_all_drawers()
                self.redraw_all()
                return True

            # Projects folder - open buttons
            for i in range(len(self.manila_folder_items)):
                if f"manila_open_{i}" in tags:
                    filename = self.manila_folder_items[i]
                    self.load_project(filename)
                    self.manila_folder_open = None
                    self.cabinet.close_all_drawers()
                    self.redraw_all()
                    return True

            # Settings folder - buttons
            if "manila_autosave_toggle" in tags:
                self.auto_save_enabled = not self.auto_save_enabled
                self.redraw_all()
                return True

            if "manila_theme_toggle" in tags:
                self.theme = "dark" if self.theme == "default" else "default"
                self.redraw_all()
                return True

            # Export buttons
            if "manila_export_csv" in tags:
                self.export_to_csv()
                return True
            if "manila_export_pdf" in tags and REPORTLAB_AVAILABLE:
                self.export_to_pdf()
                return True
            if "manila_export_docx" in tags and DOCX_AVAILABLE:
                self.export_to_docx()
                return True
            if "manila_export_xlsx" in tags and OPENPYXL_AVAILABLE:
                self.export_to_xlsx()
                return True

        # Check if clicked inside folder area
        folder_width = 400
        folder_height = 500
        folder_x = (self.root.winfo_screenwidth() - folder_width) // 2
        folder_y = (self.root.winfo_screenheight() - folder_height) // 2

        if folder_x <= x <= folder_x + folder_width and folder_y <= y <= folder_y + folder_height:
            return True  # Clicked inside folder, consume event

        # Clicked outside folder - close it
        self.manila_folder_open = None
        self.cabinet.close_all_drawers()
        self.redraw_all()
        return True

    def start_cabinet_drag(self, x, y):
        """Start dragging cabinet"""
        self.drag_data = {
            "x": x,
            "y": y,
            "item": "cabinet",
            "type": "cabinet"
        }

    def show_node_context_menu(self, node_id, event):
        """Show context menu for node"""
        menu = tk.Menu(self.root, tearoff=0)

        menu.add_command(label="Edit", command=lambda: self.edit_node(node_id))
        menu.add_command(label="Add Child", command=lambda: self.add_child_node(node_id))
        menu.add_command(label="Delete", command=lambda: self.delete_node(node_id))
        menu.add_separator()
        menu.add_command(label="Collapse", command=lambda: self.toggle_collapse(node_id))
        menu.add_command(label="Change Tier", command=lambda: self.change_node_tier(node_id))
        menu.add_separator()
        menu.add_command(label="Auto-Link Suggestions", command=lambda: self.show_auto_link_suggestions(node_id))

        menu.post(event.x_root, event.y_root)

    # ========================================================================
    # NODE OPERATIONS
    # ========================================================================

    def create_node(self, tier=1, x=None, y=None, content="New Node", parent_id=None):
        """Create a new node"""
        # Generate unique ID
        node_id = f"node_{int(time.time() * 1000000)}"

        # Default position (center of screen)
        if x is None:
            x = self.root.winfo_screenwidth() // 2
        if y is None:
            y = self.root.winfo_screenheight() // 2

        # Create node
        node = MindMapNode(node_id, content, tier, x, y, parent_id)
        self.nodes[node_id] = node

        # Create hierarchical connection if has parent
        if parent_id and parent_id in self.nodes:
            parent = self.nodes[parent_id]
            parent.children_ids.append(node_id)

            conn_id = f"conn_{int(time.time() * 1000000)}"
            conn = Connection(conn_id, parent_id, node_id, "hierarchical")
            self.connections[conn_id] = conn

        # Save state for undo
        self.save_undo_state()

        self.redraw_all()
        print(f"Created node: {node_id}")

        return node_id

    def edit_node(self, node_id):
        """Edit node content"""
        if node_id not in self.nodes:
            return

        node = self.nodes[node_id]

        # Show edit dialog (using helper to ensure it appears on top)
        new_content = self.show_dialog_topmost(
            simpledialog.askstring,
            "Edit Node",
            "Enter node content:",
            initialvalue=node.content,
            parent=self.root
        )

        if new_content is not None:
            node.content = new_content
            self.save_undo_state()
            self.redraw_all()

    def delete_node(self, node_id):
        """Delete a node and its connections"""
        if node_id not in self.nodes:
            return

        node = self.nodes[node_id]

        # Remove from parent's children
        if node.parent_id and node.parent_id in self.nodes:
            parent = self.nodes[node.parent_id]
            if node_id in parent.children_ids:
                parent.children_ids.remove(node_id)

        # Delete all connections involving this node
        to_delete = []
        for conn_id, conn in self.connections.items():
            if conn.from_node_id == node_id or conn.to_node_id == node_id:
                to_delete.append(conn_id)

        for conn_id in to_delete:
            del self.connections[conn_id]

        # Delete node
        del self.nodes[node_id]

        # Remove from selection
        if node_id in self.selected_nodes:
            self.selected_nodes.remove(node_id)

        self.save_undo_state()
        self.redraw_all()

    def delete_selected_nodes(self):
        """Delete all selected nodes"""
        for node_id in list(self.selected_nodes):
            self.delete_node(node_id)

        self.selected_nodes = []
        self.redraw_all()

    def add_child_node(self, parent_id):
        """Add a child node to a parent"""
        if parent_id not in self.nodes:
            return

        parent = self.nodes[parent_id]

        # Position child below parent
        child_tier = min(5, parent.tier + 1)
        child_x = parent.x + 150
        child_y = parent.y + 100

        self.create_node(
            tier=child_tier,
            x=child_x,
            y=child_y,
            content="Child Node",
            parent_id=parent_id
        )

    def toggle_collapse(self, node_id):
        """Toggle node collapse state"""
        if node_id not in self.nodes:
            return

        node = self.nodes[node_id]
        node.collapsed = not node.collapsed

        self.save_undo_state()
        self.redraw_all()

    def change_node_tier(self, node_id):
        """Change node tier"""
        if node_id not in self.nodes:
            return

        node = self.nodes[node_id]

        new_tier = self.show_dialog_topmost(
            simpledialog.askinteger,
            "Change Tier",
            "Enter new tier (1-5):",
            initialvalue=node.tier,
            minvalue=1,
            maxvalue=5,
            parent=self.root
        )

        if new_tier is not None:
            node.tier = new_tier
            self.save_undo_state()
            self.redraw_all()

    def clear_selection(self):
        """Clear all selections"""
        self.selected_nodes = []
        self.linking_mode = False
        self.linking_from_node = None

    # ========================================================================
    # CONNECTION OPERATIONS
    # ========================================================================

    def start_linking_mode(self):
        """Start reference linking mode"""
        if len(self.selected_nodes) == 1:
            self.linking_mode = True
            self.linking_from_node = self.selected_nodes[0]
            print("Linking mode activated. Click target node to create reference link.")
            self.update_status()
        else:
            messagebox.showwarning("Linking Mode", "Please select exactly one node to start linking.")

    def create_reference_link(self, from_node_id, to_node_id):
        """Create a reference (cross-link) connection"""
        # Check if connection already exists
        for conn in self.connections.values():
            if (conn.from_node_id == from_node_id and conn.to_node_id == to_node_id) or \
               (conn.from_node_id == to_node_id and conn.to_node_id == from_node_id):
                messagebox.showinfo("Link Exists", "A connection already exists between these nodes.")
                return

        # Ask for weight
        weight = self.show_dialog_topmost(
            simpledialog.askinteger,
            "Connection Weight",
            "Enter connection weight (1-10):\n1=max slack, 10=tight",
            initialvalue=5,
            minvalue=1,
            maxvalue=10,
            parent=self.root
        )

        if weight is None:
            return

        # Create connection
        conn_id = f"conn_{int(time.time() * 1000000)}"
        conn = Connection(conn_id, from_node_id, to_node_id, "reference", weight)
        self.connections[conn_id] = conn

        # Add to linked nodes
        if from_node_id in self.nodes:
            self.nodes[from_node_id].linked_node_ids.append(to_node_id)
        if to_node_id in self.nodes:
            self.nodes[to_node_id].linked_node_ids.append(from_node_id)

        self.save_undo_state()
        self.redraw_all()

        print(f"Created reference link: {from_node_id} -> {to_node_id}")

    def adjust_connection_tension(self):
        """Adjust tension of selected connection"""
        # This would require connection selection - simplified version
        messagebox.showinfo("Connection Tension", "Select a connection and use the context menu to adjust tension.")

    # ========================================================================
    # AUTO-LINKING
    # ========================================================================

    def show_auto_link_suggestions(self, node_id):
        """Show auto-link suggestions for a node"""
        if node_id not in self.nodes:
            return

        node = self.nodes[node_id]
        suggestions = self.calculate_link_suggestions(node)

        if not suggestions:
            messagebox.showinfo("Auto-Link", "No suitable link suggestions found.")
            return

        # Show suggestions dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Auto-Link Suggestions")
        dialog.geometry("400x300")

        tk.Label(dialog, text=f"Suggestions for: {node.content}", font=("Arial", 12, "bold")).pack(pady=10)

        listbox = tk.Listbox(dialog, height=10)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for target_id, score in suggestions:
            target_node = self.nodes[target_id]
            listbox.insert(tk.END, f"{target_node.content} (Score: {score})")

        def create_link():
            selection = listbox.curselection()
            if selection:
                target_id, _ = suggestions[selection[0]]
                self.create_reference_link(node_id, target_id)
                dialog.destroy()

        tk.Button(dialog, text="Create Link", command=create_link).pack(pady=5)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)

    def calculate_link_suggestions(self, node):
        """Calculate link suggestions based on similarity"""
        suggestions = []

        for other_id, other_node in self.nodes.items():
            if other_id == node.id:
                continue

            # Skip if already linked
            if other_id in node.linked_node_ids:
                continue

            score = 0

            # Common tags
            common_tags = set(node.tags) & set(other_node.tags)
            score += len(common_tags) * 10

            # Content similarity
            similarity = difflib.SequenceMatcher(None, node.content, other_node.content).ratio()
            score += similarity * 100

            # Same type
            if node.type == other_node.type:
                score += 5

            # Same emotion
            if node.emotion == other_node.emotion:
                score += 3

            if score > 15:
                suggestions.append((other_id, int(score)))

        # Sort by score descending
        suggestions.sort(key=lambda x: x[1], reverse=True)

        # Return top 5
        return suggestions[:5]

    def refresh_auto_links(self):
        """Refresh auto-link suggestions for all nodes"""
        print("Refreshing auto-link suggestions...")
        messagebox.showinfo("Auto-Link", "Auto-link suggestions refreshed. Right-click a node to see suggestions.")

    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================

    def new_project(self):
        """Create a new project"""
        if self.nodes:
            response = messagebox.askyesnocancel("New Project", "Save current project?")
            if response is None:  # Cancel
                return
            elif response:  # Yes
                self.save_project()

        self.nodes = {}
        self.connections = {}
        self.selected_nodes = []
        self.current_file = None
        self.undo_stack.clear()
        self.redo_stack.clear()

        self.redraw_all()
        print("New project created")

    def save_project(self):
        """Save current project"""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_project_as()

    def save_project_as(self):
        """Save project with new filename"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            self.save_to_file(filename)
            self.current_file = filename

    def save_to_file(self, filename):
        """Save project to file"""
        data = {
            "version": "1.0",
            "timestamp": datetime.datetime.now().isoformat(),
            "cabinet": self.cabinet.to_dict(),
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "connections": {conn_id: conn.to_dict() for conn_id, conn in self.connections.items()},
            "theme": self.theme,
            "canvas_offset": self.canvas_offset,
            "zoom_factor": self.zoom_factor
        }

        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

            # Create backup
            self.create_backup(filename)

            print(f"Project saved: {filename}")
            messagebox.showinfo("Save", "Project saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save project: {e}")

    def create_backup(self, filename):
        """Create rolling backup"""
        # Create backup directory
        backup_dir = filename.replace(".json", "_backups")
        os.makedirs(backup_dir, exist_ok=True)

        # Create timestamped backup
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"backup_{timestamp}.json")

        try:
            import shutil
            shutil.copy2(filename, backup_file)

            # Keep only 5 most recent backups
            backups = sorted(
                [f for f in os.listdir(backup_dir) if f.startswith("backup_")],
                reverse=True
            )

            for old_backup in backups[5:]:
                os.remove(os.path.join(backup_dir, old_backup))
        except Exception as e:
            print(f"Backup warning: {e}")

    def open_project(self):
        """Open a project file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            self.load_project(filename)

    def load_project(self, filename):
        """Load project from file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            # Validate structure
            if "nodes" not in data:
                raise ValueError("Invalid project file: missing nodes")

            # Load data
            self.nodes = {
                node_id: MindMapNode.from_dict(node_data)
                for node_id, node_data in data.get("nodes", {}).items()
            }

            self.connections = {
                conn_id: Connection.from_dict(conn_data)
                for conn_id, conn_data in data.get("connections", {}).items()
            }

            if "cabinet" in data:
                self.cabinet = FileCabinet.from_dict(data["cabinet"])

            self.theme = data.get("theme", "default")
            self.canvas_offset = data.get("canvas_offset", {"x": 0, "y": 0})
            self.zoom_factor = data.get("zoom_factor", 1.0)

            self.current_file = filename
            self.selected_nodes = []
            self.undo_stack.clear()
            self.redo_stack.clear()

            self.redraw_all()
            print(f"Project loaded: {filename}")
            messagebox.showinfo("Load", "Project loaded successfully!")

        except json.JSONDecodeError:
            # Try to recover from backup
            if self.try_load_backup(filename):
                messagebox.showwarning("Load", "Main file corrupted. Loaded from backup.")
            else:
                messagebox.showerror("Load Error", "Failed to load project: corrupted file")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load project: {e}")

    def try_load_backup(self, filename):
        """Try to load from backup if main file is corrupted"""
        backup_dir = filename.replace(".json", "_backups")

        if not os.path.exists(backup_dir):
            return False

        backups = sorted(
            [f for f in os.listdir(backup_dir) if f.startswith("backup_")],
            reverse=True
        )

        for backup_file in backups:
            try:
                backup_path = os.path.join(backup_dir, backup_file)
                with open(backup_path, 'r') as f:
                    data = json.load(f)

                # If we get here, backup is valid
                self.load_project(backup_path)
                return True
            except:
                continue

        return False

    def auto_save_timer(self):
        """Auto-save timer (every 30 seconds)"""
        if self.auto_save_enabled and self.current_file and self.nodes:
            self.save_to_file(self.current_file)
            print("Auto-save completed")

        # Schedule next auto-save
        self.root.after(30000, self.auto_save_timer)

    # ========================================================================
    # UNDO/REDO
    # ========================================================================

    def save_undo_state(self):
        """Save current state to undo stack"""
        state = {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "connections": {conn_id: conn.to_dict() for conn_id, conn in self.connections.items()}
        }

        self.undo_stack.append(state)
        self.redo_stack.clear()

    def undo(self):
        """Undo last action"""
        if not self.undo_stack:
            print("Nothing to undo")
            return

        # Save current state to redo stack
        current_state = {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "connections": {conn_id: conn.to_dict() for conn_id, conn in self.connections.items()}
        }
        self.redo_stack.append(current_state)

        # Restore previous state
        state = self.undo_stack.pop()

        self.nodes = {
            node_id: MindMapNode.from_dict(node_data)
            for node_id, node_data in state["nodes"].items()
        }

        self.connections = {
            conn_id: Connection.from_dict(conn_data)
            for conn_id, conn_data in state["connections"].items()
        }

        self.redraw_all()
        print("Undo completed")

    def redo(self):
        """Redo last undone action"""
        if not self.redo_stack:
            print("Nothing to redo")
            return

        # Save current state to undo stack
        current_state = {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "connections": {conn_id: conn.to_dict() for conn_id, conn in self.connections.items()}
        }
        self.undo_stack.append(current_state)

        # Restore redo state
        state = self.redo_stack.pop()

        self.nodes = {
            node_id: MindMapNode.from_dict(node_data)
            for node_id, node_data in state["nodes"].items()
        }

        self.connections = {
            conn_id: Connection.from_dict(conn_data)
            for conn_id, conn_data in state["connections"].items()
        }

        self.redraw_all()
        print("Redo completed")

    # ========================================================================
    # CLIPBOARD OPERATIONS
    # ========================================================================

    def copy_nodes(self):
        """Copy selected nodes to clipboard"""
        if not self.selected_nodes:
            return

        self.clipboard = {
            "nodes": [self.nodes[node_id].to_dict() for node_id in self.selected_nodes if node_id in self.nodes]
        }

        print(f"Copied {len(self.clipboard['nodes'])} nodes")

    def cut_nodes(self):
        """Cut selected nodes to clipboard"""
        self.copy_nodes()
        self.delete_selected_nodes()

    def paste_nodes(self):
        """Paste nodes from clipboard"""
        if not hasattr(self, 'clipboard') or not self.clipboard.get('nodes'):
            return

        # Paste with offset
        offset_x, offset_y = 50, 50

        for node_data in self.clipboard['nodes']:
            new_id = f"node_{int(time.time() * 1000000)}"
            node = MindMapNode.from_dict(node_data)
            node.id = new_id
            node.x += offset_x
            node.y += offset_y
            node.parent_id = None  # Remove parent relationship
            node.children_ids = []

            self.nodes[new_id] = node

        self.save_undo_state()
        self.redraw_all()
        print(f"Pasted {len(self.clipboard['nodes'])} nodes")

    # ========================================================================
    # SEARCH
    # ========================================================================

    def search_nodes(self):
        """Search for nodes by content"""
        query = self.show_dialog_topmost(
            simpledialog.askstring,
            "Search",
            "Enter search query:",
            parent=self.root
        )

        if not query:
            return

        # Find matching nodes
        matches = []
        for node_id, node in self.nodes.items():
            if query.lower() in node.content.lower() or \
               query.lower() in ' '.join(node.tags).lower():
                matches.append(node_id)

        if matches:
            self.selected_nodes = matches
            self.redraw_all()
            messagebox.showinfo("Search", f"Found {len(matches)} matching nodes")
        else:
            messagebox.showinfo("Search", "No matching nodes found")

    # ========================================================================
    # EXPORT
    # ========================================================================

    def export_to_csv(self):
        """Export to CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            import csv

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Content", "Tier", "Parent", "Tags", "X", "Y"])

                for node in self.nodes.values():
                    writer.writerow([
                        node.id,
                        node.content,
                        node.tier,
                        node.parent_id or "",
                        ','.join(node.tags),
                        node.x,
                        node.y
                    ])

            messagebox.showinfo("Export", "CSV export successful!")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV: {e}")

    def export_to_pdf(self):
        """Export to PDF"""
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("Export Error", "ReportLab not installed")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            c = pdf_canvas.Canvas(filename, pagesize=letter)

            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 750, "MindMap Export")

            y = 720
            c.setFont("Helvetica", 10)

            # Export hierarchically
            for node in self.nodes.values():
                if node.parent_id is None:  # Top-level nodes
                    y = self.write_node_to_pdf(c, node, 50, y, 0)

            c.save()
            messagebox.showinfo("Export", "PDF export successful!")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export PDF: {e}")

    def write_node_to_pdf(self, canvas, node, x, y, indent):
        """Write node and children to PDF"""
        indent_str = "  " * indent
        canvas.drawString(x + indent * 20, y, f"{indent_str}{node.content} (Tier {node.tier})")
        y -= 20

        # Write children
        for child_id in node.children_ids:
            if child_id in self.nodes:
                y = self.write_node_to_pdf(canvas, self.nodes[child_id], x, y, indent + 1)

        return y

    def export_to_docx(self):
        """Export to DOCX"""
        if not DOCX_AVAILABLE:
            messagebox.showerror("Export Error", "python-docx not installed")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word files", "*.docx"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            doc = Document()
            doc.add_heading("MindMap Export", 0)

            # Export hierarchically
            for node in self.nodes.values():
                if node.parent_id is None:
                    self.write_node_to_docx(doc, node, 0)

            doc.save(filename)
            messagebox.showinfo("Export", "DOCX export successful!")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export DOCX: {e}")

    def write_node_to_docx(self, doc, node, level):
        """Write node and children to DOCX"""
        doc.add_paragraph(f"{node.content} (Tier {node.tier})", level=level)

        for child_id in node.children_ids:
            if child_id in self.nodes:
                self.write_node_to_docx(doc, self.nodes[child_id], level + 1)

    def export_to_xlsx(self):
        """Export to XLSX"""
        if not OPENPYXL_AVAILABLE:
            messagebox.showerror("Export Error", "openpyxl not installed")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "MindMap"

            # Headers
            ws.append(["ID", "Content", "Tier", "Parent", "Tags", "X", "Y"])

            # Data
            for node in self.nodes.values():
                ws.append([
                    node.id,
                    node.content,
                    node.tier,
                    node.parent_id or "",
                    ','.join(node.tags),
                    node.x,
                    node.y
                ])

            wb.save(filename)
            messagebox.showinfo("Export", "XLSX export successful!")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export XLSX: {e}")

    # ========================================================================
    # OTHER FEATURES
    # ========================================================================

    def toggle_minimap(self):
        """Toggle minimap display"""
        messagebox.showinfo("Minimap", "Minimap feature coming soon!")

    def expand_all(self):
        """Expand all collapsed nodes"""
        for node in self.nodes.values():
            node.collapsed = False

        self.redraw_all()
        print("All nodes expanded")

    def collapse_selected(self):
        """Collapse selected nodes"""
        for node_id in self.selected_nodes:
            if node_id in self.nodes:
                self.nodes[node_id].collapsed = True

        self.redraw_all()

    def toggle_cabinet_lock(self):
        """Toggle cabinet lock"""
        self.cabinet.locked = not self.cabinet.locked
        self.redraw_all()

        status = "locked" if self.cabinet.locked else "unlocked"
        print(f"Cabinet {status}")

    def show_help(self):
        """Show help dialog with keyboard shortcuts"""
        help_text = """
KEYBOARD SHORTCUTS

File Operations:
  Ctrl+N - New node
  Ctrl+S - Save project
  Ctrl+O - Open project

Editing:
  Ctrl+C - Copy nodes
  Ctrl+X - Cut nodes
  Ctrl+V - Paste nodes
  Delete - Delete selected nodes
  Ctrl+Z - Undo
  Ctrl+Y - Redo

Node Operations:
  Single click - Select node
  Ctrl+click - Multi-select
  Double-click - Edit node
  Right-click - Context menu
  Drag - Move node

Connections:
  Ctrl+L - Start linking mode
  Ctrl+T - Adjust tension

View:
  Ctrl+M - Toggle minimap
  Ctrl+E - Expand all nodes
  Ctrl+R - Collapse selected

Other:
  Ctrl+F - Search nodes
  Ctrl+K - Lock/unlock cabinet
  F5 - Refresh auto-links
  F1 - Show this help
  Escape - Clear selection
"""

        dialog = tk.Toplevel(self.root)
        dialog.title("Keyboard Shortcuts")
        dialog.geometry("500x600")

        text_widget = tk.Text(dialog, wrap=tk.WORD, font=("Courier", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert("1.0", help_text)
        text_widget.config(state=tk.DISABLED)

        tk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def minimize_window(self):
        """Minimize/iconify the window to get it out of the way"""
        self.root.iconify()

    def exit_app(self):
        """Exit application"""
        if self.nodes:
            response = messagebox.askyesnocancel("Exit", "Save before exiting?")
            if response is None:  # Cancel
                return
            elif response:  # Yes
                self.save_project()

        self.root.quit()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    root = tk.Tk()
    app = MindMapApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
