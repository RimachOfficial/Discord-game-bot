#!/usr/bin/env bash
set -euo pipefail

echo "🎣 Bipbob Discord Fishing Bot — Setup"
echo "======================================"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "📋 Detected Python: $PYTHON_VERSION"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv (fast Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # shellcheck disable=SC1091
    source "$HOME/.cargo/env" 2>/dev/null || true
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "🔑 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Edit .env and add your DISCORD_TOKEN before running!"
fi

# Sync dependencies
echo "📦 Syncing dependencies..."
uv sync

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your Discord bot token"
echo "  2. Run: uv run code/main.py"
echo "  3. Invite the bot to your server"