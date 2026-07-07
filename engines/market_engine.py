import random
import math
from constants import FISH_DATA

chance_to_trigger_shock: float = 0.15  # chance per market update loop
weight_floor: float = 0.01
weight_ceiling: float = 99999999.0


change_percent_up = 0.2
change_percent_down = -0.2


def calculate_market_fluctuations(current_prices: list[tuple[str, float]]) -> dict[str, float]:
    """Calculates normal market fluctuations. Returns a dict of tier -> new_price."""
    new_prices = {}
    for tier, current_price in current_prices:
        base_price = float(FISH_DATA[tier]["value"])
        current_price = float(current_price)
        
        change_percent = random.uniform(change_percent_down, change_percent_up)
        new_price = current_price * (1 + change_percent)
        
        # Enforce limits safely using float checks
        new_price = max(base_price * weight_floor, min(new_price, base_price * weight_ceiling))
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


def calculate_sell_impact(tier: str, quantity_sold: float, current_unit_price: float, has_tax_evasion: bool = False, has_short_squeeze: bool = False) -> tuple[float, float, float]:
    """Calculates payout with slippage and safely applies black market modifiers."""
    quantity_sold = float(quantity_sold)
    current_unit_price = float(current_unit_price)
    base_price = float(FISH_DATA[tier]["value"])
    hard_floor = base_price * weight_floor
    
    # 1. Calculate NORMAL drop for the player's payout
    normal_price_drop = quantity_sold * (base_price * 0.005)
    normal_new_price = max(hard_floor, current_unit_price - normal_price_drop)
    
    # 🌟 ANTI-EXPLOIT: Pay them the average value of the NORMAL crash
    average_unit_price = (current_unit_price + normal_new_price) / 2.0
    total_payout = average_unit_price * quantity_sold
    
    # 2. Calculate MALICIOUS drop for the global market
    if has_short_squeeze:
        market_price_drop = normal_price_drop * 3.0
    else:
        market_price_drop = normal_price_drop
        
    market_new_price = max(hard_floor, current_unit_price - market_price_drop)
    
    # 3. Handle Tax Evasion
    if has_tax_evasion:
        actual_drop = 0.0
        final_market_price = current_unit_price # The price doesn't change!
    else:
        actual_drop = current_unit_price - market_new_price
        final_market_price = market_new_price
    
    return total_payout, actual_drop, final_market_price


def calculate_buy_impact(tier: str, quantity_bought: float, current_unit_price: float, player_cash: float, has_credit_card: bool = False) -> dict:
    """Calculates cost using slippage (average price), price bumps, and checks affordability."""
    quantity_bought = float(quantity_bought)
    current_unit_price = float(current_unit_price)
    player_cash = float(player_cash)
    base_price = float(FISH_DATA[tier]["value"])
    
    # Calculate how much the market will react BEFORE charging the player
    if has_credit_card:
        price_bump = 0.0
    else:
        price_bump = quantity_bought * (base_price * 0.005)
    
    max_allowed_price = base_price * weight_ceiling
    new_price = min(max_allowed_price, current_unit_price + price_bump)
    actual_bump = new_price - current_unit_price
    
    # 🌟 ANTI-EXPLOIT: Calculate the average slippage price
    average_unit_price = (current_unit_price + new_price) / 2.0
    total_cost = average_unit_price * quantity_bought
    
    # Now check if they can afford the dynamic cost
    if player_cash < total_cost:
        return {"success": False, "shortfall": total_cost - player_cash}
    
    return {
        "success": True, 
        "total_cost": total_cost, 
        "actual_bump": actual_bump,
        "new_price": new_price
    }


def calculate_sell_all_impact(user_inv: list[tuple[str, float]], market_prices: dict[str, float], has_tax_evasion: bool, has_short_squeeze: bool) -> dict:
    from constants import FISH_TO_TIER, FISH_DATA
    import math
    
    total_payout = 0.0
    total_fish_sold = 0.0
    
    # 🌟 STEP 1: Aggregate all individual fish species into their primary Tiers first
    tier_quantities = {}
    for fish_name, quantity in user_inv:
        quantity = float(quantity)
        if quantity > 0:
            tier = FISH_TO_TIER.get(fish_name)
            if tier:
                tier_quantities[tier] = tier_quantities.get(tier, 0.0) + quantity

    sanitized_drops = {}
    impacted_tiers_text = []

    # 🌟 STEP 2: Calculate the slippage for the entire combined tier at once!
    for tier, total_quantity in tier_quantities.items():
        base_price = float(FISH_DATA[tier]["value"])
        current_price = float(market_prices.get(tier, base_price))
        hard_floor = base_price * weight_floor
        
        # 1. Calculate NORMAL drop for the player's payout
        normal_price_drop = total_quantity * (base_price * 0.005)
        normal_new_price = max(hard_floor, current_price - normal_price_drop)
        
        # Slippage Payout (Average price across the NORMAL crash)
        average_unit_price = (current_price + normal_new_price) / 2.0
        total_payout += (average_unit_price * total_quantity)
        total_fish_sold += total_quantity
        
        # 2. Calculate MALICIOUS drop for the global market
        if has_short_squeeze:
            market_price_drop = normal_price_drop * 3.0
        else:
            market_price_drop = normal_price_drop
            
        market_new_price = max(hard_floor, current_price - market_price_drop)
        
        # 3. Record the damage for the market update
        if not has_tax_evasion:
            actual_drop = current_price - market_new_price
            if actual_drop > 0:
                sanitized_drops[tier] = actual_drop
                drop_display = f"{actual_drop:,.2f}" if actual_drop < 1e15 else f"{actual_drop:.4e}"
                
                if math.isclose(market_new_price, hard_floor) or market_new_price <= hard_floor:
                    impacted_tiers_text.append(f"**{tier}**: -${drop_display} *(📉 CRASHED TO FLOOR!)*")
                else:
                    impacted_tiers_text.append(f"**{tier}**: -${drop_display}")

    return {
        "total_payout": total_payout,
        "total_fish_sold": total_fish_sold,
        "sanitized_drops": sanitized_drops,
        "impacted_tiers_text": impacted_tiers_text
    }