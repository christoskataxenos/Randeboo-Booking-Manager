"""
Η σχεδίαση του αρχείου έγινε από την Καναβού Καλλιόπη.
Η εκτέλεση (υλοποίηση) έγινε από τον Καταξένο Χρήστο.
Συνεισφορά από τον Ασπρίδη Δημήτρη:
    - Υλοποίηση της ασφάλειας (κρυπτογράφηση κωδικών με bcrypt).
    - Υλοποίηση CRUD λειτουργιών για τους Χρήστες (USERS).
    - Υλοποίηση της Search functionality.
"""

import sqlite3
import os
import datetime
import logging
import bcrypt
import json
from datetime import datetime, timedelta

import sys

# Default Business Settings (αν δεν υπάρχουν στη βάση)
DEFAULT_DURATION_MINUTES = 30

# Project root resolution (υποστήριξη PyInstaller frozen state)
if getattr(sys, "frozen", False):
    _project_root = os.path.dirname(sys.executable)
else:
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.abspath(os.path.join(_script_dir, ".."))

DB_PATH = os.path.abspath(os.path.join(_project_root, "data", "randeboo.db"))


def get_connection() -> sqlite3.Connection:
    """Δημιουργεί σύνδεση με την SQLite βάση δεδομένων."""
    db_dir = os.path.dirname(DB_PATH)
    # Δημιουργία φακέλου data αν δεν υπάρχει
    if not os.path.exists(db_dir) or not os.path.exists("data"):
        try:
            os.makedirs(db_dir, exist_ok=True)
            if not os.path.exists("data"):
                os.makedirs("data", exist_ok=True)
        except: pass

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Ενεργοποίηση Foreign Keys για CASCADE deletes
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Δημιουργεί τους πίνακες της βάσης αν δεν υπάρχουν."""
    conn = get_connection()
    try:
        # Πίνακας Ρόλων
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ROLES (
                role_id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_name TEXT NOT NULL UNIQUE
            )
        """
        )

        # Πίνακας Χρηστών
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS USERS (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_id INTEGER,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                email TEXT UNIQUE,
                is_active INTEGER DEFAULT 1,
                first_login INTEGER DEFAULT 1,
                FOREIGN KEY (role_id) REFERENCES ROLES(role_id)
            )
        """
        )

        # Πίνακας Πελατών
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS CUSTOMERS (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Πίνακας Υπαλλήλων
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS EMPLOYEES (
                employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                specialization TEXT,
                specialty TEXT,
                phone TEXT,
                email TEXT UNIQUE,
                hire_date TEXT,
                notes TEXT,
                is_active INTEGER DEFAULT 1
            )
        """
        )

        # Πίνακας Ραντεβού
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS APPOINTMENTS (
                appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                user_id INTEGER,
                employee_id INTEGER,
                appt_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                duration INTEGER DEFAULT 30,
                notes TEXT,
                FOREIGN KEY (customer_id) REFERENCES CUSTOMERS(customer_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES USERS(user_id),
                FOREIGN KEY (employee_id) REFERENCES EMPLOYEES(employee_id)
            )
        """
        )

        # Πίνακας Καταγραφής Εισόδων (Audit Log)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS USER_LOGINS (
                login_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                login_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                logout_timestamp TIMESTAMP,
                ip_address TEXT,
                FOREIGN KEY (user_id) REFERENCES USERS(user_id)
            )
        """
        )

        # Πίνακας Ρυθμίσεων Επιχείρησης
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS BUSINESS_SETTINGS (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT
            )
        """
        )

        # Αρχικοποίηση βασικών ρόλων
        conn.execute("INSERT OR IGNORE INTO ROLES (role_name) VALUES ('admin')")
        conn.execute("INSERT OR IGNORE INTO ROLES (role_name) VALUES ('user')")
        conn.execute("INSERT OR IGNORE INTO ROLES (role_name) VALUES ('Staff')")

        # Δημιουργία default admin αν δεν υπάρχει
        admin_exists = conn.execute("SELECT 1 FROM USERS WHERE username = 'admin'").fetchone()
        if not admin_exists:
            hashed = hash_password("admin")
            conn.execute(
                "INSERT INTO USERS (username, password, role_id, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                ("admin", hashed, 1, "Admin", "Admin"),
            )

        # Default Settings
        conn.execute("INSERT OR IGNORE INTO BUSINESS_SETTINGS (setting_key, setting_value) VALUES ('company_name', 'RandeBoo Demo')")
        conn.execute("INSERT OR IGNORE INTO BUSINESS_SETTINGS (setting_key, setting_value) VALUES ('slot_duration', '30')")
        
        # Προσθήκη weekly_schedule αν λείπει (για τα tests του gui)
        sched = {
            "mon": {"s1_s": "09:00", "s1_e": "14:00", "s2_s": "17:00", "s2_e": "21:00"},
            "tue": {"s1_s": "09:00", "s1_e": "14:00", "s2_s": "17:00", "s2_e": "21:00"},
            "wed": {"s1_s": "09:00", "s1_e": "14:00", "s2_s": "17:00", "s2_e": "21:00"},
            "thu": {"s1_s": "09:00", "s1_e": "14:00", "s2_s": "17:00", "s2_e": "21:00"},
            "fri": {"s1_s": "09:00", "s1_e": "14:00", "s2_s": "17:00", "s2_e": "21:00"},
            "sat": {"s1_s": "09:00", "s1_e": "14:00"},
            "sun": {"closed": True}
        }
        conn.execute("INSERT OR IGNORE INTO BUSINESS_SETTINGS (setting_key, setting_value) VALUES ('weekly_schedule', ?)", (json.dumps(sched),))

        # Έλεγχος και προσθήκη στηλών αν λείπουν
        # Προσθήκη is_active στο USERS
        user_cols = [r["name"] for r in conn.execute("PRAGMA table_info(USERS)").fetchall()]
        if "is_active" not in user_cols:
            conn.execute("ALTER TABLE USERS ADD COLUMN is_active INTEGER DEFAULT 1")

        # Προσθήκη first_login στο USERS
        if "first_login" not in user_cols:
            conn.execute("ALTER TABLE USERS ADD COLUMN first_login INTEGER DEFAULT 1")

        # Προσθήκη specialization στο EMPLOYEES
        emp_cols = [r["name"] for r in conn.execute("PRAGMA table_info(EMPLOYEES)").fetchall()]
        if "specialization" not in emp_cols:
            conn.execute("ALTER TABLE EMPLOYEES ADD COLUMN specialization TEXT")

        # Προσθήκη specialty στο EMPLOYEES
        if "specialty" not in emp_cols:
            conn.execute("ALTER TABLE EMPLOYEES ADD COLUMN specialty TEXT")

        conn.commit()
    finally:
        conn.close()


# =============================================================================
# ΑΣΦΑΛΕΙΑ & AUTHENTICATION
# =============================================================================


def hash_password(password: str) -> str:
    """Κρυπτογραφεί έναν κωδικό πρόσβασης."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    """Ελέγχει αν ο κωδικός αντιστοιχεί στο hash."""
    try:
        if isinstance(hashed, str):
            hashed = hashed.encode("utf-8")
        return bcrypt.checkpw(password.encode("utf-8"), hashed)
    except Exception:
        return False


def authenticate_user(username: str, password: str) -> dict | None:
    """Ελέγχει τα διαπιστευτήρια του χρήστη και καταγράφει το login."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM USERS WHERE username = ? AND is_active = 1", (username,)).fetchone()
        if row and check_password(password, row["password"]):
            user_profile = dict(row)
            # Καταγραφή login
            cursor = conn.execute("INSERT INTO USER_LOGINS (user_id) VALUES (?)", (user_profile["user_id"],))
            conn.commit()
            user_profile["last_login_id"] = cursor.lastrowid
            user_profile["id_login"] = cursor.lastrowid
            user_profile["id"] = user_profile["user_id"] # Για συμβατότητα με παλιά tests
            return user_profile
        return None
    finally:
        conn.close()


