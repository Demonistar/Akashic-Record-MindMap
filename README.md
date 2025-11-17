# Akashic Record MindMap - Desktop Application

A production-ready desktop mindmap application with advanced features including a file cabinet interface, auto-linking, and comprehensive export capabilities.

## Features

### Core Features
- **Desktop Overlay System**: Fullscreen transparent window (90% opacity)
- **File Cabinet Interface**: 3-drawer cabinet for managing nodes, projects, and settings
- **Advanced Node System**: 5-tier hierarchical nodes with full metadata
- **Smart Connections**: Hierarchical and reference links with physics-based rendering
- **Auto-Linking**: AI-powered suggestions based on content similarity
- **Comprehensive Export**: CSV, PDF, DOCX, XLSX formats (with graceful fallbacks)
- **Robust File Management**: Auto-save, rolling backups, corruption detection
- **Undo/Redo**: 50-level history
- **Multi-Theme**: Default and Dark themes

## Requirements

### Required
- Python 3.6+
- tkinter (usually comes with Python)

### Optional (for enhanced features)
```bash
pip install pillow numpy reportlab python-docx openpyxl
```

The application will work with core features even if optional libraries are missing.

## Installation

1. Clone or download the repository
2. Ensure Python 3 is installed
3. (Optional) Install additional libraries for full functionality:
   ```bash
   pip install pillow numpy reportlab python-docx openpyxl
   ```

## Usage

### Starting the Application

```bash
python3 mindmap_desktop.py
```

The application will launch in fullscreen mode with a transparent overlay on your desktop.

### First Steps

1. **Create Your First Node**: Press `Ctrl+N`
2. **Edit Node Content**: Double-click the node
3. **Move Nodes**: Click and drag
4. **Add Child Nodes**: Right-click a node → "Add Child"

### File Cabinet

The file cabinet has 3 drawers:

#### Top Drawer (Nodes)
- Click to deploy a new top-tier node
- Creates nodes at tier 1 (largest size)

#### Middle Drawer (Projects)
- Opens manila folder with recent projects
- Shows 4 most recent .json files
- Click "Open" button to load a project

#### Bottom Drawer (Settings)
- **Auto-Save Toggle**: Enable/disable auto-save (every 30 seconds)
- **Theme Selector**: Switch between Default and Dark themes
- **Export Buttons**: Export to CSV, PDF, DOCX, or XLSX

### Keyboard Shortcuts

#### File Operations
- `Ctrl+N` - Create new node
- `Ctrl+S` - Save project
- `Ctrl+O` - Open project

#### Editing
- `Ctrl+C` - Copy selected nodes
- `Ctrl+X` - Cut selected nodes
- `Ctrl+V` - Paste nodes
- `Delete` - Delete selected nodes
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo

#### Node Operations
- `Single Click` - Select node
- `Ctrl+Click` - Multi-select
- `Double-Click` - Edit node
- `Right-Click` - Context menu
- `Drag` - Move node

#### Connections
- `Ctrl+L` - Start linking mode (create reference link)
- `Ctrl+T` - Adjust connection tension

#### View
- `Ctrl+M` - Toggle minimap
- `Ctrl+E` - Expand all nodes
- `Ctrl+R` - Collapse selected nodes

#### Other
- `Ctrl+F` - Search nodes
- `Ctrl+K` - Lock/unlock cabinet
- `F5` - Refresh auto-link suggestions
- `F1` - Show help dialog
- `Escape` - Clear selection

## Node System

### Node Tiers (1-5)
- **Tier 1**: 120×40px (Largest - main topics)
- **Tier 2**: 102×34px
- **Tier 3**: 84×28px
- **Tier 4**: 66×22px
- **Tier 5**: 48×16px (Smallest - details)

Each tier is 15% smaller than the previous.

### Node Metadata
Each node stores:
- Unique ID (timestamp-based)
- Content (text)
- Tier (1-5)
- Position (x, y)
- Parent/child relationships
- Collapsed state
- Tags
- Emotion
- Linked nodes
- Custom metadata

## Connection System

