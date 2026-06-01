# RandeBoo — Appointment Management System

[🇬🇷 Ελληνική Έκδοση](README.md)

**Project 07 (PLIPRO, HOU 2025-2026) — Team 1**

**RandeBoo** is a comprehensive and professional desktop appointment management application, specifically designed for the needs of small and medium-sized service providers (such as hair salons, medical clinics, beauty centers, etc.). The application is developed entirely in Python 3 with a Tkinter graphical user interface, following a consistent design language focused on simplicity and functionality, utilizing shades of blue and white, and offering a user-friendly interface designed for maximum font compatibility across all operating systems.

---

## Technologies and Libraries

The application relies on the following technologies to ensure stability, speed, and data security:

*   **Python 3 (3.10+):** The core programming language of the application.
*   **Tkinter / ttk:** The library used to design the graphical user interface (GUI). ttk widgets are used for a more modern and consistent appearance.
*   **SQLite3:** A local relational database. Chosen to keep the application self-contained (no external database server required) and to ensure fast query execution.
*   **bcrypt:** A security library used for hashing and verifying user passwords.
*   **Matplotlib:** Used to generate dynamic statistical charts (Daily Bar Chart, Monthly Line Chart, Top Customers, Employee Performance) embedded directly within Tkinter.
*   **XlsxWriter & ReportLab:** Libraries used to export data to Excel (.xlsx) and PDF (.pdf) formats respectively, with full support for Greek characters.
*   **holidays:** Used for automatic detection and import of official Greek public holidays into the system.
*   **tkcalendar (DateEntry):** Provides an easy-to-use calendar selector for entering dates.

---

## Architecture & Extensibility

RandeBoo was designed with future extensibility and code maintainability in mind, implementing modern architectural patterns:

### 1. Single Page Application (SPA) GUI Architecture
Navigation in the application is managed centrally by `gui_main.py` (`MainWindow`). Instead of opening multiple windows that strain the operating system and confuse the user, the application operates as an SPA.
*   The central router dynamically switches various panels (subclasses of `tk.Frame`) in the main display area.
*   Adding a new feature or tab simply requires creating a new panel file and registering it in the navigation mechanism of `gui_main.py`.

### 2. Separation of Concerns
The application logic is strictly separated from the presentation layer (UI):
*   Database interaction is handled exclusively through `database.py`.
*   The search mechanism (`search.py`), backup engine (`backup.py`), email service (`email_service.py`), and data export mechanisms (`export_data.py`) are implemented in independent logic files.
*   This allows for easy back-end changes (e.g., migrating from SQLite to PostgreSQL) without affecting the graphical interface.

