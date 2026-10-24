"""Knowledge entries must have traceable metadata and working local references."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class KnowledgeTests(unittest.TestCase):
    def test_entries_have_required_metadata_and_unique_ids(self):
        articles = list((ROOT / "docs/knowledge").glob("*/*.md"))
        self.assertGreaterEqual(len(articles), 12)
        ids = []
        for file in articles:
            text = file.read_text()
            for key in ["编号：", "状态：", "适用范围：", "最近验证日期：", "证据："]:
                self.assertIn(key, text, str(file))
            match = re.search(r"编号：([CDT]-[0-9]{3})", text)
            self.assertIsNotNone(match, str(file))
            ids.append(match[1])
        self.assertEqual(len(ids), len(set(ids)))

    def test_knowledge_and_operator_guide_links_exist(self):
        files = [*(ROOT / "docs/knowledge").rglob("*.md"), ROOT / "docs/CORE_V1.md"]
        for file in files:
            for target in re.findall(r"\]\(([^)]+)\)", file.read_text()):
                if "://" in target:
                    continue
                self.assertTrue(
                    (file.parent / target.split("#")[0]).exists(),
                    str(file) + ": " + target,
                )
