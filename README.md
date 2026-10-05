# NILE (PTY) LTD - Refactored Equipment Rental & Escrow Platform

This project is a refactored version of the original NILE CLI app. It keeps the same business concept but replaces the fragile JSON-only prototype with a stronger structure based on:

- SQLite persistence
- dataclass-based models
- clearer escrow calculation logic
- booking lifecycle tracking
- creator verification workflow
- exportable backup data
- automated tests for critical flows

## Features

- View equipment catalog
- Book equipment with escrow hold
- View all bookings
- Verify site photos and release escrow
- Export a backup JSON file
- Persistent storage using SQLite

## Project structure

- `app.py` — main CLI entry point
- `nile_app/config.py` — business constants and config
- `nile_app/models.py` — dataclasses for equipment, creators, and bookings
- `nile_app/storage.py` — SQLite initialization and backups
- `nile_app/services.py` — core business logic and handling
- `tests/test_services.py` — business logic verification tests

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Run tests

```bash
pytest -q
```

## Notes

The code intentionally preserves the original NILE business rules while making them easier to validate and extend for future production use.
