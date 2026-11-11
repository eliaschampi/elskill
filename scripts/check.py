#!/usr/bin/env python3
"""Check package integrity using the repository's single-line metadata format.

This is a dependency-free integrity check, not a general YAML parser or a
behavioral evaluation. Pass an alternate repository root to check a fixture.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit


def scalar(text, key, indent=0):
    matches = re.findall(rf"^{' ' * indent}{re.escape(key)}: (.+)$", text, re.M)
    if len(matches) != 1:
        raise ValueError(f"expected one single-line {key}")
    value = matches[0]
    if value.startswith('"'):
        value = json.loads(value)
    elif value.startswith(("'", "|", ">", "[", "{")) or ": " in value or " #" in value:
        raise ValueError(f"use a plain or JSON-quoted string for {key}")
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a nonempty string")
    return value


def prose(text):
    return re.sub(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$", "", text)


def check(root):
    errors = []
    skills = sorted(root.glob("el-*/SKILL.md"))
    if not skills:
        return ["no skill entrypoints found"]
    documents = {p.resolve(): p.read_text(encoding="utf-8") for p in root.rglob("*.md") if ".git" not in p.parts}
    graph = {p: set() for p in documents}
    definitions = Counter()
    mentions = set()
    for path, text in documents.items():
        body = prose(text)
        definitions.update(re.findall(r"\*\*([ABD]\d+)\.", body))
        mentions.update(re.findall(r"\b[ABD]\d+\b", body))
        for target in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", body):
            target = target.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            linked = (path.parent / unquote(parsed.path)).resolve()
            if not linked.exists():
                errors.append(f"{path.relative_to(root)}: missing link {target}")
            elif linked in documents:
                graph[path].add(linked)
    for rule, count in definitions.items():
        if count != 1:
            errors.append(f"{rule}: defined {count} times")
    for rule in sorted(mentions - definitions.keys()):
        errors.append(f"{rule}: referenced without a definition")
    for skill in skills:
        try:
            text = documents[skill.resolve()]
            frontmatter = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
            if not frontmatter:
                raise ValueError("missing YAML frontmatter")
            name = scalar(frontmatter[1], "name")
            description = scalar(frontmatter[1], "description")
            if name != skill.parent.name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
                raise ValueError("name must match its directory and use lowercase hyphens")
            if len(description) > 1024:
                raise ValueError("description exceeds 1024 characters")
            metadata = (skill.parent / "agents/openai.yaml").read_text(encoding="utf-8")
            if not re.search(r"^interface:\s*$", metadata, re.M):
                raise ValueError("missing interface metadata")
            scalar(metadata, "display_name", 2)
            summary = scalar(metadata, "short_description", 2)
            prompt = scalar(metadata, "default_prompt", 2)
            if not 25 <= len(summary) <= 64:
                raise ValueError("short_description must contain 25–64 characters")
            if f"${name}" not in prompt:
                raise ValueError("default_prompt must invoke its skill")
            reached, pending = set(), [skill.resolve()]
            while pending:
                node = pending.pop()
                if node not in reached:
                    reached.add(node)
                    pending.extend(graph[node] - reached)
            for reference in (skill.parent / "references").rglob("*.md"):
                if reference.resolve() not in reached:
                    errors.append(f"{reference.relative_to(root)}: unreachable from its skill")
        except (ValueError, OSError) as error:
            errors.append(f"{skill.relative_to(root)}: {error}")
    return errors


if __name__ == "__main__":
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    try:
        errors = check(root)
    except (OSError, UnicodeError) as error:
        errors = [str(error)]
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        sys.exit(1)
    print("Package integrity passed: metadata, local links, references, and rule IDs.")
