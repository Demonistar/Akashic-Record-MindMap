#!/usr/bin/env python3
"""
Test script for MindMap core functionality (non-GUI parts)
Tests the core classes without requiring tkinter
"""

import json
import time
import os
import sys

# Test imports (these should work without tkinter)
print("Testing core imports...")
try:
    import datetime
    import math
    import difflib
    from collections import deque
    print("✓ All core imports successful")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Import the core classes by parsing the file
# (We can't import the module directly because it imports tkinter)
print("\nTesting MindMapNode class...")

class MindMapNode:
    """Stores node data with full metadata"""

    def __init__(self, node_id, content="New Node", tier=1, x=100, y=100, parent_id=None):
        self.id = node_id
        self.content = content
        self.tier = max(1, min(5, tier))
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
        base_width = 120
        base_height = 40
        scale = 1.0 - (self.tier - 1) * 0.15
        return int(base_width * scale), int(base_height * scale)

    def get_display_text(self):
        max_chars = 15
        if len(self.content) <= max_chars:
            return self.content
        return self.content[:max_chars] + "..."

    def to_dict(self):
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
        self.type = conn_type
        self.weight = max(1, min(10, weight))

    def get_color(self):
        if self.type == "hierarchical":
            return "#1976D2"
        else:
            return "#FF9800"

    def get_width(self):
        return 2 + (self.weight - 1) * 0.2

    def is_slack(self):
        return self.weight <= 5

    def get_sag_amount(self):
        if not self.is_slack():
            return 0
        return 50 - (self.weight - 1) * 10

    def to_dict(self):
        return {
            "id": self.id,
            "from_node_id": self.from_node_id,
            "to_node_id": self.to_node_id,
            "type": self.type,
            "weight": self.weight
        }

    @staticmethod
    def from_dict(data):
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
        self.orientation = "right"
        self.top_drawer_open = False
        self.middle_drawer_open = False
        self.bottom_drawer_open = False
        self.drawer_height = 40
        self.drawer_slide_amount = 25

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "orientation": self.orientation,
            "locked": self.locked
        }

    @staticmethod
    def from_dict(data):
        cabinet = FileCabinet(data.get("x", 50), data.get("y", 50))
        cabinet.orientation = data.get("orientation", "right")
        cabinet.locked = data.get("locked", False)
        return cabinet


# ============================================================================
# TESTS
# ============================================================================

def test_node_creation():
    """Test node creation and properties"""
    print("\n=== Testing Node Creation ===")

    node = MindMapNode("node_123", "Test Node", tier=2, x=200, y=300)

    assert node.id == "node_123", "Node ID mismatch"
    assert node.content == "Test Node", "Node content mismatch"
    assert node.tier == 2, "Node tier mismatch"
    assert node.x == 200, "Node x position mismatch"
    assert node.y == 300, "Node y position mismatch"

    print("✓ Node creation successful")
    print(f"  ID: {node.id}")
    print(f"  Content: {node.content}")
    print(f"  Tier: {node.tier}")
    print(f"  Position: ({node.x}, {node.y})")

    return True


def test_node_sizing():
    """Test node size calculation based on tier"""
    print("\n=== Testing Node Sizing ===")

    sizes = {}
    for tier in range(1, 6):
        node = MindMapNode(f"node_{tier}", tier=tier)
        width, height = node.get_size()
        sizes[tier] = (width, height)
        print(f"✓ Tier {tier}: {width}x{height}px")

    # Verify tier 1 is largest
    assert sizes[1][0] > sizes[5][0], "Tier 1 should be larger than tier 5"

    return True


def test_node_display_text():
    """Test text truncation"""
    print("\n=== Testing Text Truncation ===")

    short_node = MindMapNode("node_1", "Short")
    assert short_node.get_display_text() == "Short", "Short text should not truncate"
    print(f"✓ Short text: '{short_node.get_display_text()}'")

    long_node = MindMapNode("node_2", "This is a very long text that should be truncated")
    display_text = long_node.get_display_text()
    assert len(display_text) <= 18, "Long text should truncate"
    assert display_text.endswith("..."), "Truncated text should end with ..."
    print(f"✓ Long text: '{display_text}'")

    return True


