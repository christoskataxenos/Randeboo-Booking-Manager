"""
=============================================================================
=                                                                           =
=       Ο κώδικας του αρχείου συντάχθηκε από τον Ασπρίδη Δημήτρη.           =
=                                                                           =
=                                                                           =
=============================================================================
ΑΡΧΕΙΟ: gui_users.py
ΣΚΟΠΟΣ: Διαχείριση Χρηστών — CRUD (Create, Read, Update, Delete)
=============================================================================
"""

import tkinter as tk
from tkinter import ttk
import database
from tkinter import messagebox
import gui_customers

# H βασική κλάση που χτίζει την οθόνη διαχείρισης χρηστών
# Επέλεξα να μην την κάνω υποκλάση της gui_customers.CustomersWindow γιατί με δυσκόλευε το γεγονός ότι ο πίνακας
# των δύο παραθύρων έχει διαφορετικό αριθμό στηλών. Αυτό έχει ως συνεπεια να πρέπει να μπω σε διαδικασία destroy
# και create από την αρχή. Παράλληλα το Live Search θα είχε και αυτό δυσκολία καθώς απαιτεί ξεχωριστό query
class UsersWindow:
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

        # Η κεντρική περιοχή του frame
        self.content_frame = tk.Frame(self.parent, bg=self.color_bg, padx=30, pady=2)
        self.content_frame.pack(side="right", expand=True, fill="both")

        # Header
        self.header = tk.Frame(self.content_frame, bg=self.color_bg)
        for i in range (4):
            self.content_frame.columnconfigure(i, weight=1)
        self.content_frame.rowconfigure(3, weight=1)
        self.header.grid(row=0, column=0, columnspan=3, sticky="n", pady=(2,30))
        welcome_text = f"Διαχείριση Χρηστών του RandeBoo!"
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
 
        self.label3=(tk.Label(self.content_frame, bg=self.color_bg, fg=self.color_sidebar, font=("Arial", 12), text="Όνομα Χρήστη"))
        self.label3.grid(row=1, column=2, padx=10, pady=(20,5), sticky="w")
        self.entry_username = tk.Entry(self.content_frame, bg=self.color_white, font=("Arial", 13), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.entry_username.grid(row=2, column=2, padx=10, pady=(5,35), sticky="ew")
 
        self.label4=(tk.Label(self.content_frame, bg=self.color_bg, fg=self.color_sidebar, font=("Arial", 12), text="e-mail"))
        self.label4.grid(row=1, column=3, padx=10, pady=(20,5), sticky="w")
        self.entry_email = tk.Entry(self.content_frame, bg=self.color_white, font=("Arial", 13), relief="flat", highlightthickness=1, highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.entry_email.grid(row=2, column=3, padx=10, pady=(5,35), sticky="ew")

        # Κάνει realtime filtering κατά την πληκτρολόγηση
        self.entry_name.bind('<KeyRelease>', lambda event: self._live_search_user())
        self.entry_last_name.bind('<KeyRelease>', lambda event: self._live_search_user())
        self.entry_username.bind('<KeyRelease>', lambda event: self._live_search_user())
        self.entry_email.bind('<KeyRelease>', lambda event: self._live_search_user())

        self.border_bg_2 = tk.Frame(self.content_frame,bg=self.color_bg, highlightbackground="gray", highlightthickness=2, bd=0)
        self.border_bg_2.grid(row=3, column=0, rowspan=1, columnspan=4, sticky="nsew", padx=0, pady=10)
        # Χρησιμοποιώ τη μέθοδο lower() για να "πάει" το frame του border πίσω από τα labels και τα entries, αλλιώς θα τα κρύψει.
        self.border_bg_2.lower()

        # Εδώ δηλώνω το container του πίνακα με τους πελάτες. Βοηθάει στη στοίχιση και στο styling
        self.table_container, self.table=self.show_table(self.content_frame)
        self.table_container.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=10, pady=30)

        # Γεμίζω με data τον πίνακα
        self._load_user()
        self.table.bind("<Double-1>", lambda event: self._update_user())

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
        self.add = tk.Button(self.button_container, text='Προσθήκη', command=self._call_add_user_window, bg=self.color_accent, fg="white",font=("Arial", 9, "bold"), relief="flat", padx=15, cursor="hand2")
        self.add.grid(row=0, column=0, pady=10, padx=10)

        self.update = tk.Button(self.button_container, text='Ενημέρωση', command=self._update_user, bg=self.color_accent, fg="white",font=("Arial", 9, "bold"), relief="flat", padx=15, cursor="hand2")
        self.update.grid(row=0, column=1, pady=10, padx=10)

        self.delete = tk.Button(self.button_container, text='Διαγραφή', command=self._delete_user, bg=self.color_red, fg="white",font=("Arial", 9, "bold"), relief="flat", padx=15, cursor="hand2")
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
        columns=("user_id","first_name","last_name","username", "role_id", "email", "phone", "is_active")

        # Δημιουργία Treeview
        tree=ttk.Treeview(container,columns=columns,show="headings",height=15)
        tree.heading("user_id", text="ΑΑ")
        tree.heading("first_name", text="Όνομα")
        tree.heading("last_name", text="Επώνυμο")
        tree.heading("username", text="Όν. Χρήστη")
        tree.heading("role_id", text="Ρόλος")
        tree.heading("email", text="e-mail")
        tree.heading("phone", text="Τηλέφωνο")
        tree.heading("is_active", text="Ενεργός")
        tree.column("user_id",width=35,anchor="center")
        tree.column("first_name",width=90,anchor="center")
        tree.column("last_name", width=90,anchor="center")
        tree.column("username", width=90,anchor="center")
        tree.column("role_id", width=45, anchor="center")
        tree.column("email", width=90,anchor="center")
        tree.column("phone", width=60, anchor="center")
        tree.column("is_active", width=40, anchor="center")
        tree.pack(side="left", fill="both" ,expand=True)

        # Δηλώνω τη scrollbar του πίνακα, σε περίπτωση που έχει περισσότερα από 15 αποτελέσματα
        # να δείξει(τόσα εχω ορίσει με το height παραπάνω)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Μορφοποιώ με διαφορετικό χρώμα ανά γραμμή σύμφωνα με το tag που έχει πάρει από την _load_user()
        tree.tag_configure('oddrow', background='#FFFFFF')
        tree.tag_configure('evenrow', background='#D9E2EC')

        return container,tree

    # Συνάρτηση που φτιάχνει νέο παράθυρο για την προσθήκη user
    def _call_add_user_window(self):
        # Φτιάχνω αντικείμενο νέου παραθύρου
        add_win=AddUserWindow(self.parent)
        # Περιμένω να κλείσει το πρόσθετο παράθυρο
        self.parent.wait_window(add_win.window)
        # Με το κλείσιμο του παραθύρου της προσθήκης, ξαναφορτώνω με δεδομένα τον πίνακα (για να φέρει και το νέο user)
        self._load_user()

    # Συνάρτηση για να φορτώνω με τους users τον πίνακα της οθόνης
    def _load_user(self):
        # Καθαρίζω τον πίνακα από προηγούμενα αποτελέσματα αν υπάρχουν
        for item in self.table.get_children():
            self.table.delete(item)

        # Καλώ την get_all_users() από το database.py και περνάω τα αποτελέσματα (list) σε μια δική μου μεταβλητή
        all_user = database.get_all_users()

        # Φορτώνω την επιστρεφόμενη λίστα στο πίνακα του παράθυρου (treeview)
        for i, user in enumerate(all_user):
            if user['is_active']==1:
                user_status='Ενεργός'
            else:
                user_status = 'Ανενεργός'
            if user['role_id'] == 1:
                user_role = 'Admin'
            else:
                user_role = 'User'
            user_values = (
                user['user_id'],
                user['first_name'],
                user['last_name'],
                user['username'],
                user_role,
                user['email'],
                user['phone'],
                user_status
            )
            tag='evenrow' if i%2==0 else 'oddrow'
            self.table.insert("", "end", values=user_values, tags=(tag,))


    def _live_search_user(self):
        # Διαβάζω όλα πεδία και τα περνάω σε μεταβλητή
        n = self.entry_name.get().strip()
        ln = self.entry_last_name.get().strip()
        u = self.entry_username.get().strip()
        e = self.entry_email.get().strip()

        # Αν είναι όλα τελείως άδεια, δείχνω όλη τη λίστα
        if not any([n, ln, u, e]):
            self._load_user()
            return

        # Error handling για την επικοινωνία με τη βάση
        try:
            # Καλώ την αναζήτηση χρηστών με το πεδίο που έχει δώσει ο χρήστης
            search = database.search_users(name=n, last_name=ln, username=u, email=e)
            # Αν η αναζήτηση επιστρέψει αποτελέσματα, αδειάζω τον πίνακα.
            if search:
                for item in self.table.get_children():
                    self.table.delete(item)
                # Φορτώνω την επιστρεφόμενη λίστα στο πίνακα του παράθυρου (treeview)
                for i,item in enumerate(search):
                    if item['is_active'] == 1:
                        user_status = 'Ενεργός'
                    else:
                        user_status = 'Ανενεργός'
                    if item['role_id'] == 1:
                        user_role = 'Admin'
                    else:
                        user_role = 'User'
                    user_values = (
                        item['user_id'],
                        item['first_name'],
                        item['last_name'],
                        item['username'],
                        user_role,
                        item['email'],
                        item['phone'],
                        user_status
                    )
                    # Βάζω tag για να χρωματίσω κατάλληλα τις γραμμές
                    tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                    # Γεμίζω τον πίνακα με τις τιμές
                    self.table.insert("", "end", values=user_values, tags=(tag,))
            else:
                # Αν η search είναι άδεια σημαίνει ότι δε βρέθηκε χρήστης, οπότε αδειάζω το πίνακα
                for item in self.table.get_children():
                    self.table.delete(item)
        except Exception as error:
            # PopUP message σε περίπτωση που βγει λάθος που δεν αναμένεται
            messagebox.showerror("Σφάλμα", f"Αποτυχία αναζήτησης χρήστη: \n{error}")

    # Συνάρτηση ενημέρωσης χρήστη με νέα στοιχεία που δηλώνει ο χρήστης
    def _update_user(self):
        # Παίρνω τα δεδομένα του χρήστη από την επιλεγμένη εγγραφή
        selected = self.table.selection()
        if not selected:
            # # PopUP message αν δεν έχει επιλεχθεί κάποιος χρήστης
            messagebox.showwarning("Προσοχή", "Επιλέξτε έναν χρήστη από τον πίνακα!")
            return
        item_info = self.table.item(selected[0])
        user_data=item_info['values']

        # Δημιουργώ ένα νέο αντικείμενο της κλάσης για το παράθυρο ενημέρωσης
        update_win = UpdateUserWindow(self.parent, user_data)

        # Περιμένω να κλείσει το επιπλέον παράθυρο. Μόλις κλείσει κάνω refresh τα δεδομένα του πίνακα
        self.parent.wait_window(update_win.window)
        self._load_user()

    # Συνάρτηση με την οποία διαγράφω από τη βάση τον επιλεγμένο χρήστη
    def _delete_user(self):
        # Παίρνω τα δεδομένα του χρήστη από την επιλεγμένη εγγραφή
        selected_item = self.table.selection()
        if not selected_item:
            # # PopUP message αν δεν έχει επιλεχθεί κάποιος χρήστης
            messagebox.showwarning("Προσοχή", "Παρακαλώ επιλέξτε έναν χρήστη από τον πίνακα!")
            return None
        # Μετατροπές μεταβλητών ώστε να καταλήξω με το user_id που είναι int
        item_data=self.table.item(selected_item[0])
        user_values=item_data['values']
        self.c_id = int(user_values[0])

        # Επιβεβαιωτικό μήνυμα ότι θέλουμε να διαγραφεί ο χρήστης. Στην περίπτωση του Yes προχωρώ σε διαγραφή
        confirm = messagebox.askyesno("Επιβεβαίωση Διαγραφής",f"Είστε σίγουροι ότι θέλετε να διαγράψετε τον χρήστη:\n{user_values[1]} {user_values[2]};")
        if confirm:
            try:
                database.delete_user(self.c_id)
                messagebox.showinfo("Επιτυχία", "Ο χρήστης διαγράφηκε επιτυχώς!")
                self._load_user()
            except Exception as error:
                messagebox.showerror("Σφάλμα", f"Αποτυχία διαγραφής χρήστη με μήνυμα: \n{error}")
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

# Kλάση για το παράθυρο καταχώρησης πελάτη. Κληρονομεί το παράθυρο προσθήκης πελατών από το gui_customer.py
class AddUserWindow(gui_customers.AddCustomerWindow):
    def __init__(self, parent):
        # Καλώ το constructor των πελατών που φτιάχνει νέο παράθυρο με πεδία: Όνομα, Επώνυμο, Τηλέφωνο & Email
        super().__init__(parent)

        # Αλλάζω τίτλους και το command του κουμπιού (χρήστης αντί πελάτης)
        self.window.title("Προσθήκη Χρήστη")
        self.lbl.config(text="Καταχώρηση Νέου Χρήστη")
        self.btn_add.configure(text="Καταχώρηση Νέου Χρήστη", command=self._add_user)

        # Επειδή η winfo_children() επιστρέφει λίστα από τα περιεχόμενα που εχουν γίνει pack ή grid στη μαμά κλάση.
        # Εγώ επιλέγω το στοιχείο [1] που είναι το main_frame (στοιχείο [0] είναι το label)
        main_frame = self.window.winfo_children()[1]

        # Καταστρέφουμε το πεδίο σημειώσεων (Notes) που κληρονομήθηκε από το AddCustomerWindow
        for child in main_frame.winfo_children():
            if isinstance(child, tk.Label) and child.cget("text") == "Σημειώσεις":
                child.destroy()
        if hasattr(self, "ent_notes") and self.ent_notes:
            self.ent_notes.destroy()

        # Βγάζω το κουμπί από το pack για να μπουν τα νέα πεδία από πάνω του. Αργότερα θα το ξαναβάλω
        self.btn_add.pack_forget()

        # Προσθέτω τα έξτρα πεδία που χρειάζεται ένας Χρήστης και που δεν υπήρχαν στη
        # μαμά κλαση για να τα κληρονομήσει εδώ.
        tk.Label(main_frame, text="UserName", bg="white").pack(anchor="w")
        self.ent_username = tk.Entry(main_frame, font=("Arial", 11), relief="flat", highlightthickness=1,
                                     highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_username.pack(fill="x", pady=(0, 10))

        tk.Label(main_frame, text="Password", bg="white").pack(anchor="w")
        self.ent_password = tk.Entry(main_frame, font=("Arial", 11), relief="flat", show="*", highlightthickness=1,
                                     highlightbackground="#B0BEC5", highlightcolor="#1E90FF")
        self.ent_password.pack(fill="x", pady=(0, 10))

        tk.Label(main_frame, text="Ρόλος", bg="white").pack(anchor="w")
        # Διαθέσιμες επιλογές για το dropdown menu επιλογής ρόλου
        options = ["Admin", "User"]
        # Δηλώνω το dropdown menu και το βαζω readonly για να μη μπορεί να γραψει μεσα ο χρήστης
        self.drop_menu = ttk.Combobox(main_frame, values=options, state="readonly")
        # Default κείμενο που θα φαίνεται μέχρι να επιλεγεί κάτι
        self.drop_menu.set("Επιλογή Ρόλου...")
        self.drop_menu.pack(fill="x", pady=(0, 10))
        # Bind της επιλογής με συνάρτηση on_select για να περνάω την κατάλληλη τιμή στη μεταβλητή
        self.drop_menu.bind("<<ComboboxSelected>>", self.on_select)

        # Προσθήκη του Checkbox για το Activation ή όχι του χρήστη (default τιμή να είναι ενεργός)
        self.user_activation = tk.BooleanVar(value=True)
        self.check_is_active = tk.Checkbutton(main_frame, text="Ενεργοποίηση Χρήστη", variable=self.user_activation,
                                              bg="white", font=("Arial", 10, "bold"))
        self.check_is_active.pack(pady=10)

        # Ξαναβάζω το κουμπί στο κάτω μέρος της οθόνης
        self.btn_add.pack(fill="x", pady=(30, 10))

        # Bindings για το update. Παρόλο που ορίζονται στη μαμά κλάση τα κάνω rebind για να εκτελείται η σωστή συνάρτηση
        self.ent_username.bind('<Return>', lambda event: self._add_user())
        self.ent_password.bind('<Return>', lambda event: self._add_user())
        self.ent_name.bind('<Return>', lambda event: self._add_user())
        self.ent_lastname.bind('<Return>', lambda event: self._add_user())
        self.ent_phone.bind('<Return>', lambda event: self._add_user())
        self.ent_email.bind('<Return>', lambda event: self._add_user())

    def on_select(self, event):
        # Παίρνουμε την τιμή που επέλεξε ο χρήστης
        selected = self.drop_menu.get()
        if selected == "Admin":
            self.role_id=1
        elif selected=="User":
            self.role_id=2


    # Συνάρτηση για την προσθήκη του νέου χρήστη
    def _add_user(self):
        # Διαβάζω τα στοιχεία από τα text boxes αφού εχω καθαρίσει τα κενα στην αρχή και στο τέλος του κειμένου
        name = self.ent_name.get().strip()
        lastname = self.ent_lastname.get().strip()
        username = self.ent_username.get().strip()
        password=self.ent_password.get().strip()
        role= self.role_id
        email2 = self.ent_email.get().strip()
        phone = self.ent_phone.get().strip()
        # Παίρνω το status του checkbox και το μετατρέπω σε τιμή για να το βάλω στη βάση
        if self.user_activation.get():
            is_active=1
        else:
            is_active=0

        # Αν δεν είναι τα υποχρεωτικά πεδία συμπληρωμένα βγαίνει popup message
        if not name or not lastname or not email2 or not username or not password:
            messagebox.showwarning("Προσοχή", "Το Όνομα, το Επώνυμο, το Username, o Κωδικός και το Email είναι υποχρεωτικά.", parent=self.window)
            return
        # Αν δεν εμπεριέχει τους χαρακτήρες @ . το email2 θα βγει σχετικό μήνυμα
        if "@" not in email2 or "." not in email2:
            messagebox.showwarning("Σφάλμα", "Το e-mail δεν φαίνεται έγκυρο!", parent=self.window)
            return
        if not role:
            # Αν δε δηλωθεί ρόλος κατά την εισαγωγή δίνεται default ρόλος ως χρήστης
            self.ent_role=2
        elif role != 1 and role !=2:
            messagebox.showwarning("Σφάλμα", "O ρόλος μπορεί να είναι 1 για admin και 2 για χρήστη.", parent=self.window)
            return
        if len(phone)<10 or len(phone) >10:
            messagebox.showwarning("Σφάλμα", "Το τηλέφωνο δεν φαίνεται έγκυρο!", parent=self.window)
            return

        if len(password) < 6:
            messagebox.showerror(
                "Σφάλμα",
                "Ο κωδικός δεν μπορεί να είναι μικρότερος από 6 χαρακτήρες!",
                parent=self.window,
            )
            return

        # Error handling για την επικοινωνία με τη βάση
        try:
            database.create_user(username, password, role, name, lastname, email2, phone, is_active)
            messagebox.showinfo("Επιτυχία", "Ο χρήστης προστέθηκε επιτυχώς!", parent=self.window)
            self.window.destroy()
            return
        except Exception as error:
            messagebox.showerror("Σφάλμα", f"Αποτυχία προσθήκης χρήστη με μήνυμα: \n{error}", parent=self.window)

# Υποκλάση που στηρίζεται στην AddUserWindow και σκοπός της είναι η δημιουργία παραθύρου για το update των στοιχείων του χρήστη
class UpdateUserWindow(AddUserWindow):
    def __init__(self, parent, user_data):
        # Φτιάχνω παράθυρο από την υπερκλάση
        super().__init__(parent)

        # Αλλάζω τον τίτλο και τα κείμενα
        self.window.title("Ενημέρωση Χρήστη")
        self.lbl.config(text="Ενημέρωση Στοιχείων Χρήστη")

        # Παίρνω τα στοιχεία. Προσυμπληρώνω τα πεδία με τα υπάρχοντα δεδομένα και κρατάω το ID για το update αργότερα
        self.user_id = user_data[0]
        self.ent_name.insert(0, user_data[1])
        self.ent_lastname.insert(0, user_data[2])
        self.ent_username.insert(0, user_data[3])

        # Νωρίτερα στη _load_user έχω θέσει περιγραφικά τον ρόλο (δεν είναι πια με id)
        self.role_desciption=user_data[4]

        # Ελέγχω τι ρόλο έχει ο χρήστης και εμφανίζω την κατάλληλη επιλογή στο dropdown menu
        # και δηλώνω το κατάλληλο role_id για να γίνει η τελική καταχώρηση στη βάση στο τέλος
        if  self.role_desciption=="Admin":
            self.drop_menu.set("Admin")
            self.role_id=1
        elif self.role_desciption=="User":
            self.drop_menu.set("User")
            self.role_id = 2

        self.ent_email.insert(0, user_data[5])
        self.ent_phone.insert(0, user_data[6])

        status = user_data[7]
        # Έλεγχω αν είναι ενεργός ο χρήστης ώστε να γίνει σωστή απεικόνιση στο checkbox
        if status == "Ενεργός":
            self.user_activation.set(True)
        else:
            self.user_activation.set(False)

        # Button για την ενημέρωση στοιχείων. Αλλάζω το command που τρέχει η μαμά υπερκλάση
        # Με τη .configure() πετυχαίνω να αλλάξω τις ιδιότητές του κουμπιού (το command στην προκειμένη περίπτωση)
        self.btn_add.configure(text="Ενημέρωση στοιχείων", command=self._do_update_user)

        # Bindings για το update. Παρόλο που ορίζονται στη μαμά κλάση τα κάνω rebind για να εκτελείται η σωστή συνάρτηση
        self.ent_name.bind('<Return>', lambda event: self._do_update_user())
        self.ent_lastname.bind('<Return>', lambda event: self._do_update_user())
        self.ent_username.bind('<Return>', lambda event: self._do_update_user())
        self.ent_email.bind('<Return>', lambda event: self._do_update_user())
        self.ent_phone.bind('<Return>', lambda event: self._do_update_user())

    # Συνάρτηση που εκτελεί το update των στοιχείων του χρήστη
    def _do_update_user(self):

        # Περνάω τις τιμές σε τοπικές μεταβλητές
        name = self.ent_name.get()
        lastname = self.ent_lastname.get()
        username = self.ent_username.get()
        password = self.ent_password.get()
        role_id = self.role_id
        email = self.ent_email.get()
        phone= self.ent_phone.get()
        if self.user_activation.get():
            is_active=1
        else:
            is_active=0

        # Αν δεν είναι τα υποχρεωτικά πεδία συμπληρωμένα βγαίνει popup message
        if not name or not lastname or not email or not username or not phone:
            messagebox.showwarning("Προσοχή", "Συμπληρώστε τα απαραίτητα στοιχεία", parent=self.window)
            return

        # Αν δεν εμπεριέχει τους χαρακτήρες @ . το email θα βγει σχετικό μήνυμα
        if "@" not in email or "." not in email:
            messagebox.showwarning("Σφάλμα", "Το e-mail δεν φαίνεται έγκυρο!", parent=self.window)
            return

        # Μόνο αν έχει αλλαχθεί το password να γίνεται έλεγχος για το μήκος. Διαφορετικά να μην πειράζεται το password.
        if password:
            if len(password) < 6:
                messagebox.showerror(
                    "Σφάλμα",
                    "Ο κωδικός δεν μπορεί να είναι μικρότερος από 6 χαρακτήρες!",
                    parent=self.window,
                )
            return

        if not role_id:
            # Αν δε δηλωθεί ρόλος κατά την εισαγωγή δίνεται default ρολος ως χρήστης
            self.ent_role=2
        elif role_id != 1 and role_id !=2:
            messagebox.showwarning("Σφάλμα", "O ρόλος μπορεί να είναι 1 για admin και 2 για χρήστη.", parent=self.window)
            return
        if len(phone)<10 or len(phone) >10:
            messagebox.showwarning("Σφάλμα", "Το τηλέφωνο δεν φαίνεται έγκυρο!", parent=self.window)
            return

        # Error handling για την επικοινωνία με τη βάση
        try:
            # Καλώ τη συνάρτηση update από τη βάση
            database.update_user(self.user_id, username, name, lastname, phone, email, role_id, is_active)
            messagebox.showinfo("Επιτυχία", "Η ενημέρωση ολοκληρώθηκε!", parent=self.window)
            self.window.destroy()  # Κλείνουμε το παράθυρο
        except Exception as error:
            messagebox.showerror("Σφάλμα", f"Αποτυχία ενημέρωσης: {error}", parent=self.window)