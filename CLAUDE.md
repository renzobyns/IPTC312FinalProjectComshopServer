# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Running the App

```powershell
# Activate venv first
.venv\Scripts\Activate.ps1

# Run the application
python main.py
```

**Prerequisites:** XAMPP must be running with MySQL active on port 3306 before launching.

## Database Setup

Run once to initialize the schema and seed data:

```bash
mysql -u root < setup.sql
```

Or paste the contents into phpMyAdmin's SQL tab.

- **Connection:** `localhost:3306`, user `root`, no password
- **Database:** `comshop_db`
- **Default login:** `admin` / `admin123`

## Architecture

**Entry point:** `main.py` → creates `LoginScreen` (a `ctk.CTk` root window).

**Window lifecycle:**
- `LoginScreen` (`ctk.CTk`) is the tk root — it is hidden (not destroyed) when the user logs in.
- `Dashboard` (`ctk.CTkToplevel`) is the main app window. On logout it destroys itself and re-shows `LoginScreen`. On close it destroys `LoginScreen` (exits the app).
- All seven module windows (`PCManagement`, `PackageManagement`, `SessionManagement`, `ProductManagement`, `FoodPOS`, `PrintingPOS`, `TransactionsHistory`) are `CTkToplevel` children of `Dashboard`.

**Module opening pattern:** `Dashboard._open(key, factory)` prevents duplicate windows. If a module window already exists and is alive, it lifts it instead of creating a new one. Keys: `"pc"`, `"pkg"`, `"sess"`, `"prod"`, `"food"`, `"print"`, `"trans"`.

**Database access:** Every module calls `get_connection()` from `db_connection.py` for each operation and closes the connection in a `finally` block. There is no connection pool.

**Auth:** `auth.py` hashes passwords with SHA-256 and queries the `users` table directly. `verify_login()` returns a user dict `{id, username, full_name}` on success or `None` on failure.

## Shared UI Utilities

All reusable UI components live in `ui_helpers.py` and `tree_style.py`.

| Utility | Where | Purpose |
|---|---|---|
| `bring_to_front(window)` | `ui_helpers` | **Always call at the END of `__init__`** for every `CTkToplevel`. Fixes a customtkinter bug where new windows appear behind the dashboard. |
| `section_header(parent, title, accent_color)` | `ui_helpers` | Colored header bar at the top of each module window. |
| `stat_card(parent, title, icon, accent_color)` | `ui_helpers` | Dashboard stat card; returns `(card_frame, value_label)`. |
| `apply_tree_style()` | `tree_style` | Applies a consistent dark/light `ttk.Treeview` style. Call whenever creating a Treeview. |

`ReceiptDialog` is defined in `session_management.py` but is imported and reused by `food_pos.py` and `printing_pos.py`.

## Database Schema (8 tables)

`users` → `pc_units` ← `sessions` → `time_packages`  
`products`, `print_services`  
`transactions` → `transaction_items`  
`transactions.processed_by` → `users.id`

Session billing supports two modes: `hourly` (rate from `pc_units.rate_per_hour`) and `package` (fixed price from `time_packages`).

## Adding a New Module

1. Create `your_module.py` with a class extending `ctk.CTkToplevel`.
2. In `__init__`: call `apply_tree_style()`, build UI, then call `bring_to_front(self)` **last**.
3. Use `section_header(self, "Title", accent_color="#hex")` as the first UI element.
4. Register in `dashboard.py`: add a nav item in `nav_items`, add `_open_your_module` method using `self._open("key", lambda: YourModule(self))`.
