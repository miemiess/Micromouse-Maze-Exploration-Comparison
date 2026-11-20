"""扩展层（src/ext/）的接入检查：扩展算法与基础算法同名会被拒绝，且不影响基础层。

扩展算法和规则的具体测试放在本目录，文件名以 test_ 开头。
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from core.algorithm_api import discover_algorithms  # noqa: E402


class ExtLayoutTests(unittest.TestCase):
    def test_ext_algorithms_do_not_shadow_basic(self):
        """自动发现没有错误（包括重名）；扩展层的算法都标记为 ext。"""
        infos, errors = discover_algorithms()
        self.assertEqual(errors, [])
        ext = discover_algorithms(layer="ext")[0]
        self.assertTrue(all(info.layer == "ext" for info in ext.values()))
        basic = discover_algorithms(layer="basic")[0]
        self.assertEqual(set(basic) & set(ext), set())
        self.assertEqual(set(infos), set(basic) | set(ext))


if __name__ == "__main__":
    unittest.main()