### 3. Object-Oriented Design & Inheritance
To avoid repetitive code (DRY - Don't Repeat Yourself), parent classes are used to inherit common behavior and appearance:
*   **`BaseView` (`gui_settings.py`):** Acts as a super-class for the individual settings views (`BusinessSettingsView`, `ProfileSettingsView`, `SecuritySettingsView`, `SystemInfoView`), ensuring shared color constants, button formatting methods, and input field creation.
*   **`SettingsDialogBase` (`gui_settings.py`):** The parent class for settings pop-up dialogs (`HolidaysDialog`, `ExceptionsDialog`).
*   **Form Inheritance:** The class `UpdateCustomerWindow` inherits directly from `AddCustomerWindow` (`gui_customers.py`), and similarly `UpdateEmployeeWindow` inherits from `AddEmployeeWindow` (`gui_employees.py`), modifying only the saving behavior and field initialization.

### 4. Decoupled and Secure Data Management
*   **Parameterized Queries:** The application does not execute SQL queries directly from the GUI. Database access is isolated in `database.py` and all calls are fully parameterized (using `?` placeholders), eliminating the risk of SQL Injection attacks.
*   **Schema Flexibility with `sqlite3.Row`:** The `sqlite3.Row` property is used as a `row_factory` to return records as dictionaries. This allows values to be retrieved by column name (e.g., `row["email"]`) instead of their numerical index. Consequently, any future changes or additions to the table structures will not break the GUI, significantly enhancing extensibility.
*   **Referential Integrity:** Foreign key constraints are explicitly enabled (`PRAGMA foreign_keys = ON`), ensuring record association and supporting cascade deletions (e.g., automatic deletion of related appointments when a customer is deleted).

### 5. Defensive Programming & Disaster Recovery
*   **Safe Mode Recovery (`main.py`):** In the event of a critical error or database corruption during startup, the system does not crash. It presents a special Safe Mode window to the user and suggests automated recovery from the last available backup.
*   **Automatic Backup:** Upon exiting the application, a database backup is taken automatically. Users can also perform manual backups and restores through the settings panel.

---

## Project Structure

The project directory structure is as follows:

```text
Finalized_files/
├── backups/                                    # Local database backups
├── data/                                       # SQLite database storage folder (randeboo.db)
├── src/                                        # Source Code
│   ├── main.py                                 # Application entry point & Safe Mode Recovery
│   ├── database.py                             # SQLite setup, schema, and CRUD operations
│   ├── backup.py                               # Database backup & restore management
│   ├── search.py                               # Unified appointment search logic
│   ├── email_service.py                        # SMTP email client & iCalendar (.ics) generation
│   ├── export_data.py                          # Data export to Excel, PDF, and CSV
│   ├── gui_main.py                             # Main Dashboard, Navigation & Sidebar
│   ├── gui_login.py                            # Login screen, authentication & password reset
│   ├── gui_customers.py                        # Customer management (CRUD UI)
│   ├── gui_employees.py                        # Employee management (CRUD UI)
│   ├── gui_users.py                            # User account management (Admin Panel)
│   ├── gui_appointments.py                     # Appointment calendar (Calendar View) & slots
│   ├── gui_quick_booking.py                    # Quick booking pop-up dialog
│   ├── gui_search.py                           # Advanced unified search screen
│   ├── gui_settings.py                         # Business, hours, and security settings panel
│   └── gui_stats.py                            # Statistical analysis and charts screen
├── requirements.txt                            # External application dependencies
└── [ΠΛΗΠΡΟ]-Project07 (Διαχείριση Ραντεβού).pdf    # Project assignment instructions (Greek)
```

---

## Development Team and Responsibilities

The allocation of code files and responsibilities among team members is defined as follows:

| Team Member | Code Files | Main Responsibilities & Features |
| :--- | :--- | :--- |
| **Kanavou Kalliopi** | `gui_appointments.py`<br>`gui_stats.py` | Design and modeling of the relational database, management of daily appointments, time slots, and availability (capacity control), as well as integration of dynamic Matplotlib charts. |
| **Kataxenos Christos** | `database.py`<br>`gui_main.py`<br>`gui_settings.py`<br>`backup.py`<br>`main.py`<br>`email_service.py`<br>`gui_quick_booking.py` | SQLite schema implementation & basic CRUD queries, development of the main Dashboard and navigation Sidebar, implementation of the settings system (Business/Schedule/SMTP), development of the backup engine and Safe Mode Recovery. UI/UX identity design, participation in the implementation of the email mechanism, and implementation of the quick booking dialog. |
| **Aspridis Dimitris** | `gui_login.py`<br>`gui_customers.py`<br>`gui_users.py` | Design and implementation of the user authentication (Login) screen with a role-based system, integration of bcrypt hashing in `database.py`, development of customer CRUD management with live filtering, and participation in the development of the user management panel. |
| **Varthalitis Panos** | `search.py`<br>`gui_search.py`<br>`export_data.py` | Design of the unified appointment search mechanism and the corresponding search screen with status/time filters, development of the data export modules to Excel, PDF (ReportLab), and CSV. Final UI/UX refinement of the interfaces. |
| **Kondylis Giorgos** | `gui_employees.py`<br>`gui_users.py`<br>`email_service.py` | Development of employee (staff) CRUD management, design of the user account management screen (`gui_users.py` in collaboration with D. Aspridis), and implementation of the back-end email dispatch mechanism (SMTP) and calendar file generation (`email_service.py` in collaboration with C. Kataxenos). |

---

## Setup & Run Instructions

### Prerequisites
Make sure **Python 3.10** or a newer version is installed on your system.

---

### Windows Instructions

1.  **Install Python:**
    Download the appropriate version from [python.org](https://www.python.org/) and make sure to check the box **"Add Python to PATH"** during installation.
2.  **Open Terminal:**
    Open Command Prompt or PowerShell in the `Finalized_files` folder.
3.  **Create a Virtual Environment:**
    ```cmd
    python -m venv venv
    ```
4.  **Activate the Virtual Environment:**
    ```cmd
    .\venv\Scripts\activate
    ```
5.  **Install Dependencies:**
    ```cmd
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
6.  **Run the Application:**
    ```cmd
    python src/main.py
    ```

---

### Database and Backup Storage in the EXE Edition
When the application runs as a standalone `.exe` file (frozen state), file management operates in portable mode:
*   **Database Location:** The database `randeboo.db` is **not** stored in system temporary folders (Temp) where it would be lost upon termination. The system automatically detects PyInstaller execution and sets the directory of the executable file (`sys.executable`) as the root directory. The database is saved and permanently updated inside the `data/` directory next to `RandeBoo.exe` (i.e., at the path `./data/randeboo.db`).
*   **Backup Location:** Similarly, automatic and manual backups are saved in the `backups/` folder next to `RandeBoo.exe` (i.e., at the path `./backups/`).
*   **Log Files (Logs):** The `app.log` file is also created in the same directory as the executable.

This makes the application fully portable: you can move the entire folder containing `RandeBoo.exe`, the database subdirectory (`data/`), and the backups subdirectory (`backups/`) to any other computer running Windows, and the application will run immediately with all data intact.
