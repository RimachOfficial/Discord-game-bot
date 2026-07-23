# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-07-23

### Changed
- **Tier names re-themed** to a new rarity system:
  - `Correction 1️⃣` → `Common ⚪`
  - `Correction 2️⃣` → `Uncommon 🟢`
  - `Correction 3️⃣` → `Unusual 🟡`
  - `Warning 1️⃣` → `Remarkable 🟠`
  - `Warning 2️⃣` → `Rare 🔵`
  - `Warning 3️⃣` → `Outstanding 🟣`
  - `Temporary Ban 1️⃣` → `Exceptional 🟤`
  - `Temporary Ban 2️⃣` → `Strange 💠`
  - `Rimach 🔴` — kept unchanged
  - `P-Ban 1️⃣` → `Master 🏆`
  - `P-Ban 2️⃣` → `Elite 💎`
  - `P-Ban 3️⃣` → `Legendary 👑`

## [0.2.0] - 2026-07-22

### Changed
- **Tier names re-themed** to align with Code of Conduct Enforcement Guidelines:
  - `Cringe 😬` → `Correction 1️⃣`
  - `Bozo ⚪` → `Correction 2️⃣`
  - `Clown 🤡` → `Correction 3️⃣`
  - `Common 🔘` → `Warning 1️⃣`
  - `Uncommon 🔵` → `Warning 2️⃣`
  - `El Bozo 🟢` → `Warning 3️⃣`
  - `Your Mother 🟣` → `Temporary Ban 1️⃣`
  - `Legendary 🟡` → `Temporary Ban 2️⃣`
  - `Gay 🌈` → `P-Ban 1️⃣`
  - `Divine ⚪🟣` → `P-Ban 2️⃣`
  - `God ✨` → `P-Ban 3️⃣`
  - `Rimach 🔴` — kept unchanged
- **All source code moved** from root to `code/` directory:
  - `code/main.py`, `code/commands.py`, `code/constants.py`, etc.
  - `code/engines/*.py` — business logic layer
  - `code/tests/*.py` — test suite
- Updated all documentation, CI, Dockerfile, and setup scripts to reflect directory restructuring

### Added
- `code/__init__.py` for proper Python package structure
- `sys.path` auto-configuration in `main.py` for seamless imports

## [0.1.0] - 2026-07-22

### Added
- Initial release of the Discord Fishing Bot
- Core fishing mechanic with 12 rarity tiers (Correction 1️⃣ to P-Ban 3️⃣)
- Dynamic market economy with live price fluctuations every 5 minutes
- Supply & demand slippage system (mass selling crashes prices, mass buying surges them)
- Karma system: release fish for permanent luck boosts
- Black Market item system with consumables and passives:
  - Copium Inhaler, Gamer Girl Bathwater, Car Battery
  - Tax Evasion Manual, Bogdanoff's Burner Phone, Mommy's Credit Card
  - Discord Mod Application, Boyfriend Repellent
- Joint-Stock Idle Crew Operations with 6 unique crew members
- Breaking News market shocks that randomly manipulate prices
- Live market chart generation (matplotlib)
- Full command set: `/fish`, `/sell`, `/sell_all`, `/buy`, `/market`, `/inventory`, `/balance`, `/karma`, `/free`, `/crew`, `/upgrade_crew`, `/shop`, `/items`, `/use`, `/toggle`, `/leaderboard`, `/chances`, `/setnews`, `/give_item`
- Secure `.env` based Discord token management via python-dotenv
- `uv`-based dependency management for fast, reproducible installs