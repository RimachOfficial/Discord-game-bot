"""Tests for the fishing engine."""

import pytest
from engines.fishing_engine import (
    calculate_dynamic_weights,
    calculate_catch_probabilities,
    roll_fish,
)
from constants import FISH_TIERS, FISH_WEIGHTS, FISH_DATA


class TestCalculateDynamicWeights:
    def test_no_karma_returns_base_weights(self):
        """With zero karma, dynamic weights should match base weights approximately."""
        raw_karma = {}
        weights = calculate_dynamic_weights(raw_karma, False, False)
        assert len(weights) == len(FISH_WEIGHTS)
        # Without karma, weights should be close to base
        for i, w in enumerate(weights):
            assert w == pytest.approx(FISH_WEIGHTS[i], rel=0.01)

    def test_mod_app_doubles_uncommon(self):
        """Discord Mod Application should double Uncommon 🟢 weight."""
        raw_karma = {}
        weights = calculate_dynamic_weights(raw_karma, True, False)
        bozo_idx = FISH_TIERS.index("Uncommon 🟢")
        base_bozo = FISH_WEIGHTS[bozo_idx]
        assert weights[bozo_idx] == pytest.approx(base_bozo * 2.0, rel=0.01)

    def test_bf_repellent_blocks_remarkable(self):
        """Boyfriend Repellent should set Remarkable 🟠 weight to zero."""
        raw_karma = {}
        weights = calculate_dynamic_weights(raw_karma, False, True)
        common_idx = FISH_TIERS.index("Remarkable 🟠")
        assert weights[common_idx] == 0.0

    def test_karma_increases_weight(self):
        """Karma should increase the weight of the associated tier."""
        raw_karma = {"Legendary 👑": 500.0}  # 500 karma = 5% bonus
        weights = calculate_dynamic_weights(raw_karma, False, False)
        god_idx = FISH_TIERS.index("Legendary 👑")
        assert weights[god_idx] > FISH_WEIGHTS[god_idx]


class TestRollFish:
    def test_roll_returns_valid_fish(self):
        """A fish roll should return a valid tier and fish name."""
        raw_karma = {}
        result = roll_fish(raw_karma, False, False, False)
        assert result["tier"] in FISH_TIERS
        assert isinstance(result["fish_name"], str)
        assert result["base_catch_pct"] > 0
        assert result["exact_catch_pct"] > 0

    def test_gamer_girl_restricts_tiers(self):
        """Gamer Girl Bathwater should restrict catches to Exceptional 🟤 and Master 🏆."""
        for _ in range(50):
            result = roll_fish({}, False, False, False, has_gamer_girl=True)
            assert result["tier"] in ["Exceptional 🟤", "Master 🏆"]


class TestCalculateCatchProbabilities:
    def test_probabilities_sum_to_reasonable_range(self):
        """Sum of all tier probabilities should be close to 100%."""
        raw_karma = {}
        weights = calculate_dynamic_weights(raw_karma, False, False)
        total_prob = 0.0
        for tier in FISH_TIERS:
            _, my_prob = calculate_catch_probabilities(tier, weights, False, False)
            species_count = len(FISH_DATA[tier]["species"])
            total_prob += my_prob * species_count
        # Total catch probability across all species should be roughly 100%
        assert 80.0 < total_prob < 120.0