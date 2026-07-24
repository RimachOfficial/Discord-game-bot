# Contributing to Bipbob (Discord Game Bot)

First off, thank you for considering contributing! Every contribution — whether a bug fix, feature, typo correction, or documentation improvement — is genuinely appreciated.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Environment Setup](#development-environment-setup)
4. [Project Architecture](#project-architecture)
5. [Coding Standards](#coding-standards)
6. [Commit Message Conventions](#commit-message-conventions)
7. [Branch Naming Conventions](#branch-naming-conventions)
8. [Testing Requirements](#testing-requirements)
9. [Pull Request Process](#pull-request-process)
10. [Code Review Process](#code-review-process)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior.

## Getting Started

1. **Fork the repository** and clone your fork.
2. Read the [README](README.md) for a full project overview.
3. Check the [open issues](https://github.com/RimachOfficial/Discord-game-bot/issues) for something to work on, or open a new one.

## Development Environment Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)
- Discord Bot Token ([Discord Developer Portal](https://discord.com/developers/applications))

### Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Discord-game-bot.git
cd Discord-game-bot

# Create .env file with your token
echo "DISCORD_TOKEN=your_token_here" > .env

# Install dependencies and run
uv run code/main.py
```

### Installing Development Dependencies

```bash
uv pip install -r requirements-dev.txt
```

Or install them manually:

```bash
uv pip install ruff pytest pytest-asyncio mypy
```

## Project Architecture

This project follows a strict **3-Tier Architecture**:

```
┌─────────────────────────────────────┐
│  Interface Layer (Cogs)             │
│  code/commands.py, code/market.py.. │
├─────────────────────────────────────┤
│  Business Logic Layer (Engines)     │
│  code/engines/*.py                  │
├─────────────────────────────────────┤
│  Data Access Layer                  │
│  code/database.py                   │
└─────────────────────────────────────┘
```

- **Interface Layer**: Discord interactions, embeds, UI — no math or game logic.
- **Engine Layer**: All game mechanics, calculations, and decision-making — pure Python.
- **Data Layer**: SQLite CRUD operations — no business logic.

**Never mix concerns.** If you need to add a game mechanic, add it to an engine. If you need to fetch/store data, add it to `database.py`.

## Coding Standards

- **Python version**: 3.12+
- **Style**: [PEP 8](https://peps.python.org/pep-0008/) enforced via [ruff](https://docs.astral.sh/ruff/)
- **Type hints**: Required for all function signatures and public methods.
- **Docstrings**: Google-style docstrings for all public functions and classes.
- **Line length**: 100 characters maximum.
- **Naming**:
  - `snake_case` for functions, methods, variables
  - `PascalCase` for classes
  - `UPPER_SNAKE_CASE` for constants

### Ruff Configuration

The project uses ruff with the following rules enabled by default:
- `E`, `F` (pycodestyle + pyflakes)
- `I` (isort)
- `N` (pep8-naming)
- `UP` (pyupgrade)
- `B` (bugbear)

Run linting:
```bash
ruff check .
```

## Commit Message Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>

[optional body]
[optional footer(s)]
```

### Types

| Type       | Usage                                      |
|------------|--------------------------------------------|
| `feat`     | A new feature                              |
| `fix`      | A bug fix                                  |
| `docs`     | Documentation only changes                 |
| `refactor` | Code change that neither fixes nor adds    |
| `perf`     | Performance improvement                    |
| `test`     | Adding or updating tests                   |
| `chore`    | Build process, tooling, dependencies       |

### Examples

```
feat(market): add dynamic price floor for sell_all
fix(fishing): correct karma scaling calculation for god tier
docs(readme): add docker deployment section
refactor(database): consolidate bulk market update methods
```

## Branch Naming Conventions

- `feat/<short-description>` — New features
- `fix/<short-description>` — Bug fixes
- `docs/<short-description>` — Documentation
- `refactor/<short-description>` — Refactoring
- `chore/<short-description>` — Maintenance

Use hyphens as separators: `feat/add-trade-command`

## Testing Requirements

- **New features** must include at least one basic test covering the core logic.
- **Bug fixes** must include a test that reproduces the bug.
- Tests live in the `tests/` directory and mirror the project structure.
- We use `pytest` as the test runner.

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing
```

## Pull Request Process

1. **Create an issue** describing what you want to do (unless it's a trivial fix).
2. **Create a branch** from `main` following the naming convention.
3. **Write your code**, adhering to all standards above.
4. **Run tests** and ensure they pass.
5. **Run linting**: `ruff check .`
6. **Open a Pull Request** against `main` using the PR template.
7. **Ensure CI passes** (lint + tests).
8. **Request a review** from a maintainer.
9. **Address feedback** promptly.

### PR Checklist

Before submitting:

- [ ] Code follows project coding standards
- [ ] Type hints are present for all new functions
- [ ] Tests pass (`pytest`)
- [ ] Linting passes (`ruff check .`)
- [ ] No unnecessary debug code, print statements, or commented-out code
- [ ] Documentation updated if needed (README, docs/, docstrings)

## Code Review Process

- At least one maintainer review is required.
- Reviews focus on: correctness, architecture adherence, test coverage, and readability.
- All discussions must be resolved before merging.

## Questions?

Open a [Discussion](https://github.com/RimachOfficial/Discord-game-bot/discussions) or join the community. We're happy to help you get started!