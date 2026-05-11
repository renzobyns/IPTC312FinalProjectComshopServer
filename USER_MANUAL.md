# OG GAMING HUB
## User Manual Documentation

---

| Field | Details |
|---|---|
| **System Title** | OG Gaming Hub |
| **Document Type** | User Manual Documentation |
| **Course / Subject** | IPTC312 |
| **Instructor** | _(Instructor Name)_ |
| **Group Members** | _(Student Names)_ |
| **Section / Year** | _(Section / Year Level)_ |
| **Date of Submission** | May 12, 2026 |

---

## TABLE OF CONTENTS

1. Introduction
2. System Overview
3. System Requirements
4. Installation Guide
5. User Access and Login
6. System Navigation Guide
7. Database Interaction
8. Error Handling and Troubleshooting
9. Sample Transactions / Use Cases
10. Security Features
11. System Limitations
12. Future Enhancements
13. Glossary
14. Reflection
15. Appendices

---

## 1. INTRODUCTION

The OG Gaming Hub is a desktop application developed to streamline the daily operations of a computer shop business. Computer shops traditionally rely on manual tracking of PC usage, customer billing, food orders, and printing services — a process that is prone to errors, slow, and difficult to audit. This system replaces those manual methods with a digital, database-driven solution.

The system is built using Python with the CustomTkinter library for a modern graphical user interface, connected to a MySQL database hosted through XAMPP for reliable local data storage. It is intended for use by shop cashiers and administrators who need to manage PC sessions, sell food and drinks, process printing transactions, and review daily revenue — all from a single application.

The scope of the system covers seven core operational modules: PC unit management, time package management, session management with prepaid billing, product and inventory management, a food and drinks point-of-sale, a printing services point-of-sale, and a transaction history viewer. The system does not include online connectivity, multi-branch support, or automated scheduling features.

---

## 2. SYSTEM OVERVIEW

The OG Gaming Hub operates entirely as a desktop application running on a Windows machine. The user interface is built with Python and the CustomTkinter library, which provides a modern dark-themed graphical interface with buttons, forms, dropdown menus, and data tables. All user inputs and actions are processed by Python logic that communicates directly with a MySQL database running through XAMPP's MySQL service.

The system uses the `mysql-connector-python` library to establish a connection between the Python application and the `comshop_db` database. Every time a user performs an action — such as starting a session, processing a food order, or adding a product — the system sends a SQL query to the database, which stores or retrieves the relevant data and reflects the result immediately in the interface.

**Key features of the system include:**

- **Login Authentication** — Only authorized users with valid credentials can access the system.
- **PC Unit Management** — Add, edit, and monitor the status of all PC units in the shop.
- **Time Package Management** — Define fixed-duration billing packages with custom prices.
- **Session Management** — Start prepaid PC sessions with automatic billing calculation; end or cancel sessions as needed.
- **Products and Inventory** — Manage food and drink items with stock tracking.
- **Food & Drinks POS** — Cart-based point-of-sale for selling food and drinks to customers.
- **Printing POS** — Process printing transactions with adjustable per-page pricing.
- **Transaction History** — View, filter, and review all completed transactions by date and type.
- **Dashboard** — At-a-glance view of total PCs, availability, active sessions, and today's revenue.

---

## 3. SYSTEM REQUIREMENTS

### Hardware Requirements

| Component | Minimum |
|---|---|
| Processor | Intel Core i3 or equivalent |
| RAM | 4 GB |
| Storage | 500 MB free disk space |
| Display | 1280 × 720 resolution or higher |
| Input | Keyboard and mouse |

### Software Requirements

| Software | Version / Notes |
|---|---|
| Operating System | Windows 10 or Windows 11 |
| Python | 3.10 or higher |
| XAMPP | Any version with MySQL 5.7+ |
| customtkinter | 5.2.0 or higher |
| mysql-connector-python | 8.0 or higher |

### Python Libraries Required

```
customtkinter
mysql-connector-python
```

