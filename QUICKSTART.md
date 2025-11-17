# Quick Start Guide - Akashic Record MindMap

## Installation & First Run

1. **Install tkinter** (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-tk

   # Fedora
   sudo dnf install python3-tkinter

   # macOS - included with Python
   ```

2. **Launch the application**:
   ```bash
   python3 mindmap_desktop.py
   ```

The app will open in fullscreen with a transparent overlay.

## Your First 5 Minutes

### 1. Create Your First Node (10 seconds)
- Press `Ctrl+N`
- A blue node appears: "New Node"
- **SUCCESS**: You see a blue rectangle with text

### 2. Edit the Node (15 seconds)
- Double-click the node
- Type: "My First Mind Map"
- Press OK
- **SUCCESS**: Node text updates

### 3. Move the Node (10 seconds)
- Click and drag the node
- Move it around the screen
- **SUCCESS**: Node follows your mouse

### 4. Add a Child Node (20 seconds)
- Right-click your node
- Select "Add Child"
- A smaller node appears connected by a blue line
- **SUCCESS**: Two nodes connected by a line

### 5. Use the File Cabinet (30 seconds)
- Find the brown cabinet in the corner
- Click the **Top Drawer** → Creates a new top-tier node
- Click the **Bottom Drawer** → Opens settings
- Click the **Auto-Save Toggle** → Enable/disable auto-save
- **SUCCESS**: Drawers slide out when clicked

### 6. Save Your Work (15 seconds)
- Press `Ctrl+S`
- Choose a filename: `my_mindmap.json`
- Click Save
- **SUCCESS**: File saved message appears

## Testing the Application

Run the test suite to verify everything works:
```bash
python3 test_mindmap_core.py
```

Expected output:
```
🎉 ALL TESTS PASSED!
TEST RESULTS: 11 passed, 0 failed
```

## Essential Keyboard Shortcuts

```
Ctrl+N    Create new node
Ctrl+S    Save project
Ctrl+O    Open project

Ctrl+L    Link two nodes (select one, press Ctrl+L, click another)
Ctrl+K    Lock/unlock cabinet
Ctrl+F    Search nodes

Ctrl+Z    Undo
Ctrl+Y    Redo

Delete    Delete selected nodes
Escape    Clear selection
F1        Show all shortcuts
```

## Common First-Time Questions

**Q: How do I create connections between non-related nodes?**
A: Select a node, press `Ctrl+L`, then click another node. This creates a reference link (dashed orange line).

**Q: How do I change the connection "weight"?**
A: When creating a reference link, you'll be prompted for weight (1-10):
- 1-5 = Slack/curved lines
- 6-10 = Tight/straight lines

**Q: How do I make the cabinet face the other direction?**
A: Drag it (when unlocked) to the other side of the screen. It auto-flips to face center.

**Q: Where are my backups saved?**
A: In `{your_filename}_backups/` folder (5 most recent backups kept).

**Q: What if the app won't start?**
A: Most common issue is missing tkinter. Install it:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk
```

## File Cabinet Drawers Explained

```
┌─────────┐
│ Nodes   │ ← Click: Creates new top-tier node
├─────────┤
│Projects │ ← Click: Shows recent .json files to open
├─────────┤
│Settings │ ← Click: Auto-save, Theme, Export options
└─────────┘
```

## Project Structure After Saving

```
my_mindmap.json              ← Your main project
my_mindmap_backups/          ← Backup directory
├── backup_20251117_150000.json
├── backup_20251117_143000.json
├── backup_20251117_140000.json
├── backup_20251117_133000.json
└── backup_20251117_130000.json
```

## Export Your MindMap

1. Click **Bottom Drawer** (Settings)
2. Click export button:
   - **CSV** → Always available
   - **PDF** → Requires: `pip install reportlab`
   - **DOCX** → Requires: `pip install python-docx`
   - **XLSX** → Requires: `pip install openpyxl`

## Node Tiers Visual Guide

```
┌──────────────────┐
│  Tier 1 (120px)  │ ← Main topics
└──────────────────┘

┌────────────────┐
│ Tier 2 (102px) │ ← Sub-topics
└────────────────┘

┌──────────────┐
│Tier 3 (84px) │ ← Details
└──────────────┘

┌────────────┐
│Tier 4 (66) │ ← Sub-details
└────────────┘

┌──────────┐
│Tier5(48) │ ← Fine points
└──────────┘
```

## Next Steps

1. **Build a simple mindmap** (5-10 nodes)
2. **Try linking nodes** with `Ctrl+L`
3. **Save and reload** to test persistence
4. **Explore right-click menu** on nodes
5. **Try auto-link suggestions** (right-click → "Auto-Link Suggestions")

## Getting Help

- Press `F1` in the app for full keyboard shortcuts
- See `README.md` for comprehensive documentation
- Run `test_mindmap_core.py` to verify installation

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "No module named 'tkinter'" | Install python3-tk package |
| Cabinet won't move | Press `Ctrl+K` to unlock |
| Can't click drawers | Make sure not dragging cabinet |
| Export disabled | Install optional libraries |
| Auto-save not working | Enable in Settings drawer |

## Performance Note

The application is optimized for 50-200 nodes. For larger mindmaps:
- Use node collapse feature (`Ctrl+R`)
- Disable auto-save for better performance
- Use search (`Ctrl+F`) instead of scrolling

---

**Enjoy your mindmapping!** 🧠
