#!/usr/bin/env python3
"""
Settings Management for Akashic Record MindMap
Handles application configuration and persistence
"""

import json
import os
from dataclasses import dataclass, asdict, field
from typing import List


@dataclass
class AppSettings:
    """Application settings"""
    # Grid
    snap_to_grid: bool = False
    grid_spacing: int = 100  # pixels
    show_grid_overlay: bool = False

    # Auto-save
    auto_save_enabled: bool = True
    auto_save_interval: int = 30  # seconds (0 = disabled, 30, 60, 120, 300)

    # Theme
    current_theme: str = 'default'

    # Layout
    default_layout: str = 'tree'

    # Window
    window_width: int = 1200
    window_height: int = 800
    transparency_enabled: bool = True

    # Recent projects
    recent_projects: List[str] = field(default_factory=list)
    max_recent_projects: int = 10

    # Cabinet
    cabinet_x: int = 50
    cabinet_y: int = 50

    @classmethod
    def load(cls, filepath='settings.json'):
        """Load settings from file"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    return cls(**data)
            except Exception as e:
                print(f"Warning: Could not load settings: {e}")
        return cls()

    def save(self, filepath='settings.json'):
        """Save settings to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(asdict(self), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save settings: {e}")

    def add_recent_project(self, project_path: str):
        """Add project to recent list"""
        # Normalize path
        project_path = os.path.abspath(project_path)

        # Remove if already in list
        if project_path in self.recent_projects:
            self.recent_projects.remove(project_path)

        # Add to front
        self.recent_projects.insert(0, project_path)

        # Keep only max recent
        self.recent_projects = self.recent_projects[:self.max_recent_projects]

    def get_recent_projects(self) -> List[str]:
        """Get list of recent projects that still exist"""
        # Filter out projects that no longer exist
        existing = [p for p in self.recent_projects if os.path.exists(p)]

        # Update list if any were removed
        if len(existing) != len(self.recent_projects):
            self.recent_projects = existing

        return existing
