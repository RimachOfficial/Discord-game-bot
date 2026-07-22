# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-22

### Added
- Initial release of the Discord Fishing Bot
- Core fishing mechanic with 12 rarity tiers (Bozo ⚪ to God ✨)
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