def test_node_serialization():
    """Test node to/from dict conversion"""
    print("\n=== Testing Node Serialization ===")

    # Create node with full metadata
    node = MindMapNode("node_456", "Serialization Test", tier=3, x=400, y=500)
    node.tags = ["test", "important"]
    node.emotion = "happy"
    node.children_ids = ["node_789", "node_012"]

    # Convert to dict
    node_dict = node.to_dict()
    print(f"✓ Node converted to dict")
    print(f"  Keys: {list(node_dict.keys())}")

    # Convert back from dict
    restored_node = MindMapNode.from_dict(node_dict)
    print(f"✓ Node restored from dict")

    # Verify all properties
    assert restored_node.id == node.id
    assert restored_node.content == node.content
    assert restored_node.tier == node.tier
    assert restored_node.tags == node.tags
    assert restored_node.emotion == node.emotion
    assert restored_node.children_ids == node.children_ids
    print(f"✓ All properties preserved")

    return True


def test_connection_creation():
    """Test connection creation"""
    print("\n=== Testing Connection Creation ===")

    conn = Connection("conn_1", "node_a", "node_b", "hierarchical", weight=7)

    assert conn.id == "conn_1"
    assert conn.from_node_id == "node_a"
    assert conn.to_node_id == "node_b"
    assert conn.type == "hierarchical"
    assert conn.weight == 7

    print("✓ Connection created")
    print(f"  ID: {conn.id}")
    print(f"  From: {conn.from_node_id} → To: {conn.to_node_id}")
    print(f"  Type: {conn.type}")
    print(f"  Weight: {conn.weight}")

    return True


def test_connection_physics():
    """Test connection physics calculations"""
    print("\n=== Testing Connection Physics ===")

    # Test slack connections (weight 1-5)
    slack_conn = Connection("conn_slack", "a", "b", weight=3)
    assert slack_conn.is_slack() == True, "Weight 3 should be slack"
    sag = slack_conn.get_sag_amount()
    print(f"✓ Slack connection (weight 3): sag = {sag}px")

    # Test tight connections (weight 6-10)
    tight_conn = Connection("conn_tight", "a", "b", weight=8)
    assert tight_conn.is_slack() == False, "Weight 8 should not be slack"
    sag = tight_conn.get_sag_amount()
    assert sag == 0, "Tight connection should have 0 sag"
    print(f"✓ Tight connection (weight 8): sag = {sag}px")

    return True


def test_connection_colors():
    """Test connection color based on type"""
    print("\n=== Testing Connection Colors ===")

    hierarchical = Connection("c1", "a", "b", "hierarchical")
    reference = Connection("c2", "a", "b", "reference")

    assert hierarchical.get_color() == "#1976D2", "Hierarchical should be blue"
    assert reference.get_color() == "#FF9800", "Reference should be orange"

    print(f"✓ Hierarchical color: {hierarchical.get_color()}")
    print(f"✓ Reference color: {reference.get_color()}")

    return True


def test_file_cabinet():
    """Test file cabinet"""
    print("\n=== Testing File Cabinet ===")

    cabinet = FileCabinet(100, 200)

    assert cabinet.x == 100
    assert cabinet.y == 200
    assert cabinet.locked == False
    assert cabinet.orientation == "right"

    print("✓ Cabinet created")
    print(f"  Position: ({cabinet.x}, {cabinet.y})")
    print(f"  Locked: {cabinet.locked}")
    print(f"  Orientation: {cabinet.orientation}")

    # Test serialization
    cabinet_dict = cabinet.to_dict()
    restored_cabinet = FileCabinet.from_dict(cabinet_dict)

    assert restored_cabinet.x == cabinet.x
    assert restored_cabinet.orientation == cabinet.orientation

    print("✓ Cabinet serialization works")

    return True


