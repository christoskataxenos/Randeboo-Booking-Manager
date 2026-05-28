"""
Ο κώδικας του αρχείου συντάχθηκε από τον Καταξένο Χρήστο.

=============================================================================
ΑΡΧΕΙΟ: gui_quick_booking.py
ΣΚΟΠΟΣ: Παράθυρο Γρήγορης Κράτησης
=============================================================================
"""


import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import datetime
import database
import logging
import json
from typing import Any, List, Dict, Tuple, Callable, Optional

# Ρύθμιση Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class QuickBookingWindow:
    def __init__(self, main_app: Any, user: Dict[str, Any], on_success: Callable[[], None]) -> None:
        logging.info("Opening QuickBookingWindow")
        self.main_app = main_app
        self.user = user
        self.on_success = on_success
        self.selected_customer_id: Optional[int] = None

        # --- LOAD BUSINESS SETTINGS ---
        # Φορτώνουμε τις ρυθμίσεις της επιχείρησης για να καθορίσουμε τη διάρκεια των ραντεβού
        # και να ελέγξουμε ποιες ημέρες/ώρες είναι κλειστή η επιχείρηση.
        try:
            self.business_settings = database.get_business_settings()
            self.weekly_schedule = json.loads(self.business_settings.get("weekly_schedule", "{}"))
            self.blackout_dates = self.business_settings.get("blackout_dates", "").split(",")
            self.slot_duration = int(self.business_settings.get("slot_duration", 30))
        except Exception as settings_error:
            logging.error(f"Failed to load business settings: {settings_error}")
            self.weekly_schedule = {}
            self.blackout_dates = []
            self.slot_duration = 30

        self.window = tk.Toplevel(main_app.root)
        self.window.title("Γρήγορο Ραντεβού")
        self.window.transient(main_app.root)
        self.window.grab_set()
        self.window.focus_force()
        
        # Geometry setup
        width, height = 1024, 768
        p_w = main_app.root.winfo_width()
        p_h = main_app.root.winfo_height()
        p_x = main_app.root.winfo_x()
        p_y = main_app.root.winfo_y()
        x = p_x + (p_w // 2) - (width // 2)
        y = p_y + (p_h // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.resizable(False, False)

        # Χρώματα Aegean Theme
        self.color_bg = "#F7F9FC"           # Ανοιχτό γκρι φόντο
        self.color_sidebar = "#0A3D62"      # Βαθύ μπλε για επικεφαλίδες
        self.color_accent = "#1E90FF"       # Aegean Blue για βασικές ενέργειες
        self.color_white = "#FFFFFF"        # Λευκό για panels
        self.color_border = "#E5E9F0"       # Ανοιχτό γκρι για περιγράμματα
        self.color_accent_hover = "#1877D4" # Σκούρο μπλε για hover
        self.color_red = "#EE5253"          # Κόκκινο για ακυρώσεις/σφάλματα
        self.color_green = "#27ae60"        # Πράσινο για επιβεβαιώσεις

        self.window.configure(bg=self.color_bg)

        # --- Δομή UI ---
        # Περιοχή περιεχομένου με δυνατότητα κύλισης (Scrollable)
        self.content_container = tk.Frame(self.window, bg=self.color_bg)
        self.content_container.pack(fill="both", expand=True)

        self.content_canvas = tk.Canvas(self.content_container, bg=self.color_bg, highlightthickness=0)
        self.content_scroll = tk.Scrollbar(self.content_container, orient="vertical", command=self.content_canvas.yview)
        self.content_frame = tk.Frame(self.content_canvas, bg=self.color_bg)

        self.content_frame.bind(
            "<Configure>",
            lambda event: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all")),
        )
        self.content_window_id = self.content_canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.content_canvas.configure(yscrollcommand=self.content_scroll.set)

        self.content_canvas.pack(side="left", fill="both", expand=True)
        self.content_scroll.pack(side="right", fill="y")

        # Υποστήριξη Mousewheel για κύλιση στη φόρμα
        self.window.bind("<MouseWheel>", self._on_window_mousewheel)
        self.content_canvas.bind("<Configure>", self._on_content_canvas_configure)

        # Επικεφαλίδα Παραθύρου
        self.main_container = tk.Frame(self.content_frame, bg=self.color_bg)
        self.main_container.pack(fill="both", expand=True, padx=25, pady=15)

        header = tk.Frame(self.main_container, bg=self.color_bg)
        header.pack(fill="x", pady=(0, 20))
        
        tk.Label(header, text="Γρήγορο Ραντεβού", font=("Arial", 18, "bold"), bg=self.color_bg, fg=self.color_sidebar).pack(side="left")

        # Επιλογή λειτουργίας πελάτη (Νέος vs Υπάρχων)
        self.toggle_frame = tk.Frame(self.main_container, bg=self.color_white, padx=15, pady=15, highlightthickness=1, highlightbackground=self.color_border)
        self.toggle_frame.pack(fill="x", pady=(0, 20))

        self.var_new_cust = tk.BooleanVar(value=False)
        self.chk_new_cust = tk.Checkbutton(
            self.toggle_frame, text="Νέος Πελάτης", variable=self.var_new_cust,
            command=self._toggle_customer_mode, bg=self.color_white, font=("Arial", 10, "bold")
        )
        self.chk_new_cust.pack(anchor="w")

        # Δυναμική Φόρμα Πελάτη
        self.customer_form = tk.Frame(self.main_container, bg=self.color_white, padx=20, pady=20, highlightthickness=1, highlightbackground=self.color_border)
        self.customer_form.pack(fill="x", pady=(0, 20))

        # UI για Υπάρχοντα Πελάτη
        self.frame_existing = tk.LabelFrame(self.customer_form, text="Αναζήτηση Υπάρχοντος Πελάτη", bg=self.color_white, padx=10, pady=10, font=("Arial", 10, "bold"))
        tk.Label(self.frame_existing, text="Όνομα ή Επώνυμο:", bg=self.color_white, font=("Arial", 9)).pack(anchor="w")
        self.ent_search_name = tk.Entry(self.frame_existing, font=("Arial", 10), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_search_name.pack(fill="x", pady=(0, 5))
        tk.Label(self.frame_existing, text="Email:", bg=self.color_white, font=("Arial", 9)).pack(anchor="w")
        self.ent_search_email = tk.Entry(self.frame_existing, font=("Arial", 10), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_search_email.pack(fill="x", pady=(0, 10))
        self.btn_search = tk.Button(
            self.frame_existing, text="Αναζήτηση Πελάτη", command=self._handle_search,
            bg=self.color_sidebar, fg="white", relief="flat", cursor="hand2", font=("Arial", 10, "bold")
        )
        self.btn_search.pack(fill="x")
        self.lbl_selected_cust = tk.Label(
            self.frame_existing, text="Επιλεγμένος: Κανένας",
            fg="red", bg=self.color_white, font=("Arial", 9, "italic")
        )
        self.lbl_selected_cust.pack(pady=(5, 0))

        # UI για Νέο Πελάτη
        self.frame_new = tk.LabelFrame(self.customer_form, text="Στοιχεία Νέου Πελάτη", bg=self.color_white, padx=10, pady=10, font=("Arial", 10, "bold"))
        tk.Label(self.frame_new, text="Όνομα *:", bg=self.color_white, font=("Arial", 9)).pack(anchor="w")
        self.ent_new_fname = tk.Entry(self.frame_new, font=("Arial", 10), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_new_fname.pack(fill="x", pady=(0, 5))
        tk.Label(self.frame_new, text="Επώνυμο *:", bg=self.color_white, font=("Arial", 9)).pack(anchor="w")
        self.ent_new_lname = tk.Entry(self.frame_new, font=("Arial", 10), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_new_lname.pack(fill="x", pady=(0, 5))
        tk.Label(self.frame_new, text="Τηλέφωνο:", bg=self.color_white, font=("Arial", 9)).pack(anchor="w")
        self.ent_new_phone = tk.Entry(self.frame_new, font=("Arial", 10), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_new_phone.pack(fill="x", pady=(0, 5))
        tk.Label(self.frame_new, text="Email *:", bg=self.color_white, font=("Arial", 9)).pack(anchor="w")
        self.ent_new_email = tk.Entry(self.frame_new, font=("Arial", 10), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_new_email.pack(fill="x")

        self._toggle_customer_mode()

        # Λεπτομέρειες Ραντεβού
        self.appointment_frame = tk.Frame(self.main_container, bg=self.color_white, padx=20, pady=20, highlightthickness=1, highlightbackground=self.color_border)
        self.appointment_frame.pack(fill="x", pady=(0, 20))

        tk.Label(self.appointment_frame, text="Υπάλληλος:", bg=self.color_white, font=("Arial", 9)).pack(anchor="w")
        self.employees = database.get_active_employees()
        emp_names = [f"{e['first_name']} {e['last_name']}" for e in self.employees]
        self.cb_employee = ttk.Combobox(self.appointment_frame, values=emp_names, state="readonly", font=("Arial", 10))
        self.cb_employee.pack(fill="x", pady=(0, 10))
        if emp_names: self.cb_employee.current(0)

        # Ημερομηνία & Ώρα
        dt_frame = tk.Frame(self.appointment_frame, bg=self.color_white)
        dt_frame.pack(fill="x", pady=5)
        dt_frame.grid_columnconfigure(0, weight=1)
        dt_frame.grid_columnconfigure(1, weight=1)

        tk.Label(dt_frame, text="Ημερομηνία:", bg=self.color_white, font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.date_entry = DateEntry(dt_frame, width=12, date_pattern="dd/mm/yyyy", font=("Arial", 10))
        self.date_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        self.date_entry.bind("<<DateEntrySelected>>", self._refresh_time_slots)

        tk.Label(dt_frame, text="Ώρα:", bg=self.color_white, font=("Arial", 9)).grid(row=0, column=1, sticky="w")
        self.cb_time = ttk.Combobox(dt_frame, values=[], state="readonly", font=("Arial", 10))
        self.cb_time.grid(row=1, column=1, sticky="ew")
        
        self._refresh_time_slots()

        # Σημειώσεις
        tk.Label(self.appointment_frame, text="Σημειώσεις:", bg=self.color_white, font=("Arial", 9)).pack(anchor="w", pady=(10, 0))
        notes_frame = tk.Frame(self.appointment_frame, bg=self.color_white)
        notes_frame.pack(fill="x", pady=(0, 10))
        self.ent_notes = tk.Text(
            notes_frame,
            font=("Arial", 10),
            height=4,
            wrap="word",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#B0BEC5",
            highlightcolor="#1E90FF",
        )
        self.ent_notes.pack(side="left", fill="x", expand=True)
        notes_scroll = tk.Scrollbar(notes_frame, orient="vertical", command=self.ent_notes.yview)
        notes_scroll.pack(side="right", fill="y")
        self.ent_notes.configure(yscrollcommand=notes_scroll.set)

        # Κύλιση σημειώσεων με το mousewheel όταν ο δρομέας είναι πάνω από το widget
        self.ent_notes.bind("<MouseWheel>", self._on_notes_mousewheel)

        # Πλέγμα Επιλογής Χρονικού Διαστήματος (Slots)
        self.slots_frame = tk.LabelFrame(self.main_container, text="Διαθέσιμες Ώρες", bg=self.color_white, font=("Arial", 10, "bold"), padx=15, pady=15)
        self.slots_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Κουμπιά
        self.btn_frame = tk.Frame(self.window, bg=self.color_bg, pady=15, padx=25)
        self.btn_frame.pack(side="bottom", fill="x")

        self.btn_save = tk.Button(
            self.btn_frame, text="Οριστικοποίηση Κράτησης", command=self._on_save,
            bg=self.color_green, fg="white", font=("Arial", 10, "bold"),
            relief="flat", padx=25, pady=12, cursor="hand2"
        )
        self.btn_save.pack(side="right", padx=5)

        self.btn_cancel = tk.Button(
            self.btn_frame, text="Ακύρωση", command=self.window.destroy,
            bg="#95a5a6", fg="white", font=("Arial", 10),
            relief="flat", padx=20, pady=10, cursor="hand2"
        )
        self.btn_cancel.pack(side="right", padx=5)

    def alert_error(self, msg: str) -> None:
        messagebox.showerror("Σφάλμα", msg)

    def alert_info(self, msg: str) -> None:
        messagebox.showinfo("Πληροφορία", msg)

    def alert_warning(self, msg: str) -> None:
        messagebox.showwarning("Προειδοποίηση", msg)

    def _toggle_customer_mode(self) -> None:
        self.selected_customer_id = None
        self.lbl_selected_cust.config(text="Επιλεγμένος: Κανένας", fg="red")  # UI_COLOR
        for entry_widget in [self.ent_search_name, self.ent_search_email, self.ent_new_fname, 
                             self.ent_new_lname, self.ent_new_phone, self.ent_new_email]:
            entry_widget.delete(0, tk.END)
        if self.var_new_cust.get():
            self.frame_existing.pack_forget()
            self.frame_new.pack(fill="x")  # UI_LAYOUT
        else:
            self.frame_new.pack_forget()
            self.frame_existing.pack(fill="x")  # UI_LAYOUT

    def _on_notes_mousewheel(self, event: Any) -> None:
        if self.ent_notes.winfo_exists():
            self.ent_notes.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_content_mousewheel(self, event: Any) -> None:
        if self.content_canvas.winfo_exists():
            self.content_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_window_mousewheel(self, event: Any) -> None:
        # Εάν ο δρομέας είναι πάνω από τις σημειώσεις, κάνουμε κύλιση στις σημειώσεις. 
        # Διαφορετικά, κάνουμε κύλιση σε ολόκληρη τη φόρμα για καλύτερη εμπειρία χρήστη.
        if self.ent_notes.winfo_exists():
            try:
                if event.widget is self.ent_notes or self.ent_notes == event.widget:
                    self._on_notes_mousewheel(event)
                    return
            except Exception:
                pass
        self._on_content_mousewheel(event)

    def _on_content_canvas_configure(self, event: Any) -> None:
        if self.content_window_id:
            self.content_canvas.itemconfig(self.content_window_id, width=event.width)

    def _refresh_time_slots(self, event: Any = None) -> None:
        selected_date = self.date_entry.get_date()
        slots = self._generate_time_slots(selected_date)
        self.cb_time["values"] = slots
        if slots:
            self.cb_time.set(slots[0])
        else:
            self.cb_time.set("")

    def _generate_time_slots(self, date_obj: datetime.date) -> List[str]:
        # Δημιουργούμε τις διαθέσιμες ώρες για τη συγκεκριμένη ημερομηνία
        # λαμβάνοντας υπόψη τις αργίες και το εβδομαδιαίο πρόγραμμα.
        iso_date = date_obj.isoformat()
        if iso_date in self.blackout_dates:
            return []
        weekday_idx = date_obj.weekday()
        key = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][weekday_idx]
        day_info = self.weekly_schedule.get(key, {})
        if day_info.get("closed"):
            return []
        slots = []
        s1s, s1e = day_info.get("s1_s"), day_info.get("s1_e")
        if s1s and s1e:
            slots.extend(self._range_times(s1s, s1e, self.slot_duration))
        s2s, s2e = day_info.get("s2_s"), day_info.get("s2_e")
        if s2s and s2e:
            slots.extend(self._range_times(s2s, s2e, self.slot_duration))
        return slots

    def _range_times(self, start_str: str, end_str: str, step_min: int) -> List[str]:
        # Δημιουργούμε λίστα με χρονικά διαστήματα (slots) ανάμεσα στην ώρα έναρξης και λήξης.
        time_slots_list = []
        try:
            start = datetime.datetime.strptime(start_str, "%H:%M")
            end = datetime.datetime.strptime(end_str, "%H:%M")
            curr = start
            while curr < end:
                time_slots_list.append(curr.strftime("%H:%M"))
                curr += datetime.timedelta(minutes=step_min)
        except Exception:
            pass
        return time_slots_list

    def _handle_search(self) -> None:
        name_input = self.ent_search_name.get().strip()
        email_input = self.ent_search_email.get().strip()
        
        if not name_input and not email_input:
            self.alert_warning("Παρακαλώ εισάγετε όνομα ή email.")
            return

        # Αναζήτηση πελατών με βάση τα φίλτρα ονόματος ή email στη βάση δεδομένων.
        found_customers = database.search_customers(
            name=name_input if name_input else "",
            email=email_input if email_input else ""
        )

        if not found_customers:
            self._no_customer_found()
            self.alert_error("Δεν βρέθηκε πελάτης με αυτά τα στοιχεία.")
            return

        if len(found_customers) == 1:
            self._select_customer(found_customers[0])
        else:
            self._open_selection_popup(found_customers)

    def _no_customer_found(self) -> None:
        self.selected_customer_id = None
        self.lbl_selected_cust.config(text="Δεν βρέθηκε πελάτης", fg="red")  # UI_COLOR

    def _select_customer(self, customer_dict: Dict[str, Any]) -> None:
        self.selected_customer_id = customer_dict["customer_id"]
        self.lbl_selected_cust.config(
            text=f"Επιλεγμένος: {customer_dict['first_name']} {customer_dict['last_name']}",
            fg="green"
        )  # UI_COLOR

    def _open_selection_popup(self, found_customers: List[Dict[str, Any]]) -> None:
        popup = tk.Toplevel(self.window)
        popup.title("Επιλογή Πελάτη")
        popup.geometry("400x300")
        popup.transient(self.window)
        popup.grab_set()
        popup.focus_force()
        popup.configure(bg="white")
        
        tk.Label(popup, text="Βρέθηκαν πολλαπλοί πελάτες. Επιλέξτε έναν:", bg="white", pady=10).pack()
        
        frame = tk.Frame(popup, bg="white", padx=10)
        frame.pack(fill="both", expand=True)
        
        listbox = tk.Listbox(frame, font=("Arial", 10))
        listbox.pack(side="left", fill="both", expand=True)
        
        scroll = tk.Scrollbar(frame, command=listbox.yview)
        scroll.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scroll.set)
        
        for customer_item in found_customers:
            listbox.insert(tk.END, f"{customer_item['first_name']} {customer_item['last_name']} — {customer_item['email']}")
        
        def on_ok() -> None:
            selected_indices = listbox.curselection()
            if selected_indices:
                self._select_customer(found_customers[selected_indices[0]])
                popup.destroy()
                
        listbox.bind("<Double-1>", lambda event: on_ok())
        
        button_frame = tk.Frame(popup, bg="white", pady=10)
        button_frame.pack(fill="x")
        
        tk.Button(button_frame, text="Ακύρωση", command=popup.destroy, width=10).pack(side="right", padx=10)
        tk.Button(button_frame, text="OK", command=on_ok, width=10, bg=self.color_accent, fg="white").pack(side="right")

    def _on_save(self) -> None:
        self.btn_save.config(state="disabled")
        try:
            appt_date_obj = self.date_entry.get_date()
            if appt_date_obj.isoformat() in self.blackout_dates:
                self.alert_error("Η επιχείρηση είναι κλειστή (αργία).")
                return
            weekday_key = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][appt_date_obj.weekday()]
            if self.weekly_schedule.get(weekday_key, {}).get("closed"):
                self.alert_error("Η επιχείρηση είναι κλειστή.")
                return
            appt_time = self.cb_time.get()
            if not appt_time or appt_time not in self._generate_time_slots(appt_date_obj):
                self.alert_error("Επιλέξτε μια έγκυρη ώρα λειτουργίας.")
                return

            customer_id = None
            if self.var_new_cust.get():
                fname = self.ent_new_fname.get().strip()
                lname = self.ent_new_lname.get().strip()
                email = self.ent_new_email.get().strip()
                if not fname or not lname or not email:
                    self.alert_error("Συμπληρώστε τα υποχρεωτικά πεδία πελάτη.")
                    return
                
                # Έλεγχος αν ο πελάτης υπάρχει ήδη βάσει email
                existing_cust = database.get_customer_by_email(email)
                if existing_cust:
                    self.alert_info(f"Ο πελάτης με email '{email}' υπάρχει ήδη και θα χρησιμοποιηθεί.")
                    customer_id = existing_cust["customer_id"]
                else:
                    customer_id = database.create_customer(fname, lname, self.ent_new_phone.get().strip() or None, email)
            else:
                customer_id = self.selected_customer_id
                if not customer_id:
                    self.alert_error("Δεν έχετε επιλέξει πελάτη.")
                    return

            emp_idx = self.cb_employee.current()
            if emp_idx == -1:
                self.alert_error("Επιλέξτε υπάλληλο.")
                return
            emp_id = self.employees[emp_idx]["employee_id"]
            appt_date_str = self.date_entry.get()

            if database.check_overlap(appt_date_str, appt_time, self.slot_duration):
                self.alert_error("Ο υπάλληλος έχει άλλο ραντεβού την ίδια ώρα.")
                return

            success, error_message = database.create_appointment(
                customer_id=customer_id, user_id=self.user["id"],
                date=appt_date_str, time=appt_time, employee_id=emp_id,
                notes=self.ent_notes.get("1.0", "end-1c").strip()
            )
            if success:
                self.alert_info("Το ραντεβού καταχωρήθηκε επιτυχώς!")
                self.on_success()
                self.window.destroy()
            else:
                self.alert_error(error_message)
        except Exception as booking_error:
            logging.exception("Error saving booking")
            self.alert_error(f"Αποτυχία: {booking_error}")
        finally:
            if self.window.winfo_exists():
                self.btn_save.config(state="normal")
