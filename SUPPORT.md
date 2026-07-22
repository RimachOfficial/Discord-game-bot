# Support

## Getting Help

If you need help with the Discord Game Bot, here are the best ways:

### Documentation

- **[README.md](README.md)** — Quick start, installation, and command reference
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — Development setup and contribution guide
- **[docs/](docs/)** — In-depth documentation on architecture, deployment, and API

### Community

- **GitHub Issues** — For bug reports and feature requests
- **GitHub Discussions** — For questions, ideas, and general discussion

### FAQ

**Q: How do I get a Discord Bot Token?**
A: Visit the [Discord Developer Portal](https://discord.com/developers/applications), create a new application, go to the Bot section, and copy the token.

**Q: The bot won't start. What do I check?**
1. Is your `.env` file set up correctly with `DISCORD_TOKEN=...`?
2. Are you using Python 3.12+?
3. Did you run `uv run main.py` (not `python main.py`)?
4. Check that your bot has the required Gateway Intents enabled.

**Q: How do I reset the database?**
Simply delete the `fishing_game.db` file and restart the bot. It will be recreated automatically.

**Q: How do I add new fish tiers?**
Edit `constants.py` — add entries to `FISH_DATA` and weights to `FISH_WEIGHTS`. The database syncs new tiers automatically.

**Q: The economy seems broken / prices are weird.**
That's by design! The market fluctuates every 5 minutes, and player actions (mass selling/buying) directly impact prices. Check `/market` for live trends.

### Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| `Unknown interaction` | Discord 3s timeout | Already handled via deferring |
| `No module named 'discord'` | Dependencies not installed | Run `uv run main.py` |
| Bot doesn't respond to commands | Wrong intents | Enable `message_content` intent in Dev Portal |
| Token errors | Bad `.env` file | Ensure no quotes around token |