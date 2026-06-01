"""
Ο κώδικας του αρχείου συντάχθηκε από την Ομάδα ΠΛΗΠΡΟ (Team 1)

=============================================================================
ΑΡΧΕΙΟ: main.py
ΣΚΟΠΟΣ: Σημείο εκκίνησης εφαρμογής (Entry Point)
=============================================================================

ΒΙΒΛΙΟΘΗΚΕΣ:
    - logging (standard library — καταγραφή σφαλμάτων)
    - tkinter (standard library — tk, messagebox)
    - database (εσωτερικό module — init_db)
    - backup (εσωτερικό module — create_backup)
    - gui_login (εσωτερικό module — LoginWindow)
    - gui_main (εσωτερικό module — MainWindow)

ΡΟΗ ΔΕΔΟΜΕΝΩΝ:
    Main → init_db() → LoginWindow → MainWindow
=============================================================================
"""

import logging
import os
import database
import backup
import tkinter as tk
from tkinter import messagebox
from gui_login import LoginWindow
from gui_main import MainWindow

def main() -> None:
    """
    Η κεντρική συνάρτηση εισόδου του προγράμματος.
    1. Ρυθμίζει το logging.
    2. Αρχικοποιεί τη βάση δεδομένων με error handling.
    3. Διαχειρίζεται τη ροή Login -> Main Window.
    """
    # Ρύθμιση Logging
    logging.basicConfig(
        filename="app.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )
    logging.info("Η εφαρμογή ξεκίνησε.")

    # Αρχικοποίηση βάσης με Error Handling & Safe Mode Recovery
    try:
        database.init_db()
        logging.info("Η βάση δεδομένων αρχικοποιήθηκε επιτυχώς.")
    except Exception as e:
        error_msg = f"Σφάλμα κατά την αρχικοποίηση της βάσης: {e}"
        logging.error(error_msg)
        
        # Πρέπει να δημιουργήσουμε ένα προσωρινό root για το messagebox/dialog
        recovery_root = tk.Tk()
        recovery_root.withdraw()
        
        # Έλεγχος αν υπάρχουν διαθέσιμα backups
        available_backups = backup.get_available_backups()
        
        if available_backups:
            msg = f"Η βάση δεδομένων φαίνεται να είναι κατεστραμμένη ή μη προσβάσιμη.\n\n{error_msg}\n\nΘέλετε να γίνει προσπάθεια αυτόματης επαναφοράς από το τελευταίο αντίγραφο ασφαλείας ({available_backups[0]});"
            if messagebox.askyesno("Κρίσιμο Σφάλμα - Safe Mode", msg):
                backup_path = os.path.join(backup.BACKUP_DIR, available_backups[0])
                if backup.restore_backup(backup_path, silent=False):
                    messagebox.showinfo("Επαναφορά", "Η επαναφορά ολοκληρώθηκε. Παρακαλώ ξεκινήστε ξανά την εφαρμογή.")
                    recovery_root.destroy()
                    return
        else:
            messagebox.showerror("Κρίσιμο Σφάλμα", f"{error_msg}\n\nΔεν βρέθηκαν αντίγραφα ασφαλείας για αυτόματη ανάκτηση.")
            
        recovery_root.destroy()
        return

    # Δημιουργία του root παραθύρου
    root = tk.Tk()
    root.title("RandeBoo — Σύστημα Διαχείρισης Ραντεβού")
    
    # Φόρτωση εικονιδίου εφαρμογής με υποστήριξη cross-platform
    # Δοκιμάζουμε πρώτα το αρχείο .ico για Windows, και ως fallback το .png για άλλα λειτουργικά συστήματα
    try:
        icon_path_ico = os.path.join(os.path.dirname(__file__), "randeboo.ico")
        icon_path_png = os.path.join(os.path.dirname(__file__), "randeboo.png")
        
        if os.path.exists(icon_path_ico):
            root.iconbitmap(icon_path_ico)
        elif os.path.exists(icon_path_png):
            # Χρήση iconphoto για cross-platform συμβατότητα (π.χ. Linux/macOS)
            app_icon = tk.PhotoImage(file=icon_path_png)
            root.iconphoto(True, app_icon)
    except Exception as e:
        logging.warning(f"Αδυναμία φόρτωσης εικονιδίου εφαρμογής: {e}")
    
    # Διαχείριση κλεισίματος παραθύρου (Graceful Exit + Auto-Backup)
    def on_closing() -> None:
        if messagebox.askokcancel("Έξοδος", "Θέλετε να κλείσετε την εφαρμογή;"):
            logging.info("Εκτέλεση αυτόματου backup πριν την έξοδο...")
            backup.create_backup(silent=True)
            logging.info("Η εφαρμογή τερματίστηκε από τον χρήστη.")
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    def on_login_success(user: dict) -> None:
        logging.info(f"Επιτυχής σύνδεση χρήστη: {user.get('username') if isinstance(user, dict) else 'Unknown'}")
        # Καθαρισμός του root και φόρτωση του MainWindow
        for widget in root.winfo_children():
            widget.destroy()
        MainWindow(root, user)

    # Εκκίνηση της οθόνης Login
    try:
        LoginWindow(root, on_login_success)
        root.mainloop()
    except Exception as e:
        logging.critical(f"Απρόσμενο σφάλμα στο GUI: {e}")
        messagebox.showerror("Σφάλμα Εφαρμογής", f"Παρουσιάστηκε ένα μη αναμενόμενο σφάλμα: {e}")

if __name__ == "__main__":
    main()
