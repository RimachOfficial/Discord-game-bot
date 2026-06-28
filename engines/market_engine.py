import random
from constants import FISH_DATA

chance_to_trigger_shock: float = 0.30  # chance per market update loop

def calculate_market_fluctuations(current_prices: list[tuple[str, int]]) -> dict[str, int]:
    """Calculates normal market fluctuations. Returns a dict of tier -> new_price."""
    new_prices = {}
    for tier, current_price in current_prices:
        base_price = FISH_DATA[tier]["value"]
        
        change_percent = random.uniform(-0.15, 0.20)
        new_price = int(current_price * (1 + change_percent))
        
        # Enforce limits (40% floor, 250% ceiling)
        new_price = max(int(base_price * 0.4), min(new_price, int(base_price * 2.5)))
        new_prices[tier] = new_price
        
    return new_prices

def generate_market_shock() -> dict | None:
    """Generates a random market shock event. Returns event dict or None."""
    if random.random() < chance_to_trigger_shock: 
        return random.choice([
            {"msg": "⚠️ **ANCHOVY INFLATION!** Low tier fish prices skyrocketed!", "tier": "Bozo ⚪", "mult": 1.8},
            {"msg": "🐋 **WHALE CONSERVATION ACT!** 'Your Mother' prices doubled!", "tier": "Your Mother 🟣", "mult": 2.0},
            {"msg": "🦈 **SHARK WEEK!** Apex predators are in high demand!", "tier": "Rimach 🔴", "mult": 2.2},
            {"msg": "🦠 **RED TIDE OUTBREAK!** Common populations decimated, prices surging!", "tier": "Common 🔘", "mult": 1.6},
            {"msg": "👼 **CULT AWAKENING!** Fanatics are hoarding God fish! Prices to the moon!", "tier": "God ✨", "mult": 2.5},
            {"msg": "💎 **BILLIONAIRE CRAZE!** Divine fish are the new luxury status symbol!", "tier": "Divine ⚪🟣", "mult": 2.1},
            {"msg": "📉 **CRYPTO CRASH!** Rich players panic-selling God fish!", "tier": "God ✨", "mult": 0.4},
            {"msg": "🗑️ **GREAT GARBAGE PATCH!** The waters are flooded with trash! Bozo prices tanking!", "tier": "Bozo ⚪", "mult": 0.5},
            {"msg": "🎣 **OVERFISHING!** The market is flooded with Common fish! Prices plummeting!", "tier": "Common 🔘", "mult": 0.6},
            {"msg": "🚫 **PIRATE RAID!** Black market fish dumps are crashing the Legendary tier!", "tier": "Legendary 🟡", "mult": 0.5},
            {"msg": "🧪 **LAB GROWN MEAT!** Fake shark fin soup is crashing the Rimach market!", "tier": "Rimach 🔴", "mult": 0.4}
        ])
    return None

def calculate_sell_impact(tier: str, quantity_sold: int, current_unit_price: int) -> tuple[int, int]:
    """Calculates payout and strictly safe price drops based on quantity sold."""
    total_payout = quantity_sold * current_unit_price
    base_price = FISH_DATA[tier]["value"]
    
    # Drop by 0.5% of BASE value per unit sold
    price_drop = int(quantity_sold * (base_price * 0.005))
    
    # Calculate the exact new price considering the hard floor (40%)
    hard_floor = int(base_price * 0.4)
    new_price = max(hard_floor, current_unit_price - price_drop)
    
    # Calculate the *actual* drop amount (it might be less than price_drop if hitting floor)
    actual_drop = current_unit_price - new_price
    
    return total_payout, actual_drop, new_price

def calculate_buy_impact(tier: str, quantity_bought: int, current_unit_price: int, player_cash: int, has_credit_card: bool = False) -> dict:
    """Calculates cost, price bumps, and check affordability."""
    total_cost = current_unit_price * quantity_bought
    
    if player_cash < total_cost:
        return {"success": False, "shortfall": total_cost - player_cash}
        
    base_price = FISH_DATA[tier]["value"]
    
    if has_credit_card:
        price_bump = 0
    else:
        # Surge by 0.5% of BASE value per unit bought
        price_bump = int(quantity_bought * (base_price * 0.005))
    
    # Enforce absolute max market ceiling (2.5x base)
    max_allowed_price = int(base_price * 2.5)
    new_price = min(max_allowed_price, current_unit_price + price_bump)
    
    # Calculate *actual* bump
    actual_bump = new_price - current_unit_price
    
    return {
        "success": True, 
        "total_cost": total_cost, 
        "actual_bump": actual_bump,
        "new_price": new_price
    }

def calculate_sell_all_impact(user_inv: list[tuple[str, int]], market_prices: dict[str, int], has_tax_evasion: bool, has_short_squeeze: bool) -> dict:
    from constants import FISH_TO_TIER, FISH_DATA
    
    total_payout = 0
    total_fish_sold = 0
    tier_drops = {}
    
    for fish_name, quantity in user_inv:
        if quantity > 0:
            tier = FISH_TO_TIER.get(fish_name)
            if not tier: continue 
            
            base_price = FISH_DATA[tier]["value"]
            current_price = market_prices.get(tier, base_price)
            
            total_payout += (current_price * quantity)
            total_fish_sold += quantity
            
            if not has_tax_evasion:
                price_drop = int(quantity * (base_price * 0.005))
                if has_short_squeeze:
                    price_drop *= 3 # Force a massive crash on the sold tiers
                tier_drops[tier] = tier_drops.get(tier, 0) + price_drop

    sanitized_drops = {}
    impacted_tiers_text = []

    for tier, raw_drop in tier_drops.items():
        base_price = FISH_DATA[tier]["value"]
        old_price = market_prices.get(tier, base_price)
        
        hard_floor = int(base_price * 0.4)
        new_price = max(hard_floor, old_price - raw_drop)
        actual_drop = old_price - new_price
        
        if actual_drop > 0:
            sanitized_drops[tier] = actual_drop
            if new_price == 0:
                impacted_tiers_text.append(f"**{tier}**: -${actual_drop:,} *(📉 CRASHED TO ZERO!)*")
            else:
                impacted_tiers_text.append(f"**{tier}**: -${actual_drop:,}")

    return {
        "total_payout": total_payout,
        "total_fish_sold": total_fish_sold,
        "sanitized_drops": sanitized_drops,
        "impacted_tiers_text": impacted_tiers_text
    }
