"""
Ο κώδικας του αρχείου συντάχθηκε από τον Καταξενό Χρήστο

=============================================================================
ΑΡΧΕΙΟ: gui_employees.py
ΣΚΟΠΟΣ: Διαχείριση προσωπικού (CRUD UI)
=============================================================================
"""

import tkinter as tk
from tkinter import ttk
import database
from tkinter import messagebox
from datetime import date
from typing import Any, Dict, List, Tuple, Optional, Callable


# H βασική κλάση που χτίζει την οθόνη διαχείρισης υπαλλήλων
class EmployeesWindow:
    def __init__(self, parent: tk.Widget, user: dict) -> None:
        self.parent = parent
        self.user = user
        self.color_bg = "#F7F9FC"  # Aegean Theme background
        self.color_sidebar = "#0A3D62"  # Sidebar / heading color
        self.color_accent = "#1E90FF"  # Aegean Blue accent
        self.color_white = "#FFFFFF"  # White fields
        self.color_accent_hover = "#1877D4"  # Accent hover color
        self.color_red_hover = "#C23B3C"  # Red hover color
        self.color_red = "#EE5253"  # Delete button red
        self.color_border = "#E5E9F0"  # Border / separator color
        self.parent.configure(background=self.color_bg)

        # MAIN CONTENT AREA: Η κεντρική περιοχή προβολής
        self.content_frame = tk.Frame(self.parent, bg=self.color_bg, padx=30, pady=2)
        self.content_frame.pack(side="right", expand=True, fill="both")

        # Header
        self.header = tk.Frame(self.content_frame, bg=self.color_bg)
        for i in range(4):
            self.content_frame.columnconfigure(i, weight=1)
        self.content_frame.rowconfigure(3, weight=1)
        self.header.grid(row=0, column=0, columnspan=3, sticky="n", pady=(2, 30))
        welcome_text = "Διαχείριση υπαλλήλων του RandeBoo!"
        tk.Label(self.header, text=welcome_text, font=("Arial", 20, "bold"), bg=self.color_bg, fg=self.color_sidebar).pack(side="left")

        # Search Bar & Filters with Shadow
        self.search_shadow = tk.Frame(self.content_frame, bg="#E1E8EE")
        self.search_shadow.grid(row=1, column=0, rowspan=2, columnspan=4, sticky="nsew", padx=0, pady=0)
        
        self.search_frame = tk.Frame(self.search_shadow, bg=self.color_white, padx=15, pady=15, highlightthickness=1, highlightbackground=self.color_border)
        self.search_frame.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 3))

        # Τα textboxes της αναζήτησης
        self.label1 = tk.Label(self.content_frame, bg=self.color_bg, fg=self.color_sidebar, font=("Arial", 12), text="Όνομα")
        self.label1.grid(row=1, column=0, padx=10, pady=(20, 5), sticky="w")
        self.entry_name = tk.Entry(self.content_frame, bg=self.color_white, font=("Arial", 13), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.entry_name.grid(row=2, column=0, padx=10, pady=(5, 35), sticky="ew")
        self.entry_name.focus_set()

        self.label2 = tk.Label(self.content_frame, bg=self.color_bg, fg=self.color_sidebar, font=("Arial", 12), text="Επώνυμο")
        self.label2.grid(row=1, column=1, padx=10, pady=(20, 5), sticky="w")
        self.entry_last_name = tk.Entry(self.content_frame, bg=self.color_white, font=("Arial", 13), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.entry_last_name.grid(row=2, column=1, padx=10, pady=(5, 35), sticky="ew")

        self.label3 = tk.Label(self.content_frame, bg=self.color_bg, fg=self.color_sidebar, font=("Arial", 12), text="Τηλέφωνο")
        self.label3.grid(row=1, column=2, padx=10, pady=(20, 5), sticky="w")
        self.entry_phone = tk.Entry(self.content_frame, bg=self.color_white, font=("Arial", 13), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.entry_phone.grid(row=2, column=2, padx=10, pady=(5, 35), sticky="ew")

        self.label4 = tk.Label(self.content_frame, bg=self.color_bg, fg=self.color_sidebar, font=("Arial", 12), text="Ειδικότητα")
        self.label4.grid(row=1, column=3, padx=10, pady=(20, 5), sticky="w")
        self.entry_specialty = tk.Entry(self.content_frame, bg=self.color_white, font=("Arial", 13), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.entry_specialty.grid(row=2, column=3, padx=10, pady=(5, 35), sticky="ew")

        # Live Search κατά την πληκτρολόγηση
        self.entry_name.bind("<KeyRelease>", lambda event: self._live_search_employee())
        self.entry_last_name.bind("<KeyRelease>", lambda event: self._live_search_employee())
        self.entry_phone.bind("<KeyRelease>", lambda event: self._live_search_employee())
        self.entry_specialty.bind("<KeyRelease>", lambda event: self._live_search_employee())

        self.border_bg_2 = tk.Frame(self.content_frame, bg=self.color_bg, highlightbackground="gray", highlightthickness=2, bd=0)
        self.border_bg_2.grid(row=3, column=0, rowspan=1, columnspan=4, sticky="nsew", padx=0, pady=10)
        self.border_bg_2.lower()

        # Πίνακας Treeview
        self.table_container, self.table = self.show_table(self.content_frame)
        self.table_container.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=10, pady=30)

        # Φόρτωση δεδομένων
        self._load_employees()
        self.table.bind("<Double-1>", lambda event: self._update_employee())

        self.last_hovered_item = None
        self.table.bind("<Motion>", self.on_mouse_move)
        self.table.tag_configure("hover", background="#B3E5FC")

        # Σύνδεση της ροδέλας του ποντικιού για κύλιση στον πίνακα
        self.table.bind("<MouseWheel>", lambda event: self.table.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        # Container Κουμπιών
        self.button_container = tk.Frame(self.content_frame, bg=self.color_bg, padx=30, pady=2)
        self.button_container.grid(row=4, column=0, columnspan=4, sticky="nsew")
        self.button_container.columnconfigure(2, weight=1)
        self.button_container.columnconfigure(3, weight=1)

        # Κουμπιά
        self.add = tk.Button(self.button_container, text="Προσθήκη", command=self._call_add_employee_window, bg=self.color_accent, fg="white", font=("Arial", 9, "bold"), relief="flat", padx=15, cursor="hand2")
        self.add.grid(row=0, column=0, pady=10, padx=10)

        self.update = tk.Button(self.button_container, text="Ενημέρωση", command=self._update_employee, bg=self.color_accent, fg="white", font=("Arial", 9, "bold"), relief="flat", padx=15, cursor="hand2")
        self.update.grid(row=0, column=1, pady=10, padx=10)

        self.delete = tk.Button(self.button_container, text="Διαγραφή", command=self._delete_employee, bg=self.color_red, fg="white", font=("Arial", 9, "bold"), relief="flat", padx=15, cursor="hand2")
        self.delete.grid(row=0, column=4, pady=10, padx=10, sticky="e")

        # Hover Bindings
        self.add.bind("<Enter>", lambda e: self.add.configure(bg=self.color_accent_hover))
        self.add.bind("<Leave>", lambda e: self.add.configure(bg=self.color_accent))
        self.update.bind("<Enter>", lambda e: self.update.configure(bg=self.color_accent_hover))
        self.update.bind("<Leave>", lambda e: self.update.configure(bg=self.color_accent))
        self.delete.bind("<Enter>", lambda e: self.delete.configure(bg=self.color_red_hover))
        self.delete.bind("<Leave>", lambda e: self.delete.configure(bg=self.color_red))

    def show_table(self, content_frame: tk.Frame) -> Tuple[tk.Frame, ttk.Treeview]:
        # Δημιουργία και ρύθμιση του πίνακα υπαλλήλων
        container = tk.Frame(content_frame, bg=self.color_bg)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        columns = ("employee_id", "first_name", "last_name", "phone", "email", "specialty", "hire_date", "username", "role")

        tree = ttk.Treeview(container, columns=columns, show="headings", height=15)
        tree.heading("employee_id", text="Κωδ. Υπαλλήλου")
        tree.heading("first_name", text="Όνομα")
        tree.heading("last_name", text="Επώνυμο")
        tree.heading("phone", text="Τηλέφωνο")
        tree.heading("email", text="e-mail")
        tree.heading("specialty", text="Ειδικότητα")
        tree.heading("hire_date", text="Ημ. Πρόσληψης")
        tree.heading("username", text="Όν. Χρήστη")
        tree.heading("role", text="Ρόλος")

        tree.column("employee_id", width=80, anchor="center")
        tree.column("first_name", width=100, anchor="center")
        tree.column("last_name", width=100, anchor="center")
        tree.column("phone", width=90, anchor="center")
        tree.column("email", width=130, anchor="center")
        tree.column("specialty", width=100, anchor="center")
        tree.column("hire_date", width=90, anchor="center")
        tree.column("username", width=100, anchor="center")
        tree.column("role", width=80, anchor="center")
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        tree.tag_configure("oddrow", background="#FFFFFF")
        tree.tag_configure("evenrow", background="#D9E2EC")

        return container, tree


    def _call_add_employee_window(self) -> None:
        # Εμφάνιση παραθύρου καταχώρησης νέου υπαλλήλου
        add_win = AddEmployeeWindow(self.parent, self.user)
        self.parent.wait_window(add_win.window)
        self._load_employees()

    def _load_employees(self) -> None:
        # Καθαρισμός του πίνακα από τις υπάρχουσες γραμμές
        for tree_item in self.table.get_children():
            self.table.delete(tree_item)

        # Ανάκτηση όλων των ενεργών υπαλλήλων
        all_employees = database.get_active_employees()

        # Ανάκτηση όλων των χρηστών για συσχέτιση μέσω email
        all_users = []
        try:
            all_users = database.get_all_users()
        except Exception:
            pass

        user_mapping = {}
        for u in all_users:
            if u.get("email"):
                user_mapping[u["email"].lower().strip()] = {
                    "username": u.get("username", ""),
                    "role_name": u.get("role_name", "")
                }

        for index, employee in enumerate(all_employees):
            # Μετατροπή ημερομηνίας πρόσληψης από ISO σε μορφή DD/MM/YYYY για εμφάνιση
            hire_date_display = ""
            if employee["hire_date"]:
                date_parts = employee["hire_date"].split("-")
                if len(date_parts) == 3:
                    hire_date_display = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
                else:
                    hire_date_display = employee["hire_date"]

            emp_email = (employee["email"] or "").lower().strip()
            user_info = user_mapping.get(emp_email, {"username": "-", "role_name": "-"})

            employee_values = (
                employee["employee_id"],
                employee["first_name"],
                employee["last_name"],
                employee["phone"],
                employee["email"],
                employee["specialty"],
                hire_date_display,
                user_info["username"],
                user_info["role_name"]
            )
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.table.insert("", "end", values=employee_values, tags=(tag,))

    def _live_search_employee(self) -> None:
        # Δυναμικό φιλτράρισμα υπαλλήλων με βάση τα κριτήρια αναζήτησης
        first_name_query = self.entry_name.get().strip()
        last_name_query = self.entry_last_name.get().strip()
        phone_query = self.entry_phone.get().strip()
        specialty_query = self.entry_specialty.get().strip()

        if not any([first_name_query, last_name_query, phone_query, specialty_query]):
            self._load_employees()
            return

        try:
            search_results = database.search_employees(
                name=first_name_query, 
                last_name=last_name_query, 
                phone=phone_query, 
                specialty=specialty_query
            )

            # Ανάκτηση όλων των χρηστών για συσχέτιση μέσω email
            all_users = []
            try:
                all_users = database.get_all_users()
            except Exception:
                pass

            user_mapping = {}
            for u in all_users:
                if u.get("email"):
                    user_mapping[u["email"].lower().strip()] = {
                        "username": u.get("username", ""),
                        "role_name": u.get("role_name", "")
                    }

            for tree_item in self.table.get_children():
                self.table.delete(tree_item)
            if search_results:
                for index, employee in enumerate(search_results):
                    hire_date_display = ""
                    if employee["hire_date"]:
                        date_parts = employee["hire_date"].split("-")
                        if len(date_parts) == 3:
                            hire_date_display = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
                        else:
                            hire_date_display = employee["hire_date"]

                    emp_email = (employee["email"] or "").lower().strip()
                    user_info = user_mapping.get(emp_email, {"username": "-", "role_name": "-"})

                    employee_values = (
                        employee["employee_id"],
                        employee["first_name"],
                        employee["last_name"],
                        employee["phone"],
                        employee["email"],
                        employee["specialty"],
                        hire_date_display,
                        user_info["username"],
                        user_info["role_name"]
                    )
                    tag = "evenrow" if index % 2 == 0 else "oddrow"
                    self.table.insert("", "end", values=employee_values, tags=(tag,))
        except Exception as err:
            messagebox.showerror("Σφάλμα", f"Αποτυχία αναζήτησης υπαλλήλου: \n{err}")

    def _update_employee(self) -> None:
        # Άνοιγμα παραθύρου επεξεργασίας στοιχείων για τον επιλεγμένο υπάλληλο
        selected_items = self.table.selection()
        if not selected_items:
            messagebox.showwarning("Προσοχή", "Επιλέξτε έναν υπάλληλο από τον πίνακα!")
            return
        selected_item_info = self.table.item(selected_items[0])
        employee_data = selected_item_info["values"]

        update_win = UpdateEmployeeWindow(self.parent, self.user, employee_data)
        self.parent.wait_window(update_win.window)
        self._load_employees()

    def _delete_employee(self) -> None:
        # Απενεργοποίηση/διαγραφή υπαλλήλου
        selected_items = self.table.selection()
        if not selected_items:
            messagebox.showwarning("Προσοχή", "Παρακαλώ επιλέξτε έναν υπάλληλο από τον πίνακα!")
            return
        selected_item_data = self.table.item(selected_items[0])
        employee_values = selected_item_data["values"]
        employee_id = int(employee_values[0])

        confirm_deletion = messagebox.askyesno(
            "Επιβεβαίωση Διαγραφής", 
            f"Είστε σίγουροι ότι θέλετε να διαγράψετε τον υπάλληλο:\n{employee_values[1]} {employee_values[2]};"
        )
        if confirm_deletion:
            try:
                database.delete_employee(employee_id)
                messagebox.showinfo("Επιτυχία", "Ο υπάλληλος διαγράφηκε επιτυχώς!")
                self._load_employees()
            except Exception as err:
                messagebox.showerror("Σφάλμα", f"Αποτυχία διαγραφής υπαλλήλου: \n{err}")

    def on_mouse_move(self, event: Any) -> None:
        # Hover effect στον πίνακα υπαλλήλων
        tree_item = self.table.identify_row(event.y)
        if tree_item != self.last_hovered_item:
            if self.last_hovered_item and self.table.exists(self.last_hovered_item):
                item_index = self.table.index(self.last_hovered_item)
                original_tag = "evenrow" if item_index % 2 == 0 else "oddrow"
                self.table.item(self.last_hovered_item, tags=(original_tag,))
            if tree_item:
                self.table.item(tree_item, tags=("hover",))
            self.last_hovered_item = tree_item



# Kλάση για το παράθυρο καταχώρησης υπαλλήλου
class AddEmployeeWindow:
    def __init__(self, parent: tk.Widget, user: dict) -> None:
        self.user = user
        self.window = tk.Toplevel(parent)
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_force()

        self.window.title("Προσθήκη Υπαλλήλου")
        window_width = 900
        window_height = 650
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.window.resizable(False, False)
        self.window.configure(bg="#F7F9FC")
        self.color_accent = "#1E90FF"

        # Ετικέτα τίτλου του παραθύρου
        self.lbl = tk.Label(self.window, text="Καταχώρηση Νέου Υπαλλήλου", font=("Arial", 16, "bold"), bg="#F7F9FC", fg="#0A3D62")
        self.lbl.pack(pady=(20, 10))

        # Δημιουργία bottom frame για το κουμπί υποβολής (τοποθετείται πρώτο στο side="bottom" για σωστή διάταξη)
        btn_frame = tk.Frame(self.window, bg="#F7F9FC", padx=20, pady=20)
        btn_frame.pack(fill="x", side="bottom")

        # Κουμπί υποβολής
        self.btn_add = tk.Button(btn_frame, text="Καταχώρηση Νέου Υπαλλήλου", command=self._add_employee, bg=self.color_accent, fg="white", font=("Arial", 11, "bold"), relief="flat", cursor="hand2", pady=8)
        self.btn_add.pack(fill="x")

        # Main content container με grid/pack - Καταλαμβάνει όλο τον εναπομείναντα χώρο
        main_frame = tk.Frame(self.window, bg="#F7F9FC", padx=20)
        main_frame.pack(fill="both", expand=True, pady=10)

        # Left Column: Στοιχεία Υπαλλήλου (Κάρτα 1)
        self.left_col = tk.Frame(main_frame, bg="white", padx=20, pady=20, highlightthickness=1, highlightbackground="#E5E9F0")
        self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(self.left_col, text="Στοιχεία Υπαλλήλου", font=("Arial", 12, "bold"), bg="white", fg="#0A3D62").pack(anchor="w", pady=(0, 15))

        tk.Label(self.left_col, text="Όνομα", bg="white", fg="#0A3D62", font=("Arial", 10, "bold")).pack(anchor="w")
        self.ent_name = tk.Entry(self.left_col, font=("Arial", 11), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_name.pack(fill="x", pady=(0, 10))
        self.ent_name.focus_set()

        tk.Label(self.left_col, text="Επώνυμο", bg="white", fg="#0A3D62", font=("Arial", 10, "bold")).pack(anchor="w")
        self.ent_lastname = tk.Entry(self.left_col, font=("Arial", 11), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_lastname.pack(fill="x", pady=(0, 10))

        tk.Label(self.left_col, text="Τηλέφωνο", bg="white", fg="#0A3D62", font=("Arial", 10, "bold")).pack(anchor="w")
        self.ent_phone = tk.Entry(self.left_col, font=("Arial", 11), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_phone.pack(fill="x", pady=(0, 10))

        tk.Label(self.left_col, text="e-mail", bg="white", fg="#0A3D62", font=("Arial", 10, "bold")).pack(anchor="w")
        self.ent_email = tk.Entry(self.left_col, font=("Arial", 11), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_email.pack(fill="x", pady=(0, 10))

        tk.Label(self.left_col, text="Ειδικότητα", bg="white", fg="#0A3D62", font=("Arial", 10, "bold")).pack(anchor="w")
        self.ent_specialty = tk.Entry(self.left_col, font=("Arial", 11), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_specialty.pack(fill="x", pady=(0, 10))

        tk.Label(self.left_col, text="Ημερομηνία Πρόσληψης (DD/MM/YYYY)", bg="white", fg="#0A3D62", font=("Arial", 10, "bold")).pack(anchor="w")
        self.ent_hire_date = tk.Entry(self.left_col, font=("Arial", 11), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_hire_date.pack(fill="x", pady=(0, 10))
        
        # Προεπιλογή της σημερινής ημερομηνίας
        today_str = date.today().strftime("%d/%m/%Y")
        self.ent_hire_date.insert(0, today_str)

        tk.Label(self.left_col, text="Σημειώσεις", bg="white", fg="#0A3D62", font=("Arial", 10, "bold")).pack(anchor="w")
        self.ent_notes = tk.Entry(self.left_col, font=("Arial", 11), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_notes.pack(fill="x", pady=(0, 10))

        # Right Column: Στοιχεία Σύνδεσης (Κάρτα 2)
        self.right_col = tk.Frame(main_frame, bg="white", padx=20, pady=20, highlightthickness=1, highlightbackground="#E5E9F0")
        self.right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(self.right_col, text="Πρόσβαση στο Σύστημα", font=("Arial", 12, "bold"), bg="white", fg="#0A3D62").pack(anchor="w", pady=(0, 15))

        # Checkbox για τη δημιουργία λογαριασμού χρήστη
        self.user_activation = tk.BooleanVar(value=False)
        self.check_allows_login = tk.Checkbutton(
            self.right_col, 
            text="Επιτρέπεται η είσοδος στο σύστημα (Λογαριασμός Χρήστη)", 
            variable=self.user_activation, 
            bg="white", 
            activebackground="white",
            font=("Arial", 11, "bold"),
            command=self._toggle_login_fields
        )
        self.check_allows_login.pack(pady=(0, 15), anchor="w")

        # Frame για τα στοιχεία σύνδεσης του χρήστη
        self.login_fields_frame = tk.Frame(self.right_col, bg="white")

        tk.Label(self.login_fields_frame, text="Όνομα Χρήστη", bg="white", fg="#0A3D62", font=("Arial", 10, "bold")).pack(anchor="w")
        self.ent_username = tk.Entry(self.login_fields_frame, font=("Arial", 11), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_username.pack(fill="x", pady=(0, 15))

        tk.Label(self.login_fields_frame, text="Κωδικός Πρόσβασης", bg="white", fg="#0A3D62", font=("Arial", 10, "bold")).pack(anchor="w")
        self.ent_password = tk.Entry(self.login_fields_frame, font=("Arial", 11), relief="flat", show="*", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_password.pack(fill="x", pady=(0, 15))

        tk.Label(self.login_fields_frame, text="Ρόλος", bg="white", fg="#0A3D62", font=("Arial", 10, "bold")).pack(anchor="w")
        self.ent_role = ttk.Combobox(self.login_fields_frame, font=("Arial", 11), state="readonly")
        
        # Φόρτωση των διαθέσιμων ρόλων από τη βάση
        self.roles_list = []
        try:
            self.roles_list = database.get_all_roles()
        except Exception:
            self.roles_list = [{"role_id": 1, "role_name": "admin"}, {"role_id": 2, "role_name": "user"}, {"role_id": 3, "role_name": "Staff"}]
        
        role_names = [r["role_name"] for r in self.roles_list]
        self.ent_role["values"] = role_names
        if "user" in role_names:
            self.ent_role.set("user")
        elif role_names:
            self.ent_role.current(0)
        self.ent_role.pack(fill="x", pady=(0, 15))

        # Το κουμπί υποβολής έχει μεταφερθεί και αρχικοποιηθεί νωρίτερα για σωστό layout

        # Bindings για Enter και Escape
        self.ent_name.bind("<Return>", lambda event: self._add_employee())
        self.ent_lastname.bind("<Return>", lambda event: self._add_employee())
        self.ent_phone.bind("<Return>", lambda event: self._add_employee())
        self.ent_email.bind("<Return>", lambda event: self._add_employee())
        self.ent_specialty.bind("<Return>", lambda event: self._add_employee())
        self.ent_hire_date.bind("<Return>", lambda event: self._add_employee())
        self.ent_notes.bind("<Return>", lambda event: self._add_employee())
        self.ent_username.bind("<Return>", lambda event: self._add_employee())
        self.ent_password.bind("<Return>", lambda event: self._add_employee())
        self.window.bind("<Escape>", lambda event: self.window.destroy())

    # Εμφάνιση ή απόκρυψη των πεδίων σύνδεσης
    def _toggle_login_fields(self) -> None:
        if self.user_activation.get():
            self.login_fields_frame.pack(fill="x")
        else:
            self.login_fields_frame.pack_forget()

    # Προσθήκη υπαλλήλου και (προαιρετικά) λογαριασμού χρήστη
    def _add_employee(self) -> None:
        first_name = self.ent_name.get().strip()
        last_name = self.ent_lastname.get().strip()
        phone_num = self.ent_phone.get().strip()
        email_addr = self.ent_email.get().strip()
        specialty = self.ent_specialty.get().strip()
        hire_date_str = self.ent_hire_date.get().strip()
        notes = self.ent_notes.get().strip()

        # Έλεγχος υποχρεωτικών πεδίων
        if not first_name or not last_name or not email_addr or not phone_num:
            messagebox.showwarning("Προσοχή", "Το Όνομα, το Επώνυμο, το Τηλέφωνο και το Email είναι υποχρεωτικά.", parent=self.window)
            return

        if "@" not in email_addr or "." not in email_addr:
            messagebox.showwarning("Σφάλμα", "Το e-mail δεν φαίνεται έγκυρο!", parent=self.window)
            return

        if len(phone_num) < 10:
            messagebox.showwarning("Σφάλμα", "Το τηλέφωνο πρέπει να είναι τουλάχιστον 10 ψηφία!", parent=self.window)
            return

        # Έλεγχοι για το λογαριασμό χρήστη, εφόσον ζητήθηκε ενεργοποίηση
        username = ""
        password = ""
        role_id = 2
        if self.user_activation.get():
            username = self.ent_username.get().strip()
            password = self.ent_password.get().strip()
            role_name = self.ent_role.get()

            if not username or not password:
                messagebox.showwarning("Προσοχή", "Το Username και ο Κωδικός είναι υποχρεωτικά για την ενεργοποίηση εισόδου.", parent=self.window)
                return

            if len(password) < 6:
                messagebox.showwarning("Σφάλμα", "Ο κωδικός δεν μπορεί να είναι μικρότερος από 6 χαρακτήρες!", parent=self.window)
                return

            # Έλεγχος μοναδικότητας username στη βάση δεδομένων
            existing_user_by_uname = database.get_user_by_username(username)
            if existing_user_by_uname:
                messagebox.showwarning("Σφάλμα", "Το όνομα χρήστη (Username) χρησιμοποιείται ήδη!", parent=self.window)
                return

            # Έλεγχος μοναδικότητας email στους χρήστες
            existing_users_by_email = database.search_users(email=email_addr)
            if existing_users_by_email:
                messagebox.showwarning("Σφάλμα", "Υπάρχει ήδη χρήστης με αυτό το email!", parent=self.window)
                return

            # Εύρεση του role_id βάσει ονόματος ρόλου
            for r in self.roles_list:
                if r["role_name"] == role_name:
                    role_id = r["role_id"]
                    break

        try:
            # Δημιουργία του υπαλλήλου
            user_id = self.user["id"]
            database.create_employee(
                first_name=first_name,
                last_name=last_name,
                phone=phone_num,
                email=email_addr,
                user_id=user_id,
                specialty=specialty,
                hire_date=hire_date_str,
                notes=notes
            )

            # Δημιουργία λογαριασμού χρήστη εάν ζητήθηκε
            if self.user_activation.get():
                database.create_user(
                    username=username,
                    password=password,
                    role_id=role_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email_addr,
                    phone=phone_num,
                    is_active=1
                )

            messagebox.showinfo("Επιτυχία", "Ο υπάλληλος προστέθηκε επιτυχώς!", parent=self.window)
            self.window.destroy()
        except Exception as err:
            messagebox.showerror("Σφάλμα", f"Αποτυχία προσθήκης υπαλλήλου: \n{err}", parent=self.window)


# Kλάση για το παράθυρο ενημέρωσης υπαλλήλου
class UpdateEmployeeWindow(AddEmployeeWindow):
    def __init__(self, parent: tk.Widget, user: dict, emp_data: list) -> None:
        super().__init__(parent, user)

        self.window.title("Ενημέρωση Υπαλλήλου")
        self.lbl.config(text="Ενημέρωση Στοιχείων Υπαλλήλου")

        # Προσυμπλήρωση στοιχείων υπαλλήλου
        self.employee_id = emp_data[0]
        self.ent_name.insert(0, emp_data[1] or "")
        self.ent_lastname.insert(0, emp_data[2] or "")
        self.ent_phone.insert(0, emp_data[3] or "")
        self.ent_email.insert(0, emp_data[4] or "")
        self.ent_specialty.insert(0, emp_data[5] or "")
        self.ent_hire_date.delete(0, tk.END)
        self.ent_hire_date.insert(0, emp_data[6] or "")

        # Ανάκτηση των σημειώσεων του υπαλλήλου
        all_employees_list = database.get_active_employees()
        notes = ""
        for employee in all_employees_list:
            if employee["employee_id"] == self.employee_id:
                notes = employee.get("notes", "") or ""
                break
        self.ent_notes.insert(0, notes)

        # Αναζήτηση συνδεδεμένου λογαριασμού χρήστη με βάση το email
        self.associated_user = None
        self.original_email = emp_data[4]
        if self.original_email:
            try:
                users_list = database.search_users(email=self.original_email)
                if users_list:
                    self.associated_user = users_list[0]
            except Exception:
                pass

        # Εάν υπάρχει χρήστης, προσυμπληρώνουμε τα στοιχεία
        if self.associated_user:
            self.user_activation.set(True)
            self._toggle_login_fields()
            self.ent_username.insert(0, self.associated_user.get("username", ""))
            
            current_role_id = self.associated_user.get("role_id")
            for r in self.roles_list:
                if r["role_id"] == current_role_id:
                    self.ent_role.set(r["role_name"])
                    break

        self.btn_add.configure(text="Ενημέρωση στοιχείων", command=self._do_update_employee)

        self.ent_name.bind("<Return>", lambda event: self._do_update_employee())
        self.ent_lastname.bind("<Return>", lambda event: self._do_update_employee())
        self.ent_phone.bind("<Return>", lambda event: self._do_update_employee())
        self.ent_email.bind("<Return>", lambda event: self._do_update_employee())
        self.ent_specialty.bind("<Return>", lambda event: self._do_update_employee())
        self.ent_hire_date.bind("<Return>", lambda event: self._do_update_employee())
        self.ent_notes.bind("<Return>", lambda event: self._do_update_employee())
        self.ent_username.bind("<Return>", lambda event: self._do_update_employee())
        self.ent_password.bind("<Return>", lambda event: self._do_update_employee())

    # Εκτέλεση ενημέρωσης υπαλλήλου και λογαριασμού χρήστη
    def _do_update_employee(self) -> None:
        first_name = self.ent_name.get().strip()
        last_name = self.ent_lastname.get().strip()
        phone_num = self.ent_phone.get().strip()
        email_addr = self.ent_email.get().strip()
        specialty = self.ent_specialty.get().strip()
        hire_date_str = self.ent_hire_date.get().strip()
        notes = self.ent_notes.get().strip()

        # Έλεγχοι εγκυρότητας πεδίων υπαλλήλου
        if not first_name or not last_name or not email_addr or not phone_num:
            messagebox.showwarning("Προσοχή", "Συμπληρώστε Όνομα, Επώνυμο, Τηλέφωνο και Email!", parent=self.window)
            return

        if "@" not in email_addr or "." not in email_addr:
            messagebox.showwarning("Σφάλμα", "Το e-mail δεν φαίνεται έγκυρο!", parent=self.window)
            return

        if len(phone_num) < 10:
            messagebox.showwarning("Σφάλμα", "Το τηλέφωνο πρέπει να είναι τουλάχιστον 10 ψηφία!", parent=self.window)
            return

        # Έλεγχοι στοιχείων χρήστη αν είναι ενεργοποιημένος
        username = ""
        password = ""
        role_id = 2
        if self.user_activation.get():
            username = self.ent_username.get().strip()
            password = self.ent_password.get().strip()
            role_name = self.ent_role.get()

            if not username:
                messagebox.showwarning("Προσοχή", "Το Username είναι υποχρεωτικό για την ενεργοποίηση εισόδου.", parent=self.window)
                return

            for r in self.roles_list:
                if r["role_name"] == role_name:
                    role_id = r["role_id"]
                    break

            # Έλεγχος μοναδικότητας username/email αν άλλαξαν
            if self.associated_user:
                if username != self.associated_user.get("username"):
                    existing_user = database.get_user_by_username(username)
                    if existing_user:
                        messagebox.showwarning("Σφάλμα", "Το όνομα χρήστη (Username) χρησιμοποιείται ήδη!", parent=self.window)
                        return
                
                if email_addr != self.associated_user.get("email"):
                    existing_by_email = database.search_users(email=email_addr)
                    if existing_by_email:
                        messagebox.showwarning("Σφάλμα", "Υπάρχει ήδη χρήστης με αυτό το email!", parent=self.window)
                        return
            else:
                # Για νέο λογαριασμό χρήστη, ο κωδικός είναι υποχρεωτικός
                if not password:
                    messagebox.showwarning("Προσοχή", "Ο Κωδικός είναι υποχρεωτικός για την ενεργοποίηση εισόδου.", parent=self.window)
                    return
                if len(password) < 6:
                    messagebox.showwarning("Σφάλμα", "Ο κωδικός δεν μπορεί να είναι μικρότερος από 6 χαρακτήρες!", parent=self.window)
                    return

                existing_user = database.get_user_by_username(username)
                if existing_user:
                    messagebox.showwarning("Σφάλμα", "Το όνομα χρήστη (Username) χρησιμοποιείται ήδη!", parent=self.window)
                    return

                existing_by_email = database.search_users(email=email_addr)
                if existing_by_email:
                    messagebox.showwarning("Σφάλμα", "Υπάρχει ήδη χρήστης με αυτό το email!", parent=self.window)
                    return

        try:
            # Ενημέρωση υπαλλήλου στη βάση δεδομένων
            is_success = database.update_employee(
                employee_id=self.employee_id,
                first_name=first_name,
                last_name=last_name,
                phone=phone_num,
                email=email_addr,
                specialty=specialty,
                hire_date=hire_date_str,
                notes=notes,
                is_active=1
            )

            if is_success:
                # Διαχείριση λογαριασμού χρήστη
                if self.user_activation.get():
                    if self.associated_user:
                        # Ενημέρωση υπάρχοντος χρήστη
                        database.update_user(
                            user_id=self.associated_user["user_id"],
                            username=username,
                            first_name=first_name,
                            last_name=last_name,
                            phone=phone_num,
                            email=email_addr,
                            role_id=role_id,
                            is_active=1
                        )
                        # Αλλαγή κωδικού αν συμπληρώθηκε
                        if password:
                            if len(password) < 6:
                                messagebox.showwarning("Σφάλμα", "Ο κωδικός δεν μπορεί να είναι μικρότερος από 6 χαρακτήρες!", parent=self.window)
                                return
                            database.change_password(self.associated_user["user_id"], password)
                    else:
                        # Δημιουργία νέου χρήστη
                        database.create_user(
                            username=username,
                            password=password,
                            role_id=role_id,
                            first_name=first_name,
                            last_name=last_name,
                            email=email_addr,
                            phone=phone_num,
                            is_active=1
                        )
                else:
                    # Εάν απενεργοποιήθηκε ο λογαριασμός, διαγράφουμε το χρήστη
                    if self.associated_user:
                        database.delete_user(self.associated_user["user_id"])

                messagebox.showinfo("Επιτυχία", "Η ενημέρωση ολοκληρώθηκε!", parent=self.window)
                self.window.destroy()
            else:
                messagebox.showerror("Σφάλμα", "Αποτυχία ενημέρωσης υπαλλήλου.", parent=self.window)
        except Exception as err:
            messagebox.showerror("Σφάλμα", f"Αποτυχία ενημέρωσης: {err}", parent=self.window)
