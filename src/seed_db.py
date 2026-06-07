import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker
from database import get_connection, init_db

# Αρχικοποίηση της Faker για ελληνικά δεδομένα
fake = Faker("el_GR")

# Λίστα με notes για πελάτες
CUSTOMER_NOTES_TEMPLATES = [
    "Προτιμάει ζεστά χρώματα στα μαλλιά.",
    "Ευαίσθητο τριχωτό κεφαλής, χρειάζεται υποαλλεργικό σαμπουάν.",
    "Θέλει πάντα καφέ φίλτρου κατά την περιποίηση.",
    "Συνήθως επιλέγει συνδυασμό κούρεμα και βάψιμο.",
    "Προτιμάει συγκεκριμένο σαμπουάν με κερατίνη.",
    "Εξαιρετικά συνεπής στα ραντεβού της.",
    "Προτιμάει απογευματινά ραντεβού μετά τη δουλειά.",
    "Θέλει έντονο μακιγιάζ για βραδινές εξόδους.",
    "Κάνει πάντα κράτηση για μανικιούρ και πεντικιούρ μαζί.",
    "Νέος πελάτης, σύσταση από φίλο.",
    "Προτιμάει ήσυχη γωνία κατά τη διάρκεια της βαφής."
]

# Λίστα για υπαλλήλους
EMPLOYEE_NOTES_TEMPLATES = [
    "Εξειδίκευση σε νυφικά χτενίσματα και πλεξούδες.",
    "Πολύ καλή στη διαχείριση χρόνου και στα γρήγορα χτενίσματα.",
    "Εμπειρία 5 ετών σε κομμώσεις και τεχνικές μπαλαγιάζ.",
    "Ειδικός στο ανδρικό κούρεμα (barbering).",
    "Εξειδίκευση στο μακιγιάζ για φωτογραφίσεις και γάμους.",
    "Πάντα ευγενικός και χαμογελαστός με τους πελάτες.",
    "Πολύ οργανωτικός στην υποδοχή και στα τηλέφωνα.",
    "Συνεργάζεται άψογα με την υπόλοιπη ομάδα.",
    "Εξειδίκευση σε θεραπείες αναδόμησης μαλλιών."
]

# Λίστα με σημειώσεις ραντεβού
APPOINTMENT_NOTES_TEMPLATES = [
    "Βάψιμο/κούρεμα και χτένισμα.",
    "Βάψιμο με την L'Oreal βαφή μαλλιών.",
    "Βάψιμο με την Wella βαφή μαλλιών.",
    "Κούρεμα γυναικείο και χτένισμα.",
    "Βαφή ρίζα, ρεφλέ και ανταύγειες.",
    "Μακιγιάζ για βραδινή έξοδο/πάρτι.",
    "Ανδρικό κούρεμα και περιποίηση γενειάδας με ζεστή πετσέτα.",
    "Μανικιούρ ημιμόνιμο με nail art.",
    "Θεραπεία κερατίνης για λείανση.",
    "Κούρεμα παιδικό.",
    "Αλλαγή χρώματος μαλλιών (ombre).",
    "Δοκιμαστικό νυφικού μακιγιάζ.",
    "Χτένισμα και ίσιωμα μαλλιών.",
    "Χτένισμα απλό.",
    "Βαφή/κούρεμα."
]


def seed_customers(count: int = 15) -> list[int]:
    """
    Δημιουργεί εικονικούς πελάτες στη βάση δεδομένων και επιστρέφει τα IDs τους.
    """
    # Σύνδεση με τη βάση δεδομένων
    connection = get_connection()
    cursor = connection.cursor()
    customer_ids = []

    # Δημιουργία των εγγραφών
    for _ in range(count):
        # Παραγωγή τυχαίων στοιχείων με τη Faker
        first_name = fake.first_name()
        last_name = fake.last_name()
        phone = fake.phone_number()
        email = fake.unique.email()
        notes = random.choice(CUSTOMER_NOTES_TEMPLATES)

        # Εισαγωγή στον πίνακα CUSTOMERS
        cursor.execute(
            "INSERT INTO CUSTOMERS (first_name, last_name, phone, email, notes) VALUES (?, ?, ?, ?, ?)",
            (first_name, last_name, phone, email, notes)
        )
        # Κρατάμε το ID του πελάτη που μόλις εισήχθη
        customer_ids.append(cursor.lastrowid)

    # Αποθήκευση αλλαγών και κλείσιμο σύνδεσης
    connection.commit()
    connection.close()
    
    print(f"Επιτυχής εισαγωγή {count} πελατών.")
    return customer_ids

