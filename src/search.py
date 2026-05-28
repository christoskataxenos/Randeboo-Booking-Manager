"""
προσχεδιο για την αναζητηση και το φιλτραρισμα των ραντεβου
απο τον πανο βαρθαλιτη 

ΠΑΡΑΔΕΙΓΜΑ ΧΡΗΣΗΣ:
1. Στην αρχή του αρχείου σας βάζετε:
   import search

2. Οταν πατηθει το κουμπι της αναζητησης, τραβατε τα δεδομενα: 
   apotelesmata = search.search_appointments_by_customer("Λεξη ή Τηλεφωνο")

3. Τα πετατε στο δικο σας Treeview:
   for r in apotelesmata:
       tree.insert("", "end", values=(r["appt_date"], r["customer_name"], r["phone"]))
"""

import database

def clean_greek_letters(raw_text: str) -> str:
    # Καθαρισμός τόνων από ελληνικά γράμματα για την αποφυγή απώλειας αποτελεσμάτων
    if not raw_text:
        return ""
        
    accent_mapping = {
        'ά': 'α', 'έ': 'ε', 'ή': 'η', 'ί': 'ι', 'ό': 'ο', 'ύ': 'υ', 'ώ': 'ω',
        'Ά': 'Α', 'Έ': 'Ε', 'Ή': 'Η', 'Ί': 'Ι', 'Ό': 'Ο', 'Ύ': 'Υ', 'Ώ': 'Ω',
        'ϊ': 'ι', 'ϋ': 'υ', 'ΐ': 'ι', 'ΰ': 'υ'
    }
    
    clean_str = raw_text
    for accented, unaccented in accent_mapping.items():
        clean_str = clean_str.replace(accented, unaccented)
        
    # Μετατροπή σε πεζά καθώς η SQLite δεν υποστηρίζει case-insensitive σύγκριση στα ελληνικά
    return clean_str.lower()

def search_appointments_by_customer(search_term: str) -> list[dict]:
    # Αναζήτηση ραντεβού με βάση διάφορα πεδία (όνομα, επώνυμο, τηλέφωνο, email)
    if not search_term or len(search_term.strip()) < 2:
        return []
    clean_term = search_term.strip()
    db_conn = database.get_connection()
    
    # Καταχώρηση της custom SQL συνάρτησης NO_ACCENT
    db_conn.create_function("NO_ACCENT", 1, clean_greek_letters)
    
    try:
        # SQL ερώτημα για συσχέτιση ραντεβού, πελάτη και υπαλλήλου
        sql_search_command = """
            SELECT
                a.appointment_id,
                a.appt_date,
                a.start_time,
                a.end_time,
                a.duration,
                a.notes,
                c.first_name || ' ' || c.last_name AS customer_name,
                c.phone,
                c.email,
                e.first_name || ' ' || e.last_name AS employee_name
            FROM APPOINTMENTS a
            JOIN CUSTOMERS c ON a.customer_id = c.customer_id
            LEFT JOIN EMPLOYEES e ON a.employee_id = e.employee_id
            WHERE (
                NO_ACCENT(c.last_name) LIKE NO_ACCENT(?)
                OR NO_ACCENT(c.first_name) LIKE NO_ACCENT(?)
                OR NO_ACCENT(c.first_name || ' ' || c.last_name) LIKE NO_ACCENT(?)
                OR NO_ACCENT(c.last_name || ' ' || c.first_name) LIKE NO_ACCENT(?)
                OR c.phone LIKE ?
                OR NO_ACCENT(c.email) LIKE NO_ACCENT(?)
            )
            ORDER BY a.appt_date DESC, a.start_time ASC
        """

        matching_format = f"%{clean_term}%"
        # Σύνδεση των παραμέτρων αναζήτησης με τις αντίστοιχες θέσεις στο SQL query
        fetched_lines = db_conn.execute(
            sql_search_command, 
            (matching_format, matching_format, matching_format, matching_format, matching_format, matching_format)
        ).fetchall()

        # Μετατροπή των SQL rows σε dicts για χρήση από το γραφικό περιβάλλον (GUI)
        search_matches = []
        for line in fetched_lines:
            row_dict = dict(line)
            search_matches.append(row_dict)
            
        return search_matches

    except Exception as search_err:
        print(f"Σφάλμα κατά την εκτέλεση της αναζήτησης στη βάση: {search_err}")
        return []
    finally:
        db_conn.close()