def record_logout(login_id: int) -> None:
    """Ενημερώνει το timestamp εξόδου για μια συνεδρία."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE USER_LOGINS SET logout_timestamp = CURRENT_TIMESTAMP WHERE login_id = ?",
            (login_id,),
        )
        conn.commit()
    finally:
        conn.close()


def change_password(user_id: int, new_password: str) -> bool:
    """Αλλάζει τον κωδικό πρόσβασης ενός χρήστη."""
    hashed = hash_password(new_password)
    return update_user_password_raw(user_id, hashed)


# =============================================================================
# ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ
# =============================================================================


def _to_iso_date(date_str: str) -> str:
    """Μετατρέπει ημερομηνία από DD/MM/YYYY σε YYYY-MM-DD."""
    if not date_str: return None
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return date_str


def _calculate_end_time(start_time: str, duration: int) -> str:
    """Υπολογίζει την ώρα λήξης βάσει έναρξης και διάρκειας."""
    start_dt = datetime.strptime(start_time, "%H:%M")
    end_dt = start_dt + timedelta(minutes=duration)
    return end_dt.strftime("%H:%M")


# =============================================================================
# CRUD — ΧΡΗΣΤΕΣ (USERS)
# =============================================================================


def create_user(username: str, password: str, role_id: int = 2, first_name: str = "", last_name: str = "", email: str = "", phone: str = "", is_active: int = 1) -> bool:
    """Δημιουργεί έναν νέο χρήστη."""
    hashed = hash_password(password)
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO USERS (username, password, role_id, first_name, last_name, email, phone, is_active) 
               VALUES (?, ?, ?, ?, ?, ?, ?,?)""",
            (username, hashed, role_id, first_name, last_name, email, phone,is_active),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_user_id(username: str) -> int | None:
    conn = get_connection()
    try:
        row = conn.execute("SELECT user_id FROM USERS WHERE username = ?", (username,)).fetchone()
        return row["user_id"] if row else None
    finally:
        conn.close()


