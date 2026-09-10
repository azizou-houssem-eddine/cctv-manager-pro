# Original User Request

## Initial Request — 2026-09-08T19:17:46Z

Comprehensive overhaul and redesign of CCTV Manager Pro, adding an executive analytics dashboard, barcode scanner audio/visual feedback, CSV/Excel bulk import and export, an in-app PDF previewer for official stamped documents, installation delivery receipts (PV de pose) mapping serials to clients, and an extensible multi-dossier architecture preparing for the upcoming "2ème dossier" regulatory phase.

Working directory: d:\programation\cctv
Integrity mode: development

## Requirements

### R1. Executive Analytics & Stock Dashboard
- Implement an overview dashboard displaying active metrics: total cameras in stock, total cameras assigned, number of registered clients, and low-stock warnings per model.
- Include quick-action cards for common tasks (quick scan, new client, latest dossier generated).

### R2. Advanced Barcode Scanner & Batch Inventory QoL
- Integrate responsive audio feedback using the Web Audio API (crisp positive chime on valid serial scan, distinctive warning buzzer on duplicate or invalid input).
- Provide bulk CSV/Excel export of serial numbers (filterable by model and status) and bulk CSV import to stage serials without manual line-by-line scanning.
- Add serial search and quick-filter in the inventory table.

### R3. In-App Document Preview & Installation Receipt (PV de pose)
- Add an in-app modal PDF previewer allowing users to view stamped Annex 1 and Annex 5 documents directly inside the application before or after saving.
- Add an installation receipt / delivery slip generator (*Procès-Verbal de Réception / Bordereau de Livraison*) that lists client details alongside the exact serial numbers assigned, complementing the regulatory aggregated quantities.

### R4. Modular Multi-Dossier Architecture (1er Dossier & 2ème Dossier Extensibility)
- Restructure client dossier management into a modular tabbed/folder architecture:
  - Active: **1er Dossier** (Annexes 1 & 5 for initial equipment acquisition authorization).
  - Extensible Slot: **2ème Dossier** (Exploitation license & final commissioning, ready for future template addition).
- Ensure client directory outputs cleanly separate `dossiers/<Client_Name>/1er_dossier/` and prepare for `2eme_dossier/`.

### R5. Fluent UI Redesign & Ergonomics
- Elevate the Windows 11 Fluent dark/light aesthetic with refined micro-interactions, acrylic surfaces, and compact table modes.
- Implement global keyboard shortcuts (e.g., `Ctrl+F` to search, `Ctrl+N` for new client, `Esc` to dismiss modals, `Enter` to confirm scan).
- Maintain robust bilingual French/Arabic typography with dynamic RTL/LTR direction switching.

## Acceptance Criteria

### Verification & Functionality
- [ ] Barcode scanner emits distinct audio frequencies for successful scans vs duplicate errors without external audio asset dependencies.
- [ ] Bulk CSV import accurately parses and stages serial numbers into the database without duplicates.
- [ ] CSV export produces a properly formatted file containing serial numbers, model names, and assignment statuses.
- [ ] The in-app PDF preview displays the generated Annex 1 and Annex 5 documents without requiring an external PDF viewer.
- [ ] Installation delivery receipts (*PV de pose*) can be generated and exported with client name and list of assigned serials.
- [ ] Dossier generation cleanly organizes files under a modular dossier hierarchy supporting 1er Dossier now and ready for 2ème Dossier.
- [ ] All database queries, schema migrations, and PDF generation tests pass programmatically via automated test scripts.
- [ ] PyInstaller standalone executable builds successfully into `dist/CCTV_Manager_Pro.exe` with all web assets bundled.
