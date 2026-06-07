"""
Ο κώδικας του αρχείου συντάχθηκε από τον Καταξενό Χρήστο

=============================================================================
ΑΡΧΕΙΟ: backup.py
ΣΚΟΠΟΣ: Αυτοματοποιημένη και χειροκίνητη δημιουργία αντιγράφων ασφαλείας (.db)
=============================================================================
"""

import os
import shutil
import logging
import time
from datetime import datetime, timedelta
from tkinter import messagebox

import sys

# Project root resolution 
if getattr(sys, "frozen", False):
    _project_root = os.path.dirname(sys.executable)
else:
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.abspath(os.path.join(_script_dir, ".."))

DB_PATH = os.path.abspath(os.path.join(_project_root, "data", "randeboo.db"))
BACKUP_DIR = os.path.abspath(os.path.join(_project_root, "backups"))

def create_backup(silent: bool = True) -> bool:
    """
    Δημιουργεί ένα αντίγραφο ασφαλείας της βάσης δεδομένων.
    
    Ορίσματα:
        silent (bool): Αν είναι True, δεν εμφανίζει μηνύματα.
                       Αν είναι False, εμφανίζει παράθυρο επιβεβαίωσης/σφάλματος.
    
    Επιστρέφει:
        bool: True αν η διαδικασία ήταν επιτυχής, False σε διαφορετική περίπτωση.
    """
    try:
        # 1. Έλεγχος αν υπάρχει η βάση
        if not os.path.exists(DB_PATH):
            if not silent:
                messagebox.showerror("Σφάλμα Backup", f"Η βάση δεδομένων δεν βρέθηκε στο:\n{DB_PATH}")
            return False

        # 2. Δημιουργία φακέλου backups αν δεν υπάρχει
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR, exist_ok=True)

        # 3. Δημιουργία ονόματος αρχείου με timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.db"
        dest_path = os.path.join(BACKUP_DIR, backup_filename)

        # 4. Αντιγραφή αρχείου
        shutil.copy2(DB_PATH, dest_path)
        
        logging.info(f"Το Backup ολοκληρώθηκε επιτυχώς: {backup_filename}")

        if not silent:
            messagebox.showinfo("Επιτυχία Backup", 
                                f"Το αντίγραφο ασφαλείας δημιουργήθηκε επιτυχώς!\n\nΑρχείο: {backup_filename}\nΦάκελος: {BACKUP_DIR}")
        
        # 5. Καθαρισμός παλιών backups (Διατήρηση 5 ημερών, αλλά πάντα τουλάχιστον ένα)
        cleanup_old_backups()

        
        return True

    except Exception as e:
        error_msg = f"Αποτυχία δημιουργίας Backup: {str(e)}"
        logging.error(error_msg)
        if not silent:
            messagebox.showerror("Σφάλμα Backup", error_msg)
        return False

def get_available_backups() -> list:
    """Επιστρέφει μια λίστα με τα διαθέσιμα αρχεία backup στον φάκελο backups."""
    if not os.path.exists(BACKUP_DIR):
        return []
    files = [f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_") and f.endswith(".db")]
    return sorted(files, reverse=True)

def restore_backup(backup_file_path: str, silent: bool = False) -> bool:
    """
    Επαναφέρει τη βάση δεδομένων από ένα αρχείο backup.
    ΠΡΟΣΟΧΗ: Αντικαθιστά την τρέχουσα βάση.
    """
    try:
        if not os.path.exists(backup_file_path):
            if not silent:
                messagebox.showerror("Σφάλμα Ανάκτησης", "Το αρχείο backup δεν βρέθηκε.")
            return False

        # Δημιουργία backup της τρέχουσας (προληπτικά) πριν την επαναφορά
        create_backup(silent=True)

        # Αντικατάσταση
        shutil.copy2(backup_file_path, DB_PATH)
        
        logging.info(f"Η ανάκτηση ολοκληρώθηκε από το αρχείο: {backup_file_path}")
        
        if not silent:
            messagebox.showinfo("Επιτυχία Ανάκτησης", 
                                "Η βάση δεδομένων αποκαταστάθηκε επιτυχώς!\n\nΗ εφαρμογή πρέπει να επανεκκινηθεί.")
        return True

    except Exception as e:
        error_msg = f"Αποτυχία ανάκτησης: {str(e)}"
        logging.error(error_msg)
        if not silent:
            messagebox.showerror("Σφάλμα Ανάκτησης", error_msg)
        return False

def cleanup_old_backups() -> None:
    """
    Διαγράφει backup παλαιότερα των 5 ημερών.
    ΚΑΝΟΝΑΣ ΑΣΦΑΛΕΙΑΣ: Διατηρεί πάντα τουλάχιστον το πιο πρόσφατο backup, 
    ακόμα και αν είναι παλαιότερο των 5 ημερών.
    """
    try:
        backups = get_available_backups()
        if len(backups) <= 1:
            return # Τίποτα προς διαγραφή

        # Το πρώτο στη λίστα είναι το πιο πρόσφατο (λόγω reverse=True στο get_available_backups)
        # Το προστατεύουμε οπωσδήποτε
        backups_to_check = backups[1:]
        
        now = datetime.now()
        retention_period = timedelta(days=5)
        deleted_count = 0

        for filename in backups_to_check:
            file_path = os.path.join(BACKUP_DIR, filename)
            
            # Εξαγωγή ημερομηνίας από το όνομα: backup_YYYYMMDD_HHMMSS.db
            try:
                date_str = filename.split("_")[1] # YYYYMMDD
                file_date = datetime.strptime(date_str, "%Y%m%d")
                
                if (now - file_date) > retention_period:
                    os.remove(file_path)
                    deleted_count += 1
                    logging.info(f"Αυτόματος καθαρισμός: Διαγράφηκε παλιό backup {filename}")
            except (IndexError, ValueError):
                # Αν το όνομα δεν ακολουθεί το format, ελέγχουμε την ημερομηνία τροποποίησης
                mtime = os.path.getmtime(file_path)
                file_date = datetime.fromtimestamp(mtime)
                if (now - file_date) > retention_period:
                    os.remove(file_path)
                    deleted_count += 1
                    logging.info(f"Αυτόματος καθαρισμός (mtime): Διαγράφηκε παλιό αρχείο {filename}")

        if deleted_count > 0:
            logging.info(f"Ο καθαρισμός ολοκληρώθηκε. Διαγράφηκαν {deleted_count} αρχεία.")

    except Exception as e:
        logging.error(f"Σφάλμα κατά τον καθαρισμό παλιών backups: {e}")

if __name__ == "__main__":
    # Δοκιμαστική εκτέλεση
    print("Backups:", get_available_backups())