Both libraries can be installed via pip (see Section 4).

---

## 4. INSTALLATION GUIDE

Follow these steps carefully to set up and run the OG Gaming Hub on a new machine.

### Step 1 — Install Python

1. Go to https://www.python.org/downloads/ and download Python 3.10 or higher.
2. Run the installer. **Important:** Check the box that says "Add Python to PATH" before clicking Install.
3. After installation, open Command Prompt and type `python --version` to confirm it installed correctly.

### Step 2 — Install XAMPP

1. Download XAMPP from https://www.apachefriends.org/.
2. Run the installer and complete the setup with default options.
3. Open the XAMPP Control Panel and click **Start** next to **MySQL**.
4. Confirm that MySQL shows a green "Running" status.

### Step 3 — Set Up the Database

1. Open a web browser and go to `http://localhost/phpmyadmin`.
2. Click the **SQL** tab at the top.
3. Open the project folder and find the file named `setup.sql`.
4. Copy all the contents of `setup.sql` and paste them into the phpMyAdmin SQL input box.
5. Click **Go** to execute. This creates the `comshop_db` database, all 8 tables, and the default seed data including the admin account.

Alternatively, open Command Prompt in the project folder and run:
```
"C:\xampp\mysql\bin\mysql.exe" -u root < setup.sql
```

### Step 4 — Install Python Libraries

1. Open Command Prompt.
2. Navigate to the project folder:
   ```
   cd path\to\IPTC312FinalProjectComshopServer
   ```
3. Activate the virtual environment (if provided):
   ```
   .venv\Scripts\activate
   ```
4. Install required libraries:
   ```
   pip install customtkinter mysql-connector-python
   ```

### Step 5 — Run the Application

1. Make sure XAMPP MySQL is running.
2. In the project folder, run:
   ```
   python main.py
   ```
3. The login screen will appear. Use the default credentials:
   - **Username:** `admin`
   - **Password:** `admin123`

---

## 5. USER ACCESS AND LOGIN

### Login Screen

When the application is launched, the Login Screen is the first window that appears. It displays the system title, a username field, and a password field.

**Steps to log in:**

1. Launch the application by running `python main.py`.
2. The Login Screen appears centered on the screen.
   > _(Screenshot: Login Screen)_
3. Click the **Username** field and type your username (default: `admin`).
4. Click the **Password** field and type your password (default: `admin123`). The password is masked with dots for privacy.
5. Press **Enter** or click the **Login** button.
6. If the credentials are correct, the Login Screen hides and the Dashboard opens.
7. If the credentials are incorrect, a warning dialog appears: _"Invalid username or password."_ The fields remain active so the user can try again.

### User Roles

The current version of the system supports a single administrator role. All users who log in have full access to every module. There is no guest or limited-access role.

### Password Security

Passwords are not stored as plain text in the database. The system converts the entered password to a SHA-256 hash before comparing it against the stored hash in the `users` table. This means even if someone views the database directly, they cannot read the actual password.

### Logout

To log out, click the **⎋ Logout** button at the bottom of the sidebar in the Dashboard. A confirmation dialog will ask: _"Are you sure you want to logout?"_ Clicking **Yes** returns the user to the Login Screen.

---

## 6. SYSTEM NAVIGATION GUIDE

### Dashboard

After logging in, the Dashboard opens. It consists of two main areas:

