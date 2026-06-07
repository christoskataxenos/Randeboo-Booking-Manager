"""
Ο κώδικας του αρχείου συντάχθηκε από τον Καταξενό Χρήστο

=============================================================================
ΑΡΧΕΙΟ: gui_settings.py
ΣΚΟΠΟΣ: Πάνελ Ρυθμίσεων (Επιχείρηση, Προφίλ, Ασφάλεια)
=============================================================================
"""

import json
import os
import platform
import sqlite3
import sys
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from typing import Any, List, Dict, Tuple, Set, Callable, Optional

from tkcalendar import DateEntry

import backup
import database


class SettingsPanel:
    # Διαχείριση ρυθμίσεων με πρόσβαση βάσει role_id

    def __init__(self, parent_container: tk.Widget, current_user_account: Dict[str, Any]) -> None:
        self.parent = parent_container
        self.user = current_user_account
        self.role_id = current_user_account.get("role_id", 2)  # 1=Admin, 2=User

        # --- GUI CONSTANTS (Aegean Theme) ---
        self.COLOR_BG      = "#F7F9FC"
        self.COLOR_SIDEBAR = "#0A3D62"
        self.COLOR_ACCENT  = "#1E90FF"
        self.COLOR_HOVER   = "#1877D4"
        self.COLOR_WHITE   = "#FFFFFF"
        self.COLOR_TEXT    = "#1B1F23"
        self.COLOR_BORDER  = "#E5E9F0"
        self.COLOR_MUTED   = "#95A5A6"
        self.COLOR_RED     = "#EE5253"
        self.COLOR_GREEN   = "#167C52"
        # ------------------------------------

        # Κύριο Πλαίσιο (Main Frame)
        self.main_frame = tk.Frame(parent_container, bg=self.COLOR_BG)
        self.main_frame.pack(fill="both", expand=True)

        # Μπάρα πλοήγησης (πάνω μέρος)
        self.navbar = tk.Frame(self.main_frame, bg=self.COLOR_WHITE, height=55, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        self.navbar.pack(side="top", fill="x")
        self.navbar.pack_propagate(False)
 
        # Κύρια περιοχή περιεχομένου
        self.content_area = tk.Frame(self.main_frame, bg=self.COLOR_BG, padx=30, pady=25)
        self.content_area.pack(fill="both", expand=True)
        
        self.inner_scroll_canvases: Set[tk.Canvas] = set()
        self._bind_mousewheel(self.main_frame.winfo_toplevel())

        # Διαφορετικές προβολές (Views)
        self.views: Dict[str, Any] = {}
        try:
            self._initialize_views()
            self._build_tabs()
            
            # Αρχική προβολή
            default_tab = "business" if self.role_id == 1 else "profile"
            self._show_tab(default_tab)
        except Exception as error:
            # Διαχείριση σφαλμάτων κατά την αρχικοποίηση του UI
            tk.Label(self.content_area, text=f"Σφάλμα φόρτωσης: {error}", fg="red", bg=self.COLOR_BG).pack()
            print(f"ΣΦΑΛΜΑ: Η αρχικοποίηση του SettingsPanel απέτυχε: {error}")

    def register_inner_scroll_canvas(self, canvas: tk.Canvas) -> None: 
        self.inner_scroll_canvases.add(canvas)

    def _bind_mousewheel(self, toplevel: tk.Tk) -> None:
        # Σύνδεση του mousewheel για την κύλιση του canvas
        def _on_mousewheel(event: Any) -> None:
            if not self._is_descendant(event.widget, self.main_frame): 
                return
            inner = self._get_inner_scroll_canvas(event.widget)
            if inner and inner.winfo_ismapped():
                # Λήψη των ορίων του περιεχομένου για να ελέγξουμε αν απαιτείται κύλιση
                scroll_box = inner.bbox("all")
                if scroll_box:
                    content_height = scroll_box[3] - scroll_box[1]
                    canvas_height = inner.winfo_height()
                    # Αν το περιεχόμενο χωράει πλήρως στην οθόνη, δεν κάνουμε κύλιση
                    if content_height <= canvas_height:
                        return
                inner.yview_scroll(int(-1 * (event.delta / 120)), "units")
        toplevel.bind("<MouseWheel>", _on_mousewheel, add="+")

    def _get_inner_scroll_canvas(self, widget: Any) -> Optional[tk.Canvas]:
        current_widget = widget
        while current_widget is not None:
            if current_widget in self.inner_scroll_canvases: 
                return current_widget
            current_widget = current_widget.master
        return None

    def _is_descendant(self, widget: Any, ancestor: Any) -> bool:
        current_widget = widget
        while current_widget is not None:
            if current_widget is ancestor: return True
            current_widget = current_widget.master
        return False

    def _initialize_views(self) -> None:
        if self.role_id == 1: 
            self.views["business"] = BusinessSettingsView(self.content_area, self)
            self.views["backup"] = BackupSettingsView(self.content_area, self)
        self.views["profile"] = ProfileSettingsView(self.content_area, self)
        self.views["security"] = SecuritySettingsView(self.content_area, self)
        self.views["system"] = SystemInfoView(self.content_area, self)

    def _build_tabs(self) -> None:
        if self.role_id == 1: 
            self._create_tab_btn("Επιχείρηση", "business")
            self._create_tab_btn("Αντίγραφα Ασφαλείας", "backup")
        self._create_tab_btn("Το Προφίλ μου", "profile")
        self._create_tab_btn("Ασφάλεια", "security")
        self._create_tab_btn("Πληροφορίες Συστήματος", "system")

    def _create_tab_btn(self, text: str, tab_id: str) -> tk.Button:
        btn = tk.Button(self.navbar, text=text, command=lambda: self._show_tab(tab_id),
                        bg=self.COLOR_WHITE, fg=self.COLOR_SIDEBAR, font=("Arial", 10, "bold"),
                        relief="flat", padx=20, cursor="hand2")
        btn.pack(side="left", fill="y")
        btn.bind("<Enter>", lambda event: btn.configure(bg=self.COLOR_BG))
        btn.bind("<Leave>", lambda event: btn.configure(bg=self.COLOR_WHITE))
        return btn

    def _show_tab(self, tab_id: str) -> None:
        for view_obj in self.views.values(): 
            view_obj.frame.pack_forget()
        target = self.views.get(tab_id)
        if target:
            target.frame.pack(fill="both", expand=True)
            if hasattr(target, "on_show"): target.on_show()


class BaseView:
    def __init__(self, parent: tk.Widget, controller: SettingsPanel) -> None:
        self.controller = controller
        self.frame = tk.Frame(parent, bg=controller.COLOR_BG)
        for attr in ["COLOR_ACCENT", "COLOR_WHITE", "COLOR_SIDEBAR", "COLOR_TEXT", "COLOR_BORDER", "COLOR_MUTED", "COLOR_HOVER", "COLOR_RED", "COLOR_GREEN"]:
            setattr(self, attr, getattr(controller, attr))

    def _create_label_entry(self, parent: tk.Widget, label_text: str, initial_value: str = "", state: str = "normal") -> tk.Entry:
        row_f = tk.Frame(parent, bg=self.COLOR_WHITE)
        row_f.pack(fill="x", pady=8)
        row_f.grid_columnconfigure(1, weight=1)
        
        tk.Label(row_f, text=label_text.upper(), bg=self.COLOR_WHITE, fg=self.COLOR_MUTED, width=22, anchor="w", font=("Arial", 8, "bold")).grid(row=0, column=0, sticky="w")
        
        text_entry_field = tk.Entry(row_f, font=("Arial", 10), state=state, relief="flat", highlightthickness=1, 
                       highlightbackground=self.COLOR_BORDER, highlightcolor=self.COLOR_ACCENT,
                       bg=self.COLOR_WHITE, fg=self.COLOR_TEXT)
        
        text_entry_field.insert(0, str(initial_value) if initial_value else "")
        text_entry_field.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        return text_entry_field

    def _style_button(self, btn: tk.Button, bg: str, hover: str) -> None:
        btn.configure(bg=bg, fg="white", relief="flat", cursor="hand2", font=("Arial", 9, "bold"), padx=15, pady=8)
        btn.bind("<Enter>", lambda event: btn.configure(bg=hover))
        btn.bind("<Leave>", lambda event: btn.configure(bg=bg))


class BusinessSettingsView(BaseView):
    # Προεπιλεγμένο πρότυπο email (Greek Template)
    DEFAULT_EMAIL_TEMPLATE = (
        "Αγαπητέ/ή {customer_name},\n\n"
        "Σας υπενθυμίζουμε το προγραμματισμένο ραντεβού σας με την επιχείρηση {company_name} "
        "στις {appt_date} και ώρα {start_time}.\n\n"
        "Σε περίπτωση που επιθυμείτε να ακυρώσετε ή να αλλάξετε το ραντεβού σας, "
        "παρακαλούμε επικοινωνήστε μαζί μας στο τηλέφωνο {phone}.\n\n"
        "Ευχαριστούμε,\n"
        "{company_name}"
    )

    def __init__(self, parent: tk.Widget, controller: SettingsPanel) -> None:
        super().__init__(parent, controller)
        self.settings = database.get_business_settings()
        
        # Αρχικοποίηση buffer για εξαιρέσεις (exception_days)
        try:
            self.temporary_settings_buffer = json.loads(self.settings.get("exception_days", "{}"))
        except Exception:
            self.temporary_settings_buffer = {}
            
        self._build_ui()

    def _build_ui(self) -> None:
        header_f = tk.Frame(self.frame, bg=self.controller.COLOR_BG); header_f.pack(fill="x", pady=(0, 20))
        tk.Label(header_f, text="Ρυθμίσεις Επιχείρησης", font=("Arial", 18, "bold"), bg=self.controller.COLOR_BG, fg=self.COLOR_SIDEBAR).pack(side="left")
        self.btn_save = tk.Button(header_f, text="ΑΠΟΘΗΚΕΥΣΗ", command=self._save_all); self._style_button(self.btn_save, self.COLOR_GREEN, "#1f8a4c"); self.btn_save.pack(side="right")
        
        self.nb = ttk.Notebook(self.frame); self.nb.pack(fill="both", expand=True)
        self.tab_info = tk.Frame(self.nb, bg=self.COLOR_WHITE, padx=10, pady=10)
        self.tab_hours = tk.Frame(self.nb, bg=self.COLOR_WHITE, padx=10, pady=10)
        self.tab_email = tk.Frame(self.nb, bg=self.COLOR_WHITE, padx=10, pady=10)
        self.nb.add(self.tab_info, text="  Στοιχεία  ")
        self.nb.add(self.tab_hours, text="  Ωράριο  ")
        self.nb.add(self.tab_email, text="  Email  ")
        self.ents = {}; self._build_info_tab(); self._build_hours_tab(); self._build_email_tab()

    def _scrollable_frame(self, parent: tk.Widget) -> tk.Frame:
        canvas = tk.Canvas(parent, bg=self.COLOR_WHITE, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, bg=self.COLOR_WHITE)
        window_item = canvas.create_window((0, 0), window=content_frame, anchor="nw")

        def _configure_scrollregion(event: Any) -> None:
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            if canvas.bbox("all") and canvas.bbox("all")[3] > canvas.winfo_height():
                scrollbar.pack(side="right", fill="y")
            else:
                scrollbar.pack_forget()

        content_frame.bind("<Configure>", _configure_scrollregion)
        canvas.bind("<Configure>", lambda event: canvas.itemconfig(window_item, width=event.width - 5))
        canvas.pack(side="left", fill="both", expand=True)
        self.controller.register_inner_scroll_canvas(canvas)
        return content_frame

    def _build_info_tab(self) -> None:
        scroll_content = self._scrollable_frame(self.tab_info)
        info_card = tk.Frame(scroll_content, bg=self.COLOR_WHITE, padx=25, pady=25, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        info_card.pack(fill="x", padx=15, pady=15)
        
        for label_text, setting_key in [("Επωνυμία:", "company_name"), ("Τηλέφωνο:", "phone"), ("Email:", "email"), ("Διεύθυνση:", "address"), ("Website:", "website"), ("ΑΦΜ:", "vat")]:
            self.ents[setting_key] = self._create_label_entry(info_card, label_text, self.settings.get(setting_key))
            
        description_row = tk.Frame(info_card, bg="white")
        description_row.pack(fill="x", pady=10)
        description_row.grid_columnconfigure(1, weight=1)
        
        tk.Label(description_row, text="ΠΕΡΙΓΡΑΦΗ:", bg="white", fg=self.COLOR_MUTED, width=22, anchor="w", font=("Arial", 8, "bold")).grid(row=0, column=0, sticky="nw")
        self.text_description = tk.Text(description_row, height=4, font=("Arial", 10), bg="#F8F9FA", relief="flat", highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        self.text_description.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        self.text_description.insert("1.0", self.settings.get("business_description", ""))

    def _build_hours_tab(self) -> None:
        scroll_content = self._scrollable_frame(self.tab_hours)
        hours_card = tk.Frame(scroll_content, bg=self.COLOR_WHITE, padx=25, pady=25, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        hours_card.pack(fill="x", padx=15, pady=15)
        
        # Κουμπιά για ωράριο, αργίες και εξαιρέσεις
        action_buttons_frame = tk.Frame(hours_card, bg=self.COLOR_WHITE)
        action_buttons_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(action_buttons_frame, text="ΡΥΘΜΙΣΕΙΣ:", bg=self.COLOR_WHITE, font=("Arial", 8, "bold"), fg=self.COLOR_MUTED).pack(side="left", padx=(0, 15))
        
        for button_title, command_func in [("Αργίες", self._open_h), ("Εξαιρέσεις", self._open_e)]:
            btn = tk.Button(action_buttons_frame, text=f"{button_title}", command=command_func)
            self._style_button(btn, self.COLOR_ACCENT, self.COLOR_HOVER)
            btn.pack(side="left", padx=5)

        tk.Label(hours_card, text="ΕΒΔΟΜΑΔΙΑΙΟ ΩΡΑΡΙΟ", bg=self.COLOR_WHITE, font=("Arial", 9, "bold"), fg=self.COLOR_SIDEBAR).pack(anchor="w", pady=(10, 15))
        
        schedule_grid = tk.Frame(hours_card, bg=self.COLOR_WHITE)
        schedule_grid.pack(fill="x")
        
        column_headers = ["ΗΜΕΡΑ", "ΕΝΕΡΓΟ", "Β1(Α)", "Β1(Ε)", "Β2(Α)", "Β2(Ε)"]
        for i, header in enumerate(column_headers): 
            tk.Label(schedule_grid, text=header, bg=self.COLOR_WHITE, font=("Arial", 7, "bold"), fg=self.COLOR_MUTED).grid(row=0, column=i, padx=4)
            
        days_mapping = {"mon": "Δευτέρα", "tue": "Τρίτη", "wed": "Τέταρτη", "thu": "Πέμπτη", "fri": "Παρασκευή", "sat": "Σάββατο", "sun": "Κυριακή"}
        
        self.sched_entries = {}
        schedule_config = json.loads(self.settings.get("weekly_schedule", "{}"))
        for i, (day_key, day_greek) in enumerate(days_mapping.items()):
            table_row_index = i + 1
            day_data = schedule_config.get(day_key, {"closed": False, "s1_s": "09:00", "s1_e": "14:00"})
            
            # Αν είναι τσεκαρισμένο, τότε είναι ανοιχτά
            is_open = not day_data.get("closed", False)
            open_var = tk.BooleanVar(value=is_open)
            
            tk.Label(schedule_grid, text=day_greek, width=10, anchor="w", bg=self.COLOR_WHITE, font=("Arial", 9)).grid(row=table_row_index, column=0, pady=4)
            tk.Checkbutton(schedule_grid, variable=open_var, bg=self.COLOR_WHITE, activebackground=self.COLOR_WHITE).grid(row=table_row_index, column=1)
            
            entry_style = {"bg": "#F8F9FA", "relief": "flat", "highlightthickness": 1, "highlightbackground": self.COLOR_BORDER, "font": ("Arial", 9)}
            
            ent_v1_arxi = tk.Entry(schedule_grid, width=6, **entry_style)
            ent_v1_arxi.insert(0, day_data.get("s1_s", "09:00"))
            ent_v1_arxi.grid(row=table_row_index, column=2, padx=2)
            
            ent_v1_telos = tk.Entry(schedule_grid, width=6, **entry_style)
            ent_v1_telos.insert(0, day_data.get("s1_e", "14:00"))
            ent_v1_telos.grid(row=table_row_index, column=3, padx=2)
            
            ent_v2_arxi = tk.Entry(schedule_grid, width=6, **entry_style)
            ent_v2_arxi.insert(0, day_data.get("s2_s", ""))
            ent_v2_arxi.grid(row=table_row_index, column=4, padx=2)
            
            ent_v2_telos = tk.Entry(schedule_grid, width=6, **entry_style)
            ent_v2_telos.insert(0, day_data.get("s2_e", ""))
            ent_v2_telos.grid(row=table_row_index, column=5, padx=2)
            
            self.sched_entries[day_key] = {
                "open_var": open_var, 
                "s1_s": ent_v1_arxi, 
                "s1_e": ent_v1_telos, 
                "s2_s": ent_v2_arxi, 
                "s2_e": ent_v2_telos
            }

    def _open_h(self) -> None: HolidaysDialog(self.controller.parent, self)
    def _open_e(self) -> None: ExceptionsDialog(self.controller.parent, self)

    def _build_email_tab(self) -> None:
        scroll_content = self._scrollable_frame(self.tab_email)
        email_card = tk.Frame(scroll_content, bg=self.COLOR_WHITE, padx=25, pady=25, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        email_card.pack(fill="x", padx=15, pady=15)
        
        tk.Label(email_card, text="ΕΙΔΟΠΟΙΗΣΕΙΣ EMAIL", bg=self.COLOR_WHITE, font=("Arial", 9, "bold"), fg=self.COLOR_SIDEBAR).pack(anchor="w", pady=(0, 15))
        
        calendar_integration_var = tk.BooleanVar(value=self.settings.get("add_to_calendar") == "1")
        tk.Checkbutton(email_card, text="Επισύναψη .ics αρχείου", variable=calendar_integration_var, bg=self.COLOR_WHITE).pack(anchor="w")
        
        for label_text, setting_key in [("SMTP Server:", "smtp_server"), ("Θύρα:", "smtp_port"), ("Χρήστης Email:", "email_user")]:
            self.ents[setting_key] = self._create_label_entry(email_card, label_text, self.settings.get(setting_key))
        
        password_row = tk.Frame(email_card, bg="white")
        password_row.pack(fill="x", pady=8)
        password_row.grid_columnconfigure(1, weight=1)
        
        tk.Label(password_row, text="ΚΩΔΙΚΟΣ:", bg="white", fg=self.COLOR_MUTED, width=22, anchor="w", font=("Arial", 8, "bold")).grid(row=0, column=0, sticky="w")
        self.entry_email_pass = tk.Entry(password_row, font=("Arial", 10), show="*", relief="flat", highlightthickness=1, highlightbackground=self.COLOR_BORDER, bg="white")
        self.entry_email_pass.insert(0, self.settings.get("email_password", ""))
        self.entry_email_pass.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        
        # Πλαίσιο Οδηγιών για placeholders
        help_frame = tk.Frame(email_card, bg="#EBF5FB", padx=15, pady=15, highlightthickness=1, highlightbackground="#AED6F1")
        help_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(help_frame, text="ΟΔΗΓΙΕΣ ΣΥΝΤΑΞΗΣ", bg="#EBF5FB", font=("Arial", 9, "bold"), fg="#2E86C1").pack(anchor="w", pady=(0, 5))
        instructions_text = (
            "Χρησιμοποιήστε τα παρακάτω σύμβολα για να εισάγετε αυτόματα στοιχεία του ραντεβού:\n\n"
            "• {customer_name} : Το ονοματεπώνυμο του πελάτη\n"
            "• {appt_date} : Η ημερομηνία του ραντεβού (π.χ. 12/05/2024)\n"
            "• {start_time} : Η ώρα έναρξης (π.χ. 10:30)\n"
            "• {company_name} : Η επωνυμία της επιχείρησής σας\n"
            "• {phone} : Το τηλέφωνο επικοινωνίας της επιχείρησης"
        )
        tk.Label(email_card, text=instructions_text, bg="#EBF5FB", font=("Arial", 8), fg="#34495E", justify="left").pack(anchor="w")

        # Κεφαλίδα για το Πρότυπο Email με κουμπί επαναφοράς
        template_header = tk.Frame(email_card, bg=self.COLOR_WHITE)
        template_header.pack(fill="x", pady=(5, 5))

        tk.Label(template_header, text="ΠΡΟΤΥΠΟ EMAIL:", bg=self.COLOR_WHITE, font=("Arial", 8, "bold"), fg=self.COLOR_MUTED).pack(side="left")

        btn_restore = tk.Button(template_header, text="ΕΠΑΝΑΦΟΡΑ ΠΡΟΤΥΠΟΥ", command=self._restore_default_email,
                               bg=self.COLOR_WHITE, fg=self.COLOR_ACCENT, font=("Arial", 7, "bold"),
                               relief="flat", cursor="hand2", activebackground=self.COLOR_WHITE)
        btn_restore.pack(side="right")

        self.text_email_template = tk.Text(email_card, height=8, font=("Arial", 10), bg="#F8F9FA", relief="flat", highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        self.text_email_template.pack(fill="x")

        # Φόρτωση από τη βάση ή χρήση του προεπιλεγμένου αν είναι κενό
        current_template = self.settings.get("email_body_template", "").strip()
        if not current_template:
            current_template = self.DEFAULT_EMAIL_TEMPLATE

        self.text_email_template.insert("1.0", current_template)
        self.var_ics_ref = calendar_integration_var

    def _restore_default_email(self) -> None:
        """Επαναφέρει το προεπιλεγμένο κείμενο στο πρότυπο email."""
        if messagebox.askyesno("Επιβεβαίωση", "Θέλετε να επαναφέρετε το προεπιλεγμένο πρότυπο email;"):
            self.text_email_template.delete("1.0", "end")
            self.text_email_template.insert("1.0", self.DEFAULT_EMAIL_TEMPLATE)


    def _save_all(self) -> None:
        # Συγκέντρωση όλων των αλλαγών από τις καρτέλες ρυθμίσεων
        new_schedule_state = {}
        for day_key, entry_group in self.sched_entries.items():
            # Αντιστροφή λογικής: Αν δεν είναι επιλεγμένο, τότε θεωρείται κλειστό (closed=True)
            is_closed = not entry_group["open_var"].get()
            if is_closed: 
                new_schedule_state[day_key] = {"closed": True}
            else: 
                new_schedule_state[day_key] = {
                    "closed": False, 
                    "s1_s": entry_group["s1_s"].get(), 
                    "s1_e": entry_group["s1_e"].get(), 
                    "s2_s": entry_group["s2_s"].get(), 
                    "s2_e": entry_group["s2_e"].get()
                }
        
        # Δημιουργία αντιγράφου των τρεχουσών ρυθμίσεων για ενημέρωση
        updated_settings_copy = self.settings.copy()
        for setting_key, entry_widget in self.ents.items(): 
            updated_settings_copy[setting_key] = entry_widget.get()
            
        updated_settings_copy.update({
            "business_description": self.text_description.get("1.0", "end-1c"), 
            "weekly_schedule": json.dumps(new_schedule_state), 
            "exception_days": json.dumps(self.temporary_settings_buffer), 
            "email_body_template": self.text_email_template.get("1.0", "end-1c"), 
            "add_to_calendar": "1" if self.var_ics_ref.get() else "0", 
            "email_password": self.entry_email_pass.get()
        })
        
        if database.update_business_settings(updated_settings_copy): 
            messagebox.showinfo("Επιτυχία", "Οι ρυθμίσεις αποθηκεύτηκαν!")
        else: 
            messagebox.showerror("Σφάλμα", "Αποτυχία ενημέρωσης των ρυθμίσεων στη βάση.")


class SecuritySettingsView(BaseView):
    def __init__(self, parent: tk.Widget, controller: SettingsPanel) -> None:
        super().__init__(parent, controller)
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Label(self.frame, text="Ασφάλεια", font=("Arial", 18, "bold"), bg=self.controller.COLOR_BG, fg=self.COLOR_SIDEBAR).pack(anchor="w", pady=(0, 20))
        security_container = tk.Frame(self.frame, bg=self.COLOR_WHITE, padx=30, pady=30, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        security_container.pack(fill="x")
        
        self.entry_old_pass = self._create_label_entry(security_container, "Τρέχων Κωδικός:", "")
        self.entry_old_pass.config(show="*")
        
        self.entry_new_pass = self._create_label_entry(security_container, "Νέος Κωδικός:", "")
        self.entry_new_pass.config(show="*")
        
        change_btn = tk.Button(security_container, text="ΑΛΛΑΓΗ ΚΩΔΙΚΟΥ", command=self._change)
        self._style_button(change_btn, self.COLOR_RED, "#cc3f46")
        change_btn.pack(anchor="e", pady=20)

    def _change(self) -> None:
        if database.authenticate_user(self.controller.user["username"], self.entry_old_pass.get()):
            if database.change_password(self.controller.user.get("user_id"), self.entry_new_pass.get()):
                messagebox.showinfo("Επιτυχία", "Ο κωδικός άλλαξε!")
                return
        messagebox.showerror("Σφάλμα", "Λάθος στοιχεία.")


class ProfileSettingsView(BaseView):
    def __init__(self, parent: tk.Widget, controller: SettingsPanel) -> None:
        super().__init__(parent, controller)
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Label(self.frame, text="Το Προφίλ μου", font=("Arial", 18, "bold"), bg=self.controller.COLOR_BG, fg=self.COLOR_SIDEBAR).pack(anchor="w", pady=(0, 20))
        profile_container = tk.Frame(self.frame, bg=self.COLOR_WHITE, padx=30, pady=30, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        profile_container.pack(fill="x")
        
        self.ent_fname = self._create_label_entry(profile_container, "Όνομα:", self.controller.user.get("first_name"))
        self.ent_lname = self._create_label_entry(profile_container, "Επώνυμο:", self.controller.user.get("last_name"))
        self.ent_phone = self._create_label_entry(profile_container, "Τηλέφωνο:", self.controller.user.get("phone"))
        self.ent_email = self._create_label_entry(profile_container, "Email:", self.controller.user.get("email"))
        
        update_btn = tk.Button(profile_container, text="ΕΝΗΜΕΡΩΣΗ ΠΡΟΦΙΛ", command=self._save)
        self._style_button(update_btn, self.COLOR_ACCENT, self.COLOR_HOVER)
        update_btn.pack(anchor="e", pady=20)

    def _save(self) -> None:
        user_account = self.controller.user
        if database.update_user(user_account.get("user_id"), user_account["username"], self.ent_fname.get(), self.ent_lname.get(), self.ent_phone.get(), self.ent_email.get(), user_account["role_id"]):
            messagebox.showinfo("Επιτυχία", "Το προφίλ ενημερώθηκε.")
            user_account.update({"first_name": self.ent_fname.get(), "last_name": self.ent_lname.get(), "phone": self.ent_phone.get(), "email": self.ent_email.get()})


class SystemInfoView(BaseView):
    def __init__(self, parent: tk.Widget, controller: SettingsPanel) -> None:
        super().__init__(parent, controller)
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Label(self.frame, text="Πληροφορίες Συστήματος", font=("Arial", 18, "bold"), bg=self.controller.COLOR_BG, fg=self.COLOR_SIDEBAR).pack(anchor="w", pady=(0, 20))
        info_container = tk.Frame(self.frame, bg=self.COLOR_WHITE, padx=30, pady=30, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        info_container.pack(fill="both", expand=True)
        
        system_stats = [
            ("Έκδοση", "1.0.0"), 
            ("Python", sys.version.split()[0]), 
            ("Βάση Δεδομένων", database.DB_PATH)
        ]
        
        for label_text, value_text in system_stats:
            info_row = tk.Frame(info_container, bg="white")
            info_row.pack(fill="x", pady=6)
            tk.Label(info_row, text=f"{label_text}:", bg="white", font=("Arial", 9, "bold"), width=15, anchor="w").pack(side="left")
            tk.Label(info_row, text=value_text, bg="white", font=("Arial", 9)).pack(side="left")


class BackupSettingsView(BaseView):
    # Προβολή για τη διαχείριση των αντιγράφων ασφαλείας (Backup & Restore)
    
    def __init__(self, parent: tk.Widget, controller: SettingsPanel) -> None:
        super().__init__(parent, controller)
        self._build_ui()

    def _build_ui(self) -> None:
        # Κύριος τίτλος της οθόνης
        tk.Label(self.frame, text="Αντίγραφα Ασφαλείας", font=("Arial", 18, "bold"), bg=self.controller.COLOR_BG, fg=self.COLOR_SIDEBAR).pack(anchor="w", pady=(0, 20))
        
        # Πλαίσιο περιεχομένου
        backup_container = tk.Frame(self.frame, bg=self.COLOR_WHITE, padx=30, pady=30, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        backup_container.pack(fill="both", expand=True)
        
        # Επεξηγηματικό κείμενο για τον χρήστη
        desc_text = "Διαχείριση αντιγράφων ασφαλείας της βάσης δεδομένων. Μπορείτε να δημιουργήσετε ένα νέο αντίγραφο ασφαλείας ή να κάνετε επαναφορά της βάσης σε προηγούμενη κατάσταση επιλέγοντας ένα αρχείο από την παρακάτω λίστα."
        desc_label = tk.Label(backup_container, text=desc_text, bg=self.COLOR_WHITE, fg=self.COLOR_TEXT, font=("Arial", 10), wraplength=550, justify="left")
        desc_label.pack(anchor="w", pady=(0, 20))
        
        # Πλαίσιο για τα κουμπιά ενεργειών
        buttons_frame = tk.Frame(backup_container, bg=self.COLOR_WHITE)
        buttons_frame.pack(fill="x", pady=(0, 20))
        
        # Κουμπί δημιουργίας νέου backup
        self.btn_create = tk.Button(buttons_frame, text="ΔΗΜΙΟΥΡΓΙΑ BACKUP", command=self._create_backup)
        self._style_button(self.btn_create, self.COLOR_GREEN, "#167C52")
        self.btn_create.pack(side="left", padx=(0, 10))
        
        # Κουμπί επαναφοράς επιλεγμένου backup
        self.btn_restore = tk.Button(buttons_frame, text="ΕΠΑΝΑΦΟΡΑ BACKUP", command=self._restore_backup)
        self._style_button(self.btn_restore, self.COLOR_RED, "#EE5253")
        self.btn_restore.pack(side="left")
        
        # Ετικέτα λίστας αντιγράφων
        list_label = tk.Label(backup_container, text="ΔΙΑΘΕΣΙΜΑ ΑΝΤΙΓΡΑΦΑ ΑΣΦΑΛΕΙΑΣ (BACKUPS):", bg=self.COLOR_WHITE, fg=self.COLOR_MUTED, font=("Arial", 8, "bold"))
        list_label.pack(anchor="w", pady=(10, 5))
        
        # Πλαίσιο λίστας με scrollbar
        list_frame = tk.Frame(backup_container, bg=self.COLOR_WHITE)
        list_frame.pack(fill="both", expand=True)
        
        self.listbox_backups = tk.Listbox(list_frame, height=10, font=("Arial", 10), highlightthickness=1, highlightbackground=self.COLOR_BORDER, selectbackground=self.COLOR_ACCENT)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox_backups.yview)
        self.listbox_backups.configure(yscrollcommand=scrollbar.set)
        
        self.listbox_backups.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Αρχικό γέμισμα της λίστας
        self._refresh_list()
        
    def _format_backup_name(self, filename: str) -> str:
        # Μετατροπή του ονόματος αρχείου backup σε φιλική μορφή ημερομηνίας/ώρας
        try:
            if filename.startswith("backup_") and filename.endswith(".db"):
                # Αφαίρεση προθέματος και κατάληξης: backup_YYYYMMDD_HHMMSS.db -> YYYYMMDD_HHMMSS
                parts = filename.replace("backup_", "").replace(".db", "").split("_")
                if len(parts) == 2:
                    date_str, time_str = parts[0], parts[1]
                    day = date_str[6:8]
                    month = date_str[4:6]
                    year = date_str[0:4]
                    hour = time_str[0:2]
                    minute = time_str[2:4]
                    second = time_str[4:6]
                    return f"{day}/{month}/{year}, {hour}:{minute}:{second}"
        except Exception:
            pass
        return filename

    def _refresh_list(self) -> None:
        # Καθαρισμός και επαναφόρτωση της λίστας των backups
        self.listbox_backups.delete(0, "end")
        self.backups_list = backup.get_available_backups()
        for filename in self.backups_list:
            display_name = self._format_backup_name(filename)
            self.listbox_backups.insert("end", display_name)
            
    def _create_backup(self) -> None:
        # Κλήση της συνάρτησης δημιουργίας backup και ανανέωση της λίστας
        if backup.create_backup(silent=False):
            self._refresh_list()
            
    def _restore_backup(self) -> None:
        # Επαναφορά της βάσης από το επιλεγμένο αρχείο της λίστα ή χειροκίνητα
        selection = self.listbox_backups.curselection()
        
        if not selection:
            # Αν δεν έχει επιλεγεί αρχείο, ρωτάμε τον χρήστη αν θέλει να βρει το αρχείο χειροκίνητα
            choose_manual = messagebox.askyesno(
                "Επιλογή Αρχείου",
                "Δεν έχετε επιλέξει κάποιο αρχείο από τη λίστα.\n"
                "Θέλετε να αναζητήσετε και να επιλέξετε ένα αρχείο βάσης δεδομένων (.db) από τον υπολογιστή σας;"
            )
            if not choose_manual:
                return
            
            # Άνοιγμα Windows Explorer για επιλογή αρχείου
            selected_file_path = filedialog.askopenfilename(
                title="Επιλογή αρχείου βάσης δεδομένων για Επαναφορά",
                filetypes=[("Database Files", "*.db"), ("All Files", "*.*")]
            )
            if not selected_file_path:
                return
                
            backup_file_path = selected_file_path
            display_name = os.path.basename(selected_file_path)
        else:
            # Αν έχει γίνει επιλογή από τη λίστα, παίρνουμε το αντίστοιχο αρχείο
            selected_file = self.backups_list[selection[0]]
            backup_file_path = os.path.join(backup.BACKUP_DIR, selected_file)
            display_name = selected_file
        
        # Ερώτηση επιβεβαίωσης στον χρήστη
        confirm = messagebox.askyesno(
            "Επιβεβαίωση Επαναφοράς", 
            f"Είστε σίγουροι ότι θέλετε να επαναφέρετε τη βάση δεδομένων από το αρχείο:\n{display_name}?\n\n"
            "ΠΡΟΣΟΧΗ: Όλα τα τρέχοντα δεδομένα θα αντικατασταθούν. Η εφαρμογή θα κλείσει αυτόματα μετά την επαναφορά."
        )
        
        if confirm:
            if backup.restore_backup(backup_file_path, silent=False):
                # Κλείσιμο της εφαρμογής για να εξαναγκαστεί η επαναφόρτωση της βάσης
                self.controller.parent.winfo_toplevel().destroy()
                
    def on_show(self) -> None:
        # Ανανέωση της λίστας όταν εμφανίζεται η καρτέλα
        self._refresh_list()


class SettingsDialogBase(tk.Toplevel):
    def __init__(self, parent, caller, title, width=500, height=450):
        super().__init__(parent)
        self.caller = caller
        self.title(title)
        
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{width}x{height}+{(screen_width - width) // 2}+{(screen_height - height) // 2}")
        self.configure(bg="#F7F9FC")
        self.transient(parent)
        self.grab_set()
        
        header_frame = tk.Frame(self, bg="white", height=65, highlightthickness=1, highlightbackground="#E5E9F0")
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=title.upper(), fg=self.caller.COLOR_SIDEBAR, bg="white", font=("Arial", 11, "bold")).pack(side="left", padx=25)
        
        self.cnt = tk.Frame(self, bg="white", padx=25, pady=25, highlightthickness=1, highlightbackground="#E5E9F0")
        self.cnt.pack(fill="both", expand=True, padx=20, pady=(20, 10))
        
        footer_frame = tk.Frame(self, bg="#F7F9FC", pady=20)
        footer_frame.pack(fill="x", side="bottom")
        
        btn_save = tk.Button(footer_frame, text="Αποθήκευση", command=self.save, bg=self.caller.COLOR_ACCENT, fg="white", font=("Arial", 9, "bold"), padx=30, pady=10, relief="flat")
        btn_save.pack(side="right", padx=25)
        
        btn_cancel = tk.Button(footer_frame, text="Ακύρωση", command=self.destroy, bg="#95A5A6", fg="white", font=("Arial", 9, "bold"), padx=25, pady=10, relief="flat")
        btn_cancel.pack(side="right")

    def save(self): 
        self.destroy()

    def _row(self, label_text, initial_value):
        row_frame = tk.Frame(self.cnt, bg="white")
        row_frame.pack(fill="x", pady=10)
        tk.Label(row_frame, text=label_text.upper(), bg="white", fg="#95A5A6", width=20, anchor="w", font=("Arial", 8, "bold")).pack(side="left")
        
        entry_field = tk.Entry(row_frame, font=("Arial", 10), relief="flat", highlightthickness=1, highlightbackground="#E5E9F0", highlightcolor=self.caller.COLOR_ACCENT)
        entry_field.insert(0, initial_value)
        entry_field.pack(side="left", fill="x", expand=True)
        return entry_field

class HolidaysDialog(SettingsDialogBase):
    def __init__(self, parent: tk.Widget, caller: BaseView) -> None:
        super().__init__(parent, caller, "Διαχείριση Αργιών", 450, 520)
        
        tk.Label(self.cnt, text="ΕΠΙΛΕΞΤΕ ΗΜΕΡΕΣ ΠΟΥ Η ΕΠΙΧΕΙΡΗΣΗ ΘΑ ΠΑΡΑΜΕΙΝΕΙ ΚΛΕΙΣΤΗ", 
                 bg="white", font=("Arial", 8, "bold"), fg=self.caller.COLOR_MUTED, wraplength=380, justify="left").pack(anchor="w", pady=(0,15))
        
        list_frame = tk.Frame(self.cnt, bg="white")
        list_frame.pack(fill="both", expand=True)
        
        self.listbox_holidays = tk.Listbox(list_frame, height=8, font=("Arial", 10), 
                                         highlightthickness=1, highlightbackground="#E5E9F0", 
                                         selectbackground=self.caller.COLOR_ACCENT)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox_holidays.yview)
        self.listbox_holidays.configure(yscrollcommand=scrollbar.set)
        
        self.listbox_holidays.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        existing_dates = caller.settings.get("blackout_dates", "").split(",")
        for date_str in sorted([x.strip() for x in existing_dates if x.strip()]):
            self.listbox_holidays.insert("end", date_str)
        
        input_f = tk.Frame(self.cnt, bg="#F8F9FA", padx=15, pady=15, highlightthickness=1, highlightbackground="#E5E9F0")
        input_f.pack(fill="x", pady=(15, 0))
        
        tk.Label(input_f, text="ΝΕΑ ΑΡΓΙΑ:", bg="#F8F9FA", font=("Arial", 7, "bold"), fg=self.caller.COLOR_MUTED).grid(row=0, column=0, sticky="w", padx=5)
        
        self.date_picker = DateEntry(
            input_f, 
            width=12, 
            date_pattern="dd/mm/yyyy", 
            background=self.caller.COLOR_SIDEBAR, 
            foreground="white",
            headersbackground=self.caller.COLOR_WHITE,
            headersforeground=self.caller.COLOR_SIDEBAR,
            selectbackground=self.caller.COLOR_ACCENT,
            selectforeground="white",
            bordercolor=self.caller.COLOR_BORDER,
            normalbackground=self.caller.COLOR_WHITE,
            normalforeground="#2D3436",
            weekendbackground="#F8F9FA",
            weekendforeground=self.caller.COLOR_SIDEBAR
        )
        self.date_picker.grid(row=1, column=0, padx=5, pady=5)
        
        btn_add = tk.Button(input_f, text="+ ΠΡΟΣΘΗΚΗ", command=self._add_holiday)
        self.caller._style_button(btn_add, self.caller.COLOR_ACCENT, self.caller.COLOR_HOVER)
        btn_add.grid(row=1, column=1, padx=5)
        
        btn_rem = tk.Button(input_f, text="- ΑΦΑΙΡΕΣΗ", command=self._remove_holiday)
        self.caller._style_button(btn_rem, self.caller.COLOR_RED, "#cc3f46")
        btn_rem.grid(row=1, column=2, padx=5)

    def _add_holiday(self) -> None:
        try:
            date_obj = self.date_picker.get_date()
            date_iso_str = date_obj.isoformat()
            current_items = self.listbox_holidays.get(0, "end")
            if date_iso_str not in current_items:
                self.listbox_holidays.insert("end", date_iso_str)
            else:
                messagebox.showwarning("Προσοχή", "Η ημερομηνία υπάρχει ήδη στη λίστα.")
        except Exception as error:
            messagebox.showerror("Σφάλμα", f"Μη έγκυρη ημερομηνία: {error}")

    def _remove_holiday(self) -> None:
        selection = self.listbox_holidays.curselection()
        if selection:
            self.listbox_holidays.delete(selection)
        else:
            messagebox.showinfo("Πληροφορία", "Παρακαλώ επιλέξτε μια ημερομηνία από τη λίστα για αφαίρεση.")

    def save(self) -> None:
        all_dates = self.listbox_holidays.get(0, "end")
        self.caller.settings["blackout_dates"] = ",".join(all_dates)
        self.destroy()


class ExceptionsDialog(SettingsDialogBase):
    def __init__(self, parent: tk.Widget, caller: BaseView) -> None:
        super().__init__(parent, caller, "Έκτακτο Ωράριο", 580, 580)
        
        tk.Label(self.cnt, text="ΟΡΙΣΤΕ ΔΙΑΦΟΡΕΤΙΚΟ ΩΡΑΡΙΟ ΓΙΑ ΣΥΓΚΕΚΡΙΜΕΝΕΣ ΗΜΕΡΟΜΗΝΙΕΣ", 
                 bg="white", font=("Arial", 8, "bold"), fg=self.caller.COLOR_MUTED).pack(anchor="w", pady=(0,15))
        
        list_frame = tk.Frame(self.cnt, bg="white")
        list_frame.pack(fill="both", expand=True)
        
        self.listbox_exceptions = tk.Listbox(list_frame, height=6, font=("Arial", 10), 
                                           highlightthickness=1, highlightbackground="#E5E9F0",
                                           selectbackground=self.caller.COLOR_ACCENT)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox_exceptions.yview)
        self.listbox_exceptions.configure(yscrollcommand=scrollbar.set)
        
        self.listbox_exceptions.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.temporary_settings_buffer = caller.temporary_settings_buffer.copy()
        self.refresh_list()
        
        input_panel = tk.Frame(self.cnt, bg="#F8F9FA", padx=20, pady=20, highlightthickness=1, highlightbackground="#E5E9F0")
        input_panel.pack(fill="x", pady=(20, 0))
        
        tk.Label(input_panel, text="ΗΜΕΡΟΜΗΝΙΑ:", bg="#F8F9FA", font=("Arial", 7, "bold"), fg=self.caller.COLOR_MUTED).grid(row=0, column=0, sticky="w", padx=5)
        self.date_entry = DateEntry(
            input_panel, 
            width=12, 
            date_pattern="dd/mm/yyyy",
            background=self.caller.COLOR_SIDEBAR, 
            foreground="white",
            headersbackground=self.caller.COLOR_WHITE,
            headersforeground=self.caller.COLOR_SIDEBAR,
            selectbackground=self.caller.COLOR_ACCENT,
            selectforeground="white",
            bordercolor=self.caller.COLOR_BORDER,
            normalbackground=self.caller.COLOR_WHITE,
            normalforeground="#2D3436",
            weekendbackground="#F8F9FA",
            weekendforeground=self.caller.COLOR_SIDEBAR
        )
        self.date_entry.grid(row=1, column=0, padx=5, pady=5)
        
        tk.Label(input_panel, text="ΚΑΤΑΣΤΑΣΗ:", bg="#F8F9FA", font=("Arial", 7, "bold"), fg=self.caller.COLOR_MUTED).grid(row=0, column=1, sticky="w", padx=5)
        self.combo_type = ttk.Combobox(input_panel, values=["Κλειστό", "Προσαρμοσμένο"], width=15, state="readonly")
        self.combo_type.set("Κλειστό")
        self.combo_type.bind("<<ComboboxSelected>>", self._toggle_time_fields)
        self.combo_type.grid(row=1, column=1, padx=5, pady=5)
        
        self.time_f = tk.Frame(input_panel, bg="#F8F9FA")
        self.time_f.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        tk.Label(self.time_f, text="ΑΠΟ:", bg="#F8F9FA", font=("Arial", 7, "bold"), fg=self.caller.COLOR_MUTED).pack(side="left", padx=5)
        self.ent_start = tk.Entry(self.time_f, width=7, justify="center")
        self.ent_start.insert(0, "09:00")
        self.ent_start.pack(side="left", padx=5)
        
        tk.Label(self.time_f, text="ΕΩΣ:", bg="#F8F9FA", font=("Arial", 7, "bold"), fg=self.caller.COLOR_MUTED).pack(side="left", padx=5)
        self.ent_end = tk.Entry(self.time_f, width=7, justify="center")
        self.ent_end.insert(0, "17:00")
        self.ent_end.pack(side="left", padx=5)
        
        self.time_f.grid_remove()
        
        btn_add = tk.Button(input_panel, text="ΠΡΟΣΘΗΚΗ", command=self.add_exception)
        self.caller._style_button(btn_add, self.caller.COLOR_ACCENT, self.caller.COLOR_HOVER)
        btn_add.grid(row=1, column=2, padx=10)
        
        btn_rem = tk.Button(input_panel, text="ΑΦΑΙΡΕΣΗ", command=self._remove_exception)
        self.caller._style_button(btn_rem, self.caller.COLOR_RED, "#cc3f46")
        btn_rem.grid(row=2, column=2, padx=10)

    def _toggle_time_fields(self, event: Any = None) -> None:
        if self.combo_type.get() == "Προσαρμοσμένο":
            self.time_f.grid()
        else:
            self.time_f.grid_remove()

    def refresh_list(self) -> None:
        self.listbox_exceptions.delete(0, "end")
        for date_key in sorted(self.temporary_settings_buffer.keys()):
            single_entry = self.temporary_settings_buffer[date_key]
            if single_entry.get("closed"):
                status_text = "ΚΛΕΙΣΤΟ"
            else:
                status_text = f"{single_entry.get('s1_s')} - {single_entry.get('s1_e')}"
            self.listbox_exceptions.insert("end", f"{date_key}: {status_text}")

    def add_exception(self) -> None:
        try:
            date_obj = self.date_entry.get_date()
            target_date = date_obj.isoformat()
            if self.combo_type.get() == "Κλειστό":
                self.temporary_settings_buffer[target_date] = {"closed": True}
            else:
                start_time = self.ent_start.get()
                end_time = self.ent_end.get()
                if not start_time or not end_time:
                    messagebox.showwarning("Προσοχή", "Παρακαλώ συμπληρώστε τις ώρες.")
                    return
                self.temporary_settings_buffer[target_date] = {
                    "closed": False, 
                    "s1_s": start_time, 
                    "s1_e": end_time
                }
            self.refresh_list()
        except Exception as error:
            messagebox.showerror("Σφάλμα", f"Μη έγκυρη ημερομηνία: {error}")

    def _remove_exception(self) -> None:
        selection = self.listbox_exceptions.curselection()
        if selection:
            text = self.listbox_exceptions.get(selection)
            date_key = text.split(":")[0]
            if date_key in self.temporary_settings_buffer:
                del self.temporary_settings_buffer[date_key]
            self.refresh_list()
        else:
            messagebox.showinfo("Πληροφορία", "Επιλέξτε μια εξαίρεση για διαγραφή.")

    def save(self) -> None:
        self.caller.temporary_settings_buffer = self.temporary_settings_buffer
        self.destroy()
