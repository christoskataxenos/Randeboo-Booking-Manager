"""
=============================================================================
=                                                                           =
=       Ο κώδικας του αρχείου συντάχθηκε από τον Ασπρίδη Δημήτρη            =
=                                                                           =
=============================================================================
ΑΡΧΕΙΟ: gui_login.py
ΣΚΟΠΟΣ: Οθόνη σύνδεσης χρήστη (Login Window)
=============================================================================
"""

import tkinter as tk
from tkinter import messagebox
from typing import Any, Callable

import database


# Δήλωση κλάσης για την login οθόνη
class LoginWindow:
    def __init__(self, root, on_login_success):
        # Παράμετροι της κλάσης
        self.root = root
        self.on_login_success = on_login_success
        self.top = None

        # Σταθερές για ομοιόμορφη απόσταση στα forms (Premium UI Overhaul)
        self.LABEL_PADY = (10, 4)
        self.ENTRY_PADY = (0, 8)

        self.color_bg = "#F7F9FC"
        self.color_sidebar = "#0A3D62"
        self.color_accent = "#1E90FF"
        self.color_white = "#FFFFFF"
        self.color_accent_hover = "#1877D4"
        self.color_red_hover = "#C23B3C"
        self.color_red = "#EE5253"
        self.color_shadow = "#E1E8EE"
        self.color_border = "#E5E9F0"
        self.color_hover_light = "#F0F7FF"
        self.color_text = "#1B1F23"
        self.root.configure(bg=self.color_bg)

        # Ρυθμίσεις Παραθύρου
        self.root.title(f"Καλωσήρθατε στο RandeBoo")
        # Κεντράρω το παράθυρο στο κέντρο της οθόνης και του ορίζω μέγεθος
        self.setup_window(self.root)


        self.sidebar = tk.Frame(self.root, bg=self.color_sidebar, width=160)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.exit = tk.Button(self.sidebar, text="Έξοδος", command=self._call_on_closing, bg=self.color_red, fg=self.color_white, font=("Arial", 11, "bold"), relief="flat", pady=15, cursor="hand2")
        self.exit.pack(side="bottom", fill="x")
        self.root.bind("<Escape>", lambda event: self.on_closing(self.root))

        # Αλλάζει χρώμα το κουμπί όταν κάνω hover το ποντίκι από πάνω
        self.exit.bind(
            "<Enter>", lambda e: self.exit.configure(bg=self.color_red_hover)
        )
        self.exit.bind("<Leave>", lambda e: self.exit.configure(bg=self.color_red))

        tk.Label(self.sidebar, text="RandeBoo", fg=self.color_white, bg=self.color_sidebar, font=("Arial", 18, "bold"), pady=30).pack()


        self.content_frame = tk.Frame(self.root, bg=self.color_bg, padx=20, pady=20)
        self.content_frame.pack(side="right", expand=True, fill="both")

        # Header: Καλωσόρισμα
        self.header = tk.Frame(self.content_frame, bg=self.color_bg)
        self.header.pack(fill="x")
        welcome_text = "Καλωσήρθατε στο RandeBoo!"
        tk.Label(self.header, text=welcome_text, font=("Arial", 20, "bold"), bg=self.color_bg, fg=self.color_sidebar).pack(side="left")

        # Μεταβλητές για τα string του username & password
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()


        # Φτιάχνουμε πρώτα ένα frame για τη σκιά (Shadow)
        self.login_shadow = tk.Frame(
            self.content_frame,
            bg=self.color_shadow,
        )
        self.login_shadow.place(relx=0.5, rely=0.5, anchor="center", x=3, y=3)

        self.login_box = tk.Frame(
            self.content_frame,
            bg=self.color_bg,
            highlightbackground=self.color_border,
            highlightthickness=1,
            padx=30,
            pady=30,
        )
        # Το τοποθετούμε ΤΕΛΕΙΑ ΣΤΟ ΚΕΝΤΡΟ του content_frame χωρίς σταθερό width/height, 
        # ώστε να "ξεχειλώσει" ακριβώς όσο χρειάζεται.
        self.login_box.place(relx=0.5, rely=0.5, anchor="center")
        
        # Ενημερώνουμε τις διαστάσεις της σκιάς αυτόματα βάσει του Login Box
        self.login_box.bind("<Configure>", lambda e: self.login_shadow.place(width=e.width, height=e.height))

        # Εδώ δηλώνονται τα textboxes & labels για το username & password αντίστοιχα
        tk.Label(self.login_box, bg=self.color_bg, font=("Arial", 10), text="Όνομα Χρήστη", anchor="center", justify="center", fg=self.color_text).pack(pady=self.LABEL_PADY)
        # Username Entry
        self.entry_user = tk.Entry(self.login_box, bg=self.color_white, font=("Arial", 10), width=24, textvariable=self.username_var, relief="flat", highlightthickness=1, highlightbackground=self.color_border, highlightcolor=self.color_accent, fg=self.color_text)
        self.entry_user.pack(pady=self.ENTRY_PADY, anchor="center")

        # Ορίζω να τραβάει το focus το παράθυρο και μετά το πεδίο του username.
        # Γίνεται χρήση της .after για να δώσει καθυστέρηση 100ms. Δεν έπαιζε χωρίς καθυστέρηση.
        self.root.after(
            100, lambda: [self.root.focus_force(), self.entry_user.focus_set()]
        )

        tk.Label(self.login_box, bg=self.color_bg, font=("Arial", 10), text="Κωδικός Πρόσβασης", anchor="center", justify="center", fg=self.color_text).pack(pady=self.LABEL_PADY)
        # Password Entry
        self.entry_password = tk.Entry(self.login_box, bg=self.color_white, font=("Arial", 10), width=24, textvariable=self.password_var, show="*", relief="flat", highlightthickness=1, highlightbackground=self.color_border, highlightcolor=self.color_accent, fg=self.color_text)
        self.entry_password.pack(pady=self.ENTRY_PADY, anchor="center")

        # Ορίζω το ματάκι που όσο το κρατάω πατημένο εμφανίζει το password
        self.eye_btn = tk.Label(self.login_box, text="👁️", bg=self.color_bg, cursor="hand2")
        self.eye_btn.place(in_=self.entry_password, relx=1.0, rely=0.5, anchor="w", x=8, y=0)

        # Bindings για την εμφάνιση ή όχι του κωδικού
        self.eye_btn.bind(
            "<ButtonPress-1>",
            lambda event: self.toggle_password(self.entry_password, True),
        )
        self.eye_btn.bind(
            "<ButtonRelease-1>",
            lambda event: self.toggle_password(self.entry_password, False),
        )

        # Hover Feedback για το ματάκι (Premium UI Overhaul)
        self.eye_btn.bind("<Enter>", lambda e: self.eye_btn.configure(fg=self.color_accent))
        self.eye_btn.bind("<Leave>", lambda e: self.eye_btn.configure(fg=self.color_text))

        # Καλώ την handle_login() όταν πατηθεί enter μέσα στο textboxes του username & password
        self.entry_user.bind("<Return>", lambda event: self.handle_login())
        self.entry_password.bind("<Return>", lambda event: self.handle_login())

        # Κεντρικό frame μέσα στο οποίο μπαίνουν τα στοιχεία για στοίχιση και ομαδοποίηση
        self.frame = tk.Frame(self.login_box, bg=self.color_bg)
        self.frame.pack(pady=5)

        # Εδώ δηλώνονται τα buttons
        self.login = tk.Button(self.frame, text="Είσοδος", command=self.handle_login, bg=self.color_accent, fg=self.color_white, font=("Arial", 9, "bold"), relief="flat", padx=15, pady=5, cursor="hand2")
        self.login.grid(row=0, column=0, padx=10, pady=10)

        self.forgot = tk.Button(self.frame, text="Ξέχασα τον κωδικό", command=self.open_change_password_window, bg=self.color_white, fg=self.color_accent, font=("Arial", 9, "bold"), relief="flat", padx=15, pady=5, cursor="hand2")
        self.forgot.grid(row=0, column=1, padx=10, pady=10)


        self.login.bind(
            "<Enter>", lambda e: self.login.configure(bg=self.color_accent_hover)
        )
        self.login.bind("<Leave>", lambda e: self.login.configure(bg=self.color_accent))

        self.forgot.bind(
            "<Enter>", lambda e: self.forgot.configure(bg=self.color_hover_light)
        )
        self.forgot.bind("<Leave>", lambda e: self.forgot.configure(bg=self.color_white))

    # Συνάρτηση για κεντράρισμα του παραθύρου. Είναι ορισμένη ως static αφού δεν αλλάζει τα δεδομένα της κλάσης
    @staticmethod
    def setup_window(window, window_width=1024, window_height=768):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        # Προστασία για να μη "σπάει" το UI αν μικρύνει πολύ
        window.minsize(window_width, window_height)

    # Συνάρτηση που εκτελείται από το button "Είσοδος"
    def handle_login(self):
        # Με τη .get() διαβάζω τη μεταβλητή που έχει περαστεί το κείμενο που έχει πληκτρολογήσει ο χρήστης
        user = self.username_var.get().strip()
        user_pass = self.password_var.get().strip()

        # Επιβεβαιώνω ότι δεν είναι κενά τα πεδία
        if user != "" and user_pass != "":
            # Γίνεται ο έλεγχος αυθεντικοποίησης στην database με κλήση της σχετικής συνάρτησης.
            # Το dictionary που επιστρέφεται αποθηκεύεται σε μεταβλητή για να ελεγχθεί με το if μετά.
            authenticated = database.authenticate_user(user, user_pass)
            if authenticated:
                # Αφού πλέον έχει αυθεντικοποιηθεί ο χρήστης, καλώ το callback που μας έδωσε η main για να συνεχίσει το πρόγραμμα
                self.on_login_success(authenticated)
            elif authenticated is None:
                # Μήνυμα ότι δεν ταυτοποιήθηκε ο χρήστης
                messagebox.showerror(
                    "Αποτυχημένη ταυτοποίηση χρήστη",
                    "Λάθος χρήστης ή κωδικός πρόσβασης. \nΠαρακαλώ ξαναδοκιμάστε!",
                )
            elif authenticated is False:
                messagebox.showerror(
                    "Απαιτείται αλλαγή κωδικού",
                    'Πρέπει να αλλάξετε κωδικό!\nΠαρακαλώ επιλέξτε "Ξέχασα το κωδικό"',
                )
        else:
            # Δικλείδα ασφαλείας για να βεβαιωθεί ότι θα εισαχθεί username & password
            messagebox.showwarning(
                "Σφάλμα Εισαγωγής",
                "Παρακαλώ συμπληρώστε όνομα χρήστη & κωδικό πρόσβασης!",
            )

    # Συνάρτηση για να ανοίξει νέο παράθυρο για την αλλαγή password
    def open_change_password_window(self):
        # Παίρνω το ID που επιστρέφεται από την database.get_user_id γνωρίζοντας μονο το username που εχει πληκτρολογήσει ο χρήστης
        user = self.username_var.get()
        user_id = database.get_user_id(user)

        # Επιβεβαιώνω ότι έχω το username που απαιτείται για να προχωρήσω
        if not user_id:
            messagebox.showwarning("Προσοχή", "Πληκτρολογήστε πρώτα σωστό Username!")
            return

        # Δημιουργία νέου παραθύρου (Toplevel) ώστε να δοθεί ο νέος κωδικός
        # Κεντράρισμα του Toplevel σε σχέση με το αρχικό login παράθυρο
        self.top = tk.Toplevel(self.root)
        self.top.title("Αλλαγή Κωδικού")
        self.top.transient(self.root)
        self.top.grab_set()
        self.top.focus_force()

        # Κεντράρω το παράθυρο στο κέντρο της οθόνης και του ορίζω μέγεθος
        self.setup_window(self.top, window_width=1024, window_height=768)

        # 1. SIDEBAR: Περιέχει το logo και τα βασικά κουμπιά πλοήγησης
        sidebar_frame = tk.Frame(self.top, bg=self.color_sidebar, width=160)
        sidebar_frame.pack(side="left", fill="y")
        sidebar_frame.pack_propagate(False)
        
        cancel_btn = tk.Button(sidebar_frame, text="Πίσω", command=self.top.destroy, bg=self.color_red, fg=self.color_white, font=("Arial", 11, "bold"), relief="flat", pady=15, cursor="hand2")
        cancel_btn.pack(side="bottom", fill="x")

        # Αλλάζει χρώμα το κουμπί όταν κάνω hover το ποντίκι από πάνω
        cancel_btn.bind(
            "<Enter>", lambda e: cancel_btn.configure(bg=self.color_red_hover)
        )
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.configure(bg=self.color_red))

        tk.Label(sidebar_frame, text="RandeBoo", fg=self.color_white, bg=self.color_sidebar, font=("Arial", 18, "bold"), pady=30).pack()

        # 2. MAIN CONTENT AREA: Η κεντρική περιοχή προβολής
        content_area = tk.Frame(self.top, bg=self.color_bg, padx=20, pady=20)
        content_area.pack(side="left", expand=True, fill="both")

        # Header: Καλωσόρισμα
        top_header = tk.Frame(content_area, bg=self.color_bg)
        top_header.pack(fill="x")
        welcome_text = "Αλλαγή Κωδικού"
        tk.Label(top_header, text=welcome_text, font=("Arial", 20, "bold"), bg=self.color_bg, fg=self.color_sidebar).pack(side="left")


        # Φτιάχνουμε πρώτα ένα frame για τη σκιά (Shadow)
        pwd_box_shadow = tk.Frame(
            content_area,
            bg=self.color_shadow,
        )
        # relx=0.5 κεντράρει το αντικείμενο στο parent (content_area)
        pwd_box_shadow.place(relx=0.5, rely=0.5, anchor="center", width=332, height=242, x=2, y=2)

        pwd_main_box = tk.Frame(
            content_area,
            bg=self.color_bg,
            highlightbackground=self.color_border,
            highlightthickness=1,
            padx=20,
            pady=20,
        )
        pwd_main_box.place(relx=0.5, rely=0.5, anchor="center", width=330, height=240)

        self.new_pass_var1 = tk.StringVar()
        self.new_pass_var2 = tk.StringVar()

        # Εδώ δηλώνονται τα textboxes & labels για το νέο password
        tk.Label(pwd_main_box, bg=self.color_bg, font=("Arial", 10), text=f"Νέος κωδικός για: {user}", anchor="center", justify="center", fg=self.color_text).pack(pady=self.LABEL_PADY)
        
        entry_new_pass1 = tk.Entry(pwd_main_box, bg=self.color_white, font=("Arial", 10), width=24, textvariable=self.new_pass_var1, show="*", relief="flat", highlightthickness=1, highlightbackground=self.color_border, highlightcolor=self.color_accent, fg=self.color_text)
        entry_new_pass1.pack(pady=self.ENTRY_PADY, anchor="center")
        
        tk.Label(pwd_main_box, bg=self.color_bg, font=("Arial", 10), text="Επιβεβαίωση κωδικού", anchor="center", justify="center", fg=self.color_text).pack(pady=self.LABEL_PADY)
        
        entry_new_pass2 = tk.Entry(pwd_main_box, bg=self.color_white, font=("Arial", 10), width=24, textvariable=self.new_pass_var2, show="*", relief="flat", highlightthickness=1, highlightbackground=self.color_border, highlightcolor=self.color_accent, fg=self.color_text)
        entry_new_pass2.pack(pady=self.ENTRY_PADY, anchor="center")

        eye_btn1 = tk.Label(pwd_main_box, text="👁️", bg=self.color_bg, cursor="hand2")
        eye_btn1.place(in_=entry_new_pass1, relx=1.0, rely=0.5, anchor="w", x=8, y=0)
        eye_btn2 = tk.Label(pwd_main_box, text="👁️", bg=self.color_bg, cursor="hand2")
        eye_btn2.place(in_=entry_new_pass2, relx=1.0, rely=0.5, anchor="w", x=8, y=0)

        # Hover feedback για τα ματάκια
        eye_btn1.bind("<Enter>", lambda e: eye_btn1.configure(fg=self.color_accent))
        eye_btn1.bind("<Leave>", lambda e: eye_btn1.configure(fg=self.color_text))
        eye_btn2.bind("<Enter>", lambda e: eye_btn2.configure(fg=self.color_accent))
        eye_btn2.bind("<Leave>", lambda e: eye_btn2.configure(fg=self.color_text))

        # Bindings για την εμφάνιση ή όχι του κωδικού
        eye_btn1.bind(
            "<ButtonPress-1>", lambda event: self.toggle_password(entry_new_pass1, True)
        )
        eye_btn1.bind(
            "<ButtonRelease-1>",
            lambda event: self.toggle_password(entry_new_pass1, False),
        )
        eye_btn2.bind(
            "<ButtonPress-1>", lambda event: self.toggle_password(entry_new_pass2, True)
        )
        eye_btn2.bind(
            "<ButtonRelease-1>",
            lambda event: self.toggle_password(entry_new_pass2, False),
        )

        # Βάζω το focus στο 1ο πεδίο προς συμπλήρωση και θέτω ότι με enter θα εκτελεστεί η confirm_changes()
        entry_new_pass1.focus_set()
        entry_new_pass1.bind("<Return>", lambda event: self.confirm_change())
        entry_new_pass2.bind("<Return>", lambda event: self.confirm_change())

        # Εδώ δηλώνεται το button για την αποθήκευση
        save_btn = tk.Button(pwd_main_box, text="Αποθήκευση", command=self.confirm_change, bg=self.color_accent, fg=self.color_white, font=("Arial", 9, "bold"), relief="flat", padx=15, pady=5, cursor="hand2", anchor="center")
        save_btn.pack(pady=15, anchor="center")
        
        # Αλλάζει χρώμα το κουμπί όταν κάνω hover το ποντίκι από πάνω
        save_btn.bind(
            "<Enter>", lambda e: save_btn.configure(bg=self.color_accent_hover)
        )
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=self.color_accent))
        
        self.top.bind("<Escape>", lambda event: self.top.destroy())

    # Συνάρτηση που καλείται κατά την αποθήκευση του νέου password η οποία θα κάνει το update στη βάση
    def confirm_change(self):
        # Παίρνω το ID που επιστρέφεται από την database.get_user_id γνωρίζοντας μόνο το username που έχει πληκτρολογήσει ο χρήστης
        user = self.username_var.get().strip()
        user_id = database.get_user_id(user)
        # Διαβάζω τους νέους κωδικούς που πληκτρολογεί ο χρήστης και επιβεβαιώνω ότι ταιριάζουν
        new_pwd1 = self.new_pass_var1.get().strip()
        new_pwd2 = self.new_pass_var2.get().strip()

        # Έλεγχος ότι είναι ίδιοι οι νέοι κωδικοί
        if new_pwd1 != new_pwd2:
            messagebox.showerror(
                "Σφάλμα", "Οι κωδικοί δεν ταιριάζουν!", parent=self.top
            )
            return

        # Έλεγχος ότι δεν είναι κενός ο νέος κωδικός
        if not new_pwd1:
            messagebox.showerror(
                "Σφάλμα", "Ο κωδικός δεν μπορεί να είναι κενός!", parent=self.top
            )
            return

        if len(new_pwd1) < 6:
            messagebox.showerror(
                "Σφάλμα",
                "Ο κωδικός δεν μπορεί να είναι μικρότερος από 6 χαρακτήρες!",
                parent=self.top,
            )
            return

        # Κλήση της βάσης δεδομένων
        success = database.change_password(user_id, new_pwd1)
        if success:
            messagebox.showinfo("Επιτυχία", "Ο κωδικός άλλαξε!", parent=self.top)
            # Μηδενίζω για λόγους ασφαλείας τις μεταβλητές των κωδικών και κλείνω το παράθυρο
            self.new_pass_var1.set("")
            self.new_pass_var2.set("")
            self.top.destroy()
        else:
            messagebox.showwarning(
                "Αποτυχία", "Η αλλαγή κωδικού απέτυχε. Δοκιμάστε ξανά.", parent=self.top
            )

    # Συνάρτηση για το bind του escape ώστε να κλείνει η εφαρμογή αφού βγάλει ερώτηση
    def on_closing(self, root):
        if messagebox.askokcancel("Έξοδος", "Θέλετε να κλείσετε την εφαρμογή;"):
            self.root.destroy()

    # Συνάρτηση που καλεί τον on_closing. Τη χρειάστηκα για να καλείται από το κουμπί και η on_closing θα έπρεπε
    # να περνάω όρισμα το παράθυρο που θα κλείνει
    def _call_on_closing(self):
        self.on_closing(self.root)

    # Η συνάρτηση που εμφανίζει ή όχι τον κωδικό που πληκτρολογεί ο χρήστης
    def toggle_password(self, pwd, show):
        if show:
            pwd.config(show="")
        else:
            pwd.config(show="*")

