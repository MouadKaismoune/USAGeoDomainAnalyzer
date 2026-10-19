# USAGeoDomainAnalyzer

**USA Geo Domain Analyzer** — a desktop application built with **Python + PySide6** that checks domain availability across US cities for your target niches.

## Features

- Modern **frameless window** with rounded corners, soft shadow, drag-from-header, and flexible minimize/maximize
- **Collapsible sidebar** with navigation groups (Main / Analysis / System) and an active-page indicator
- **Light / Dark themes** with a toggle button in the header
- **8 pages**: Dashboard, Cities, Niches, Analyzer, Domains, Maintenance, Database Backup, Info
- Domain checks for `<city><niche>.com` via the **Verisign RDAP** interface
- **SQLite** database with **backup and restore**
- **JSON** based translation system
- **Info** page with contact links (LinkedIn / GitHub / Email)

## Getting started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

## Project structure

```text
main.py               Entry point
app/
  core/               Settings, icons, and contact links
  ui/
    components/       Header, Sidebar, Footer
    layouts/          Window frame, main layout, and main window
    navigation/       Navigation system (config → registry → manager)
    pages/            Pages (Home dashboard)
    themes/           Light/dark color schemes
moduls/
  cities/             Cities management
  niches/             Niches management
  analyzer/           Analyzer (domain checking)
  domains/            Domains explorer
  strength/           Domain strength scoring
  maintenance/        Unknown domains re-check
  backup/             Database backup and restore
  info/               App info and contact
database/             SQLite (models + manager + app_data.db)
translator/           JSON translation files
widgets.py            Sortable table widgets
config/               Saved settings (theme, window size)
assets/icons/         SVG icons
```

## Analyzer page

Follows the `ui.py → controller.py → services.py → database/models.py` pattern. Batch analysis runs on a `QThread` with live output of results.

## License

This project is licensed under the [MIT License](LICENSE). Copyright © 2026 Mouad Kaismoune.