def get_user_by_username(username: str) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM USERS WHERE username = ?", (username,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all_users() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT u.*, r.role_name FROM USERS u JOIN ROLES r ON u.role_id = r.role_id"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def search_users(keyword: str | None = None, name: str | None = None, last_name: str | None = None, email: str | None = None, username: str | None = None) -> list[dict]:
    """Αναζήτηση χρηστών βάσει πολλαπλών κριτηρίων."""
    conn = get_connection()
    try:
        query = "SELECT * FROM USERS WHERE 1=1"
        params = []
        if keyword:
            query += " AND (first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR username LIKE ?)"
            p = f"%{keyword}%"
            params.extend([p, p, p, p])
        if name:
            query += " AND first_name LIKE ?"
            params.append(f"%{name}%")
        if last_name:
            query += " AND last_name LIKE ?"
            params.append(f"%{last_name}%")
        if email:
            query += " AND email LIKE ?"
            params.append(f"%{email}%")
        if username:
            query += " AND username LIKE ?"
            params.append(f"%{username}%")
            
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_user(user_id: int) -> bool:
    """Διαγράφει έναν χρήστη."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM USERS WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def update_user(user_id: int, username: str, first_name: str, last_name: str, phone: str | None = None, email: str | None = None, role_id: int | None = None, is_active: int = 1) -> bool:
    """Ενημερώνει τα στοιχεία ενός χρήστη."""
    conn = get_connection()
    try:
        # Έλεγχος αν ο χρήστης υπάρχει
        exists = conn.execute("SELECT 1 FROM USERS WHERE user_id = ?", (user_id,)).fetchone()
        if not exists: return False

        # Έλεγχος για διπλότυπο username (αν άλλαξε)
        dupe = conn.execute("SELECT 1 FROM USERS WHERE username = ? AND user_id != ?", (username, user_id)).fetchone()
        if dupe: return False

        conn.execute(
            """UPDATE USERS SET username=?, first_name=?, last_name=?, phone=?, email=?, role_id=?, is_active=?
               WHERE user_id=?""",
            (username, first_name, last_name, phone, email, role_id, is_active, user_id),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def update_user_password_raw(user_id: int, new_password_hash: str) -> bool:
    """Εσωτερική συνάρτηση για αλλαγή κωδικού με ήδη έτοιμο hash."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE USERS SET password = ?, first_login = 0 WHERE user_id = ?",
            (new_password_hash, user_id),
        )
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def update_user_password(user_id: int, new_password_hash: str) -> bool:
    # Alias για συμβατότητα με υπάρχοντα κώδικα
    return update_user_password_raw(user_id, new_password_hash)

