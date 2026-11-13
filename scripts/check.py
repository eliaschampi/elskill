#!/usr/bin/env python3
"""Validate package metadata, portable links, references, and rule citations.

Install requirements-dev.txt to run. This checks structure, not agent behavior
or preservation of unreferenced rules across revisions.
"""

import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:
    raise SystemExit("Install development dependencies: python3 -m pip install -r requirements-dev.txt")


class UniqueSafeLoader(yaml.SafeLoader):
    """Use YAML's safe types while rejecting ambiguous duplicate mapping keys."""

    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        keys = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                if key in keys:
                    raise ValueError(f"duplicate YAML key: {key}")
                keys.add(key)
            except TypeError as error:
                raise ValueError("YAML mapping keys must be scalar") from error
        return super().construct_mapping(node, deep=deep)


def mapping(text):
    value = yaml.load(text, Loader=UniqueSafeLoader)
    if not isinstance(value, dict):
        raise ValueError("expected a YAML mapping")
    return value


def text_field(data, key):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a nonempty string")
    return value


def prose(text):
    return re.sub(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$", "", text)


def rule_sequence_errors(definitions, readme):
    """Each rule group must run 1..N without gaps, and the README must state that range.

    Counting definitions alone cannot see a rule deleted from the middle of a
    sequence, and a deleted last rule is only noticed if something else cites it.
    """
    errors = []
    numbers = {}
    for rule in definitions:
        numbers.setdefault(rule[0], set()).add(int(rule[1:]))
    for group, found in sorted(numbers.items()):
        missing = sorted(set(range(1, max(found) + 1)) - found)
        if missing:
            errors.append(f"{group}: missing rule IDs {', '.join(f'{group}{n}' for n in missing)}")
    if readme is None:
        return errors
    claimed = {group: int(last) for group, last in re.findall(r"`([ABD])1`\s*[–-]\s*`\1(\d+)`", readme)}
    for group, found in sorted(numbers.items()):
        if claimed.get(group) != max(found):
            errors.append(f"README.md: {group} range must be stated as `{group}1`–`{group}{max(found)}`")
    for group in sorted(claimed.keys() - numbers.keys()):
        errors.append(f"README.md: {group} range is stated but no {group} rule is defined")
    return errors


def check(root):
    root = root.resolve()
    errors = []
    skills = sorted(root.glob("el-*/SKILL.md"))
    if not skills:
        return ["no skill entrypoints found"]
    documents = {}
    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        if not path.resolve().is_relative_to(root):
            errors.append(f"{path.relative_to(root)}: document resolves outside the package")
            continue
        documents[path.resolve()] = path.read_text(encoding="utf-8")
    graph = {p: set() for p in documents}
    definitions = Counter()
    mentions = set()
    for path, text in documents.items():
        body = prose(text)
        definitions.update(re.findall(r"\*\*([ABD]\d+)\.", body))
        mentions.update(re.findall(r"\b[ABD]\d+\b", body))
        for target in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", body):
            target = target.strip().strip("<>")
            try:
                parsed = urlsplit(target)
            except ValueError:
                errors.append(f"{path.relative_to(root)}: invalid link {target}")
                continue
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            link_path = Path(unquote(parsed.path))
            linked = (path.parent / link_path).resolve()
            if link_path.is_absolute() or not linked.is_relative_to(root):
                errors.append(f"{path.relative_to(root)}: nonportable link {target}")
            elif not linked.exists():
                errors.append(f"{path.relative_to(root)}: missing link {target}")
            elif linked in documents:
                graph[path].add(linked)
    for rule, count in definitions.items():
        if count != 1:
            errors.append(f"{rule}: defined {count} times")
    for rule in sorted(mentions - definitions.keys()):
        errors.append(f"{rule}: referenced without a definition")
    errors.extend(rule_sequence_errors(definitions, documents.get((root / "README.md").resolve())))
    for skill in skills:
        try:
            if skill.resolve() not in documents:
                raise ValueError("skill entrypoint resolves outside the package")
            text = documents[skill.resolve()]
            frontmatter = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
            if not frontmatter:
                raise ValueError("missing YAML frontmatter")
            fields = mapping(frontmatter[1])
            name = text_field(fields, "name")
            description = text_field(fields, "description")
            if name != skill.parent.name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
                raise ValueError("name must match its directory and use lowercase hyphens")
            if len(description) > 1024:
                raise ValueError("description exceeds 1024 characters")
            metadata = mapping((skill.parent / "agents/openai.yaml").read_text(encoding="utf-8"))
            interface = metadata.get("interface")
            if not isinstance(interface, dict):
                raise ValueError("interface must be a mapping")
            text_field(interface, "display_name")
            summary = text_field(interface, "short_description")
            prompt = text_field(interface, "default_prompt")
            if not 25 <= len(summary) <= 64:
                raise ValueError("short_description must contain 25–64 characters")
            if not re.search(rf"\${re.escape(name)}(?![\w-])", prompt):
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
        except (ValueError, OSError, yaml.YAMLError) as error:
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
