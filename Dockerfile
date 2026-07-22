FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy source code
COPY . .

# Create .env from example (user must edit)
RUN cp .env.example .env 2>/dev/null || true

# Run the bot
CMD ["uv", "run", "main.py"]