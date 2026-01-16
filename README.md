# Merkato

Minimal, python-based, stock market monitoring bot using GitHub and email notifications.

The **real goal** of this small project is to demonstrate how much can be achieved with just a free GitHub repo.

* Automated tasks execution via GitHub Actions.
* Storage of processed data in the GitHub repo itself, committed by the GitHub Actions bot.
* Email notifications: Gmail API (free)

## Get started

### Prerequisites

- Python 3.11+
- [UV](https://docs.astral.sh/uv/)

### Setup

1. Install project dependencies: `uv sync`.
2. Configure env variables in GitHub workflows (`.github/workflows/`) and in the repository.

```
EMAIL_SENDER=
EMAIL_PASSWORD=
EMAIL_RECIPIENT=
EMAIL_SMTP_SERVER=
EMAIL_SMTP_PORT=
```
3. Configure stocks via `config.json`.

```json
{
  "stocks": [
    {
      "symbol": "SPY",
      "target_price": 450.00
    },
    {
      "symbol": "AAPL",
      "target_price": 180.00
    }
  ]
}
```

**Stock Symbols:** Use Yahoo Finance ticker symbols (e.g., SPY, QQQ, AAPL, MSFT, VTI).
By default, `stock_monitor.py` runs every hour, while `weekly_report.py` runs every Thursday at 08:00 UTC.

# Development

```bash
# Format code
make format

# Lint code
make lint
```

# Testing

```bash
# Run integration tests
uv run it

# Run the actual monitor (will send emails)
uv run stock-monitor

# Run weekly reporting (will send emails)
uv run weekly-report
```

Or use Makefile targets, see `make help` to list all targets.