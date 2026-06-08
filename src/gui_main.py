"""
Ο κώδικας του αρχείου συντάχθηκε από τον Καταξενό Χρήστο.
Συνεισφορά από τον Ασπρίδη Δημήτρη: προσθήκη συντόμευσης πλήκτρου 'Escape' για απευθείας αποσύνδεση του χρήστη.

=============================================================================
ΑΡΧΕΙΟ: gui_main.py
ΣΚΟΠΟΣ: Κεντρικό παράθυρο εφαρμογής (Dashboard & UI Architecture)
=============================================================================

ΒΙΒΛΙΟΘΗΚΕΣ:
    - tkinter (standard library — tk, ttk, messagebox)
    - tkcalendar (external — DateEntry widget για επιλογή ημερομηνίας)
    - database (εσωτερικό module — CRUD operations)
    - datetime (standard library — timestamp handling)
    - backup (εσωτερικό module — αυτόματο backup κατά την έξοδο)

ΚΛΑΣΗ: MainWindow


ΠΕΡΙΟΡΙΣΜΟΙ ΣΧΕΔΙΑΣΗΣ:
    - minsize(980, 680): Υποχρεωτικό ελάχιστο μέγεθος για να μην "σπάει" το UI.
=============================================================================
"""


import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Any
import logging
from tkcalendar import DateEntry
import backup
import database
from gui_quick_booking import QuickBookingWindow
import json


# 6) LOGGING: Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ... rest of constants ...

# Ελληνικά ονόματα ημερών και μηνών (fallback αν δεν υποστηρίζεται το locale)
_DAYS_GR = [
    "Δευτέρα",
    "Τρίτη",
    "Τετάρτη",
    "Πέμπτη",
    "Παρασκευή",
    "Σάββατο",
    "Κυριακή",
]
_MONTHS_GR = [
    "",
    "Ιανουαρίου",
    "Φεβρουαρίου",
    "Μαρτίου",
    "Απριλίου",
    "Μαΐου",
    "Ιουνίου",
    "Ιουλίου",
    "Αυγούστου",
    "Σεπτεμβρίου",
    "Οκτωβρίου",
    "Νοεμβρίου",
    "Δεκεμβρίου",
]



