import random
from constants import FISH_TIERS, FISH_WEIGHTS, FISH_DATA

def execute_car_battery(current_karma: list[tuple[str, int]]) -> dict:
    """
    Executes the 'Throw a Car Battery in the Ocean' logic.
    Returns caught fish and karma deductions to pass to the DB.
    """
    # 1. Pull 15 random fish using base weights
    caught_fishes = []
    fish_counts = {}
    
    for _ in range(15):
        caught_tier = random.choices(FISH_TIERS, weights=FISH_WEIGHTS, k=1)[0]
        fish_name = random.choice(FISH_DATA[caught_tier]["species"])
        caught_fishes.append({"name": fish_name, "tier": caught_tier})
        fish_counts[fish_name] = fish_counts.get(fish_name, 0) + 1
        
    catch_text = ", ".join([f"**{count}x** {name}" for name, count in fish_counts.items()])
    
    # 2. Calculate Karma deductions (total 50 points lost)
    points_to_lose = 50
    deductions = []
    
    for tier, points in current_karma:
        if points_to_lose <= 0: break
        if points > 0:
            deduct = min(points, points_to_lose)
            deductions.append((tier, deduct))
            points_to_lose -= deduct
            
    return {
        "caught_fishes": caught_fishes,
        "catch_text": catch_text,
        "karma_deductions": deductions,
        "karma_lost": 50 - points_to_lose
    }
