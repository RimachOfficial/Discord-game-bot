# Security Policy

## Supported Versions

We currently provide security updates for the latest stable release only.

| Version | Supported          |
|---------|--------------------|
| latest  | ✅ Yes             |
| < latest| ❌ No              |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please **do not** open a public issue.

### How to Report

1. **Open a private security advisory** on GitHub:
   - Go to: `https://github.com/RimachOfficial/Discord-game-bot/security/advisories`
   - Click "New draft security advisory"
   - Provide a detailed description of the vulnerability
   - Include reproduction steps if possible

2. **Alternatively**, contact the maintainers directly via Discord.

### What to Expect

- **Acknowledgment**: Within 48 hours of reporting.
- **Investigation**: We will assess the severity and impact.
- **Fix timeline**: Critical issues are prioritized and addressed within 7 days.
- **Disclosure**: We coordinate public disclosure after a fix is released.

## Scope

Security issues include, but are not limited to:
- Remote code execution
- SQL injection
- Authentication/bypass vulnerabilities
- Token leakage (Discord bot tokens, API keys)
- Data corruption or unauthorized data access
- Denial of service

## Best Practices for Self-Hosting

- **Never commit your `.env` file** or any file containing your Discord bot token.
- Use environment variables or a secrets manager in production.
- Keep dependencies updated — especially `discord.py` and the Python runtime.
- Restrict bot permissions to the minimum required.
- Monitor your bot's logs for unusual activity.