### Hierarchical Connections
- **Solid blue lines** (#1976D2)
- Auto-created when adding child nodes
- Represent parent-child relationships

### Reference Connections
- **Dashed orange lines** (#FF9800)
- Created via `Ctrl+L` linking mode
- Cross-link related nodes

### Connection Physics (Weight 1-10)
- **Weight 1-5**: Slack lines with visible sag (catenary curve)
  - Weight 1 = maximum sag (50px)
  - Weight 5 = slight sag (10px)
- **Weight 6-10**: Tight lines, increasingly straight
  - Weight 10 = perfectly straight

## Auto-Linking

The auto-linking system suggests connections based on:
- **Common tags**: +10 points per tag
- **Content similarity**: +0-100 points (difflib)
- **Same type**: +5 points
- **Same emotion**: +3 points

Suggestions with score > 15 are shown. Right-click any node → "Auto-Link Suggestions" to see recommendations.

## File Management

### Project Structure (JSON)
```json
{
  "version": "1.0",
  "timestamp": "ISO format",
  "cabinet": {
    "x": 50,
    "y": 50,
    "orientation": "right",
    "locked": false
  },
  "nodes": {
    "node_id": {
      "id": "node_id",
      "content": "Node text",
      "tier": 1,
      "x": 100,
      "y": 100,
      "parent_id": null,
      "children_ids": [],
      "tags": [],
      ...
    }
  },
  "connections": {
    "conn_id": {
      "id": "conn_id",
      "from_node_id": "node_1",
      "to_node_id": "node_2",
      "type": "hierarchical",
      "weight": 5
    }
  },
  "theme": "default",
  "canvas_offset": {"x": 0, "y": 0},
  "zoom_factor": 1.0
}
```

### Auto-Save
- Automatically saves every 30 seconds (if enabled)
- Toggle in Settings drawer
- Only saves if file has been named (use Save As first)

### Backups
- 5 rolling backups in `{filename}_backups/` directory
- Timestamped: `backup_YYYYMMDD_HHMMSS.json`
- Automatic corruption detection
- Auto-offers valid backup if main file is corrupted

## Export Formats

### CSV (Always Available)
- Node hierarchy with full metadata
- Columns: ID, Content, Tier, Parent, Tags, X, Y

### PDF (requires reportlab)
```bash
pip install reportlab
```
- Hierarchical structure with indentation
- Formatted for printing

### DOCX (requires python-docx)
```bash
pip install python-docx
```
- Word document with hierarchical headings
- Compatible with Microsoft Word

### XLSX (requires openpyxl)
```bash
pip install openpyxl
```
- Excel spreadsheet with node data
- Compatible with Microsoft Excel

## Themes

### Default Theme
- **Nodes**: Blue gradient (#E3F2FD → #42A5F5)
- **Hierarchical connections**: #1976D2 (blue)
- **Reference connections**: #FF9800 (orange)

### Dark Theme
- **Nodes**: Gray gradient (#424242 → #BDBDBD)
- **Hierarchical connections**: #FFC107 (amber)
- **Reference connections**: #FF5722 (red)

Switch themes in Settings drawer (bottom drawer).

## Architecture

### Core Classes

#### `MindMapNode`
Stores node data with full metadata including:
- Content, tier, position
- Parent/child relationships
- Tags, emotion, type
- Custom metadata

#### `Connection`
Manages connections between nodes with:
- Connection type (hierarchical/reference)
- Weight-based physics (1-10)
- Color and line style

#### `FileCabinet`
Handles the 3-drawer cabinet interface:
- Draggable when unlocked
- Auto-flips orientation based on screen position
- Lock/unlock capability

#### `MindMapApp`
Main application controller managing:
- Window and canvas
- Event handling
- File operations
- Rendering

## Critical Bug Fixes

This implementation includes fixes for critical bugs found in previous attempts:

### Bug #1: Node ID Parsing ✓ FIXED
**Problem**: Node IDs like `node_1234567890` were incorrectly parsed using `split("_")[1]`, which returned `"node"` instead of the full ID.

**Solution**: Use string slicing:
```python
node_tag = [tag for tag in tags if tag.startswith("node_")][0]
node_id = node_tag[5:]  # Remove "node_" prefix correctly
```

### Bug #2: Cabinet Click Detection ✓ FIXED
**Problem**: Cabinet body clicks intercepted drawer clicks.

**Solution**: Proper priority order:
1. Manila folder clicks
2. Drawer clicks
3. Node clicks
4. Cabinet body clicks (only if unlocked)
5. Empty space clicks

### Bug #3: Dragging vs Clicking ✓ FIXED
**Problem**: Trying to click drawer started cabinet drag.

**Solution**: Separate click detection for drawers with cabinet dragging only on body clicks when unlocked.

## Testing

Run the core functionality tests:
```bash
python3 test_mindmap_core.py
```

This validates:
- Node creation and properties
- Node sizing based on tier
- Text truncation
- Serialization/deserialization
- Connection physics
- File cabinet operations
- Project save/load
- **Critical bug fixes**
- Auto-linking algorithm

## Troubleshooting

### Application Won't Start
- **Error: No module named 'tkinter'**
  - On Ubuntu/Debian: `sudo apt-get install python3-tk`
  - On Fedora: `sudo dnf install python3-tkinter`
  - On macOS: tkinter is included with Python

### Export Functions Disabled
- Install optional libraries:
  ```bash
  pip install reportlab python-docx openpyxl
  ```

### File Won't Load
- Check for corruption message
- Try loading from backup in `{filename}_backups/` directory
- Verify JSON structure is valid

### Cabinet Not Responding
- Check if cabinet is locked (🔒 icon visible)
- Press `Ctrl+K` to unlock
- Drawers always clickable regardless of lock state

## Performance Tips

1. **Large Projects**: Use collapsed nodes to hide subtrees
2. **Many Connections**: Use hierarchical connections for structure, reference connections sparingly
3. **Auto-Save**: Disable for very large projects, save manually
4. **Search**: Use `Ctrl+F` instead of scrolling for large mindmaps

## File Locations

- **Main Application**: `mindmap_desktop.py`
- **Projects**: Save anywhere as `.json` files
- **Backups**: `{project_name}_backups/` directory
- **Recent Projects**: Shown in Middle Drawer (Projects folder)

## Version

**Version 1.0** - Production Release

## Support

For issues or questions, refer to:
- Test script: `test_mindmap_core.py`
- In-app help: Press `F1`
- Keyboard shortcuts: Press `F1` in application
