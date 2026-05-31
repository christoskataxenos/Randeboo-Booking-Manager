"""
=============================================================================
=                                                                           =
=       Ο κώδικας του αρχείου συντάχθηκε από τον Ασπρίδη Δημήτρη.           =
=                                                                           =
=   ΣΗΜΕΙΩΣΗ: Οι αλλαγές στις γραμμές 356 και 410 έγιναν από τον            =
=   Καταξένο Χρήστο για την υποστήριξη του Email-First συστήματος.          =
=                                                                           =
=============================================================================
ΑΡΧΕΙΟ: gui_customers.py
ΣΚΟΠΟΣ: Διαχείριση Πελατών — CRUD (Create, Read, Update, Delete)
=============================================================================
"""
"""
ANCHOR INDEX (CTRL+F):
UI_COLOR   → Όλα τα χρώματα (bg/fg)
UI_LAYOUT  → Στοίχιση, padding, pack/grid/place
UI_FONT    → Γραμματοσειρές, μεγέθη, bold
UI_BUTTON  → Κουμπιά & hover effects
UI_SECTION → Μεγάλα UI blocks (π.χ. Search Bar, Customer Table, Action Buttons)
"""

import tkinter as tk
from tkinter import ttk
import database
from tkinter import messagebox

# H βασική κλάση που χτίζει την οθόνη διαχείρισης πελατών
class CustomersWindow:
    def __init__(self,parent,user):
        self.parent = parent
        self.user = user
        self.color_bg = "#F7F9FC"
        self.color_sidebar = "#0A3D62"
        self.color_accent = "#1E90FF"
        self.color_white = "#FFFFFF"
        self.color_accent_hover = "#1877D4"
        self.color_red_hover = "#C23B3C"
        self.color_red = "#EE5253"
        self.color_border = "#E5E9F0"
        self.parent.configure(bg=self.color_bg)

        # MAIN CONTENT AREA: Η κεντρική περιοχή προβολής
        self.content_frame = tk.Frame(self.parent, bg=self.color_bg, padx=30, pady=2)
        self.content_frame.pack(side="right", expand=True, fill="both")

        # Header: Καλωσόρισμα
        self.header = tk.Frame(self.content_frame, bg=self.color_bg)
        for i in range (4):
            self.content_frame.columnconfigure(i, weight=1)
        self.content_frame.rowconfigure(3, weight=1)
        self.header.grid(row=0, column=0, columnspan=3, sticky="n", pady=(2,30))
        welcome_text = f"Διαχείριση πελατών του RandeBoo!"
        tk.Label(self.header, text=welcome_text, font=("Arial", 20, "bold"), bg=self.color_bg, fg=self.color_sidebar).pack(side="left")

        self.search_shadow = tk.Frame(self.content_frame, bg="#E1E8EE")
        self.search_shadow.grid(row=1, column=0, rowspan=2, columnspan=4, sticky="nsew", padx=0, pady=0)
        
        self.search_frame = tk.Frame(self.search_shadow, bg=self.color_white, padx=15, pady=15, highlightthickness=1, highlightbackground=self.color_border)
        self.search_frame.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 3))

        # Τα textboxes της αναζήτησης και τα labels τους. Σε στοίχιση grid για να είναι στοιχισμένα σε "κολώνες"
        self.label1=(tk.Label(self.content_frame, bg=self.color_bg, fg=self.color_sidebar, font=("Arial", 12), text="Όνομα"))
        self.label1.grid(row=1, column=0, padx=10, pady=(20,5), sticky="w")
        self.entry_name = tk.Entry(self.content_frame, bg=self.color_white, font=("Arial", 13), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.entry_name.grid(row=2, column=0, padx=10, pady=(5,35), sticky="ew")
        self.entry_name.focus_set()
 
        self.label2=(tk.Label(self.content_frame, bg=self.color_bg, fg=self.color_sidebar, font=("Arial", 12), text="Επώνυμο"))
        self.label2.grid(row=1, column=1, padx=10, pady=(20,5), sticky="w")
        self.entry_last_name = tk.Entry(self.content_frame, bg=self.color_white, font=("Arial", 13), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.entry_last_name.grid(row=2, column=1, padx=10, pady=(5,35), sticky="ew")
 
        self.label3=(tk.Label(self.content_frame, bg=self.color_bg, fg=self.color_sidebar, font=("Arial", 12), text="Τηλέφωνο"))
        self.label3.grid(row=1, column=2, padx=10, pady=(20,5), sticky="w")
        self.entry_phone = tk.Entry(self.content_frame, bg=self.color_white, font=("Arial", 13), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.entry_phone.grid(row=2, column=2, padx=10, pady=(5,35), sticky="ew")
 
        self.label4=(tk.Label(self.content_frame, bg=self.color_bg, fg=self.color_sidebar, font=("Arial", 12), text="e-mail"))
        self.label4.grid(row=1, column=3, padx=10, pady=(20,5), sticky="w")
        self.entry_email = tk.Entry(self.content_frame, bg=self.color_white, font=("Arial", 13), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.entry_email.grid(row=2, column=3, padx=10, pady=(5,35), sticky="ew")

        # Κάνει realtime filtering κατά την πληκτρολόγηση
        self.entry_name.bind('<KeyRelease>', lambda event: self._live_search_customer())
        self.entry_last_name.bind('<KeyRelease>', lambda event: self._live_search_customer())
        self.entry_phone.bind('<KeyRelease>', lambda event: self._live_search_customer())
        self.entry_email.bind('<KeyRelease>', lambda event: self._live_search_customer())

        self.border_bg_2 = tk.Frame(self.content_frame,bg=self.color_bg, highlightbackground="gray", highlightthickness=2, bd=0)
        self.border_bg_2.grid(row=3, column=0, rowspan=1, columnspan=4, sticky="nsew", padx=0, pady=10)
        # Χρησιμοποιώ τη μέθοδο lower() για να "πάει" το frame του border πίσω από τα labels και τα entries, αλλιώς θα τα κρύψει.
        self.border_bg_2.lower()

        # Εδώ δηλώνω το container του πίνακα με τους πελάτες. Βοηθάει στη στοίχιση και στο styling
        self.table_container, self.table=self.show_table(self.content_frame)
        self.table_container.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=10, pady=30)

        # Γεμίζω με data τον πίνακα
        self._load_customers()
        self.table.bind("<Double-1>", lambda event: self._update_customer())

        self.last_hovered_item = None
        self.table.bind("<Motion>", self.on_mouse_move)
        self.table.tag_configure('hover', background='#B3E5FC')

        # Εδώ δηλώνω το container των κουμπιών. Βοηθάει στη στοίχιση και στο styling
        self.button_container = tk.Frame(self.content_frame, bg=self.color_bg, padx=30, pady=2)
        self.button_container.grid(row=4, column=0, columnspan=4, sticky="nsew")
        # To weight στις κολώνες 2 και 3 βοηθάει ώστε να σπρώχνω το κουμπί της Διαγραφής (κολώνα 4) τέρμα δεξιά
        self.button_container.columnconfigure(2, weight=1)
        self.button_container.columnconfigure(3, weight=1)

        # Τα κουμπιά στοιχισμένα σε κολώνες από το grid
        self.add = tk.Button(self.button_container, text='Προσθήκη', command=self._call_add_customer_window, bg=self.color_accent, fg="white",font=("Arial", 9, "bold"), relief="flat", padx=15, cursor="hand2")
        self.add.grid(row=0, column=0, pady=10, padx=10)

        self.update = tk.Button(self.button_container, text='Ενημέρωση', command=self._update_customer, bg=self.color_accent, fg="white",font=("Arial", 9, "bold"), relief="flat", padx=15, cursor="hand2")
        self.update.grid(row=0, column=1, pady=10, padx=10)

        self.delete = tk.Button(self.button_container, text='Διαγραφή', command=self._delete_customer, bg=self.color_red, fg="white",font=("Arial", 9, "bold"), relief="flat", padx=15, cursor="hand2")
        self.delete.grid(row=0, column=4, pady=10, padx=10, sticky="e")

        # Αλλάζει χρώμα το κουμπί όταν κάνω hover το ποντίκι από πάνω
        self.add.bind("<Enter>", lambda e: self.add.configure(bg=self.color_accent_hover))
        self.add.bind("<Leave>", lambda e: self.add.configure(bg=self.color_accent))
        self.update.bind("<Enter>", lambda e: self.update.configure(bg=self.color_accent_hover))
        self.update.bind("<Leave>", lambda e: self.update.configure(bg=self.color_accent))
        self.delete.bind("<Enter>", lambda e: self.delete.configure(bg=self.color_red_hover))
        self.delete.bind("<Leave>", lambda e: self.delete.configure(bg=self.color_red))

    # Δήλωση συνάρτηση για την απεικόνιση του πίνακα
    def show_table(self,content_frame):
        container = tk.Frame(content_frame, bg=self.color_bg)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        # Δήλωση στηλών
        columns=("customer_id","first_name","last_name","phone","email")

        # Δημιουργία Treeview
        tree=ttk.Treeview(container,columns=columns,show="headings",height=15)
        tree.heading("customer_id", text="Κωδ. Πελάτη")
        tree.heading("first_name", text="Όνομα")
        tree.heading("last_name", text="Επώνυμο")
        tree.heading("phone", text="Τηλέφωνο")
        tree.heading("email", text="e-mail")
        tree.column("customer_id",width=60,anchor="center")
        tree.column("first_name",width=140,anchor="center")
        tree.column("last_name", width=140,anchor="center")
        tree.column("phone", width=100,anchor="center")
        tree.column("email", width=100,anchor="center")
        tree.pack(side="left", fill="both" ,expand=True)

        # Δηλώνω τη scrollbar του πίνακα, σε περίπτωση που έχει περισσότερα από 15 αποτελέσματα
        # να δείξει(τόσα εχω ορίσει με το height παραπάνω)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Μορφοποιώ με διαφορετικό χρώμα ανά γραμμή σύμφωνα με το tag που έχει πάρει από την _load_customers()
        tree.tag_configure('oddrow', background='#FFFFFF')
        tree.tag_configure('evenrow', background='#D9E2EC')

        return container,tree

    # Συνάρτηση που φτιάχνει νέο παράθυρο για την προσθήκη πελάτη
    def _call_add_customer_window(self):
        # Φτιάχνω αντικείμενο νέου παραθύρου
        add_win=AddCustomerWindow(self.parent)
        # Περιμένω να κλείσει το πρόσθετο παράθυρο
        self.parent.wait_window(add_win.window)
        # Με το κλείσιμο του παραθύρου της προσθήκης, ξαναφορτώνω με δεδομένα τον πίνακα (για να φέρει και το νέο πελάτη)
        self._load_customers()

    # Συνάρτηση για να φορτώνω με τους πελάτες τον πίνακα της οθόνης
    def _load_customers(self):
        # Καθαρίζω τον πίνακα από προηγούμενα αποτελέσματα αν υπάρχουν
        for item in self.table.get_children():
            self.table.delete(item)

        # Καλώ την get_all_customers() από το database.py και περνάω τα αποτελέσματα (list) σε μια δική μου μεταβλητή
        all_customers = database.get_all_customers()

        # Φορτώνω την επιστρεφόμενη λίστα στο πίνακα του παράθυρου (treeview)
        for i, customer in enumerate(all_customers):
            customer_values = (
                customer['customer_id'],
                customer['first_name'],
                customer['last_name'],
                customer['phone'],
                customer['email']
            )
            tag='evenrow' if i%2==0 else 'oddrow'
            self.table.insert("", "end", values=customer_values, tags=(tag,))

    def _live_search_customer(self):
        # Διαβάζω όλα πεδία και τα περνάω σε μεταβλητή
        n = self.entry_name.get().strip()
        ln = self.entry_last_name.get().strip()
        p = self.entry_phone.get().strip()
        e = self.entry_email.get().strip()

        # Αν είναι όλα τελείως άδεια, δείχνω όλη τη λίστα
        if not any([n, ln, p, e]):
            self._load_customers()
            return

        # Error handling για την επικοινωνία με τη βάση
        try:
            # Καλώ την αναζήτηση πελατών με το πεδίο που έχει δώσει ο χρήστης
            search = database.search_customers(name=n, last_name=ln, phone=p, email=e)
            # Αν η αναζήτηση επιστρέψει αποτελέσματα, αδειάζω τον πίνακα.
            if search:
                for item in self.table.get_children():
                    self.table.delete(item)
                # Φορτώνω την επιστρεφόμενη λίστα στο πίνακα του παράθυρου (treeview)
                for i,item in enumerate(search):
                    customer_values = (
                        item['customer_id'],
                        item['first_name'],
                        item['last_name'],
                        item['phone'],
                        item['email']
                    )
                    # Βάζω tag για να χρωματίσω κατάλληλα τις γραμμές
                    tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                    # Γεμίζω τον πίνακα με τις τιμές
                    self.table.insert("", "end", values=customer_values, tags=(tag,))
            else:
                # Αν η search είναι άδεια σημαίνει ότι δε βρέθηκε πελάτης, οπότε αδειάζω το πίνακα
                for item in self.table.get_children():
                    self.table.delete(item)
        except Exception as error:
            # PopUP message σε περίπτωση που βγει λάθος που δεν αναμένεται
            messagebox.showerror("Σφάλμα", f"Αποτυχία αναζήτησης πελάτη: \n{error}")

    # Συνάρτηση ενημέρωσης πελάτη με νέα στοιχεία που δηλώνει ο χρήστης
    def _update_customer(self):
        # Παίρνω τα δεδομένα του πελάτη από την επιλεγμένη εγγραφή
        selected = self.table.selection()
        if not selected:
            # # PopUP message αν δεν έχει επιλεχθεί κάποιος πελάτης
            messagebox.showwarning("Προσοχή", "Επιλέξτε έναν πελάτη από τον πίνακα!")
            return
        item_info = self.table.item(selected[0])
        customer_data=item_info['values']

        # Δημιουργώ ένα νέο αντικείμενο της κλάσης για το παράθυρο ενημέρωσης
        update_win = UpdateCustomerWindow(self.parent, customer_data)

        # Περιμένω να κλείσει το επιπλέον παράθυρο. Μόλις κλείσει κάνω refresh τα δεδομένα του πίνακα
        self.parent.wait_window(update_win.window)
        self._load_customers()

    # Συνάρτηση με την οποία διαγράφω από τη βάση τον επιλεγμένο πελάτη
    def _delete_customer(self):
        # Παίρνω τα δεδομένα του πελάτη από την επιλεγμένη εγγραφή
        selected_item = self.table.selection()
        if not selected_item:
            # # PopUP message αν δεν έχει επιλεχθεί κάποιος πελάτης
            messagebox.showwarning("Προσοχή", "Παρακαλώ επιλέξτε έναν πελάτη από τον πίνακα!")
            return None
        # Μετατροπές μεταβλητών ώστε να καταλήξω με το customer_id που είναι int
        item_data=self.table.item(selected_item[0])
        customer_values=item_data['values']
        self.c_id = int(customer_values[0])

        # Επιβεβαιωτικό μήνυμα ότι θέλουμε να διαγραφεί ο πελάτης. Στην περίπτωση του Yes προχωρώ σε διαγραφή
        confirm = messagebox.askyesno("Επιβεβαίωση Διαγραφής",f"Είστε σίγουροι ότι θέλετε να διαγράψετε τον πελάτη:\n{customer_values[1]} {customer_values[2]};")
        if confirm:
            try:
                database.delete_customer(self.c_id)
                messagebox.showinfo("Επιτυχία", "Ο πελάτης διαγράφηκε επιτυχώς!")
                self._load_customers()
            except Exception as error:
                messagebox.showerror("Σφάλμα", f"Αποτυχία διαγραφής πελάτη με μήνυμα: \n{error}")
        else:
            return None

    def on_mouse_move(self, event):
        item = self.table.identify_row(event.y)

        if item != self.last_hovered_item:
            # Επαναφορά της προηγούμενης γραμμής στο αρχικό της tag (even/odd)
            if self.last_hovered_item and self.table.exists(self.last_hovered_item):
                # Βρίσκουμε το index για να ξέρουμε αν ήταν even ή odd
                idx = self.table.index(self.last_hovered_item)
                original_tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                self.table.item(self.last_hovered_item, tags=(original_tag,))

            # Εφαρμογή του hover στη νέα γραμμή
            if item:
                self.table.item(item, tags=('hover',))

            self.last_hovered_item = item



# Kλάση για το παράθυρο καταχώρησης πελάτη
class AddCustomerWindow:
    def __init__(self, parent):
        # Ορίζω το παράθυρο
        self.window = tk.Toplevel(parent)
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_force()

        # Κεντράρω το παράθυρο στο κέντρο της οθόνης και βάζω κάποια βασικά χρώματα και ρυθμίσεις
        self.window.title("Προσθήκη Πελάτη")
        window_width = 1024
        window_height = 768
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.window.resizable(False, False)
        self.window.configure(bg="#F7F9FC")
        self.color_accent = "#1E90FF"

        # Δήλωση βασικού label
        self.lbl=tk.Label(self.window, text="Καταχώρηση Νέου Πελάτη", font=("Arial", 14, "bold"), bg="white", fg="#0A3D62")
        self.lbl.pack(pady=20)
        main_frame = tk.Frame(self.window, bg="white", padx=20)
        main_frame.pack(fill="both", expand=True)

        # Πεδία για την καταχώρηση των στοιχείων του πελάτη
        tk.Label(main_frame, text="Όνομα", bg="white").pack(anchor="w")
        self.ent_name = tk.Entry(main_frame, font=("Arial", 11), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_name.pack(fill="x", pady=(0, 10))
        self.ent_name.focus_set()
        tk.Label(main_frame, text="Επώνυμο", bg="white").pack(anchor="w")
        self.ent_lastname = tk.Entry(main_frame, font=("Arial", 11), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_lastname.pack(fill="x", pady=(0, 10))
        tk.Label(main_frame, text="Τηλέφωνο", bg="white").pack(anchor="w")
        self.ent_phone = tk.Entry(main_frame, font=("Arial", 11), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_phone.pack(fill="x", pady=(0, 10))
        tk.Label(main_frame, text="e-mail", bg="white").pack(anchor="w")
        self.ent_email= tk.Entry(main_frame, font=("Arial", 11), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_email.pack(fill="x", pady=(0, 10))

        # Το κουμπί της καταχώρησης
        self.btn_add = tk.Button(main_frame, text="Καταχώρηση Νέου Πελάτη", command=self._add_customer, bg=self.color_accent, fg="white", font=("Arial", 10, "bold"),relief="flat", cursor="hand2", pady=5)
        self.btn_add.pack(fill="x", pady=(30, 10))

        # Ορίζω να καλείται η _add_customer() με enter όταν είναι ο κέρσορας στα πεδία αυτα
        self.ent_name.bind('<Return>', lambda event: self._add_customer())
        self.ent_lastname.bind('<Return>', lambda event: self._add_customer())
        self.ent_phone.bind('<Return>', lambda event: self._add_customer())
        self.ent_email.bind('<Return>', lambda event: self._add_customer())
        self.window.bind('<Escape>', lambda event: self.window.destroy())

    # Συνάρτηση για την προσθήκη του νέου πελάτη
    def _add_customer(self):
        # Διαβάζω τα στοιχεία από τα text boxes
        first_name = self.ent_name.get().strip()
        last_name = self.ent_lastname.get().strip()
        phone = self.ent_phone.get().strip()
        email = self.ent_email.get().strip()

        # Αν δεν είναι τα υποχρεωτικά πεδία συμπληρωμένα βγαίνει popup message (Το τηλέφωνο είναι πλέον προαιρετικό)
        if not first_name or not last_name or not email:
            messagebox.showwarning("Προσοχή", "Το Όνομα, το Επώνυμο και το Email είναι υποχρεωτικά.", parent=self.window)
            return
        # Αν δεν εμπεριέχει τους χαρακτήρες @ . το email θα βγει σχετικό μήνυμα
        if "@" not in email or "." not in email:
            messagebox.showwarning("Σφάλμα", "Το e-mail δεν φαίνεται έγκυρο!", parent=self.window)
            return
        # Αν έχει εισαχθεί τηλέφωνο, ελέγχουμε αν είναι έγκυρο (τουλάχιστον 10 ψηφία)
        if phone and len(phone) < 10:
            messagebox.showwarning("Σφάλμα", "Το τηλέφωνο δεν φαίνεται έγκυρο!", parent=self.window)
            return

        # Error handling για την επικοινωνία με τη βάση
        try:
            database.create_customer(first_name, last_name, phone, email)
            messagebox.showinfo("Επιτυχία", "Ο πελάτης προστέθηκε επιτυχώς!", parent=self.window)
            self.window.destroy()
            return
        except Exception as error:
            messagebox.showerror("Σφάλμα", f"Αποτυχία προσθήκης πελάτη με μήνυμα: \n{error}", parent=self.window)

# Υποκλάση που στηρίζεται στην AddCustomerWindow και σκοπός της είναι η δημιουργία παραθύρου για το update των στοιχείων του πελάτη
class UpdateCustomerWindow(AddCustomerWindow):
    def __init__(self, parent,customer_data):

        # Φτιάχνω παράθυρο από την υπερκλάση
        super().__init__(parent)

        # Αλλάζω τον τίτλο και τα κείμενα
        self.window.title("Ενημέρωση Πελάτη")
        self.lbl.config(text="Ενημέρωση Στοιχείων Πελάτη")

        # Παίρνω τα στοιχεία. Προσυμπληρώνω τα πεδία με τα υπάρχοντα δεδομένα και κρατάω το ID για το update αργότερα
        self.customer_id = customer_data[0]
        self.ent_name.insert(0, customer_data[1])
        self.ent_lastname.insert(0, customer_data[2])
        self.ent_phone.insert(0, customer_data[3])
        self.ent_email.insert(0, customer_data[4])

        # Button για την ενημέρωση στοιχείων
        self.btn_add.configure(text="Ενημέρωση στοιχείων", command=self._do_update_customer)

        # Ορίζω να καλείται η _do_update_customer() με enter όταν είναι ο κέρσορας στα πεδία αυτα
        self.ent_name.bind('<Return>', lambda event: self._do_update_customer())
        self.ent_lastname.bind('<Return>', lambda event: self._do_update_customer())
        self.ent_phone.bind('<Return>', lambda event: self._do_update_customer())
        self.ent_email.bind('<Return>', lambda event: self._do_update_customer())
        self.window.bind('<Escape>', lambda event: self.window.destroy())

    # Συνάρτηση που εκτελεί το update των στοιχείων του πελάτη
    def _do_update_customer(self):

        first_name = self.ent_name.get()
        last_name = self.ent_lastname.get()
        phone = self.ent_phone.get()
        email = self.ent_email.get()

        # Αν δεν είναι τα υποχρεωτικά πεδία συμπληρωμένα βγαίνει popup message
        if not first_name or not last_name or not email:
            messagebox.showwarning("Προσοχή", "Συμπληρώστε Όνομα, Επώνυμο και Email!", parent=self.window)
            return

        # Αν δεν εμπεριέχει τους χαρακτήρες @ . το email θα βγει σχετικό μήνυμα
        if "@" not in email or "." not in email:
            messagebox.showwarning("Σφάλμα", "Το e-mail δεν φαίνεται έγκυρο!", parent=self.window)
            return
        # Αν έχει εισαχθεί τηλέφωνο, ελέγχουμε αν είναι έγκυρο (τουλάχιστον 10 ψηφία)
        if phone and len(phone) < 10:
            messagebox.showwarning("Σφάλμα", "Το τηλέφωνο δεν φαίνεται έγκυρο!", parent=self.window)
            return

        # Error handling για την επικοινωνία με τη βάση
        try:
            # Καλώ τη συνάρτηση update από τη βάση
            database.update_customer(self.customer_id, first_name, last_name, phone, email)
            messagebox.showinfo("Επιτυχία", "Η ενημέρωση ολοκληρώθηκε!", parent=self.window)
            self.window.destroy()  # Κλείνουμε το παράθυρο
        except Exception as error:
            messagebox.showerror("Σφάλμα", f"Αποτυχία ενημέρωσης: {error}", parent=self.window)
