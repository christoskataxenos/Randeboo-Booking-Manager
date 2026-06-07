
"""
Ο κώδικας του αρχείου συντάχθηκε από τον Βαρθαλίτη Πάνο

=============================================================================
ΑΡΧΕΙΟ: gui_search.py
ΣΚΟΠΟΣ: κεντρικη οθονη αναζητησης, μπαινει μεσα στο βασικο παραθυρο μεσω του sidebar
=============================================================================
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta


class SearchPanel:
    # κεντρικη οθονη αναζητησης, μπαινει μεσα στο βασικο παραθυρο μεσω του sidebar

    def __init__(self, parent, user=None):
   
        # ΜΕΡΟΣ 1: ΑΡΧΙΚΟΠΟΙΗΣΗ ΚΑΙ ΧΡΩΜΑΤΑ (SETUP)
        self.parent = parent
        self.user = user or {}

        # αποθηκευση δεδομενων ραντεβου (χρησιμευει για double-click και context menu)
        self._results_data = {}

        # default φιλτρο: ολα / 3 μηνες πισω
        self.active_status_filter = "all"
        self.active_time_preset = "3months"

        # αποθηκευση ΟΛΩΝ των αποτελεσματων (πριν φιλτραριστουν)
        self._all_results = []

        # αρχικα το popup φιλτρων ειναι κλειστο
        self._filter_popup = None

        # default ταξινομηση (στλη, αναποδα) - πιο προσφατα πρωτα
        self._sort_column = "Date"
        self._sort_reverse = True

        # τα χρωματα του app για να ταιριαζουν με την υπολοιπη εφαρμογη
        self.color_bg = "#F7F9FC"           # φοντο σελιδας
        self.color_sidebar = "#0A3D62"      # βασικο σκουρο μπλε
        self.color_accent = "#1E90FF"       # ανοιχτο μπλε 
        self.color_white = "#FFFFFF"        
        self.color_border = "#E5E9F0"       
        self.color_text = "#1B1F23"         

        # τα χρωματα για να ξεχωριζουν οι διαφορες καταστασεις (οπως στο display panel)
        self.color_upcoming = "#27ae60"     
        self.color_completed = "#95a5a6"    
        self.color_modified = "#F39C12"     
        self.color_cancelled = "#e74c3c"    

        # χτισιμο του ui 
        self.parent.configure(bg=self.color_bg)  
        self._build_header()        
        self._build_search_bar()    
        self._build_filters_data()  
        self._build_treeview()      
        self._build_status_bar()    
        self._build_context_menu()  
    
    # ΜΕΡΟΣ 2: ΣΧΕΔΙΑΣΜΟΣ ΓΡΑΦΙΚΟΥ ΠΕΡΙΒΑΛΛΟΝΤΟΣ (UI)
    # συναρτησεις κατασκευης του ui (χωρισμενες σε κομματια)

    def _build_header(self):
        # ο τιτλος πανω πανω στη σελιδα
        tk.Label(
            self.parent,
            text="Γενική Αναζήτηση",
            font=("Arial", 20, "bold"),  
            bg=self.color_bg,            
            fg=self.color_sidebar        
        ).pack(pady=(10, 15))  

    def _build_search_bar(self):
        # πεδιο αναζητησης και κουμπι φιλτρων 
        # το container κραταει το search entry και filter button σε μια γραμμη
        search_frame = tk.Frame(self.parent, bg=self.color_bg)
        search_frame.pack(fill="x", padx=40, pady=(0, 5))

        # label "Αναζήτηση:" αριστερα
        tk.Label(
            search_frame,
            text="Αναζήτηση:",
            font=("Arial", 11),    
            bg=self.color_bg,       
            fg=self.color_sidebar   
        ).pack(side="left", padx=(0, 8))  

        # placeholder text για να ξερει ο χρηστης τι ψαχνει
        self.placeholder_text = "Αναζήτηση με όνομα, τηλέφωνο, email..."

        # πεδιο εισαγωγης (entry) - εδω γραφει ο χρηστης
        self.search_entry = tk.Entry(
            search_frame,
            font=("Arial", 13),                      
            relief="flat",                            
            highlightthickness=1,                     
            highlightbackground=self.color_border,    
            highlightcolor=self.color_accent          
        )
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))  

        # αρχικοποιηση placeholder 
        self.search_entry.insert(0, self.placeholder_text)
        self.search_entry.config(fg="gray")

        # triggers για συμπεριφορα placeholder και live-search
        self.search_entry.bind("<FocusIn>", self._on_entry_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_entry_focus_out)
        self.search_entry.bind("<KeyRelease>", self._on_search)

        # το κουμπι που ανοιγει το παραθυρακι με τα φιλτρα
        self.btn_filter_toggle = tk.Button(
            search_frame,
            text="Φίλτρα ▼",
            font=("Arial", 9),                       
            bg=self.color_white,                      
            fg=self.color_sidebar,                    
            relief="flat",                            
            highlightthickness=1,
            highlightbackground=self.color_border,    
            padx=12,
            cursor="hand2",                           
            command=self._toggle_filters
        )
        self.btn_filter_toggle.pack(side="right")  

        # το κουμπι για την εξαγωγη του excel
        self.btn_export = tk.Button(
            search_frame,
            text="Εξαγωγή",
            font=("Arial", 9, "bold"),
            bg=self.color_accent,
            fg="white",
            relief="flat",
            padx=12,
            cursor="hand2",
            command=self._on_export_click
        )
        self.btn_export.pack(side="right", padx=(0, 10))

    def _on_entry_focus_in(self, event):
        # οταν κανει κλικ μεσα το κρυβουμε
        if self.search_entry.get() == self.placeholder_text:
            self.search_entry.delete(0, "end")
            self.search_entry.config(fg=self.color_text)

    def _on_entry_focus_out(self, event):
        # οταν βγαινει απο το πεδιο και ειναι κενο, το ξαναβαζουμε
        if not self.search_entry.get().strip():
            self.search_entry.delete(0, "end")
            self.search_entry.insert(0, self.placeholder_text)
            self.search_entry.config(fg="gray")

    def _build_filters_data(self):
        # ορισμος φιλτρων 
        # τα φιλτρα εμφανιζονται ως dropdown popup μεσω _toggle_filters()

        # χρονικα presets: (κειμενο, κλειδι, ημερες πισω)
        # none = χωρις περιορισμο
        self._time_presets = [
            ("Σήμερα", "today", 0),
            ("Εβδομάδα", "week", 7),
            ("Μήνας", "month", 30),
            ("3 Μήνες", "3months", 90),
            ("Όλα", "all_time", None),
        ]

        # φιλτρα καταστασης
        self._status_filters = [
            ("Όλα", self.color_accent, "all"),
            ("Επικείμενα", self.color_upcoming, "upcoming"),
            ("Παλιά", self.color_completed, "completed"),
            ("Ακυρωμένα", self.color_cancelled, "cancelled"),
        ]

    def _build_treeview(self):
        # πινακας αποτελεσματων με 6 στηλες
        
        # frame για τον πινακα και το scrollbar
        tree_frame = tk.Frame(self.parent, bg=self.color_bg)  
        tree_frame.pack(expand=True, fill="both", padx=40, pady=(10, 5))  

        # ορισμος στηλων του πινακα
        columns = ("Date", "Time", "Customer", "Phone", "Employee", "Status")

        # δημιουργια treeview (πινακας)
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",    
            height=15           
        )

        # τιτλοι στηλων (οταν κανεις κλικ ταξινομουνται)
        heading_config = [
            ("Date", "Ημερομηνία ▼", 120),     
            ("Time", "Ώρα", 80),
            ("Customer", "Πελάτης", 200),
            ("Phone", "Τηλέφωνο", 120),
            ("Employee", "Υπάλληλος", 150),
            ("Status", "Κατάσταση", 130),
        ]

        for col_id, col_text, col_width in heading_config:
            self.tree.heading(
                col_id,
                text=col_text,
                anchor="center",
                command=lambda c=col_id: self._sort_by_column(c)
            )
            self.tree.column(col_id, width=col_width, anchor="center")

        # καθετο scroll
        scrollbar_y = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        # οριζοντιο scroll (για να βλεπεις ολες τις στηλες)
        scrollbar_x = ttk.Scrollbar(
            tree_frame, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(xscrollcommand=scrollbar_x.set)

        # τοποθετηση: πινακας αριστερα, καθετο scroll δεξια, οριζοντιο κατω
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")

        # tags για χρωματα καταστασης
        self.tree.tag_configure("upcoming", foreground=self.color_upcoming)    
        self.tree.tag_configure("completed", foreground=self.color_completed)  
        self.tree.tag_configure("modified", foreground=self.color_modified)    
        self.tree.tag_configure("cancelled", foreground=self.color_cancelled)  

        # tags για ζεμπρε γραμμες (εναλλαγη χρωματος)
        self.tree.tag_configure("oddrow", background="#FFFFFF")   
        self.tree.tag_configure("evenrow", background="#D9E2EC")  

        # χρωμα γραμμης στο hover του ποντικιου
        self.tree.tag_configure("hover", background="#B3E5FC")    
        self._last_hovered_item = None
        self.tree.bind("<Motion>", self._on_mouse_move)

        # triggers για διαφορα κλικς
        self.tree.bind("<Double-1>", self._on_double_click)       
        self.tree.bind("<Button-3>", self._on_right_click)

    def _build_status_bar(self):
        # μπαρα καταστασης (στο κατω μερος) που δειχνει ποσα βρεθηκαν
        self.status_label = tk.Label(
            self.parent,
            text="",
            font=("Arial", 10),       
            bg=self.color_bg,          
            fg=self.color_completed,   
            anchor="w"                 
        )
        self.status_label.pack(fill="x", padx=45, pady=(0, 10))  

    def _build_context_menu(self):
        # μενου με δεξι κλικ πανω στις γραμμες του πινακα
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(
            label="Αντιγραφή Τηλεφώνου",
            command=lambda: self._copy_field("phone")
        )
        self.context_menu.add_command(
            label="Αντιγραφή Email",
            command=lambda: self._copy_field("email")
        )

    # ΜΕΡΟΣ 3: ΛΟΓΙΚΗ ΑΝΑΖΗΤΗΣΗΣ ΚΑΙ ΦΙΛΤΡΩΝ
    # τι γινεται οταν γραφουμε κατι στο πεδιο η αλλαζουμε φιλτρο

    def _on_search(self, event=None):
        # καλειται οταν γραφουμε κατι στo entry η οταν γινεται αλλαγη στα φιλτρα
        keyword = self.search_entry.get().strip()

        # αγνοουμε το placeholder
        if keyword == self.placeholder_text:
            return

        # αν γραψει λιγοτερο απο 2 χαρακτηρες, καθαριζουμε
        if len(keyword) < 2:
            self._clear_tree()
            self._all_results = []
            self.status_label.config(text="")
            return

        # κληση στο search.py για να παρουμε τα αποτελεσματα
        try:
            import search
            results = search.search_appointments_by_customer(keyword)
        except ImportError:
            results = []

        # αποθηκευουμε ολα τα αποτελεσματα πριν το φιλτραρισμα
        self._all_results = results

        # εφαρμογη φιλτρων
        self._apply_filters_and_display()

    def _apply_filters_and_display(self):
        # εφαρμοζει τα φιλτρα χρονου και καταστασης και γεμιζει τον πινακα
        
        # καθαρισμος πινακα
        self._clear_tree()
        self._results_data = {}

        # φιλτραρισμα χρονου και καταστασης
        today = datetime.now().date()
        filtered = []

        for result in self._all_results:
            # υπολογισμος καταστασης ραντεβου
            status = self._determine_status(
                result.get("appt_date", ""),
                result.get("notes", "")
            )
            result["_status"] = status

            # βρισκουμε ποσες ημερες πισω να κοιταξουμε
            days_back = None
            for _, key, days in self._time_presets:
                if key == self.active_time_preset:
                    days_back = days
                    break

            if days_back is not None:
                try:
                    appt_date = datetime.strptime(
                        str(result.get("appt_date", "")), "%Y-%m-%d"
                    ).date()

                    if days_back == 0:
                        # σημερα 
                        if appt_date != today:
                            continue
                    else:
                        # ημερες πισω
                        cutoff = today - timedelta(days=days_back)
                        if appt_date < cutoff:
                            continue
                except (ValueError, TypeError):
                    continue
            
            # φιλτρο καταστασης
            if self.active_status_filter != "all":
                if status != self.active_status_filter:
                    continue

            filtered.append(result)

        # ταξινομηση
        filtered = self._sort_results(filtered)

        # εισαγωγη στον πινακα
        for i, result in enumerate(filtered):
            status = result["_status"]

            # ημερομηνια σε κανονικο format
            display_date = self._format_date(result.get("appt_date", ""))

            # κειμενο καταστασης
            status_text = {
                "upcoming": "ΕΠΙΚΕΙΜΕΝΟ",
                "completed": "ΟΛΟΚΛΗΡΩΜΕΝΟ",
                "modified": "ΤΡΟΠΟΠΟΙΗΜΕΝΟ",
                "cancelled": "ΑΚΥΡΩΜΕΝΟ"
            }.get(status, "—")

            # χρωμα γραμμης (απαλο/λευκο)
            zebra_tag = "evenrow" if i % 2 == 0 else "oddrow"

            # insert στον πινακα (treeview)
            item = self.tree.insert("", "end", values=(
                display_date,
                result.get("start_time", "—"),
                result.get("customer_name", "—"),
                result.get("phone", "—"),
                result.get("employee_name", "—"),
                status_text
            ), tags=(status, zebra_tag))

            # αποθηξευση data για εντοπισμο double click / right click
            self._results_data[item] = result

        # ενημερωση status bar
        count = len(filtered)
        self.status_label.config(text=f"Βρέθηκαν: {count} ραντεβού")


    # ΜΕΡΟΣ 4: ΤΑΞΙΝΟΜΗΣΗ ΔΕΔΟΜΕΝΩΝ (SORTING)
    # ταξινομηση οταν ο χρηστης κανει κλικ στις στηλες του πινακα

    def _sort_by_column(self, column):
        # καλειται οταν ο χρηστης πατησει τον τιτλο της στηλης 
        
        # αν πατησει στην ιδια στηλη, απλα αντιστρεφει τη σειρα
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False

        # ενημερωση με βελακια στους τιτλους στηλων
        heading_names = {
            "Date": "Ημερομηνία",
            "Time": "Ώρα",
            "Customer": "Πελάτης",
            "Phone": "Τηλέφωνο",
            "Employee": "Υπάλληλος",
            "Status": "Κατάσταση",
        }
        for col_id, base_name in heading_names.items():
            if col_id == column:
                # βαζουμε βελακι ταξινομησης
                arrow = " ▼" if self._sort_reverse else " ▲"
                self.tree.heading(col_id, text=base_name + arrow)
            else:
                self.tree.heading(col_id, text=base_name)

        # καλει παλι την εμφανιση
        self._apply_filters_and_display()

    def _sort_results(self, results):
        # ταξινομει λιστα αποτελεσματων

        # mapping της στηλης treeview στο field της βασης
        column_to_key = {
            "Date": "appt_date",
            "Time": "start_time",
            "Customer": "customer_name",
            "Phone": "phone",
            "Employee": "employee_name",
            "Status": "_status",
        }
        key_field = column_to_key.get(self._sort_column, "appt_date")

        # ταξινομηση με προσθετη προστασια (str) για τα κενα
        return sorted(
            results,
            key=lambda r: str(r.get(key_field, "")),
            reverse=self._sort_reverse
        )

    # ΜΕΡΟΣ 5: ΠΑΡΑΘΥΡΟ ΦΙΛΤΡΩΝ (DROPDOWN MENU)
    # διαχειριση του dropdown menu για τα φιλτρα ημερομηνιας/καταστασης

    def _toggle_filters(self):
        # εμφανιση / αποκρυψη popup για φιλτρα
        
        # αν ειναι ηδη ανοιχτο, κλεισε το
        if self._filter_popup is not None:
            self._close_filter_popup()
            return

        # νεο frame που εμφανιζεται απο πανω
        self._filter_popup = tk.Frame(
            self.parent,
            bg=self.color_white,
            highlightthickness=1,
            highlightbackground=self.color_border,
            padx=16,
            pady=12
        )

        # δυο στηλες μεσα στο popup
        columns_frame = tk.Frame(self._filter_popup, bg=self.color_white)
        columns_frame.pack(fill="x")

        # στηλη 1: χρονικο ευρος
        col1 = tk.Frame(columns_frame, bg=self.color_white)
        col1.pack(side="left", anchor="n", padx=(0, 15))
        
        tk.Label(
            col1,
            text="ΗΜΕΡΟΜΗΝΙΑ",
            font=("Arial", 8, "bold"),
            bg=self.color_white,
            fg=self.color_completed
        ).pack(anchor="w", pady=(0, 6))

        for text, key, _ in self._time_presets:
            is_active = (key == self.active_time_preset)
            btn = tk.Button(
                col1,
                text=f"◉  {text}" if is_active else f"○  {text}",
                font=("Arial", 9, "bold") if is_active else ("Arial", 9),
                bg=self.color_white,
                fg=self.color_accent if is_active else self.color_text,
                relief="flat", borderwidth=0, anchor="w", width=14, cursor="hand2",
                activebackground=self.color_white,
                activeforeground=self.color_accent,
                command=lambda k=key: self._set_time_preset(k)
            )
            btn.pack(anchor="w", pady=1)
            btn.bind("<Enter>", lambda e, b=btn: b.config(font=("Arial", 9, "bold underline")))
            btn.bind("<Leave>", lambda e, b=btn, a=is_active: b.config(font=("Arial", 9, "bold") if a else ("Arial", 9)))

        # καθετη γραμμη στη μεση
        ttk.Separator(columns_frame, orient="vertical").pack(side="left", fill="y", padx=5)

        # στηλη 2: κατασταση
        col2 = tk.Frame(columns_frame, bg=self.color_white)
        col2.pack(side="left", anchor="n", padx=(15, 0))

        tk.Label(
            col2,
            text="ΚΑΤΑΣΤΑΣΗ",
            font=("Arial", 8, "bold"),
            bg=self.color_white,
            fg=self.color_completed
        ).pack(anchor="w", pady=(0, 6))

        for text, color, key in self._status_filters:
            is_active = (key == self.active_status_filter)
            btn = tk.Button(
                col2,
                text=f"◉  {text}" if is_active else f"○  {text}",
                font=("Arial", 9, "bold") if is_active else ("Arial", 9),
                bg=self.color_white,
                fg=color if is_active else self.color_text,
                relief="flat", borderwidth=0, anchor="w", width=14, cursor="hand2",
                activebackground=self.color_white,
                activeforeground=color,
                command=lambda k=key: self._set_status_filter(k)
            )
            btn.pack(anchor="w", pady=1)
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(font=("Arial", 9, "bold underline")))
            btn.bind("<Leave>", lambda e, b=btn, a=is_active, c=color: b.config(font=("Arial", 9, "bold") if a else ("Arial", 9)))

        # επαναφορα φιλτρων 
        ttk.Separator(self._filter_popup, orient="horizontal").pack(fill="x", pady=10)
        
        reset_btn = tk.Button(
            self._filter_popup,
            text="Καθαρισμός Φίλτρων",
            font=("Arial", 9, "bold"),
            bg="#FFF0F0",             
            fg="#D32F2F",             
            relief="flat", borderwidth=0, pady=4, cursor="hand2",
            activebackground="#FFE0E0", activeforeground="#B71C1C",
            command=self._reset_filters
        )
        reset_btn.pack(fill="x")
        reset_btn.bind("<Enter>", lambda e: reset_btn.config(bg="#FFE0E0"))
        reset_btn.bind("<Leave>", lambda e: reset_btn.config(bg="#FFF0F0"))

        # τοποθετηση ακριβως κατω απο το κουμπι δυναμικα
        self.parent.update_idletasks()
        search_bottom = (self.search_entry.master.winfo_y() + self.search_entry.master.winfo_height())
        self._filter_popup.place(relx=1.0, y=search_bottom + 4, anchor="ne", x=-40)
        self._filter_popup.lift()
        self.btn_filter_toggle.config(text="Φίλτρα ▲")

    def _close_filter_popup(self):
        # κλεινει το popup των φιλτρων
        if self._filter_popup is not None:
            self._filter_popup.place_forget()
            self._filter_popup.destroy()
            self._filter_popup = None
            self._update_filter_button_text()

    def _update_filter_button_text(self):
        # αλλαζει το χρωμα αν υπαρχουν επιλεγμενα φιλτρα
        if self.active_time_preset != "3months" or self.active_status_filter != "all":
            self.btn_filter_toggle.config(text="Φίλτρα (Ενεργά) ▼", fg=self.color_accent)
        else:
            self.btn_filter_toggle.config(text="Φίλτρα ▼", fg=self.color_sidebar)

    def _set_time_preset(self, preset_key):
        # αλλαγη χρονικου φιλτρου
        self.active_time_preset = preset_key
        self._close_filter_popup()
        self._apply_filters_and_display()

    def _set_status_filter(self, filter_key):
        # αλλαγη φιλτρου καταστασης
        self.active_status_filter = filter_key
        self._close_filter_popup()
        self._apply_filters_and_display()

    def _reset_filters(self):
        # καθαρισμος ολων των φιλτρων
        self.active_time_preset = "3months"
        self.active_status_filter = "all"
        self._close_filter_popup()
        self._apply_filters_and_display()

    # ΜΕΡΟΣ 6: ΟΠΤΙΚΑ ΕΦΕ (HOVER)
    # hover εφε για τις γραμμες του πινακα οταν περναει το ποντικι

    def _on_mouse_move(self, event):
        # αλλαζει χρωμα στη γραμμη οταν περναει το ποντικι απο πανω
        item = self.tree.identify_row(event.y)

        if item != self._last_hovered_item:
            # καθαρισμος της προηγουμενης
            if self._last_hovered_item and self.tree.exists(self._last_hovered_item):
                idx = self.tree.index(self._last_hovered_item)
                original_tag = "evenrow" if idx % 2 == 0 else "oddrow"
                # κραταμε το χρωμα κειμενου αναλογα την κατασταση
                result = self._results_data.get(self._last_hovered_item)
                status_tag = result.get("_status", "completed") if result else "completed"
                self.tree.item(self._last_hovered_item, tags=(status_tag, original_tag))

            # υπολογισμος χρωματος στη νεα ενεργη 
            if item:
                result = self._results_data.get(item)
                status_tag = result.get("_status", "completed") if result else "completed"
                self.tree.item(item, tags=(status_tag, "hover"))

            self._last_hovered_item = item

    # ΜΕΡΟΣ 7: ΔΕΞΙ ΚΛΙΚ ΚΑΙ ΑΝΤΙΓΡΑΦΗ
    # τι γινεται οταν κανουμε δεξι κλικ πανω σε ενα ραντεβου

    def _on_right_click(self, event):
        # δεξι κλικ πανω στον πινακα πεταει popup επιλογων
        
        # βρες ποια γραμμη πατησε
        item = self.tree.identify_row(event.y)
        if not item:
            return

        # Επιλογή της γραμμής (highlight)
        self.tree.selection_set(item)

        # Εμφάνιση context menu στη θέση του ποντικιού
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _copy_field(self, field):
        # αντιγραφει τηλεφωνο η email στο clipboard
        
        # βρες ποια ειναι επιλεγμενη
        selected = self.tree.selection()
        if not selected:
            return

        # παρε τα data
        result = self._results_data.get(selected[0])
        if not result:
            return

        # αντιγραφη στο clipboard (μνημη)
        value = str(result.get(field, ""))
        if value:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(value)

    # ΜΕΡΟΣ 8: ΔΙΠΛΟ ΚΛΙΚ ΚΑΙ ΚΑΡΤΕΛΑ ΛΕΠΤΟΜΕΡΕΙΩΝ
    # τι γινεται οταν κανουμε διπλο κλικ πανω σε ενα ραντεβου

    def _on_double_click(self, event):
        # ανοιγει παραθυρακι με ολες τις πληροφοριες του ραντεβου
        item = self.tree.identify_row(event.y)
        if not item:
            return

        result = self._results_data.get(item)
        if not result:
            return

        # ανοιγουμε καρτελα για οποιοδηποτε ραντεβου
        self._show_details_popup(result)

    def _show_details_popup(self, result):
        # φτιαχνει ενα νεο παραθυρακι με ολες τις πληροφοριες του ραντεβου
        
        # δημιουργια top level παραθυρου
        popup = tk.Toplevel(self.parent)
        popup.title("Λεπτομέρειες Ραντεβού")
        popup.geometry("450x400")
        popup.configure(bg=self.color_white)  
        popup.resizable(False, False)

        # το βαζουμε στο κεντρο της οθονης
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 225
        y = (popup.winfo_screenheight() // 2) - 200
        popup.geometry(f"450x400+{x}+{y}")

        # εικονιδιο αναλογα την κατασταση
        status = result.get("_status", "completed")
        status_icons = {
            "upcoming": ("Επικείμενο Ραντεβού", self.color_upcoming),
            "completed": ("Ολοκληρωμένο Ραντεβού", self.color_completed),
            "modified": ("Τροποποιημένο Ραντεβού", self.color_modified),
            "cancelled": ("Ακυρωμένο Ραντεβού", self.color_cancelled),
        }
        title_text, title_color = status_icons.get(status, ("Ραντεβού", self.color_sidebar))


        # τιτλος παραθυρου
        tk.Label(
            popup,
            text=title_text,
            font=("Arial", 14, "bold"),
            bg=self.color_white,
            fg=title_color
        ).pack(pady=(20, 15))

        # frame για τα πεδια (αριστερα label, δεξια τιμη)
        info_frame = tk.Frame(popup, bg=self.color_white, padx=30)
        info_frame.pack(fill="x")

        # λιστα με τα πεδια που θελουμε να δειξουμε
        display_date = self._format_date(result.get("appt_date", ""))
        fields = [
            ("Πελάτης", result.get("customer_name", "—")),
            ("Τηλέφωνο", result.get("phone", "—")),
            ("Email", result.get("email", "—")),
            ("Ημερομηνία", display_date),
            ("Ώρα Έναρξης", result.get("start_time", "—")),
            ("Ώρα Λήξης", result.get("end_time", "—")),
            ("Διάρκεια", f"{result.get('duration', '—')} λεπτά"),
            ("Υπάλληλος", result.get("employee_name", "—")),
        ]

        for label_text, value_text in fields:
            row = tk.Frame(info_frame, bg=self.color_white)
            row.pack(fill="x", pady=3)

            tk.Label(
                row,
                text=f"{label_text}:",
                font=("Arial", 10, "bold"),
                bg=self.color_white,
                fg=self.color_sidebar,
                width=14, anchor="w"
            ).pack(side="left")

            tk.Label(
                row,
                text=str(value_text),
                font=("Arial", 10),
                bg=self.color_white,
                fg=self.color_text,
                anchor="w"
            ).pack(side="left", fill="x")

        # σημειωσεις (αν υπαρχουν)
        raw_notes = str(result.get("notes", ""))
        clean_notes = raw_notes.replace("[MODIFIED]", "").replace("[DELETED]", "").strip()
        if clean_notes:
            tk.Label(
                popup,
                text=f"Σημειώσεις: {clean_notes}",
                font=("Arial", 10, "italic"),
                bg=self.color_white,
                fg=self.color_completed,
                wraplength=380
            ).pack(pady=(10, 0), padx=30, anchor="w")

        # απλο κουμπι για να κλεισει
        tk.Button(
            popup,
            text="Κλείσιμο",
            font=("Arial", 10, "bold"),
            bg=self.color_accent,
            fg="white",
            relief="flat",
            padx=20, pady=5,
            cursor="hand2",
            command=popup.destroy
        ).pack(pady=(20, 10))

        # το παραθυρο πρεπει να πιανει ολο το focus
        popup.transient(self.parent)
        popup.grab_set()

    # ΜΕΡΟΣ 9: ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ (UTILITIES)
    # διαφορες μικρες διαφορες που βοηθανε τον υπολοιπο κωδικα

    def _determine_status(self, appt_date, notes):
        # βρισκει αυτοματα τι κατασταση εχει το ραντεβου
        # 1: ανυρωμενο, 2: τροποποιημενο, 3: επικειμενο, 4: ολοκληρωμενο
        notes_str = str(notes or "")

        # τα tags δειχνουν τι εχει γινει αλλαγες
        if "[DELETED]" in notes_str:
            return "cancelled"
        if "[MODIFIED]" in notes_str:
            return "modified"

        # συγκρινουμε ημερομηνια ραντεβου με τη σημερινη
        try:
            appt = datetime.strptime(str(appt_date), "%Y-%m-%d").date()
            today = datetime.now().date()
            if appt >= today:
                return "upcoming"
            else:
                return "completed"
        except (ValueError, TypeError):
            # αν δεν υπαρχει ημερομηνια, απλα το κλεινουμε
            return "completed"

    def _format_date(self, iso_date):
        # απο αγγλικο συστημα YYYY-MM-DD το κανουμε δικο μας DD/MM/YYYY
        try:
            parts = str(iso_date).split("-")
            if len(parts) == 3:
                return f"{parts[2]}/{parts[1]}/{parts[0]}"
        except (ValueError, IndexError):
            pass
        return iso_date

    def _clear_tree(self):
        # αδειαζει τον πινακα πριν ξαναγεμισει με νεα δεδομενα
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _on_export_click(self):
        # εξαγωγη των αποτελεσματων σε excel η pdf μεσω του export_data module
        if not self._all_results:
            from tkinter import messagebox
            messagebox.showwarning("Προσοχή", "Δεν υπάρχουν ραντεβού για εξαγωγή!")
            return

        # 1. Κοιτάμε αν υπάρχουν επιλεγμένα (με κλικ) ραντεβού
        selected_items = self.tree.selection()
        data_to_export = self._all_results  # Από προεπιλογή εξάγουμε τα πάντα

        # 2. Αν ο χρήστης έχει επιλέξει συγκεκριμένα:
        if selected_items:
            from tkinter import messagebox
            # Τον ρωτάμε τι θέλει να κάνει
            answer = messagebox.askyesnocancel(
                "Επιλογή Εξαγωγής", 
                f"Έχετε επιλέξει {len(selected_items)} ραντεβού.\n\n"
                "Ναι = Εξαγωγή ΜΟΝΟ των επιλεγμένων\n"
                "Όχι = Εξαγωγή ΟΛΩΝ των αποτελεσμάτων\n"
                "Άκυρο = Ακύρωση",
                default="yes"
            )
            
            if answer is None:  # Αν πατήσει Άκυρο σταματάμε
                return
            elif answer is True:  # Αν πατήσει Ναι, βάζουμε στη λίστα μόνο αυτά που επέλεξε
                data_to_export = [self._results_data[item] for item in selected_items if item in self._results_data]

        # 3. Στέλνουμε τη σωστή λίστα για εξαγωγή!
        import export_data
        export_data.export_results(data_to_export)


# -------------------------------------------------------------------
# testing: αν το τρεξουμε μονο του το αρχειο

if __name__ == "__main__":
    # δημιουργια root για δοκιμη
    root = tk.Tk()
    root.title("RandeBoo — Γενική Αναζήτηση (Test)")
    root.geometry("950x650")
    root.configure(bg="#F7F9FC")

    # Frame σαν content_frame του MainWindow
    content = tk.Frame(root, bg="#F7F9FC", padx=20, pady=10)
    content.pack(expand=True, fill="both")

    # Δημιουργία SearchPanel
    panel = SearchPanel(content)

    root.mainloop()