def get_all_roles() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM ROLES").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_user_logins(user_id: int | None = None, limit: int | None = None) -> list[dict]:
    """Επιστρέφει το ιστορικό εισόδων."""
    conn = get_connection()
    try:
        query = "SELECT * FROM USER_LOGINS"
        params = []
        if user_id:
            query += " WHERE user_id = ?"
            params.append(user_id)
        query += " ORDER BY login_timestamp DESC"
        if limit:
            query += f" LIMIT {int(limit)}"
        
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# =============================================================================
# CRUD — ΠΕΛΑΤΕΣ (CUSTOMERS)
# =============================================================================


def create_customer(first_name: str, last_name: str, phone: str | None, email: str) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO CUSTOMERS (first_name, last_name, phone, email) VALUES (?, ?, ?, ?)",
            (first_name, last_name, phone, email),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_customers() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM CUSTOMERS ORDER BY last_name ASC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_customer_by_id(customer_id: int) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM CUSTOMERS WHERE customer_id = ?", (customer_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_customer_by_email(email: str) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM CUSTOMERS WHERE email = ?", (email,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_customer(customer_id: int, first_name: str, last_name: str, phone: str | None, email: str) -> bool:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE CUSTOMERS SET first_name=?, last_name=?, phone=?, email=? WHERE customer_id=?",
            (first_name, last_name, phone, email, customer_id),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def delete_customer(customer_id: int) -> bool:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM CUSTOMERS WHERE customer_id=?", (customer_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def search_customers(keyword: str | None = None, name: str | None = None, last_name: str | None = None, email: str | None = None, phone: str | None = None) -> list[dict]:
    """Αναζήτηση πελατών βάσει πολλαπλών κριτηρίων."""
    conn = get_connection()
    try:
        query = "SELECT * FROM CUSTOMERS WHERE 1=1"
        params = []
        if keyword:
            query += " AND (first_name LIKE ? OR last_name LIKE ? OR email LIKE ? OR phone LIKE ?)"
            p = f"%{keyword}%"
            params.extend([p, p, p, p])
        if name:
            query += " AND first_name LIKE ?"
            params.append(f"%{name}%")
        if last_name:
            query += " AND last_name LIKE ?"
            params.append(f"%{last_name}%")
        if email:
            query += " AND email LIKE ?"
            params.append(f"%{email}%")
        if phone:
            query += " AND phone LIKE ?"
            params.append(f"%{phone}%")
            
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# =============================================================================
# CRUD — ΥΠΑΛΛΗΛΟΙ (EMPLOYEES)
# =============================================================================


def create_employee(first_name: str, last_name: str, phone: str | None, email: str, specialization: str | None = None, specialty: str | None = None, hire_date: str | None = None, notes: str | None = None, user_id: int | None = None, is_active: int = 1) -> int:
    """Δημιουργεί έναν νέο υπάλληλο."""
    iso_hire = _to_iso_date(hire_date) if hire_date else None
    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO EMPLOYEES (first_name, last_name, specialization, specialty, phone, email, hire_date, notes, is_active) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (first_name, last_name, specialization or specialty, specialty or specialization, phone, email, iso_hire, notes, is_active),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_employees() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM EMPLOYEES ORDER BY last_name").fetchall()
        employee_records = []
        for r in rows:
            d = dict(r)
            d["id"] = d["employee_id"] # Compatibility
            employee_records.append(d)
        return employee_records
    finally:
        conn.close()


def get_active_employees() -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM EMPLOYEES WHERE is_active = 1 ORDER BY last_name"
        ).fetchall()
        employee_records = []
        for r in rows:
            d = dict(r)
            d["id"] = d["employee_id"] # Compatibility
            employee_records.append(d)
        return employee_records
    finally:
        conn.close()


