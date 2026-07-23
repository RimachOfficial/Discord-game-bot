# Architecture

Bipbob follows a strict **3-Tier Architecture (Separation of Concerns)**:

```
┌───────────────────────────────────────────────────┐
│                INTERFACE LAYER                    │
│  (Discord Cogs — code/commands.py, ...)           │
│                                                   │
│  • Parses Discord slash commands & interactions   │
│  • Formats responses as Discord Embeds            │
│  • Delegates all logic to engines                 │
│  • Zero math, zero game logic                     │
├───────────────────────────────────────────────────┤
│              BUSINESS LOGIC LAYER                 │
│  (Engines — code/engines/*.py)                    │
│                                                   │
│  • fishing_engine.py: RNG, karma scaling, items   │
│  • market_engine.py: fluctuations, shocks, trades │
│  • economy_engine.py: portfolios, net worth       │
│  • item_engine.py: item effects & purchases       │
│  • crew_engine.py: crew leveling & payroll math   │
│  • market_chart_engine.py: matplotlib chart gen   │
├───────────────────────────────────────────────────┤
│               DATA ACCESS LAYER                   │
│  (code/database.py)                               │
│                                                   │
│  • Pure SQLite CRUD operations                    │
│  • No business logic, no math, no item configs    │
│  • Serves as a clean abstraction layer            │
└───────────────────────────────────────────────────┘
```

## Data Flow

```
User Command (/fish)
       │
       ▼
Interface Layer (code/commands.py)
  ┌─ Parses Discord interaction
  └─ Calls fishing_engine.roll_fish()
       │
       ▼
Business Logic Layer (code/engines/fishing_engine.py)
  ┌─ Reads karma from DB via database.py
  ├─ Applies passive item effects
  ├─ Rolls random tier & species
  └─ Returns result dict
       │
       ▼
Data Access Layer (code/database.py)
  ┌─ Saves caught fish to inventory
  └─ Returns market prices for display
       │
       ▼
Interface Layer (code/commands.py)
  ┌─ Builds Discord Embed
  └─ Sends response to Discord
```

## Key Design Decisions

- **SQLite for storage** — lightweight, zero-config, file-based. Perfect for small-to-medium Discord bots.
- **uv for dependency management** — faster than pip, deterministic lock files.
- **matplotlib for charts** — generates live market trend images server-side.
- **All prices are floats** — to handle hyper-scaled economies without integer overflow.
- **Deferred responses** — every command uses `await interaction.response.defer()` to avoid Discord's 3-second timeout.
- **All source code lives under `code/`** — clean project root with only configuration and documentation.