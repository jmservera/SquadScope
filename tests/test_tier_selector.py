"""Tests for scripts/tier_selector.py."""
from __future__ import annotations

import json

import pytest

from scripts.tier_selector import build_config, main, select_tier


class TestSelectTier:
    def test_normal(self):
        assert select_tier(0.10, 2.00) == "normal"

    def test_budget_by_estimated_cost(self):
        assert select_tier(0.50, 2.00) == "budget"

    def test_budget_by_monthly_spent(self):
        assert select_tier(0.10, 5.00) == "budget"

    def test_minimal(self):
        assert select_tier(0.10, 8.00) == "minimal"

    def test_emergency(self):
        assert select_tier(0.10, 10.00) == "emergency"

    def test_emergency_custom_budget(self):
        assert select_tier(0.10, 20.00, monthly_budget=20.00) == "emergency"

    def test_boundary_normal(self):
        assert select_tier(0.49, 4.99) == "normal"

    def test_boundary_budget(self):
        assert select_tier(0.50, 4.99) == "budget"


class TestBuildConfig:
    def test_normal_config(self):
        cfg = build_config("normal")
        assert cfg == {"tier": "normal", "model": "claude-sonnet-4", "max_repos": None, "skip_ai": False}

    def test_budget_config(self):
        cfg = build_config("budget")
        assert cfg == {"tier": "budget", "model": "gpt-5.4-mini", "max_repos": 100, "skip_ai": False}

    def test_minimal_config(self):
        cfg = build_config("minimal")
        assert cfg == {"tier": "minimal", "model": "gpt-5-mini", "max_repos": 30, "skip_ai": False}

    def test_emergency_config(self):
        cfg = build_config("emergency")
        assert cfg == {"tier": "emergency", "model": None, "max_repos": None, "skip_ai": True}


class TestMain:
    def test_normal_output(self, capsys):
        code = main(["--estimated-cost", "0.10", "--monthly-spent", "2.00"])
        assert code == 0
        output = json.loads(capsys.readouterr().out)
        assert output["tier"] == "normal"

    def test_emergency_output(self, capsys):
        code = main(["--estimated-cost", "0.10", "--monthly-spent", "10.00"])
        assert code == 0
        output = json.loads(capsys.readouterr().out)
        assert output["tier"] == "emergency"
        assert output["skip_ai"] is True

    def test_always_exits_0(self, capsys):
        code = main(["--estimated-cost", "5.00", "--monthly-spent", "99.00"])
        assert code == 0