def update_employee(employee_id: int, first_name: str, last_name: str, phone: str | None, email: str, specialization: str | None = None, specialty: str | None = None, hire_date: str | None = None, notes: str | None = None, is_active: int = 1) -> bool:
    """Ενημερώνει τα στοιχεία ενός υπαλλήλου."""
    iso_hire = _to_iso_date(hire_date) if hire_date else None
    conn = get_connection()
    try:
        conn.execute(
            """UPDATE EMPLOYEES SET first_name=?, last_name=?, specialization=?, specialty=?, phone=?, email=?, hire_date=?, notes=?, is_active=? 
               WHERE employee_id=?""",
            (first_name, last_name, specialization or specialty, specialty or specialization, phone, email, iso_hire, notes, is_active, employee_id),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def delete_employee(employee_id: int) -> bool:
    conn = get_connection()
    try:
        conn.execute("UPDATE EMPLOYEES SET is_active = 0 WHERE employee_id=?", (employee_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def search_employees(name: str = "", last_name: str = "", spec: str = "", email: str = "", specialization: str | None = None, specialty: str | None = None, phone: str | None = None) -> list[dict]:
    """Αναζήτηση υπαλλήλων."""
    conn = get_connection()
    try:
        # Αναζήτηση μόνο ενεργών υπαλλήλων
        query = "SELECT * FROM EMPLOYEES WHERE is_active = 1"
        params = []

        actual_spec = specialization or specialty or spec
        if name:
            query += " AND (first_name LIKE ? OR last_name LIKE ?)"
            params.extend([f"%{name}%", f"%{name}%"])
        if last_name:
            query += " AND last_name LIKE ?"
            params.append(f"%{last_name}%")
        if actual_spec:
            query += " AND (specialization LIKE ? OR specialty LIKE ?)"
            params.extend([f"%{actual_spec}%", f"%{actual_spec}%"])
        if email:
            query += " AND email LIKE ?"
            params.append(f"%{email}%")
        if phone:
            query += " AND phone LIKE ?"
            params.append(f"%{phone}%")

        query += " ORDER BY last_name"

        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()



# =============================================================================
# CRUD — ΡΑΝΤΕΒΟΥ (APPOINTMENTS)
# =============================================================================


def check_overlap(
    date: str, time: str, duration: int, employee_id: int | None = None, exclude_id: int | None = None
) -> bool:
    """
    Ελέγχου αν ο συγκεκριμένος υπάλληλος έχει άλλο ραντεβού την ίδια ώρα.
    """
    if employee_id is None:
        return False

    iso_date = _to_iso_date(date)
    new_end = _calculate_end_time(time, duration)
    conn = get_connection()
    try:
        query = """
            SELECT appointment_id FROM APPOINTMENTS 
            WHERE appt_date = ? AND employee_id = ? 
            AND ? < end_time AND start_time < ? 
            AND notes NOT LIKE '%[DELETED]%'
        """
        params = [iso_date, employee_id, time, new_end]
        if exclude_id:
            query += " AND appointment_id != ?"
            params.append(exclude_id)

        row = conn.execute(query, params).fetchone()
        return row is not None
    finally:
        conn.close()


def check_business_capacity(
    date: str, time: str, duration: int, exclude_id: int | None = None
) -> bool:
    """
    Ελέγχου αν η επιχείρηση έχει φτάσει στο μέγιστο όριο (πλήθος υπαλλήλων) για το συγκεκριμένο slot.
    """
    iso_date = _to_iso_date(date)
    new_end = _calculate_end_time(time, duration)
    conn = get_connection()
    try:
        query = """
            SELECT COUNT(*) as count FROM APPOINTMENTS 
            WHERE appt_date = ? AND ? < end_time AND start_time < ? 
            AND notes NOT LIKE '%[DELETED]%'
        """
        params = [iso_date, time, new_end]
        if exclude_id:
            query += " AND appointment_id != ?"
            params.append(exclude_id)

        appt_count = conn.execute(query, params).fetchone()["count"]
        active_emp_count = conn.execute(
            "SELECT COUNT(*) as count FROM EMPLOYEES WHERE is_active = 1"
        ).fetchone()["count"]
        limit = max(1, active_emp_count)

        return appt_count >= limit
    finally:
        conn.close()


def create_appointment(
    customer_id: int,
    user_id: int,
    date: str,
    time: str,
    duration: int = DEFAULT_DURATION_MINUTES,
    notes: str = "",
    employee_id: int | None = None,
) -> tuple[bool, str | int]:
    """Δημιουργεί ένα νέο ραντεβού, αφού ελέγξει για επικαλύψεις υπαλλήλου και χωρητικότητα."""

    # 1. Έλεγχος αν ο υπάλληλος είναι ήδη κλεισμένος
    if employee_id and check_overlap(date, time, duration, employee_id):
        return (False, "Ο επιλεγμένος υπάλληλος έχει ήδη άλλο ραντεβού την ίδια ώρα!")

    # 2. Έλεγχος συνολικής χωρητικότητας επιχείρησης
    if check_business_capacity(date, time, duration):
        return (
            False,
            "Η επιχείρηση είναι πλήρης για αυτή την ώρα (υπάρχει ήδη κλεισμένο ραντεβού)!",
        )

    iso_date = _to_iso_date(date)
    end_time = _calculate_end_time(time, duration)
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO APPOINTMENTS (customer_id, user_id, employee_id, appt_date, start_time, end_time, duration, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer_id,
                user_id,
                employee_id,
                iso_date,
                time,
                end_time,
                duration,
                notes,
            ),
        )
        conn.commit()
        last_id = cursor.lastrowid
        return (True, last_id)
    except Exception as e:
        return (False, str(e))
    finally:
        conn.close()


def update_appointment(
    appointment_id: int,
    customer_id: int,
    user_id: int,
    date: str,
    time: str,
    duration: int = DEFAULT_DURATION_MINUTES,
    notes: str = "",
    employee_id: int | None = None,
) -> tuple[bool, str]:
    """Ενημερώνει ένα ραντεβού, ελέγχοντας για επικαλύψεις υπαλλήλου και χωρητικότητα."""

    # 1. Έλεγχος αν ο υπάλληλος είναι ήδη κλεισμένος (εξαιρουμένου του τρέχοντος ραντεβού)
    if employee_id and check_overlap(
        date, time, duration, employee_id, exclude_id=appointment_id
    ):
        return (False, "Ο επιλεγμένος υπάλληλος έχει ήδη άλλο ραντεβού την ίδια ώρα!")

    # 2. Έλεγχος συνολικής χωρητικότητας (εξαιρουμένου του τρέχοντος ραντεβού)
    if check_business_capacity(date, time, duration, exclude_id=appointment_id):
        return (False, "Η επιχείρηση είναι πλήρης για αυτή την ώρα (υπάρχει ήδη κλεισμένο ραντεβού)!")

    iso_date = _to_iso_date(date)
    end_time = _calculate_end_time(time, duration)
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE APPOINTMENTS
            SET customer_id = ?, user_id = ?, employee_id = ?, appt_date = ?, start_time = ?, end_time = ?, duration = ?, notes = ?
            WHERE appointment_id = ?
            """,
            (
                customer_id,
                user_id,
                employee_id,
                iso_date,
                time,
                end_time,
                duration,
                notes,
                appointment_id,
            ),
        )
        conn.commit()
        return (True, "Success")
    except Exception as e:
        return (False, str(e))
    finally:
        conn.close()


def delete_appointment(appointment_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "DELETE FROM APPOINTMENTS WHERE appointment_id = ?", (appointment_id,)
        )
        conn.commit()
    finally:
        conn.close()


def get_day_appointments(date_str: str) -> list:
    iso_date = _to_iso_date(date_str)
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT a.*, c.first_name || ' ' || c.last_name AS customer_name,
                   e.first_name || ' ' || e.last_name AS employee_name
            FROM APPOINTMENTS a
            LEFT JOIN CUSTOMERS c ON a.customer_id = c.customer_id
            LEFT JOIN EMPLOYEES e ON a.employee_id = e.employee_id
            WHERE a.appt_date = ? ORDER BY a.start_time ASC
        """,
            (iso_date,),
        ).fetchall()
        appointments_records = []
        for r in rows:
            d = dict(r)
            d["id"] = d["appointment_id"]
            appointments_records.append(d)
        return appointments_records
    finally:
        conn.close()


def get_dashboard_stats() -> dict:
    """
    ΣΚΟΠΟΣ: Επιστρέφει εμπλουτισμένα στατιστικά για το Dashboard.
    ΔΕΔΟΜΕΝΑ: Σημερινά, αυριανά, εβδομαδιαία ραντεβού, πελάτες, υπάλληλοι,
              συνολικά ραντεβού.
    """
    conn = get_connection()
    try:
        today_iso = datetime.now().strftime("%Y-%m-%d")
        tomorrow_iso = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        week_end_iso = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        month_start_iso = datetime.now().strftime("%Y-%m-01")

        today_count = conn.execute(
            "SELECT COUNT(*) FROM APPOINTMENTS WHERE appt_date = ?",
            (today_iso,),
        ).fetchone()[0]

        tomorrow_count = conn.execute(
            "SELECT COUNT(*) FROM APPOINTMENTS WHERE appt_date = ?",
            (tomorrow_iso,),
        ).fetchone()[0]

        week_count = conn.execute(
            "SELECT COUNT(*) FROM APPOINTMENTS WHERE appt_date BETWEEN ? AND ?",
            (today_iso, week_end_iso),
        ).fetchone()[0]

        month_count = conn.execute(
            "SELECT COUNT(*) FROM APPOINTMENTS WHERE appt_date >= ?",
            (month_start_iso,),
        ).fetchone()[0]

        total_customers = conn.execute("SELECT COUNT(*) FROM CUSTOMERS").fetchone()[0]

        active_employees = conn.execute(
            "SELECT COUNT(*) FROM EMPLOYEES WHERE is_active = 1"
        ).fetchone()[0]

        total_appointments = conn.execute(
            "SELECT COUNT(*) FROM APPOINTMENTS"
        ).fetchone()[0]

        return {
            "today_appointments": today_count,
            "tomorrow_appointments": tomorrow_count,
            "week_appointments": week_count,
            "month_appointments": month_count,
            "total_customers": total_customers,
            "active_employees": active_employees,
            "total_appointments": total_appointments,
        }
    finally:
        conn.close()


# =============================================================================
# CRUD — ΡΥΘΜΙΣΕΙΣ (BUSINESS SETTINGS)
# =============================================================================


def get_business_settings() -> dict:
    """Επιστρέφει τις ρυθμίσεις της επιχείρησης ως λεξικό."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT setting_key, setting_value FROM BUSINESS_SETTINGS"
        ).fetchall()
        settings_dict = {r["setting_key"]: r["setting_value"] for r in rows}
        # Default values αν λείπουν
        if "company_name" not in settings_dict: settings_dict["company_name"] = "RandeBoo Demo"
        return settings_dict
    finally:
        conn.close()


def update_business_settings(settings: dict) -> bool:
    """Ενημερώνει τις ρυθμίσεις της επιχείρησης βάσει κλειδιού."""
    conn = get_connection()
    try:
        for key, value in settings.items():
            conn.execute(
                "INSERT OR REPLACE INTO BUSINESS_SETTINGS (setting_key, setting_value) VALUES (?, ?)",
                (key, value),
            )
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()


def get_appointment_count_by_date() -> list:
    """Συγκεντρωτικά δεδομένα ραντεβού ανά ημέρα για γραφήματα."""
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT appt_date AS date, COUNT(*) AS count
            FROM APPOINTMENTS
            GROUP BY appt_date
            ORDER BY appt_date
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_appointment_count_by_month() -> list:
    """Συγκεντρωτικά δεδομένα ραντεβού ανά μήνα για αναφορές."""
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT strftime("%m/%Y", appt_date) AS month, COUNT(*) AS count
            FROM APPOINTMENTS
            GROUP BY month
            ORDER BY strftime("%Y-%m", appt_date)
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_appointment_count_by_customer() -> list:
    """Κατάταξη πελατών βάσει αριθμού ραντεβού."""
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT c.first_name || " " || c.last_name AS name, COUNT(*) AS count
            FROM APPOINTMENTS a
            JOIN CUSTOMERS c ON a.customer_id = c.customer_id
            GROUP BY a.customer_id
            ORDER BY count DESC
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_appointment_count_by_employee() -> list:
    """Κατάταξη υπαλλήλων βάσει αριθμού ραντεβού."""
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT e.first_name || " " || e.last_name AS name, COUNT(*) AS count
            FROM APPOINTMENTS a
            JOIN EMPLOYEES e ON a.employee_id = e.employee_id
            GROUP BY a.employee_id
            ORDER BY count DESC
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
