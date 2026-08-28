"""Unit tests for the repository validator."""

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import validate  # noqa: E402


class TrailerCheckTest(unittest.TestCase):
    """The trailer check is what keeps co-author trailers out of history.

    It reads `git log`, and a commit message containing a character the host
    locale cannot encode used to kill the reader thread, leaving `stdout` as
    None and crashing the check. A guard that crashes is a guard that is not
    guarding, so the decode is pinned to UTF-8.
    """

    def test_git_log_is_decoded_as_utf8(self):
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "log", "--format=%h%x1f%B%x1e"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertIsNotNone(result.stdout)

    def test_the_check_runs_over_real_history(self):
        validate.failures.clear()
        validate.check_trailer()
        self.assertEqual([], validate.failures)


if __name__ == "__main__":
    unittest.main()