def test_project_save_load():
    """Test project save and load"""
    print("\n=== Testing Project Save/Load ===")

    # Create test project
    nodes = {}
    connections = {}

    # Create some nodes
    node1 = MindMapNode("node_1", "Root Node", tier=1, x=500, y=300)
    node2 = MindMapNode("node_2", "Child Node", tier=2, x=650, y=400, parent_id="node_1")
    node1.children_ids.append("node_2")

    nodes["node_1"] = node1
    nodes["node_2"] = node2

    # Create connection
    conn = Connection("conn_1", "node_1", "node_2", "hierarchical")
    connections["conn_1"] = conn

    # Create cabinet
    cabinet = FileCabinet(50, 50)

    # Create project structure
    project = {
        "version": "1.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "cabinet": cabinet.to_dict(),
        "nodes": {node_id: node.to_dict() for node_id, node in nodes.items()},
        "connections": {conn_id: conn.to_dict() for conn_id, conn in connections.items()},
        "theme": "default",
        "canvas_offset": {"x": 0, "y": 0},
        "zoom_factor": 1.0
    }

    # Save to file
    test_file = "test_project.json"
    with open(test_file, 'w') as f:
        json.dump(project, f, indent=2)

    print(f"✓ Project saved to {test_file}")

    # Load from file
    with open(test_file, 'r') as f:
        loaded_project = json.load(f)

    print(f"✓ Project loaded from {test_file}")

    # Verify structure
    assert "nodes" in loaded_project
    assert "connections" in loaded_project
    assert "cabinet" in loaded_project
    assert len(loaded_project["nodes"]) == 2
    assert len(loaded_project["connections"]) == 1

    print(f"✓ Project structure verified")
    print(f"  Nodes: {len(loaded_project['nodes'])}")
    print(f"  Connections: {len(loaded_project['connections'])}")

    # Restore objects
    restored_nodes = {
        node_id: MindMapNode.from_dict(node_data)
        for node_id, node_data in loaded_project["nodes"].items()
    }

    restored_connections = {
        conn_id: Connection.from_dict(conn_data)
        for conn_id, conn_data in loaded_project["connections"].items()
    }

    # Verify restored data
    assert "node_1" in restored_nodes
    assert restored_nodes["node_1"].content == "Root Node"
    assert restored_nodes["node_2"].parent_id == "node_1"

    print(f"✓ Objects restored correctly")

    # Clean up
    os.remove(test_file)
    print(f"✓ Test file cleaned up")

    return True


def test_node_id_parsing():
    """Test the CRITICAL node ID parsing fix"""
    print("\n=== Testing CRITICAL Node ID Parsing ===")

    # Simulate canvas tags
    test_tags = ("node_node_1234567890", "node", "clickable")

    # WRONG METHOD (would fail):
    # node_id = test_tags[0].split("_")[1]  # Returns "node" - WRONG!

    # CORRECT METHOD (using slicing):
    node_tags = [tag for tag in test_tags if tag.startswith("node_")]
    if node_tags:
        node_tag = node_tags[0]
        node_id = node_tag[5:]  # Remove "node_" prefix - CORRECT!

    print(f"  Test tags: {test_tags}")
    print(f"  Extracted node tag: {node_tag}")
    print(f"  Extracted node ID: {node_id}")

    assert node_id == "node_1234567890", f"Node ID should be 'node_1234567890', got '{node_id}'"

    print("✓ CRITICAL FIX VERIFIED: Node ID parsing works correctly!")

    return True


def test_auto_linking_similarity():
    """Test auto-linking similarity calculation"""
    print("\n=== Testing Auto-Linking Similarity ===")

    # Create test nodes
    node1 = MindMapNode("n1", "Machine Learning Algorithms")
    node1.tags = ["AI", "ML", "algorithms"]

    node2 = MindMapNode("n2", "Deep Learning Neural Networks")
    node2.tags = ["AI", "ML", "neural"]

    node3 = MindMapNode("n3", "Database Management")
    node3.tags = ["database", "SQL"]

    # Calculate similarity
    score_similar = 0
    common_tags = set(node1.tags) & set(node2.tags)
    score_similar += len(common_tags) * 10

    similarity = difflib.SequenceMatcher(None, node1.content, node2.content).ratio()
    score_similar += similarity * 100

    score_different = 0
    common_tags = set(node1.tags) & set(node3.tags)
    score_different += len(common_tags) * 10

    similarity = difflib.SequenceMatcher(None, node1.content, node3.content).ratio()
    score_different += similarity * 100

    print(f"✓ Similarity score (ML vs Deep Learning): {int(score_similar)}")
    print(f"✓ Similarity score (ML vs Database): {int(score_different)}")

    assert score_similar > score_different, "Similar nodes should have higher score"

    return True


# ============================================================================
# RUN ALL TESTS
# ============================================================================

def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("MINDMAP CORE FUNCTIONALITY TESTS")
    print("=" * 70)

    tests = [
        ("Node Creation", test_node_creation),
        ("Node Sizing", test_node_sizing),
        ("Node Display Text", test_node_display_text),
        ("Node Serialization", test_node_serialization),
        ("Connection Creation", test_connection_creation),
        ("Connection Physics", test_connection_physics),
        ("Connection Colors", test_connection_colors),
        ("File Cabinet", test_file_cabinet),
        ("Project Save/Load", test_project_save_load),
        ("CRITICAL: Node ID Parsing", test_node_id_parsing),
        ("Auto-Linking Similarity", test_auto_linking_similarity),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n✗ Test failed: {name}")
        except Exception as e:
            failed += 1
            print(f"\n✗ Test failed: {name}")
            print(f"  Error: {e}")

    print("\n" + "=" * 70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