def seed_employees(count: int = 5) -> list[int]:
    """
    Δημιουργεί εικονικούς υπαλλήλους στη βάση δεδομένων και επιστρέφει τα IDs τους.
    """
    connection = get_connection()
    cursor = connection.cursor()
    employee_ids = []

    # Λίστα με τις πραγματικές ειδικότητες της επιχείρησης
    specialties = ["Μακιγιάζ", "Γενικών Καθηκόντων", "Κομμωτής/τρια"]

    for _ in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        phone = fake.phone_number()
        email = fake.unique.email()
        specialty = random.choice(specialties)
        # Τυχαία ημερομηνία πρόσληψης τα τελευταία 2 χρόνια
        hire_date = fake.date_between(start_date = "-2y", end_date = "today").strftime("%Y-%m-%d")
        notes = random.choice(EMPLOYEE_NOTES_TEMPLATES)

        # Εισαγωγή στον πίνακα EMPLOYEES
        cursor.execute(
            """INSERT INTO EMPLOYEES (first_name, last_name, specialization, specialty, phone, email, hire_date, notes, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            (first_name, last_name, specialty, specialty, phone, email, hire_date, notes)
        )
        employee_ids.append(cursor.lastrowid)

    connection.commit()
    connection.close()

    print(f"Επιτυχής εισαγωγή {count} υπαλλήλων.")
    return employee_ids

def seed_appointments(customer_ids: list[int], employee_ids: list[int], count: int = 30, days_span: int = 30, start_date: str | datetime = "today") -> None:
    """
    Δημιουργεί εικονικά ραντεβού συνδέοντας τυχαία πελάτες και υπαλλήλους.
    Διασφάλιση των ραντεβού σύμφωνα με τις ρυθμίσεις της επιχείρησης.
    """
    import holidays as gr_holidays_lib
    from database import get_business_settings

    connection = get_connection()
    cursor = connection.cursor()

    # Λήψη αργιών επιχείρησης
    try:
        settings = get_business_settings()
        blackouts = settings.get("blackout_dates", "").split(",")
        duration = int(settings.get("slot_duration", 30))
    except Exception:
        blackouts = []
        duration = 30

    # Ορίζουμε τις ώρες έναρξης των ραντεβού
    start_times = ["09:00", "10:00", "11:00", "12:00", "13:00", "17:00", "18:00", "19:00", "20:00"]

    for _ in range(count):
        customer_id = random.choice(customer_ids)
        employee_id = random.choice(employee_ids)
        
        # Εύρεση έγκυρης εργάσιμης ημέρας
        while True:
            # Καθορισμός χρονικών ορίων για τη Faker με βάση την ημερομηνία έναρξης
            if start_date == "today":
                start_ref = "today"
                end_ref = f"+{days_span}d"
            else:
                start_ref = start_date
                end_ref = start_date + timedelta(days = days_span)

            appt_date_obj = fake.date_between(start_date = start_ref, end_date = end_ref)
            
            # 1. Έλεγχος αν είναι Κυριακή
            if appt_date_obj.weekday() == 6:
                continue
                
            # 2. Έλεγχος αν είναι επίσημη αργία στην Ελλάδα
            gr_holidays = gr_holidays_lib.Greece(years = appt_date_obj.year, language = "el")
            if appt_date_obj in gr_holidays:
                continue
                
            # 3. Έλεγχος αν είναι custom αργία της επιχείρησης (blackout date)
            if appt_date_obj.isoformat() in blackouts:
                continue
                
            # Αν περάσει όλους τους ελέγχους, η ημερομηνία είναι έγκυρη
            appt_date = appt_date_obj.strftime("%Y-%m-%d")
            break

        start_time = random.choice(start_times)
        
        # Υπολογισμός ώρας λήξης
        start_dt = datetime.strptime(start_time, "%H:%M")
        end_dt = start_dt + timedelta(minutes = duration)
        end_time = end_dt.strftime("%H:%M")
        
        notes = random.choice(APPOINTMENT_NOTES_TEMPLATES)

        # Εισαγωγή στον πίνακα APPOINTMENTS
        cursor.execute(
            """INSERT INTO APPOINTMENTS (customer_id, user_id, employee_id, appt_date, start_time, end_time, duration, notes)
               VALUES (?, 1, ?, ?, ?, ?, ?, ?)""",
            (customer_id, employee_id, appt_date, start_time, end_time, duration, notes)
        )

    connection.commit()
    connection.close()
    print(f"Επιτυχής εισαγωγή {count} ραντεβού σε εργάσιμες ημέρες.")

def get_existing_customers() -> list[int]:
    """
    Ανακτά τα IDs των ήδη υπαρχόντων πελατών από τη βάση δεδομένων.
    """
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT customer_id FROM CUSTOMERS")
    customer_ids = [row[0] for row in cursor.fetchall()]
    connection.close()
    return customer_ids

def get_existing_employees() -> list[int]:
    """
    Ανακτά τα IDs των ήδη υπαρχόντων ενεργών υπαλλήλων από τη βάση δεδομένων.
    """
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT employee_id FROM EMPLOYEES WHERE is_active = 1")
    employee_ids = [row[0] for row in cursor.fetchall()]
    connection.close()
    return employee_ids

def run_seeder() -> None:
    """
    Κεντρική συνάρτηση που εκτελεί τη διαδικασία αρχικοποίησης και εισαγωγής δεδομένων.
    Παρέχει ένα διαδραστικό μενού (CLI menu) για την παραμετροποίηση των δεδομένων.
    """
    print("=== Μενού Δημιουργίας Mock Δεδομένων ===")
    
    # 1. Εισαγωγή πλήθους υπαλλήλων
    try:
        employees_input = input("Πόσους νέους υπαλλήλους θέλετε να δημιουργήσετε; [Default: 5]: ")
        num_employees = int(employees_input) if employees_input.strip() else 5
    except ValueError:
        print("Μη έγκυρος αριθμός. Χρήση default τιμής: 5")
        num_employees = 5

    # 2. Εισαγωγή πλήθους πελατών
    try:
        customers_input = input("Πόσους νέους πελάτες θέλετε να δημιουργήσετε; [Default: 20]: ")
        num_customers = int(customers_input) if customers_input.strip() else 20
    except ValueError:
        print("Μη έγκυρος αριθμός. Χρήση default τιμής: 20")
        num_customers = 20

    # 3. Εισαγωγή πλήθους ραντεβού
    try:
        appts_input = input("Πόσα ραντεβού θέλετε να δημιουργήσετε; [Default: 40]: ")
        num_appts = int(appts_input) if appts_input.strip() else 40
    except ValueError:
        print("Μη έγκυρος αριθμός. Χρήση default τιμής: 40")
        num_appts = 40

    # 4. Εισαγωγή χρονικής περιόδου σε ημέρες
    try:
        days_input = input("Σε πόσες ημέρες από σήμερα να εκτείνονται τα ραντεβού; [Default: 30]: ")
        days_span = int(days_input) if days_input.strip() else 30
    except ValueError:
        print("Μη έγκυρος αριθμός. Χρήση default τιμής: 30")
        days_span = 30

    # 5. Εισαγωγή ημερομηνίας έναρξης ραντεβού
    start_date_input = input("Από ποια ημερομηνία να ξεκινήσουν τα ραντεβού; (DD/MM/YYYY ή 'today') [Default: today]: ")
    start_date = "today"
    if start_date_input.strip() and start_date_input.strip().lower() != "today":
        try:
            start_date = datetime.strptime(start_date_input.strip(), "%d/%m/%Y").date()
        except ValueError:
            print("Μη έγκυρη μορφή ημερομηνίας. Χρήση default τιμής: today")
            start_date = "today"

    print("\nΈναρξη αρχικοποίησης βάσης δεδομένων...")
    init_db()

    # Δημιουργία των δεδομένων με βάση τις επιλογές του χρήστη
    customer_ids = seed_customers(num_customers)
    employee_ids = seed_employees(num_employees)
    
    # Αν επιλέχθηκε να μη δημιουργηθούν νέοι, χρησιμοποιούμε τους ήδη υπάρχοντες στη βάση
    if not customer_ids:
        customer_ids = get_existing_customers()
    if not employee_ids:
        employee_ids = get_existing_employees()

    # Έλεγχος αν υπάρχουν διαθέσιμα στοιχεία για τη δημιουργία των ραντεβού
    if num_appts > 0:
        if not customer_ids or not employee_ids:
            print("Σφάλμα: Δεν υπάρχουν πελάτες ή υπάλληλοι στη βάση για να δημιουργηθούν ραντεβού!")
        else:
            seed_appointments(customer_ids, employee_ids, num_appts, days_span, start_date)
    
    print("\nΗ διαδικασία ολοκληρώθηκε με επιτυχία!")

if __name__ == "__main__":
    run_seeder()
