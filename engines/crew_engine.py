from constants import CREW_CATALOG

def get_upgrade_details(crew_name: str, current_level: int):
    """Calculates scaling costs and production shifts for upgrades."""
    config = CREW_CATALOG.get(crew_name)
    if not config:
        return None
        
    base_cost = config["base_cost"]
    multiplier = config["cost_multiplier"]
    base_prod = config["base_production"]
    
    # Cost formula: base * (multiplier ^ level)
    next_upgrade_cost = int(base_cost * (multiplier ** current_level))
    
    current_production = base_prod * current_level
    next_production = base_prod * (current_level + 1)
    
    return {
        "next_cost": next_upgrade_cost,
        "current_prod": current_production,
        "next_prod": next_production,
        "desc": config["description"]
    }