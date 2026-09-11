#!/usr/bin/env python3
"""Fail when a .claude/rules/ file scopes itself to globs that match nothing.

A rule with a wrong glob is the silent failure of a path-scoped corpus: it is valid
markdown, commits cleanly, reviews cleanly, and never loads once. Run in CI.

    python3 scripts/validate-rule-paths.py [repo_root]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_BRACE = re.compile(r"\{([^{}]*)\}")


def expand_braces(pattern: str) -> list[str]:
    """Expand {a,b} groups, innermost first. Returns pattern unchanged if none."""
    match = _BRACE.search(pattern)
    if not match:
        return [pattern]
    head, tail = pattern[: match.start()], pattern[match.end() :]
    out: list[str] = []
    for option in match.group(1).split(","):
        out.extend(expand_braces(f"{head}{option}{tail}"))
    return out


def rule_paths(text: str) -> list[str]:
    """Extract the paths: list from YAML frontmatter. Empty means repo-wide."""
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    if end == -1:
        return []
    front, found = text[3:end], False
    globs: list[str] = []
    for line in front.splitlines():
        if re.match(r"^\s*paths:\s*$", line):
            found = True
            continue
        if found:
            item = re.match(r"""^\s*-\s*["']?(.+?)["']?\s*$""", line)
            if item:
                globs.append(item.group(1))
            elif line.strip() and not line.startswith((" ", "\t")):
                break
    return globs


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    rules_dir = root / ".claude" / "rules"
    if not rules_dir.is_dir():
        print(f"no .claude/rules/ in {root} - nothing to validate")
        return 0

    dead: list[tuple[Path, list[str]]] = []
    checked = 0
    for rule in sorted(rules_dir.rglob("*.md")):
        globs = rule_paths(rule.read_text(encoding="utf-8", errors="replace"))
        if not globs:
            print(f"  repo-wide  {rule.relative_to(root)}")
            continue
        checked += 1
        hits, unmatched = 0, []
        for raw in globs:
            expanded = expand_braces(raw)
            found = sum(1 for pattern in expanded for _ in root.glob(pattern))
            hits += found
            if found == 0:
                unmatched.append(raw)
        status = "OK " if hits else "DEAD"
        print(f"  {status}       {rule.relative_to(root)}  ({hits} files)")
        if unmatched:
            for pattern in unmatched:
                print(f"       unmatched glob: {pattern}")
        if not hits:
            dead.append((rule, globs))

    if dead:
        print(f"\n{len(dead)} rule(s) match no files and will never load:")
        for rule, globs in dead:
            print(f"  {rule.relative_to(root)}: {', '.join(globs)}")
        return 1
    print(f"\n{checked} scoped rule(s) validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
