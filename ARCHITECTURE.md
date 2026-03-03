# Platform Architecture (Phase 1)

This project is now split into modular platform components while keeping `dashboard.py` as the stable entrypoint.

## Modules

- `portfolio_platform/config.py`
  - central constants and market mappings
- `portfolio_platform/data.py`
  - live market/news data adapters (`yfinance`)
- `portfolio_platform/portfolio.py`
  - portfolio persistence + holdings table/domain model
- `portfolio_platform/analytics.py`
  - risk, exposure, valuation, optimization math

## Runtime wiring

`dashboard.py` contains UI/pages and a compatibility bridge that routes core logic to platform modules.

This keeps behavior stable during migration and enables future separation into:
- API/service layer
- strategy/signal engines
- broker/execution adapters
- background jobs

## Rollback

If needed, ask to restore **version 3** from:
- `/Users/AlexandreLiaudet/Documents/New project/dashboard_version3.py`
