from constants import FISH_DATA, FISH_TO_TIER

def get_net_worth_status(total_net_worth: int) -> str:
    """Returns a title string based on a player's net worth."""
    if total_net_worth >= 1_000_000:
        return "🐋 Market Whale"
    elif total_net_worth >= 100_000:
        return "Business Mogul"
    elif total_net_worth >= 10_000:
        return "Experienced Angler"
    else:
        return "Hobbyist Fisherman"

def calculate_portfolio(wallet_cash: float, user_inv: list[tuple[str, int]], market_prices_dict: dict) -> dict:
    """Calculates the total value of the player's wallet and assets."""
    inventory_value = 0
    
    for fish_name, quantity in user_inv:
        if quantity > 0:
            tier = FISH_TO_TIER.get(fish_name)
            if tier:
                base_price = FISH_DATA[tier]["value"]
                current_price = market_prices_dict.get(tier, base_price)
                inventory_value += (current_price * quantity)

    total_net_worth = wallet_cash + inventory_value
    status = get_net_worth_status(total_net_worth)

    return {
        "wallet_cash": wallet_cash,
        "inventory_value": inventory_value,
        "total_net_worth": total_net_worth,
        "status": status
    }