- **Sidebar (left, 230px wide)** — Contains the navigation menu with buttons for all seven modules, a theme toggle button, the logged-in user's name, and the Logout button.
- **Content area (right)** — Shows four stat cards at the top (Total PCs, Available, Occupied, Today's Revenue) and a Recent Transactions table below. The dashboard refreshes automatically every 30 seconds.

> _(Screenshot: Dashboard)_

To open any module, click its button in the sidebar. If the module is already open, clicking the button again brings it to the front instead of opening a duplicate.

---

### Module 1 — PC Units

**Purpose:** Add, edit, delete, and monitor the status of all PC units in the shop.

1. Click **🖥 PC Units** in the sidebar.
2. The PC Units window opens showing a table of all units with columns: ID, Unit Name, Status, and Rate/Hour.
   > _(Screenshot: PC Units window)_
3. **To add a PC:** Fill in the Unit Name and Rate per Hour fields on the left form, then click **Add PC**.
4. **To edit a PC:** Click a row in the table to select it. The form fields populate with that PC's data. Make changes and click **Update**.
5. **To delete a PC:** Select a row and click **Delete**. A confirmation dialog appears before deletion.
6. PC status (Available / Occupied / Maintenance) updates automatically when sessions start and end.

---

### Module 2 — Time Packages

**Purpose:** Define fixed-duration billing packages that customers can choose instead of hourly billing.

1. Click **📦 Time Packages** in the sidebar.
2. The Time Packages window shows existing packages with Package Name, Hours, and Price.
   > _(Screenshot: Time Packages window)_
3. **To add a package:** Enter a name (e.g., "3HRS Deal"), the number of hours (e.g., 3), and the price. Click **Add Package**.
4. **To edit:** Select a package row, modify the fields, click **Update**.
5. **To delete:** Select a row and click **Delete**.

When starting a session, if the entered duration matches a package's hours, the system automatically applies the package price instead of the hourly rate.

---

### Module 3 — Session Management

**Purpose:** Start, monitor, end, or cancel PC usage sessions with prepaid billing.

1. Click **▶ Sessions** in the sidebar.
2. The Session Management window opens with a start-session form on the left and an active sessions table on the right.
   > _(Screenshot: Session Management window)_

**Starting a Session:**

1. Select an available PC from the **Select PC** dropdown.
2. Enter the customer's name in **Customer Name**.
3. Enter the duration in hours in the **Duration (hours)** field (e.g., `2` for 2 hours, `1` for the 1HR Promo package).
4. A preview label shows the calculated price or matching package automatically.
5. Click **▶ Start Session**.
6. A confirmation dialog appears: _"Collect payment from [customer]? Amount: ₱X.XX"_
7. Click **Yes** to collect payment. The transaction is recorded, a receipt dialog opens, and the PC status changes to Occupied.
   > _(Screenshot: Payment confirmation dialog and Receipt)_

**Ending a Session:**

1. Select an active session row in the right-side table.
2. Click **End Session**.
3. The session is marked completed, the PC is freed, and a short info message confirms: _"Session ended. PC-01 is now available."_
4. No second receipt is shown since payment was already collected at the start.

**Cancelling a Session (Refund):**

1. Select an active session row.
2. Click **Cancel & Refund** (orange button).
3. A dialog shows the refund amount. Click **Yes** to confirm.
4. The transaction is voided, the session is marked cancelled, and the PC is freed.

---

### Module 4 — Products

**Purpose:** Manage food and drink inventory.

1. Click **🍔 Products** in the sidebar.
2. The Products window shows all items with Name, Category, Price, and Stock columns.
   > _(Screenshot: Products window)_
3. **To add:** Fill in the product name, select category (food/drink), enter price and stock quantity. Click **Add Product**.
4. **To edit:** Select a row, modify fields, click **Update**.
5. **To delete:** Select a row and click **Delete**.
6. Stock levels decrease automatically when items are sold through the Food POS.

---

### Module 5 — Food & Drinks POS

**Purpose:** Sell food and drink items to customers using a cart-based interface.

1. Click **🛒 Food POS** in the sidebar.
2. The window is split: product buttons on the left, cart on the right.
   > _(Screenshot: Food POS window)_
3. Click a product button to add it to the cart. Each click adds one unit.
4. To remove an item from the cart, select it in the cart list and click **Remove**.
5. Enter the customer's name in the **Customer Name** field.
6. Click **Process Sale** to complete the transaction.
7. A receipt dialog opens showing all items, quantities, and total amount.
8. The system deducts the sold quantities from the product stock and records the transaction in the database.

---

### Module 6 — Printing POS

**Purpose:** Process printing service transactions.

1. Click **🖨 Printing** in the sidebar.
2. The Printing POS window shows a form with Service Type, Customer Name, Number of Pages, and Price per Page.
   > _(Screenshot: Printing POS window)_
3. Select the service type from the dropdown (e.g., B&W Print or Colored Print). The Price per Page field auto-fills with the service's default rate.
4. Enter the customer name and number of pages.
5. The **Price per Page** field can be edited if needed (e.g., for a discount or special rate).
6. The **Total** label updates live as you type.
7. Click **Process Transaction**. A receipt dialog opens and the transaction is recorded.

---

### Module 7 — Transaction History

**Purpose:** View and filter all completed transactions.

1. Click **📋 Transactions** in the sidebar.
2. The Transaction History window shows a full table of all transactions with Date, Type, Customer, and Amount columns.
   > _(Screenshot: Transaction History window)_
3. Use the filter dropdowns to filter by **Type** (PC Rental / Food / Printing) or by **Date**.
4. Click a transaction row to see its individual line items in the detail panel below.

---

## 7. DATABASE INTERACTION

The OG Gaming Hub stores all data in a MySQL database named `comshop_db`, running locally through XAMPP. The database contains 8 tables: `users`, `pc_units`, `time_packages`, `products`, `print_services`, `sessions`, `transactions`, and `transaction_items`.

Every time a user performs an action in the system, the Python application connects to MySQL, sends a SQL query, and immediately reflects the result in the interface. The connection is opened only for the duration of each individual operation and is closed immediately after — this keeps the system lightweight and prevents stale connections.

**Examples of database interactions:**

| User Action | Database Operation |
|---|---|
| Login | SELECT from `users` WHERE username and password hash match |
| Start a Session | INSERT into `sessions`, INSERT into `transactions`, INSERT into `transaction_items`, UPDATE `pc_units` status to 'occupied' |
| End a Session | UPDATE `sessions` status to 'completed', UPDATE `pc_units` status to 'available' |
| Cancel a Session | DELETE from `transaction_items` and `transactions`, UPDATE `sessions` status to 'cancelled', UPDATE `pc_units` status to 'available' |
| Process Food Sale | INSERT into `transactions` and `transaction_items`, UPDATE `products` stock |
| Process Printing | INSERT into `transactions` and `transaction_items` |
| View Dashboard Stats | SELECT COUNT from `pc_units`, SELECT SUM from `transactions` for today's date |
| View Transaction History | SELECT from `transactions` with optional filters |

All SQL queries in the system use **parameterized statements** (using `%s` placeholders), which prevents SQL injection attacks.

---

## 8. ERROR HANDLING AND TROUBLESHOOTING

### Issue 1 — Cannot Connect to the Database

**Symptom:** A popup appears saying _"Cannot connect to the database. Please make sure XAMPP MySQL is running."_

**Cause:** The XAMPP MySQL service is not running when the application tries to connect.

**Solution:**
1. Open the XAMPP Control Panel.
2. Click **Start** next to **MySQL**.
3. Wait for the status to turn green (Running).
4. Restart the application or retry the action.

---

### Issue 2 — Blank or Invalid Input Warning

**Symptom:** A warning dialog says _"Please fill in all required fields."_ when trying to save or process a transaction.

**Cause:** One or more required fields were left empty or contain invalid values (e.g., entering letters in a number field).

**Solution:**
1. Check all input fields in the form. Required fields are clearly labeled.
2. Make sure numeric fields (hours, pages, price, stock) contain valid positive numbers.
3. Re-enter the correct values and try again.

---

### Issue 3 — Selected PC Is Not Available

**Symptom:** A warning says _"Selected PC is not available."_ when trying to start a session.

**Cause:** The PC was already assigned to an active session, or its status was manually set to Maintenance.

**Solution:**
1. Go to the **Sessions** module and check if the PC already has an active session.
2. If the session should have ended, select it and click **End Session**.
3. Alternatively, choose a different PC from the dropdown that shows as Available.

---

### Issue 4 — Application Closes Immediately on Launch

**Symptom:** The application window flashes and closes, or a Python error appears in the terminal.

**Cause:** A required library (`customtkinter` or `mysql-connector-python`) is not installed, or the virtual environment is not activated.

**Solution:**
1. Open Command Prompt in the project folder.
2. Activate the virtual environment: `.venv\Scripts\activate`
3. Install missing libraries: `pip install customtkinter mysql-connector-python`
4. Run `python main.py` again.

---

### Issue 5 — Login Fails with Correct Credentials

**Symptom:** The login page shows _"Invalid username or password."_ even when typing the correct credentials.

**Cause:** The `users` table may be empty if the database was not seeded, or the password hash is incorrect.

**Solution:**
1. Open phpMyAdmin at `http://localhost/phpmyadmin`.
2. Navigate to `comshop_db` → `users` table.
3. If the table is empty, re-run `setup.sql` to re-seed the default admin account.
4. Default credentials are username: `admin`, password: `admin123`.

---

## 9. SAMPLE TRANSACTIONS / USE CASES

### Use Case 1 — Starting a Prepaid PC Session (Hourly)

**Scenario:** A customer named Juan wants to use PC-03 for 2 hours at the standard rate of ₱20.00/hour.

**Steps:**
1. Log in to the system and click **▶ Sessions** in the sidebar.
2. From the **Select PC** dropdown, choose **PC-03**.
3. In **Customer Name**, type `Juan`.
4. In **Duration (hours)**, type `2`. The preview shows: _"⏱ Hourly: 2.0h × ₱20.00/hr = ₱40.00"_
5. Click **▶ Start Session**.
6. A confirmation dialog appears: _"Collect payment from Juan? Amount: ₱40.00"_ — click **Yes**.
7. The receipt dialog opens showing Transaction #, customer name, duration (2.0 hours), and total ₱40.00.
8. Close the receipt. PC-03 now shows as **Occupied** in the PC Units module and the Dashboard.
9. Today's Revenue on the Dashboard increases by ₱40.00.

---

### Use Case 2 — Selling Food and Drinks

**Scenario:** A customer wants 1 Coke (₱20.00) and 1 Chips (₱15.00).

**Steps:**
1. Click **🛒 Food POS** in the sidebar.
2. Click the **Coke** product button once — it appears in the cart with quantity 1.
3. Click the **Chips** product button once — it appears in the cart.
4. The cart total shows ₱35.00.
5. Enter the customer name and click **Process Sale**.
6. A receipt opens showing both items and a total of ₱35.00.
7. The system deducts 1 unit each from Coke and Chips stock in the database.

---

### Use Case 3 — Processing a Printing Job (Custom Price)

**Scenario:** A customer needs 10 pages of colored printing, but the cashier is giving a discount at ₱4.00/page instead of the standard ₱5.00.

**Steps:**
1. Click **🖨 Printing** in the sidebar.
2. From the **Service Type** dropdown, select **Colored Print — ₱5.00/page**.
3. Enter the customer name.
4. In **Number of Pages**, type `10`.
5. The **Price per Page** field shows `5.00`. Change it to `4.00`.
6. The Total label updates to ₱40.00.
7. Click **Process Transaction**. The receipt shows the discounted total of ₱40.00.

---

### Use Case 4 — Cancelling a Session with Refund

**Scenario:** A customer paid for a 3-hour session but changed their mind after 10 minutes and wants a refund.

**Steps:**
1. Click **▶ Sessions** in the sidebar.
2. Locate the customer's active session in the Active Sessions table.
3. Click the row to select it.
4. Click the **Cancel & Refund** button (orange).
5. A dialog shows: _"Cancel session? Refund amount: ₱60.00"_ — click **Yes**.
6. The session is marked cancelled, the transaction is voided, and PC is freed.
7. Today's Revenue on the Dashboard decreases by ₱60.00.

---

## 10. SECURITY FEATURES

### Password Hashing

User passwords are never stored in plain text. When a user registers or when the default admin is seeded, the password is converted to a SHA-256 hash (a 64-character string) before being written to the `users` table. When a user logs in, the system hashes the entered password and compares it to the stored hash. Even if someone gains direct access to the database, they cannot reverse the hash back into the original password.

### Parameterized SQL Queries

All database queries in the system use parameterized statements with `%s` placeholders instead of string concatenation. This protects the system against SQL injection attacks, where a malicious user might try to enter special characters in input fields to manipulate database queries.

**Example from the code:**
```python
cursor.execute(
    "SELECT id, username, full_name FROM users WHERE username = %s AND password_hash = %s",
    (username, hash_password(plain_password)),
)
```

### Input Validation

Every form in the system validates user input before sending it to the database. The system checks that:
- Required fields are not empty.
- Numeric fields (hours, pages, prices, stock) contain valid positive numbers.
- PC selections are valid and available before starting sessions.

If validation fails, a warning dialog is shown and no database operation is performed.

### Access Control

The login screen acts as a gate — no module can be opened without a valid login session. The Dashboard is only shown after successful authentication, and the application closes or returns to the login screen on logout.

---

## 11. SYSTEM LIMITATIONS

1. **Single-user access** — The system is designed for one cashier at a time. There is no multi-user or concurrent access support.
2. **No network connectivity** — The system runs entirely on a local machine. It cannot be accessed remotely or across multiple branches.
3. **No automatic session expiry** — The system does not automatically end a session when the preset time runs out. The cashier must manually click **End Session**.
4. **No role-based access** — All logged-in users have full administrative access. There is no cashier-only or read-only role.
5. **No report generation** — The system displays transaction history but does not generate printable daily sales reports or summaries.
6. **No data backup feature** — There is no built-in backup mechanism. Database backups must be done manually through phpMyAdmin or MySQL tools.
7. **Windows only** — The application is configured and tested for Windows. Running it on macOS or Linux would require path adjustments and additional setup.

---

## 12. FUTURE ENHANCEMENTS

1. **Automatic session timeout** — Implement a background timer that alerts the cashier (or automatically ends the session) when a customer's paid time is about to expire.
2. **Role-based access control** — Add separate roles for Cashier (limited to POS and sessions) and Admin (full access including CRUD operations and reports).
3. **Daily and monthly sales reports** — Generate printable PDF summaries of daily revenue broken down by transaction type.
4. **Low stock alerts** — Notify the cashier when a product's stock falls below a configurable threshold.
5. **Customer loyalty tracking** — Record returning customer profiles and apply loyalty discounts automatically.
6. **Receipt printing** — Integrate thermal printer support so physical receipts can be printed directly from the system.
7. **Multi-branch support** — Connect multiple shop locations to a central server with a shared database.
8. **Refund transaction record** — Instead of deleting cancelled transactions, record them as refund entries for better audit trail compliance.

---

## 13. GLOSSARY

| Term | Definition |
|---|---|
| **CRUD** | Create, Read, Update, Delete — the four basic operations performed on database records. |
| **CustomTkinter** | A modern Python UI library built on top of Tkinter that provides styled, themed widgets. |
| **Dashboard** | The main screen after login showing key statistics and quick navigation to all modules. |
| **Database** | An organized collection of structured data. In this system, MySQL is used as the database. |
| **Hourly Billing** | A billing mode where the customer pays based on the number of hours used multiplied by the hourly rate. |
| **MySQL** | A widely used open-source relational database management system. |
| **Package Billing** | A billing mode where the customer purchases a fixed-duration time bundle at a set price. |
| **Parameterized Query** | A SQL query that uses placeholders (`%s`) instead of directly embedding user input, preventing SQL injection. |
| **PC Unit** | A computer station in the shop that customers pay to use. |
| **Prepaid Session** | A session where the customer pays the full amount upfront before using the PC, and a receipt is issued immediately. |
| **POS (Point of Sale)** | A module where transactions for food, drinks, or printing services are processed. |
| **Receipt** | A dialog window displayed after a successful transaction showing the transaction number, items, and total amount. |
| **Session** | A timed period of PC usage by a customer, tracked from start to end. |
| **SHA-256** | A cryptographic hash function used to securely store passwords. |
| **XAMPP** | A free, cross-platform software bundle that includes Apache and MySQL servers for local development. |

---

## 14. REFLECTION

Working on the OG Gaming Hub provided meaningful experience in developing a real-world desktop application from the ground up. Connecting a Python GUI to a live MySQL database required careful handling of database connections, query parameterization, and ensuring data consistency across multiple related tables.

One of the most challenging aspects was designing the session billing flow. The system needed to calculate billing upfront (for both hourly and package-based sessions), show a payment confirmation to the cashier, issue a receipt immediately, and later allow cancellation with full reversal of the transaction — all while keeping the database in a consistent state.

Building the Cancel & Refund feature reinforced the importance of thinking about edge cases: what happens to revenue when a session is voided? The solution — deleting the original transaction rows and marking the session as "cancelled" — keeps the revenue reporting clean and accurate without requiring changes to the database structure.

This project also highlighted the importance of reusable components. The `ReceiptDialog`, `bring_to_front`, `section_header`, and `apply_tree_style` utilities were written once and reused across all seven modules, reducing code duplication and making the codebase easier to maintain.

Overall, the system demonstrates how a relatively small Python codebase, when well-structured, can deliver a fully functional business application that solves real operational problems in a computer shop environment.

---

## 15. APPENDICES

### Appendix A — Database Schema Summary

| Table | Key Columns | Purpose |
|---|---|---|
| `users` | id, username, password_hash, full_name | Stores admin login credentials |
| `pc_units` | id, unit_name, status, rate_per_hour | Tracks all PC stations and their status |
| `time_packages` | id, package_name, hours, price | Defines fixed-duration billing packages |
| `products` | id, name, category, price, stock | Manages food and drink inventory |
| `print_services` | id, service_name, price_per_page | Defines printing service types and rates |
| `sessions` | id, pc_id, customer_name, billing_type, start_time, total_amount, status | Records all PC usage sessions |
| `transactions` | id, type, customer_name, total_amount, datetime, processed_by | Records all completed and prepaid transactions |
| `transaction_items` | id, transaction_id, item_name, quantity, unit_price, subtotal | Line items for each transaction |

### Appendix B — Default Seed Data

**Default Admin Account:**
- Username: `admin`
- Password: `admin123`

**Default PC Units:** PC-01 through PC-05 at ₱20.00/hour

**Default Time Packages:**
- 1HR Promo — 1 hour — ₱15.00
- 3HRS Deal — 3 hours — ₱40.00
- 5HRS Value — 5 hours — ₱60.00

**Default Products:** Coke (₱20), Water (₱10), Coffee (₱25), Chips (₱15), Bread (₱10)

**Default Print Services:**
- B&W Print — ₱2.00/page
- Colored Print — ₱5.00/page

### Appendix C — File Structure

```
IPTC312FinalProjectComshopServer/
├── main.py                  # Application entry point
├── login_screen.py          # Login window (root CTk window)
├── auth.py                  # Password hashing and login verification
├── db_connection.py         # MySQL connection factory
├── dashboard.py             # Main dashboard with sidebar navigation
├── pc_management.py         # PC Units CRUD module
├── package_management.py    # Time Packages CRUD module
├── session_management.py    # Session management and ReceiptDialog
├── product_management.py    # Products/Inventory CRUD module
├── food_pos.py              # Food & Drinks POS module
├── printing_pos.py          # Printing POS module
├── transactions_history.py  # Transaction History viewer
├── tree_style.py            # Shared Treeview styling utility
├── ui_helpers.py            # Shared UI utilities (bring_to_front, section_header, stat_card)
└── setup.sql                # Database schema and seed data
```