class MainWindow:
    """
    ΣΚΟΠΟΣ: Κεντρικό παράθυρο εφαρμογής (Dashboard).
    ΣΤΥΛ: Μοντέρνο Sidebar Layout με Aegean Blue παλέτα.
    """

    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.username = user.get("username", "Unknown")
        self.role_id = user.get("role_id", 2)  # 1=Admin, 2=User

        # --- Χρωματική Παλέτα (Aegean Theme) ---
        self.color_bg = "#F7F9FC"            # Κύριο φόντο (ανοιχτό γκρι)
        self.color_sidebar = "#0A3D62"       # Φόντο Sidebar (Deep Greek Blue)
        self.color_accent = "#1E90FF"        # Βασικό χρώμα έμφασης (Aegean Blue)
        self.color_border = "#E5E9F0"        # Περιγράμματα / Διαχωριστικά
        self.color_white = "#FFFFFF"         # Λευκά panels
        self.color_text = "#1B1F23"          # Κύριο κείμενο
        self.color_accent_hover = "#1877D4"  # Χρώμα hover (πιο σκούρο μπλε)

        # 1) ΚΕΝΤΡΙΚΗ ΠΛΟΗΓΗΣΗ: Αντιστοίχιση ονομάτων views με τις μεθόδους τους
        self.views = {
            "dashboard": self._open_dashboard,
            "appointments": self._open_appointments,
            "customers": self._open_customers,
            "search": self._open_search,
            "stats": self._open_stats,
            "employees": self._open_employees,
            "users": self._open_users,
            "settings": self._open_settings
        }

        # Ρυθμίσεις Παραθύρου
        self.root.title(f"RandeBoo Dashboard — {self.username}")
        self.root.geometry("1000x700")
        self.root.minsize(980, 680)  # Προστασία για να μην "σπάει" το UI αν μικρύνει πολύ
        self.root.configure(bg=self.color_bg)

        # Διαχείριση κλεισίματος παραθύρου (X button)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Sidebar — logo και κουμπιά πλοήγησης
        self.sidebar = tk.Frame(self.root, bg=self.color_sidebar, width=160)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)


        tk.Label(
            self.sidebar,
            text="RandeBoo",
            fg=self.color_white,
            bg=self.color_sidebar,
            font=("Arial", 18, "bold"),
            pady=30,
        ).pack()


        # Menu Items - UPDATED to use open_view
        self._create_side_btn("Αρχική", lambda: self.open_view("dashboard"))
        self._create_side_btn("Ραντεβού", lambda: self.open_view("appointments"))
        self._create_side_btn("Πελάτες", lambda: self.open_view("customers"))
        self._create_side_btn("Αναζήτηση", lambda: self.open_view("search"))
        self._create_side_btn("Στατιστικά", lambda: self.open_view("stats"))

        if self.role_id == 1:  # Εμφάνιση Υπαλλήλων μόνο για Διαχειριστές
            self._create_side_btn("Υπάλληλοι", lambda: self.open_view("employees"))

        if self.role_id == 1:  # Εμφάνιση Χρηστών μόνο για Διαχειριστές
            self._create_side_btn("Χρήστες", lambda: self.open_view("users"))

        tk.Label(self.sidebar, bg=self.color_sidebar).pack(
            expand=True, fill="y"
        )  # Spacer
        self._create_side_btn("Ρυθμίσεις", lambda: self.open_view("settings"))


        # Κουμπί Αποσύνδεσης στο τέλος της Sidebar
        self.logout_btn = tk.Button(
            self.sidebar,
            text="Αποσύνδεση",
            command=self._logout,
            bg="#EE5253",
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            pady=15,
            cursor="hand2",
        )
        self.logout_btn.pack(side="bottom", fill="x")


        # Περιοχή Κύριου Περιεχομένου — δυναμική φόρτωση σελίδων (SPA)
        self.content_frame = tk.Frame(self.root, bg=self.color_bg, padx=20, pady=20)
        self.content_frame.pack(side="right", expand=True, fill="both")

        # Σύνδεση της μεθόδου παραγωγής dynamic slots στο root για υποστήριξη του EditAppointmentWindow
        self.root.generate_dynamic_slots = self.generate_dynamic_slots

        # Load the default view - UPDATED to use open_view
        self.open_view("dashboard")
        self.root.bind("<Escape>", lambda event: self._logout())

        # Μεταβλητή για το Dimmer Overlay
        self.dimmer = None
        # Metaβλητές για το Ρολόι
        self.clock_after_id = None
        self.clock_label = None

    # 7) UNIFIED POPUP HELPERS
    def alert_error(self, msg: str) -> None: messagebox.showerror("Σφάλμα", msg)
    def alert_info(self, msg: str) -> None: messagebox.showinfo("Πληροφορία", msg)
    def alert_warning(self, msg: str) -> None: messagebox.showwarning("Προειδοποίηση", msg)

    # 2) ERROR HANDLING BOUNDARIES
    def safe_db_call(self, func: Callable, fallback: Any = None) -> Any:
        """Εκτελεί μια κλήση στη βάση με προστασία."""
        try:
            return func()
        except Exception as e:
            logging.error(f"Database error: {e}")
            self.alert_error(f"Πρόβλημα στη βάση δεδομένων: {e}")
            return fallback

    # 1) CENTRALIZED NAVIGATION
    def open_view(self, name: str) -> None:
        """Κεντρική μέθοδος πλοήγησης με προστασία για σφάλματα κατά το φόρτωμα."""
        if name not in self.views:
            logging.warning(f"Attempted to open unknown view: {name}")
            return
        
        logging.info(f"Opening view: {name}")
        try:
            self._clear_content()
            self.views[name]()
        except Exception as e:
            logging.exception(f"Error loading view {name}: {e}")
            self.alert_error(f"Αποτυχία φόρτωσης της ενότητας '{name}':\n{e}\n\nΕλέγξτε το αρχείο app.log για λεπτομέρειες.")

    def _clear_content(self):
        """Αδειάζει το κεντρικό frame για να φορτώσει νέα σελίδα."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # =========================================================================
    # VIEWS & ROUTING
    # =========================================================================
    def _open_dashboard(self):
        """
        ΣΚΟΠΟΣ: Φορτώνει το κεντρικό Dashboard (πλήρους πλάτους, στυλ CRUD/Appointments).
        """
        self._clear_content()

        # Κύρια Περιοχή: Καταλαμβάνει όλο το πλάτος
        self.main_area = tk.Frame(self.content_frame, bg=self.color_bg)
        self.main_area.pack(side="left", fill="both", expand=True)

        # Δεν υπάρχει πλέον sidebar container (απενεργοποίηση για ομοιόμορφο look)
        self.sidebar_container = None

        # Επικεφαλίδα Dashboard — χαιρετισμός και ρολόι
        self.header = tk.Frame(self.main_area, bg=self.color_bg)
        self.header.pack(fill="x", pady=(0, 10))

        first_name = self.user.get("first_name", self.username)
        tk.Label(
            self.header,
            text=f"Καλωσήρθατε, {first_name}!",
            font=("Arial", 18, "bold"),
            bg=self.color_bg,
            fg=self.color_sidebar,
        ).pack(side="left")

        # Ψηφιακό Ρολόι: Τοποθέτηση στο header (πάνω δεξιά)
        self.clock_label = tk.Label(
            self.header,
            text="--:--:--\n--/--/--",
            font=("Arial", 11, "bold"),
            bg=self.color_bg,
            fg=self.color_sidebar,
            justify="right"
        )
        self.clock_label.pack(side="right")
        self._update_clock()

        # Κάρτες Στατιστικών Dashboard — 3 compact κάρτες σε 1 σειρά
        self.cards_frame = tk.Frame(self.main_area, bg=self.color_bg)
        self.cards_frame.pack(fill="x", pady=(0, 10))
        self._refresh_stats()

        # Toolbar Dashboard — πλοήγηση ημερομηνίας + κουμπιά ενεργειών
        self.toolbar_frame = tk.Frame(
            self.main_area,
            bg=self.color_white,
            padx=10,
            pady=8,
            highlightthickness=1,
            highlightbackground=self.color_border,
        )
        self.toolbar_frame.pack(fill="x", pady=(0, 8))

        # Αριστερά: ◀ Επιλογή Ημερομηνίας ▶ Σήμερα
        btn_prev = tk.Button(
            self.toolbar_frame,
            text="<",
            command=self._date_prev,
            bg=self.color_sidebar,
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=6,
            cursor="hand2",
        )
        btn_prev.pack(side="left")

        self.date_entry = DateEntry(self.toolbar_frame,width=12,date_pattern="dd/mm/yyyy",background=self.color_sidebar,foreground="white",selectbackground=self.color_accent,font=("Arial", 10),)
        self.date_entry.bind("<<DateEntryPopup>>", lambda event: event.widget._top_cal.overrideredirect(False))
        self.date_entry.pack(side="left", padx=4)
        self.date_entry.bind("<<DateEntrySelected>>", lambda e: self._refresh_agenda())

        btn_next = tk.Button(
            self.toolbar_frame,
            text=">",
            command=self._date_next,
            bg=self.color_sidebar,
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=6,
            cursor="hand2",
        )
        btn_next.pack(side="left")

        tk.Button(
            self.toolbar_frame,
            text="Σήμερα",
            command=self._date_today,
            bg=self.color_accent,
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=10,
            cursor="hand2",
        ).pack(side="left", padx=(8, 0))

        # Separator: κάθετη γραμμή
        sep = tk.Frame(self.toolbar_frame, bg=self.color_border, width=1)
        sep.pack(side="left", fill="y", padx=12, pady=2)

        # Κουμπί Ανανέωσης (δεξιά)
        self.btn_refresh = tk.Button(
            self.toolbar_frame,
            text="Ανανέωση",
            command=self._refresh_all,
            font=("Arial", 9, "bold"),
            bg=self.color_white,
            fg=self.color_sidebar,
            relief="flat",
            cursor="hand2",
            padx=10,
        )
        self.btn_refresh.pack(side="right")

        # Τίτλος ατζέντας
        self.agenda_title_label = tk.Label(
            self.main_area,
            text="",
            font=("Arial", 12, "bold"),
            bg=self.color_bg,
            fg=self.color_sidebar
        )
        self.agenda_title_label.pack(anchor="w", pady=(10, 5))

        # Container για τον πίνακα της ατζέντας (Treeview + Scrollbar)
        self.agenda_container = tk.Frame(self.main_area, bg=self.color_bg)
        self.agenda_container.pack(fill="both", expand=True, pady=(5, 10))

        columns = ("time", "customer", "employee", "notes", "status")
        self.agenda_table = ttk.Treeview(self.agenda_container, columns=columns, show="headings", height=12)
        self.agenda_table.heading("time", text="Ώρα")
        self.agenda_table.heading("customer", text="Πελάτης")
        self.agenda_table.heading("employee", text="Υπάλληλος")
        self.agenda_table.heading("notes", text="Σημειώσεις")
        self.agenda_table.heading("status", text="Κατάσταση")
        
        self.agenda_table.column("time", width=100, anchor="center")
        self.agenda_table.column("customer", width=200, anchor="center")
        self.agenda_table.column("employee", width=150, anchor="center")
        self.agenda_table.column("notes", width=250, anchor="center")
        self.agenda_table.column("status", width=120, anchor="center")
        
        self.agenda_table.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(self.agenda_container, orient="vertical", command=self.agenda_table.yview)
        self.agenda_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Config tags
        self.agenda_table.tag_configure("oddrow", background="#FFFFFF")
        self.agenda_table.tag_configure("evenrow", background="#D9E2EC")
        self.agenda_table.tag_configure("hover", background="#B3E5FC")
        
        self.agenda_table.tag_configure("completed", foreground="#95a5a6")
        self.agenda_table.tag_configure("in_progress", foreground="#1E90FF")
        self.agenda_table.tag_configure("upcoming", foreground="#27ae60")

        self.last_hovered_item = None
        self.agenda_table.bind("<Motion>", self._on_agenda_table_hover)
        self.agenda_table.bind("<Double-1>", lambda event: self._btn_edit_click())

        # Σύνδεση της ροδέλας του ποντικιού για κύλιση στον πίνακα
        self.agenda_table.bind("<MouseWheel>", lambda event: self.agenda_table.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        # Mapping των σειρών με τα λεξικά ραντεβού
        self._agenda_appt_map = {}

        # Container κουμπιών ενεργειών (στο κάτω μέρος)
        self.button_container = tk.Frame(self.main_area, bg=self.color_bg)
        self.button_container.pack(fill="x", pady=10)

        self.btn_quick = tk.Button(
            self.button_container,
            text="+ Γρήγορο Ραντεβού",
            command=self._open_quick_booking,
            bg=self.color_accent,
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=15,
            cursor="hand2"
        )
        self.btn_quick.pack(side="left", padx=5)

        self.btn_checkin = tk.Button(
            self.button_container,
            text="Check-in",
            command=self._btn_checkin_click,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=15,
            cursor="hand2"
        )
        self.btn_checkin.pack(side="left", padx=5)

        self.btn_edit = tk.Button(
            self.button_container,
            text="Επεξεργασία",
            command=self._btn_edit_click,
            bg=self.color_accent,
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=15,
            cursor="hand2"
        )
        self.btn_edit.pack(side="left", padx=5)

        self.btn_cancel = tk.Button(
            self.button_container,
            text="Ακύρωση",
            command=self._btn_delete_click,
            bg="#EE5253",
            fg="white",
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=15,
            cursor="hand2"
        )
        self.btn_cancel.pack(side="right", padx=5)

        # Hover effects στα κουμπιά ενεργειών
        self.btn_quick.bind("<Enter>", lambda e: self.btn_quick.configure(bg=self.color_accent_hover))
        self.btn_quick.bind("<Leave>", lambda e: self.btn_quick.configure(bg=self.color_accent))
        self.btn_checkin.bind("<Enter>", lambda e: self.btn_checkin.configure(bg="#27ae60"))
        self.btn_checkin.bind("<Leave>", lambda e: self.btn_checkin.configure(bg="#2ecc71"))
        self.btn_edit.bind("<Enter>", lambda e: self.btn_edit.configure(bg=self.color_accent_hover))
        self.btn_edit.bind("<Leave>", lambda e: self.btn_edit.configure(bg=self.color_accent))
        self.btn_cancel.bind("<Enter>", lambda e: self.btn_cancel.configure(bg="#C23B3C"))
        self.btn_cancel.bind("<Leave>", lambda e: self.btn_cancel.configure(bg="#EE5253"))

        self._refresh_all()


    def _on_checkin(self, appt):
        """Εκτελεί check-in για το ραντεβού."""
        appt_id = appt["appointment_id"]
        # Εδώ θα μπορούσε να μπει η λογική check-in (π.χ. αλλαγή status σε 'in_progress' ή 'completed')
        self.alert_info(f"Το ραντεβού (ID: {appt_id}) σημειώθηκε ως σε εξέλιξη.")
        self._refresh_all()

    def _on_delete(self, appt):
        """Ακύρωση ραντεβού από την κάρτα."""
        appt_id = appt["appointment_id"]
        creator_id = appt.get("user_id")

        if self.role_id != 1 and creator_id != self.user["id"]:
            self.alert_warning("Δεν έχετε δικαίωμα να ακυρώσετε ραντεβού άλλων χρηστών.")
            return

        confirm = messagebox.askyesno(
            "Ακύρωση Ραντεβού",
            f"Θέλετε να ακυρώσετε το ραντεβού με τον/την {appt['customer_name']};"
        )
        if confirm:
            self.safe_db_call(lambda: database.delete_appointment(appt_id))
            self.alert_info("Το ραντεβού ακυρώθηκε.")
            self._refresh_all()

    def _create_side_btn(self, text, command):
        """Helper για την ομοιόμορφη δημιουργία κουμπιών Sidebar με hover εφέ."""
        btn = tk.Button(
            self.sidebar,
            text=text,
            command=command,
            bg=self.color_sidebar,
            fg=self.color_white,
            font=("Arial", 11),
            relief="flat",
            anchor="w",
            padx=20,
            pady=12,
            activebackground=self.color_accent_hover,
            activeforeground="white",
            cursor="hand2",
        )
        btn.pack(fill="x")
        btn.bind("<Enter>", lambda e: btn.configure(bg=self.color_accent_hover))
        btn.bind("<Leave>", lambda e: btn.configure(bg=self.color_sidebar))

    def _create_dashboard_card(self, title, stat_value, col, icon=""):
        """
        ΣΚΟΠΟΣ: Compact κάρτα στατιστικών (1 σειρά, inline layout).
        ΣΧΕΔΙΑΣΗ: Αριθμός αριστερά (bold), τίτλος δεξιά (subtle).
        """
        card = tk.Frame(
            self.cards_frame,
            bg=self.color_white,
            padx=12,
            pady=8,
            highlightthickness=1,
            highlightbackground=self.color_border,
        )
        card.grid(row=0, column=col, padx=4, sticky="nsew")
        self.cards_frame.grid_columnconfigure(col, weight=1)

        # Inline layout: αριθμός + τίτλος στην ίδια γραμμή
        tk.Label(
            card,
            text=stat_value,
            font=("Arial", 20, "bold"),
            bg=self.color_white,
            fg=self.color_sidebar,
        ).pack(side="left", padx=(0, 8))

        display_title = f"{icon}\n{title}" if icon else title
        tk.Label(
            card,
            text=display_title,
            font=("Arial", 9),
            bg=self.color_white,
            fg="#95a5a6",
            justify="left",
        ).pack(side="left", anchor="w")


    def _logout(self):
        """Επιβεβαίωση και επιστροφή στην οθόνη εισόδου."""
        if messagebox.askyesno("Αποσύνδεση", "Θέλετε να αποσυνδεθείτε;"):
            # Καταγραφή logout στη βάση
            login_id = self.user.get("id_login")
            if login_id:
                self.safe_db_call(lambda: database.record_logout(login_id))

            self.root.destroy()
            import main

            main.main()

    def _on_closing(self):
        """Εκτελείται όταν ο χρήστης πατάει το Χ στο παράθυρο."""
        if messagebox.askokcancel("Έξοδος", "Θέλετε να κλείσετε την εφαρμογή;"):
            # Καταγραφή logout στη βάση πριν το κλείσιμο
            login_id = self.user.get("id_login")
            if login_id:
                self.safe_db_call(lambda: database.record_logout(login_id))

            # Αυτόματο Backup στην έξοδο
            backup.create_backup(silent=True)
            self.root.destroy()

    def _show_placeholder(self, title, dev):
        """Δείχνει ένα placeholder panel."""
        frame = tk.Frame(self.content_frame, bg=self.color_bg)
        frame.pack(expand=True, fill="both")

        card = tk.LabelFrame(
            frame,
            text=title,
            bg=self.color_white,
            font=("Arial", 14, "bold"),
            padx=50,
            pady=50,
        )
        card.pack(expand=True)

        tk.Label(
            card,
            text="Υπό Κατασκευή",
            font=("Arial", 20, "bold"),
            bg=self.color_white,
            fg="#e67e22",
        ).pack(pady=10)
        tk.Label(
            card,
            text=f"Αυτή η ενότητα υλοποιείται από: {dev}",
            font=("Arial", 12),
            bg=self.color_white,
            fg=self.color_text,
        ).pack(pady=10)


    # --- Πλοήγηση σε άλλες ενότητες ---
    def _open_customers(self):
        """
        Φορτώνει την οθόνη Πελατών.
        """
        import gui_customers
        gui_customers.CustomersWindow(self.content_frame, self.user)

    def _open_search(self):
        """
        Φορτώνει την οθόνη Αναζήτησης.
        """
        # Εισαγωγή του module της αναζήτησης και φόρτωση του γραφικού panel
        import gui_search
        gui_search.SearchPanel(self.content_frame, self.user)

    def _open_appointments(self):
        self._clear_content()
        
        # 1. Import και των δύο κλάσεων από το αρχείο σου
        from gui_appointments import CalendarView, AppointmentSearch
        from tkinter import ttk

        # 2. Δημιουργία του Notebook (Tab Control)
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # 3. Προσθήκη Tab 1: Ημερολόγιο
        tab1 = CalendarView(notebook, user=self.user)
        notebook.add(tab1, text="  Ημερήσιο Πρόγραμμα  ")

        # 4. Προσθήκη Tab 2: Αναζήτηση Ιστορικού
        tab2 = AppointmentSearch(notebook)
        notebook.add(tab2, text="  Αναζήτηση Ιστορικού  ")

    def _open_stats(self):
        import gui_stats
        gui_stats.StatsPanel(self.content_frame, self.user)

    def _open_employees(self):
        import gui_employees
        gui_employees.EmployeesWindow(self.content_frame, self.user)

    def _open_users(self):
        import gui_users
        gui_users.UsersWindow(self.content_frame, self.user)

    def _open_settings(self):
        import gui_settings
        gui_settings.SettingsPanel(self.content_frame, self.user)

    def _refresh_stats(self):
        """
        ΣΚΟΠΟΣ: Ανάκτηση στατιστικών και ενημέρωση των 3 compact καρτών.
        LAYOUT: 1 σειρά × 3 κάρτες (Σήμερα / Αύριο / Εβδομάδα).
        """
        logging.info("Refreshing dashboard stats...")
        # ERROR HANDLING: Χρήση της safe_db_call για ασφάλεια
        stats = self.safe_db_call(database.get_dashboard_stats, fallback={"today_appointments":0, "tomorrow_appointments":0, "week_appointments":0})
        
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        self._create_dashboard_card(
            "Σήμερα", str(stats.get("today_appointments", 0)), 0, icon=""
        )
        self._create_dashboard_card(
            "Αύριο", str(stats.get("tomorrow_appointments", 0)), 1, icon=""
        )
        self._create_dashboard_card(
            "Εβδομάδα", str(stats.get("week_appointments", 0)), 2, icon=""
        )


    def _get_appointment_status(self, start_time_str, end_time_str, selected_date):
        """
        ΣΚΟΠΟΣ: Αυτόματος υπολογισμός κατάστασης ραντεβού βάσει χρόνου.
        """
        today = datetime.date.today()

        if selected_date < today:
            return "Ολοκληρωμένο", "completed"
        elif selected_date > today:
            return "Επικείμενο", "upcoming"
        else:
            # Σήμερα: σύγκριση ωρών
            now_time = datetime.datetime.now().time()
            try:
                start_t = datetime.datetime.strptime(start_time_str, "%H:%M").time()
                now_time = datetime.datetime.now().time()
                # fix to avoid ambiguity in end_time
                if not end_time_str: end_time_str = (datetime.datetime.strptime(start_time_str, "%H:%M") + datetime.timedelta(minutes=30)).strftime("%H:%M")
                end_t = datetime.datetime.strptime(end_time_str, "%H:%M").time()
            except (ValueError, TypeError):
                return "Επικείμενο", "upcoming"

            if now_time > end_t:
                return "Ολοκληρωμένο", "completed"
            elif start_t <= now_time <= end_t:
                return "Σε Εξέλιξη", "in_progress"
            else:
                return "Επικείμενο", "upcoming"

    def _refresh_agenda(self):
        """
        ΣΚΟΠΟΣ: Ανάκτηση ραντεβού της επιλεγμένης ημέρας και εμφάνιση στον πίνακα (Treeview).
        """
        try:
            logging.info("Refreshing agenda table...")
            
            # 1. Καθαρισμός πίνακα
            for tree_item in self.agenda_table.get_children():
                self.agenda_table.delete(tree_item)
            self._agenda_appt_map.clear()

            # 2. Λήψη ημερομηνίας
            selected_date = self.date_entry.get_date()
            selected_date_str = selected_date.strftime("%d/%m/%Y")
            
            # 3. Ανάκτηση από βάση
            appts = self.safe_db_call(lambda: database.get_day_appointments(selected_date_str), fallback=[])
            
            # 4. Ενημέρωση τίτλου με πλήθος
            count = len(appts)
            day_gr = _DAYS_GR[selected_date.weekday()]
            date_gr = f"{selected_date.day} {_MONTHS_GR[selected_date.month]}"
            summary_text = f"{day_gr}, {date_gr}  ·  {count} ραντεβού"
            self.agenda_title_label.config(text=summary_text)

            # 5. Εισαγωγή εγγραφών
            for i, a in enumerate(appts):
                status_label, status_tag = self._get_appointment_status(
                    a["start_time"], a.get("end_time", ""), selected_date
                )
                
                # Καθαρισμός σημειώσεων από tags
                notes_clean = a.get("notes", "").replace("[MODIFIED]", "").replace("[DELETED]", "").strip()
                
                values = (
                    f"{a['start_time']}–{a.get('end_time', '')}",
                    a["customer_name"],
                    a["employee_name"],
                    notes_clean,
                    status_label
                )
                
                # Καθορισμός tags για χρώματα και zebra εφέ
                zebra_tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                item_id = self.agenda_table.insert("", "end", values=values, tags=(status_tag, zebra_tag))
                self._agenda_appt_map[item_id] = a
                
            # Force UI update
            self.root.update_idletasks()
            
        except Exception as e:
            logging.error(f"Error in _refresh_agenda: {e}")
            self.alert_error(f"Σφάλμα κατά την ανανέωση της λίστας: {e}")

    def _on_agenda_table_hover(self, event):
        """Εφαρμόζει εφέ hover στις γραμμές του πίνακα ατζέντας."""
        tree_item = self.agenda_table.identify_row(event.y)
        if tree_item != self.last_hovered_item:
            # Επαναφορά προηγούμενης γραμμής
            if self.last_hovered_item and self.agenda_table.exists(self.last_hovered_item):
                idx = self.agenda_table.index(self.last_hovered_item)
                original_zebra = 'evenrow' if idx % 2 == 0 else 'oddrow'
                item_tags = self.agenda_table.item(self.last_hovered_item, "tags")
                status_tag = [t for t in item_tags if t in ('completed', 'in_progress', 'upcoming')][0] if any(t in ('completed', 'in_progress', 'upcoming') for t in item_tags) else ''
                self.agenda_table.item(self.last_hovered_item, tags=(status_tag, original_zebra))
            
            # Εφαρμογή hover στη νέα γραμμή
            if tree_item:
                item_tags = self.agenda_table.item(tree_item, "tags")
                status_tag = [t for t in item_tags if t in ('completed', 'in_progress', 'upcoming')][0] if any(t in ('completed', 'in_progress', 'upcoming') for t in item_tags) else ''
                self.agenda_table.item(tree_item, tags=(status_tag, 'hover'))
                
            self.last_hovered_item = tree_item

    def _get_selected_agenda_appointment(self):
        """Επιστρέφει το επιλεγμένο ραντεβού από την ατζέντα."""
        selected = self.agenda_table.selection()
        if not selected:
            self.alert_warning("Επιλέξτε ένα ραντεβού από τον πίνακα!")
            return None
        return self._agenda_appt_map.get(selected[0])

    def _btn_checkin_click(self):
        """Διαχειρίζεται το πάτημα του κουμπιού Check-in."""
        appt = self._get_selected_agenda_appointment()
        if not appt:
            return
        selected_date = self.date_entry.get_date()
        _, status_tag = self._get_appointment_status(appt["start_time"], appt.get("end_time", ""), selected_date)
        if status_tag != "upcoming":
            self.alert_warning("Το Check-in είναι διαθέσιμο μόνο για επικείμενα (upcoming) ραντεβού!")
            return
        self._on_checkin(appt)

    def _btn_edit_click(self):
        """Διαχειρίζεται το πάτημα του κουμπιού Επεξεργασία."""
        appt = self._get_selected_agenda_appointment()
        if appt:
            self._show_appointment_detail(appt)

    def _btn_delete_click(self):
        """Διαχειρίζεται το πάτημα του κουμπιού Ακύρωση."""
        appt = self._get_selected_agenda_appointment()
        if appt:
            self._on_delete(appt)

    def _show_appointment_detail(self, appt):
        """Ανοίγει το παράθυρο επεξεργασίας για το επιλεγμένο ραντεβού."""
        if not appt:
            return
        
        # Έλεγχος δικαιωμάτων
        if self.role_id != 1 and appt.get("user_id") != self.user["id"]:
            self.alert_warning("Δεν έχετε δικαίωμα να αλλάξετε ραντεβού άλλων χρηστών.")
            return

        from gui_appointments import EditAppointmentWindow
        EditAppointmentWindow(self.root, appt, self._confirm_edit)

    def _confirm_edit(self, appt_id, customer_id, user_id, new_date, new_time, duration, notes, new_emp_id):
        """Εκτελεί την ενημέρωση του ραντεβού στη βάση δεδομένων."""
        clean_notes = str(notes)
        if "[MODIFIED]" not in clean_notes and "[DELETED]" not in clean_notes:
            clean_notes = f"[MODIFIED] {clean_notes}".strip()

        success, msg = database.update_appointment(
            appointment_id=appt_id,
            customer_id=customer_id,
            user_id=user_id,
            date=new_date,
            time=new_time,
            duration=duration,
            notes=clean_notes,
            employee_id=new_emp_id
        )
        
        if success:
            self.alert_info("Το ραντεβού ενημερώθηκε επιτυχώς!")
            self._refresh_all()
        else:
            self.alert_error(f"Αποτυχία ενημέρωσης: {msg}")

    def generate_dynamic_slots(self, date_obj):
        """Παράγει slots βάσει Business Settings (χρησιμοποιείται από το EditAppointmentWindow)."""
        settings = database.get_business_settings()
        try:
            sched = json.loads(settings.get("weekly_schedule", "{}"))
            duration = int(settings.get("slot_duration", 30))
        except:
            return []

        weekday_key = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][date_obj.weekday()]
        day_info = sched.get(weekday_key, {})

        if day_info.get("closed"):
            return []

        slots = []
        for s_prefix in ["s1", "s2"]:
            start_str = day_info.get(f"{s_prefix}_s")
            end_str = day_info.get(f"{s_prefix}_e")
            if start_str and end_str:
                try:
                    curr = datetime.datetime.strptime(start_str, "%H:%M")
                    end = datetime.datetime.strptime(end_str, "%H:%M")
                    while curr < end:
                        nxt = curr + datetime.timedelta(minutes=duration)
                        slots.append(f"{curr.strftime('%H:%M')} - {nxt.strftime('%H:%M')}")
                        curr = nxt
                except: pass
        return slots



    # ---- Date Navigator βοηθητικές μέθοδοι ----

    def _date_prev(self):
        """ΣΚΟΠΟΣ: Μετακίνηση -1 ημέρα στο DateEntry."""
        current = self.date_entry.get_date()
        self.date_entry.set_date(current - datetime.timedelta(days=1))
        self._refresh_agenda()

    def _date_next(self):
        """ΣΚΟΠΟΣ: Μετακίνηση +1 ημέρα στο DateEntry."""
        current = self.date_entry.get_date()
        self.date_entry.set_date(current + datetime.timedelta(days=1))
        self._refresh_agenda()

    def _date_today(self):
        """ΣΚΟΠΟΣ: Επαναφορά DateEntry στη σημερινή ημερομηνία."""
        self.date_entry.set_date(datetime.date.today())
        self._refresh_agenda()


    def _update_clock(self):
        """Ανανεώνει την ώρα κάθε 1 δευτερόλεπτο."""
        # Έλεγχος αν το widget του ρολογιού υπάρχει ακόμα και δεν έχει καταστραφεί (π.χ. λόγω αλλαγής οθόνης)
        if not hasattr(self, "clock_label") or not self.clock_label or not self.clock_label.winfo_exists():
            return

        try:
            now = datetime.datetime.now()
            time_str = now.strftime("%H:%M:%S")
            day_gr = _DAYS_GR[now.weekday()]
            date_str = f"{day_gr}, {now.day} {_MONTHS_GR[now.month]} {now.year}"
            
            # Ενημέρωση του label με νέα ώρα/ημ/νια
            self.clock_label.config(text=f"{time_str}\n{date_str}")
            
            # Επανάληψη μετά από 1000ms
            self.clock_after_id = self.root.after(1000, self._update_clock)
        except Exception as e:
            logging.error(f"Clock update error: {e}")

    # ---- Ανανέωση (Stats + Agenda μαζί) ----

    def _refresh_all(self):
        """ΣΚΟΠΟΣ: Ανανέωση στατιστικών και ατζέντας."""
        self._refresh_stats()
        self._refresh_agenda()

    # ---- Quick Booking ----

    def _open_quick_booking(self):
        """Ανοίγει το Popup παράθυρο για νέο ραντεβού."""
        logging.info("Opening quick booking window")
        QuickBookingWindow(self, self.user, self._on_booking_success)


    def _on_booking_success(self):
        """Ανανεώνει το UI μετά από επιτυχή κράτηση στο popup."""
        logging.info("Quick booking success callback received")
        self._refresh_all()
