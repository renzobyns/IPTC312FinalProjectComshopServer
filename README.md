# Comshop Management System

A desktop computer shop management system built with Python + CustomTkinter + MySQL (XAMPP). Final project for IPTC312.

## Features

- **PC Session Management** — Prepaid billing (hourly or package), receipt at session start, cancel & refund
- **Food & Drinks POS** — Cart-based sales with live stock deduction
- **Printing POS** — Per-page billing with editable price per transaction
- **Products / Inventory** — CRUD with stock tracking
- **PC Units & Time Packages** — Full CRUD management
- **Transaction History** — Filterable history of all transactions
- **Dashboard** — Live stats: total PCs, availability, occupied, today's revenue

## Stack

| Layer | Technology |
|---|---|
| GUI | Python 3.10+, CustomTkinter 5.2+ |
| Database | MySQL 5.7+ via XAMPP |
| DB Connector | mysql-connector-python |
| Auth | SHA-256 password hashing |

## Setup

### 1. Prerequisites

- [Python 3.10+](https://www.python.org/downloads/) — check "Add to PATH" during install
- [XAMPP](https://www.apachefriends.org/) — start MySQL in the Control Panel before running the app

### 2. Install dependencies

```bash
pip install customtkinter mysql-connector-python
```

Or with the virtual environment:

```bash
.venv\Scripts\activate
pip install customtkinter mysql-connector-python
```

### 3. Initialize the database

```bash
"C:\xampp\mysql\bin\mysql.exe" -u root < setup.sql
```

Or paste `setup.sql` into phpMyAdmin's SQL tab and click **Go**.

### 4. Run

```bash
python main.py
```

**Default login:** `admin` / `admin123`

## Database

Database name: `comshop_db` — 8 tables:

```
users → pc_units ← sessions → time_packages
products, print_services
transactions → transaction_items
```

To migrate an existing DB (adds `cancelled` session status):

```sql
ALTER TABLE sessions MODIFY status ENUM('active','completed','cancelled') DEFAULT 'active';
```

## Project Structure

```
├── main.py                  # Entry point
├── login_screen.py          # Login window
├── auth.py                  # SHA-256 auth
├── db_connection.py         # get_connection() factory
├── dashboard.py             # Sidebar dashboard
├── pc_management.py
├── package_management.py
├── session_management.py    # Also contains ReceiptDialog
├── product_management.py
├── food_pos.py
├── printing_pos.py
├── transactions_history.py
├── tree_style.py            # Shared Treeview styling
├── ui_helpers.py            # bring_to_front, section_header, stat_card
└── setup.sql                # Schema + seed data
```

## Default Seed Data

| Type | Data |
|---|---|
| PCs | PC-01 to PC-05 at ₱20.00/hr |
| Packages | 1HR Promo ₱15, 3HRS Deal ₱40, 5HRS Value ₱60 |
| Products | Coke, Water, Coffee, Chips, Bread |
| Print Services | B&W ₱2.00/page, Colored ₱5.00/page |
