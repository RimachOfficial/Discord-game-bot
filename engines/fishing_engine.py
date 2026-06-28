import random
from constants import FISH_TIERS, FISH_WEIGHTS, FISH_DATA

def calculate_dynamic_weights(raw_karma: dict, has_mod_app: bool, has_bf_repellent: bool) -> list[float]:
    """Calculates the personalized fishing weights based on karma and passive items."""
    dynamic_weights = []
    for i, tier in enumerate(FISH_TIERS):
        base_weight = FISH_WEIGHTS[i]
        points = raw_karma.get(tier, 0)
        
        luck_bonus_pct = points / 100.0 
        adjusted_weight = base_weight * (1 + (luck_bonus_pct / 100.0))
        
        # Apply Passives
        if has_mod_app and tier == "Bozo ⚪":
            adjusted_weight *= 2.0  # Doubles Bozo chance as a penalty
        if has_bf_repellent and tier == "Common 🔘":
            adjusted_weight = 0.0   # Blocks Common completely
            
        dynamic_weights.append(adjusted_weight)
    return dynamic_weights

def calculate_catch_probabilities(tier: str, dynamic_weights: list[float], has_copium: bool = False, has_gamer_girl: bool = False) -> tuple[float, float]:
    """Calculates the exact chance a player had to catch their specific fish vs base rates."""
    total_weight_sum = sum(dynamic_weights)
    total_base_weight_sum = sum(FISH_WEIGHTS)
    
    tier_index = FISH_TIERS.index(tier)
    my_tier_weight = dynamic_weights[tier_index]
    base_tier_weight = FISH_WEIGHTS[tier_index]
    
    species_in_tier = len(FISH_DATA[tier]["species"])
    
    # Global Base Probability
    base_tier_probability = base_tier_weight / total_base_weight_sum if total_base_weight_sum > 0 else 0
    base_catch_pct = (base_tier_probability / species_in_tier) * 100
    
    # If Gamer Girl Bathwater is active, chances are strictly 50/50 for the two tiers
    if has_gamer_girl:
        if tier in ["Your Mother 🟣", "Gay 🌈"]:
            exact_catch_pct = (0.50 / species_in_tier) * 100
        else:
            exact_catch_pct = 0.0
        return base_catch_pct, exact_catch_pct

    # Player's Karma Probability
    tier_probability = my_tier_weight / total_weight_sum if total_weight_sum > 0 else 0
    
    if has_copium:
        if tier == "God ✨":
            tier_probability = 0.50 + (0.50 * tier_probability)
        else:
            tier_probability = 0.50 * tier_probability
            
    exact_catch_pct = (tier_probability / species_in_tier) * 100
    return base_catch_pct, exact_catch_pct

def roll_fish(raw_karma: dict, has_mod_app: bool, has_bf_repellent: bool, has_copium: bool, has_gamer_girl: bool = False) -> dict:
    """Executes the core fishing RNG logic."""
    dynamic_weights = calculate_dynamic_weights(raw_karma, has_mod_app, has_bf_repellent)
    
    # Determine the tier
    if has_gamer_girl:
        tier = random.choice(["Your Mother 🟣", "Gay 🌈"])
    elif has_copium:
        if random.random() < 0.50:
            tier = "God ✨"
        else:
            tier = random.choices(FISH_TIERS, weights=dynamic_weights, k=1)[0]
    else:
        tier = random.choices(FISH_TIERS, weights=dynamic_weights, k=1)[0]
        
    fish_name = random.choice(FISH_DATA[tier]["species"])
    
    # Calculate probabilities
    base_catch_pct, exact_catch_pct = calculate_catch_probabilities(tier, dynamic_weights, has_copium, has_gamer_girl)
    
    return {
        "tier": tier,
        "fish_name": fish_name,
        "base_catch_pct": base_catch_pct,
        "exact_catch_pct": exact_catch_pct,
        "dynamic_weights": dynamic_weights
    }
