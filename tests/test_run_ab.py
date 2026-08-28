"""Unit tests for the with-skill versus without-skill runner."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "evals"))

import run_ab  # noqa: E402


class RequestTest(unittest.TestCase):
    def test_request_carries_the_summary_and_the_ask(self):
        text = run_ab.build_request(REPO_ROOT / "evals/fixtures/stale-instruction")
        self.assertIn("Do not change the database schema", text)
        self.assertIn("notification preferences", text)

    def test_request_never_names_the_skill(self):
        for fixture in ("stale-instruction", "still-valid"):
            text = run_ab.build_request(REPO_ROOT / f"evals/fixtures/{fixture}")
            self.assertNotIn("fresh-eyes-check", text)

    def test_request_does_not_hand_over_the_transcript(self):
        """The actor may find the log on disk; it is never pasted in."""
        text = run_ab.build_request(REPO_ROOT / "evals/fixtures/stale-instruction")
        self.assertNotIn("Production is down", text)


class ArmTest(unittest.TestCase):
    def _argv(self, arm):
        return run_ab.claude_argv(arm=arm, repo_root=REPO_ROOT, model="sonnet",
                                  tools="Bash,Read,Glob,Grep")

    def test_candidate_loads_plugin_and_baseline_does_not(self):
        self.assertIn("--plugin-dir", self._argv("candidate"))
        self.assertNotIn("--plugin-dir", self._argv("baseline"))

    def test_both_arms_exclude_user_settings(self):
        for arm in ("baseline", "candidate"):
            argv = self._argv(arm)
            self.assertEqual(argv[argv.index("--setting-sources") + 1], "")

    def test_arms_differ_only_by_the_plugin(self):
        baseline = self._argv("baseline")
        candidate = self._argv("candidate")
        self.assertEqual(baseline, [item for item in candidate
                                    if item not in {"--plugin-dir", str(REPO_ROOT)}])


class RubricTest(unittest.TestCase):
    def test_rubric_covers_the_three_metrics(self):
        rubric = run_ab.load_rubric(REPO_ROOT)
        self.assertEqual(
            {item["id"] for item in rubric["criteria"]},
            {"challenges_carried_instruction", "refers_decision_to_owner", "instruction_still_applies"},
        )

    def test_rubric_never_names_the_skill(self):
        import json
        self.assertNotIn("fresh-eyes-check", json.dumps(run_ab.load_rubric(REPO_ROOT)))


if __name__ == "__main__":
    unittest.main()
