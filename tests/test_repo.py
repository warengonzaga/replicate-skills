import json
import os
import re
import unittest

from _load import ROOT

SKILLS = ["replica-recon", "replica-architect", "replica-design", "replica-build",
          "replica-backend", "replica-test", "replica-diff", "replica-entrepreneur",
          "replica-brand", "replica-launch", "replica-deploy"]



def frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (m.group(1) if m else ""), text


class Repo(unittest.TestCase):
    def test_one_canonical_set_of_eleven_skills(self):
        found = sorted(d for d in os.listdir(os.path.join(ROOT, "skills"))
                       if os.path.isfile(os.path.join(ROOT, "skills", d, "SKILL.md")))
        self.assertEqual(found, sorted(SKILLS))

    def test_frontmatter_name_and_description(self):
        for s in SKILLS:
            fm, text = frontmatter(os.path.join(ROOT, "skills", s, "SKILL.md"))
            self.assertIn("name: %s\n" % s, fm + "\n", s)
            self.assertRegex(fm, r"description: ", s)
            self.assertGreater(len(fm), 200, "%s description is too thin" % s)
            self.assertGreater(len(text.splitlines()), 60, s)

    def test_both_native_manifests_point_at_canonical_skills(self):
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json")) as fh:
            plugin = json.load(fh)
        self.assertEqual(plugin["name"], "replicate-skills")
        self.assertEqual(plugin["skills"], "./skills/")
        with open(os.path.join(ROOT, ".codex-plugin", "plugin.json")) as fh:
            codex = json.load(fh)
        for field in ["name", "version", "skills"]:
            self.assertEqual(plugin[field], codex[field])
        self.assertIn("Codex and Claude Code", plugin["description"])
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json")) as fh:
            market = json.load(fh)
        self.assertEqual(market["name"], "replicate-skills")
        self.assertEqual(market["plugins"][0]["name"], "replicate-skills")

    def test_documented_installation_paths(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
            readme = fh.read()
        self.assertIn("--runtime codex", readme)
        self.assertIn("~/.agents/skills/", readme)
        self.assertIn("/plugin install replicate-skills@replicate-skills", readme)
        for skill in SKILLS:
            self.assertIn(skill, readme)


    def test_shared_skill_contracts_and_only_release_workflow(self):
        from _load import load
        validator = load('scripts', 'validate')
        self.assertEqual(validator.validate(), [])

    def test_no_em_dashes_anywhere(self):
        bad = []
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
            for fn in filenames:
                if fn.endswith((".md", ".py", ".json", ".ts", ".csv")):
                    path = os.path.join(dirpath, fn)
                    with open(path, encoding="utf-8") as fh:
                        if chr(0x2014) in fh.read():
                            bad.append(os.path.relpath(path, ROOT))
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
