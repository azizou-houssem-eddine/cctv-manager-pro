# CCTV Manager Pro

A modern Windows 11-style desktop application for managing CCTV equipment inventory, client assignments, and official Algerian document generation (Annex 1 & Annex 5).

## Features
- **Modern UI**: Built with PyQt6 and PyQt-Fluent-Widgets for a premium Windows 11 dark theme experience.
- **Inventory Management**: Real-time barcode/serial number scanning and validation.
- **Client Management**: Complete client lifecycle management with localized fields.
- **Official PDF Generation**: Generates official Algerian Annex 1 (Mellikha 1) and Annex 5 documents with 99% layout accuracy.
- **Localizations**: Full support for French and Arabic (including RTL).
- **Standalone Portable**: Can be bundled as a single .exe for easy distribution.

## Tech Stack
- **UI**: PyQt6, QFluentWidgets
- **Database**: SQLite3
- **PDF Generation**: Jinja2, Headless Microsoft Edge
- **Packaging**: PyInstaller

## Setup
1. Clone the repository.
2. Install dependencies: `pip install PyQt6 PyQt-Fluent-Widgets jinja2`
3. Run `python main.py`
