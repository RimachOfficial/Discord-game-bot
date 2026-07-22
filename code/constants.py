from discord.app_commands import Choice

FISH_DATA = {
    "Correction 1️⃣": {
        "value": 5,
        "species": ["Skibidi Salmon", "Discord Modfish", "Fedora Carp", "Brainrot Bass", "UwUfish"],
        "gif": "https://cdn.discordapp.com/attachments/1112776516460347433/1524463913461223524/ac2573a1fd5cf32e107c18a4b240e725.gif?ex=6a507fe8&is=6a4f2e68&hm=3e1a10dbced9a83c71201fdf101b006b24d71d5034916838948e297d0909c977&"
    },
    "Correction 2️⃣": {
        "value": 10,
        "species": ["Old Boot", "Wet Cardboard", "Plastic Bottle"],
        "gif": "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExaXZycDRqY3k1cHBiOWhmbGxmNTN3bTI4cmpybXZmM25xN24zaXRiYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/n6z0sYdK2qIUI6Uf8g/giphy.gif"
    },
    "Correction 3️⃣": {
        "value": 15,
        "species": ["Clownfish", "Squeaky Puffer", "Honking Shark", "Juggling Eel"],
        "gif": "https://cdn.discordapp.com/attachments/1112776516460347433/1524462773306921100/toontown-clown-fish.gif?ex=6a507ed8&is=6a4f2d58&hm=c9d0be378ef41c56f59db66def6bc5b581837796487cc9fa821357574dd1748a&"
    },
    "Warning 1️⃣": {
        "value": 25,
        "species": ["Atlantic Cod", "River Carp", "Pond Tilapia"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZHN6amt4Y3JwdmM2MWx4aTFkY21wNTFoeXZsa2hsanhueXlsZ3kzZSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/lPuW5AlR9AeWzSsIqi/giphy.gif"
    },
    "Warning 2️⃣": {
        "value": 50,
        "species": ["Sockeye Salmon", "Rainbow Trout", "Red Snapper"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZHN6amt4Y3JwdmM2MWx4aTFkY21wNTFoeXZsa2hsanhueXlsZ3kzZSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/7eVp9MHlNI90c/giphy.gif"
    },
    "Warning 3️⃣": {
        "value": 100,
        "species": ["Mako Shark (1,221 lbs)", "Hammerhead Shark (1,280 lbs)", "Sixgill Shark (1,298 lbs)"],
        "gif": "https://media.tenor.com/x8v1oNUOmg4AAAAM/clown-makeup.gif"
    },
    "Temporary Ban 1️⃣": {
        "value": 500,
        "species": ["Whale Shark (41,000 lbs - Absolute Unit)"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3aTQ5NHBucjV0MndsaG50a3dvbHFwczgzN3pheW1lMGxtbXZtcGticSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/dJeVcFUo10kcU/giphy.gif"
    },
    "Temporary Ban 2️⃣": {
        "value": 1000,
        "species": ["Pacific Blue Marlin (1,376 lbs)", "Atlantic Blue Marlin (1,402 lbs)", "Black Marlin (1,560 lbs)"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3c2RjNXlldjcwYndxeDVycTgwZjU5dHFucmV2bXZrNXI5eDFzY2swZSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/wWXH3OgwPGXlJdZw26/giphy.gif"
    },
    "Rimach 🔴": {
        "value": 5000,
        "species": ["Greenland Shark (1,708 lbs)", "Tiger Shark (1,785 lbs)"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZnVreXRoNHo5MGQ3bzljeHN1ODZ6ODQ0OG0zYnd5YjE3NjNremNieCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ZNLKLh8vlfRrWnL4mj/giphy.gif"
    },
    "P-Ban 1️⃣": {
        "value": 20000,
        "species": ["Blobfish 👁️👄👁️", "Ocean Sunfish 🐋", "Goblin Shark 👺"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaWx4MHpnM2J0enZpYmt3YnBuNzlvdDVxbDNoeGdhc2dyajVkYThmdyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/W5NrtmMTEBP3pTKr1L/giphy.gif"
    },
    "P-Ban 2️⃣": {
        "value": 100000,
        "species": ["Great White Shark (2,664 lbs - Alfred Dean Record)"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3ajhtZWk0NmhwMXlzZngxM2J2YXp5MDMxbDJmczN0YTIyN29leGV0eSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ai0YLvAS4kbTy/giphy.gif"
    },
    "P-Ban 3️⃣": {
        "value": 1000000,
        "species": ["The Legendary Kraken 🦑", "Poseidon's Goldfish 🔱"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdnhjdTljdTZtYXVvMTA0Y3p6N2NpYmxhZzUxamJlNTN3YzEyazNoZSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/NWqFfIIxiJyAE/giphy.gif"
    }
}

FISH_TIERS = list(FISH_DATA.keys())
FISH_WEIGHTS = [24, 18, 14, 12, 10, 8, 7, 5, 1.5, 0.4, 0.09, 0.01]

FISH_VALUES = {}
for tier, info in FISH_DATA.items():
    for fish in info["species"]:
        FISH_VALUES[fish] = info["value"]

FISH_TO_TIER = {species: tier for tier, info in FISH_DATA.items() for species in info["species"]}

ITEM_CHOICES = [
    Choice(name="🔋 Car Battery", value="🔋 Throw a Car Battery in the Ocean"),
    Choice(name="🍼 Copium Inhaler", value="🍼 Copium Inhaler"),
    Choice(name="🧼 Gamer Girl Bathwater", value="🧼 Gamer Girl Bathwater"),
    Choice(name="📱 Bogdanoff's Burner Phone", value="📱 Bogdanoff's Burner Phone"),
    Choice(name="📄 Tax Evasion Manual", value="📄 Tax Evasion Manual"),
    Choice(name="💳 Mommy's Credit Card", value="💳 Mommy's Credit Card"),
    Choice(name="♻️ Discord Mod Application", value="♻️ Discord Mod Application"),
    Choice(name="🧢 Boyfriend Repellent", value="🧢 The \"I Have a Boyfriend\" Repellent")
]

ITEM_CATALOG = {
    "⚠️ Illegal Fishing Gear": {
        "🔋 Throw a Car Battery in the Ocean": {
            "type": "Consumable",
            "price": 10000,
            "desc": "Instantly pulls 15 random fish into your bucket, but you lose 50 Karma because the ocean ecosystem absolutely hates you for it."
        },
        "🍼 Copium Inhaler": {
            "type": "Consumable",
            "price": 100000,
            "desc": "makes you have +1% chance plus karma to catch a `P-Ban 3️⃣` tier for exactly one cast. If you still catch an `Old Boot`, the bot publicly pings you to laugh at your horrible luck."
        },
        "🧼 Gamer Girl Bathwater": {
            "type": "Lure",
            "price": 50000,
            "desc": "Guarantees your next 3 catches will exclusively be from the `Temporary Ban 1️⃣` or `P-Ban 1️⃣` tiers."
        }
    },
    "📉 Market Manipulation": {
        "📱 Bogdanoff's Burner Phone": {
            "type": "Consumable",
            "price": 50000,
            "desc": "\"He bought? Crash it.\" Force a targeted Market Crash on a specific tier *after* you sell, ruining the price for everyone else on the server."
        },
        "📄 Tax Evasion Manual": {
            "type": "Passive",
            "price": 2500000,
            "desc": "Your `/sell_all` dumps no longer trigger market crashes because you technically routed the sale through an offshore Cayman Islands account."
        },
        "💳 Mommy's Credit Card": {
            "type": "Passive",
            "price": 5000000,
            "desc": "Using `/buy` no longer triggers a \"Price Surge\" penalty. The market just accepts the swiped card, allowing you to hoard endlessly."
        }
    },
    "🗑️ Server Degeneracy": {
        "♻️ Discord Mod Application": {
            "type": "Passive",
            "price": 500000,
            "desc": "Makes you legally immune to catching `Wet Cardboard`. However, it doubles your chance of catching `Correction 2️⃣`."
        },
        "🧢 The \"I Have a Boyfriend\" Repellent": {
            "type": "Passive",
            "price": 1000000,
            "desc": "Completely blocks the `Warning 1️⃣` tier from spawning. You will either catch total trash or something incredibly rare, with zero in-between."
        }
    }
}

CREW_CATALOG = {
    "Rimach The Fisherman": {
        "base_cost": 1000,
        "cost_multiplier": 1.5,
        "assigned_tiers": ["Correction 2️⃣", "Warning 1️⃣"],
        "base_production": 3.0,
        "description": "The founding father and supreme architect. Coding this bot while his internet dies every 15 minutes. Pure dedication."
    },
    "Ka2lina": {
        "base_cost": 1500,
        "cost_multiplier": 1.4,
        "assigned_tiers": ["Correction 1️⃣", "Correction 3️⃣"],
        "base_production": 5.0,
        "description": "Future kindergarten teacher currently testing her patience limits by dealing with Rimach. She spends 99% of her lecture hours glued to her phone screen. Has huge... amount of unread notifications and zero screen time boundaries."
    },
    "Jim The Wolf": {
        "base_cost": 2500,
        "cost_multiplier": 1.6,
        "assigned_tiers": ["Warning 2️⃣", "Warning 3️⃣"],
        "base_production": 1.5,
        "description": "The youngest playtester. Gave him 1-second cooldown privileges once and he immediately developed a severe dopamine addiction. Needs supervision."
    },
    "Magician Oceans Red": {
        "base_cost": 7500,
        "cost_multiplier": 1.7,
        "assigned_tiers": ["Temporary Ban 1️⃣", "Temporary Ban 2️⃣"],
        "base_production": 0.8,
        "description": "Professional master of rage baiting. The team has a toxic love-hate relationship with him. Catches fish just to insult them until they bite."
    },
    "Secret the airplane": {
        "base_cost": 20000,
        "cost_multiplier": 1.8,
        "assigned_tiers": ["Rimach 🔴", "P-Ban 1️⃣"],
        "base_production": 0.3,
        "description": "An actual pilot-in-training with zero conversational filter. Will crash your relationship status faster than a Boeing 737."
    },
    "Katratzoglou": {
        "base_cost": 75000,
        "cost_multiplier": 2.0,
        "assigned_tiers": ["P-Ban 2️⃣", "P-Ban 3️⃣"],
        "base_production": 0.1,
        "description": "Cinema student who went missing to go hard-stuck in MOBA games. Rarely logs in unless there's a gacha banner he can swipe his credit card on."
    }
}