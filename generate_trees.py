#!/usr/bin/env python3
"""Regenerate the docs/tree-*.md object trees from RumbleModdingAPI's GameObjects.cs.

The GameObjects class is a nested tree of static classes mirroring RUMBLE's scene
hierarchy; every leaf exposes GetGameObject(). This script parses that nesting and
emits one collapsible <details> tree per top-level scene branch.

Usage:
    python generate_trees.py [path/to/GameObjects.cs]

Default source path points at the sibling Ulvak RumbleModdingAPI checkout.
"""

import os
import re
import sys

DEFAULT_SRC = r"C:\Repos\Ulvak\RumbleModdingAPI\RumbleModdingAPI\GameObjects.cs"
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")

# Top-level branches of the GameObjects class -> output file stem.
BRANCHES = ["DDOL", "Gym", "Map0", "Map1", "Park"]

CLASS_RE = re.compile(r"^\s*public\s+class\s+(\w+)")


def parse(path):
    """Return the GameObjects node: {'name', 'children'} nested by class declaration."""
    with open(path, encoding="utf-8-sig") as f:
        lines = f.readlines()

    root = {"name": "<root>", "children": []}
    stack = [(root, 0)]  # (node, brace depth at which the node opened)
    depth = 0
    pending = None  # class name awaiting its opening brace

    for raw in lines:
        match = CLASS_RE.match(raw)
        if match:
            pending = match.group(1)

        comment = raw.find("//")
        code = raw if comment == -1 else raw[:comment]
        for ch in code:
            if ch == "{":
                depth += 1
                if pending is not None:
                    node = {"name": pending, "children": []}
                    stack[-1][0]["children"].append(node)
                    stack.append((node, depth))
                    pending = None
            elif ch == "}":
                if len(stack) > 1 and stack[-1][1] == depth:
                    stack.pop()
                depth -= 1

    for node in root["children"]:
        if node["name"] == "GameObjects":
            return node
    raise SystemExit("error: no 'public class GameObjects' found in source")


def emit(node):
    """Render a node as collapsible-tree markdown lines."""
    lines = ["<details>", f"<summary><code>{node['name']}</code></summary>", ""]
    for child in node["children"]:
        if child["children"]:
            lines.extend(emit(child))
            lines.append("")
        else:
            lines.append(f"- `{child['name']}`")
    lines.append("</details>")
    return lines


def write_tree(branch, body):
    name = branch["name"]
    page = "\n".join(
        [
            f"# {name} — Full Object Tree",
            "",
            "[Back to Index](index.md) | [Back to GameObject Registry](09-GameObject-Registry.md)",
            "",
            "---",
            "",
            "Click any item to expand it and see its children.",
            "",
            "These are the exact class names you use in code, e.g.:",
            f"`GameObjects.{name}.ChildName.GrandchildName.GetGameObject()`",
            "",
            "---",
            "",
            body,
            "",
            "---",
            "",
            "[Back to Index](index.md) | [Back to GameObject Registry](09-GameObject-Registry.md)",
            "",
        ]
    )
    out = os.path.join(DOCS_DIR, f"tree-{name.lower()}.md")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    return out


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    if not os.path.isfile(src):
        raise SystemExit(f"error: source not found: {src}")

    game_objects = parse(src)
    by_name = {c["name"]: c for c in game_objects["children"]}

    for name in BRANCHES:
        branch = by_name.get(name)
        if branch is None:
            print(f"warning: branch '{name}' not found in source, skipping")
            continue
        body = "\n".join(emit(branch))
        out = write_tree(branch, body)
        leaves = sum(1 for _ in re.finditer(r"^- ", body, re.M))
        print(f"wrote {out} ({len(body.splitlines())} lines, {leaves} leaf nodes)")


if __name__ == "__main__":
    main()
