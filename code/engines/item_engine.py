from engines import fishing_engine

def execute_car_battery(current_karma: list[tuple[str, float]]) -> dict:
    """
    Executes the 'Throw a Car Battery in the Ocean' logic.
    Requires at least 50 total karma across all tiers to use.
    """
    # 1. Safely parse the DB data into a dictionary once
    raw_karma = dict(current_karma)
    
    # 2. Sum up the karma using the safe dictionary values
    total_available_karma = sum(float(points) for points in raw_karma.values())
    
    # Check if the player has enough karma to use the item
    if total_available_karma < 50.0:
        return {
            "success": False, 
            "msg": "❌ The ocean is already dead. You don't even have 50 Karma left to lose!"
        }

    caught_fishes = []
    fish_counts = {}
    
    # 3. Roll the 15 fish
    for _ in range(15):
        result = fishing_engine.roll_fish(
            raw_karma=raw_karma, 
            has_mod_app=False, 
            has_bf_repellent=False, 
            has_copium=False, 
            has_gamer_girl=False
        )
        
        caught_tier = result["tier"]
        fish_name = result["fish_name"]
        
        caught_fishes.append({"name": fish_name, "tier": caught_tier})
        fish_counts[fish_name] = fish_counts.get(fish_name, 0) + 1
        
    catch_text = ", ".join([f"**{count}x** {name}" for name, count in fish_counts.items()])
    
    # 4. Calculate the 50 point deduction using the safe dictionary items
    points_to_lose = 50.0
    deductions = []
    
    for tier, points in raw_karma.items():
        points = float(points)
        if points_to_lose <= 0.0: 
            break
            
        if points > 0.0:
            deduct = min(points, points_to_lose)
            deductions.append((tier, deduct))
            points_to_lose -= deduct
            
    return {
        "success": True,
        "caught_fishes": caught_fishes,
        "catch_text": catch_text,
        "karma_deductions": deductions,
        "karma_lost": 50.0 - points_to_lose
    }

def calculate_item_purchase(item_name: str, player_cash: int, owned_count: int) -> dict:
    """
    Validates if a player can buy an item based on cash and type limits.
    """
    from constants import ITEM_CATALOG
    
    # 1. Find item details
    item_info = None
    for category, items in ITEM_CATALOG.items():
        if item_name in items:
            item_info = items[item_name]
            break
            
    if not item_info:
        return {"success": False, "msg": f"❌ Item `{item_name}` not found in the catalog."}
        
    price = item_info.get("price", 999999999) # fallback
    item_type = item_info.get("type", "Consumable")
    
    # 2. Check Limits
    if item_type == "Passive" and owned_count >= 1:
        return {"success": False, "msg": f"❌ You already own **{item_name}**! Passives do not stack."}
        
    if player_cash < price:
        shortfall = price - player_cash
        return {"success": False, "msg": f"💸 You need **${shortfall:,}** more to buy **{item_name}**!"}
        
    return {
        "success": True,
        "price": price,
        "msg": f"✅ Successfully purchased **{item_name}** for `${price:,}`!"
    }

def toggle_item_usage(item_name: str, owned_count: int, currently_disabled: bool) -> dict:
    """
    Validates and toggles the enabled/disabled state of a passive item.
    Constraints:
      - Only Passives can be toggled.
      - The player must own the item.
    Returns the new state and a message for the interface layer.
    """
    from constants import ITEM_CATALOG

    # 1. Find item in catalog
    item_info = None
    for category, items in ITEM_CATALOG.items():
        if item_name in items:
            item_info = items[item_name]
            break

    if not item_info:
        return {"success": False, "msg": f"❌ Item `{item_name}` not found in the catalog."}

    item_type = item_info.get("type", "Consumable")

    # 2. Only Passives can be toggled
    if item_type != "Passive":
        return {"success": False, "msg": f"❌ **{item_name}** is a *{item_type}* — only Passive items can be toggled!"}

    # 3. Must own the item
    if owned_count < 1:
        return {"success": False, "msg": f"❌ You don't own **{item_name}**!"}

    # 4. Flip state
    new_state_disabled = not currently_disabled
    if new_state_disabled:
        return {
            "success": True,
            "new_disabled": True,
            "msg": f"🔴 **{item_name}** has been **disabled**. Its effect is now inactive."
        }
    else:
        return {
            "success": True,
            "new_disabled": False,
            "msg": f"🟢 **{item_name}** has been **enabled**. Its effect is now active."
        }

