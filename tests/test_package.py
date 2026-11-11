"""Regression tests for package validation and non-destructive installation."""

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check", ROOT / "scripts/check.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

ENTRY = """---
name: el-test
description: Check a focused fixture.
---
# Test

- **A1.** One responsibility.

[Reference](references/example.md)
"""
METADATA = """interface:
  display_name: "Test"
  short_description: "Focused package validation fixture"
  default_prompt: "Use $el-test to inspect this fixture."
"""


class PackageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="elskill-package-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / "package"
        self.skill = self.root / "el-test"
        (self.skill / "agents").mkdir(parents=True)
        (self.skill / "references").mkdir()
        self.entry = self.skill / "SKILL.md"
        self.metadata = self.skill / "agents/openai.yaml"
        self.entry.write_text(ENTRY)
        self.metadata.write_text(METADATA)
        (self.skill / "references/example.md").write_text("# Example\n\nApplies A1.\n")

    def test_clean_package_and_multiline_yaml(self):
        self.assertEqual(checker.check(self.root), [])
        self.entry.write_text(ENTRY.replace("description: Check a focused fixture.", "description: >\n  Check a focused\n  fixture."))
        self.assertEqual(checker.check(self.root), [])

    def test_invalid_frontmatter(self):
        for replacement in ("description: true", "description: 42", "description: null", "description: [", "description: Valid.\nbroken: [", "description: First.\ndescription: Second."):
            with self.subTest(replacement=replacement):
                self.entry.write_text(ENTRY.replace("description: Check a focused fixture.", replacement))
                self.assertTrue(checker.check(self.root))

    def test_invalid_interface_metadata(self):
        for text in (
            METADATA.replace("interface:\n", "interface:\nother:\n"),
            METADATA.replace('display_name: "Test"', "display_name: false"),
            METADATA + "  display_name: Duplicate\n",
            METADATA.replace("$el-test", "$el-test-other"),
            "interface: []\n",
        ):
            with self.subTest(metadata=text):
                self.metadata.write_text(text)
                self.assertTrue(checker.check(self.root))

    def test_existing_external_and_absolute_links_are_rejected(self):
        external = self.base / "external.md"
        external.write_text("# External\n")
        for target in ("../../external.md", str(external), str(self.entry)):
            with self.subTest(target=target):
                self.entry.write_text(ENTRY + f"\n[External]({target})\n")
                self.assertTrue(checker.check(self.root))

    def test_symlink_cannot_escape_package(self):
        external = self.base / "external.md"
        external.write_text("# External\n")
        (self.skill / "linked.md").symlink_to(external)
        self.entry.write_text(ENTRY + "\n[External](linked.md)\n")
        self.assertTrue(checker.check(self.root))

    def test_broken_links_unreachable_references_and_rule_citations(self):
        for text in (
            ENTRY.replace("references/example.md", "references/missing.md"),
            ENTRY.replace("[Reference](references/example.md)", ""),
            ENTRY + "\n- **A1.** Duplicate.\n",
            ENTRY + "\nApply B999.\n",
        ):
            with self.subTest(entry=text):
                self.entry.write_text(text)
                self.assertTrue(checker.check(self.root))


class InstallerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="elskill-installer-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.target = self.root / "target with spaces"
        self.skills = sorted(path.parent for path in ROOT.glob("el-*/SKILL.md"))

    def run_installer(self, *arguments):
        return subprocess.run(["bash", str(ROOT / "install.sh"), *map(str, arguments)], text=True, capture_output=True)

    def test_explicit_target_and_idempotent_install(self):
        first = self.run_installer("--target", self.target)
        self.assertEqual(first.returncode, 0, first.stderr)
        before = {}
        for skill in self.skills:
            link = self.target / skill.name
            self.assertTrue(link.is_symlink())
            self.assertEqual(link.resolve(), skill.resolve())
            before[link] = link.lstat().st_ino
        second = self.run_installer("--target", self.target)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(before, {link: link.lstat().st_ino for link in before})

    def test_conflicting_entries_are_preserved(self):
        self.target.mkdir()
        for kind in ("file", "directory", "symlink", "dangling"):
            with self.subTest(kind=kind):
                link = self.target / self.skills[0].name
                foreign = self.root / f"foreign-{kind}"
                if kind == "file":
                    link.write_text("keep this content")
                elif kind == "directory":
                    link.mkdir()
                    (link / "keep").write_text("keep this content")
                else:
                    if kind == "symlink":
                        foreign.mkdir()
                    link.symlink_to(foreign, target_is_directory=True)
                inode = link.lstat().st_ino
                result = self.run_installer("--target", self.target)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(link.lstat().st_ino, inode)
                if kind == "directory":
                    self.assertEqual((link / "keep").read_text(), "keep this content")
                    (link / "keep").unlink()
                    link.rmdir()
                else:
                    if kind == "file":
                        self.assertEqual(link.read_text(), "keep this content")
                    else:
                        self.assertEqual(link.readlink(), foreign)
                    link.unlink()

    def test_help_and_invalid_arguments_do_not_mutate(self):
        # Sentinel commands fail before any filesystem operation, even if a
        # regression accidentally selects the user's default install targets.
        shell = 'mkdir() { echo MUTATION >&2; return 99; }; ln() { echo MUTATION >&2; return 99; }; export -f mkdir ln; bash "$@"'
        cases = [(('--help',), 0), (('--unknown',), 2), (('--target',), 2),
                 (('--target', ''), 2), (('--target', self.target, '--opencode'), 2),
                 (('--opencode', '--target', self.target), 2)]
        for arguments, expected in cases:
            with self.subTest(arguments=arguments):
                result = subprocess.run(['bash', '-c', shell, 'installer-test', str(ROOT / 'install.sh'), *map(str, arguments)], text=True, capture_output=True)
                self.assertEqual(result.returncode, expected, result.stderr)
                self.assertNotIn('MUTATION', result.stderr)
                self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
