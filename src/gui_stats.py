"""
=============================================================================
ΑΡΧΕΙΟ: gui_stats.py
ΣΚΟΠΟΣ: Εμφάνιση στατιστικών γραφημάτων (matplotlib ενσωματωμένο σε tkinter)
=============================================================================
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, List, Dict, Tuple, Callable, Optional
import datetime
import calendar
import json
from tkcalendar import DateEntry

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import database
import export_data

# --- GUI CONSTANTS (Aegean Theme) ---
COLOR_BG      = "#F7F9FC"
COLOR_SIDEBAR = "#0A3D62"
COLOR_ACCENT  = "#1E90FF"
COLOR_WHITE   = "#FFFFFF"
COLOR_TEXT    = "#1B1F23"
COLOR_BORDER  = "#E5E9F0"
COLOR_GREEN   = "#167C52"
COLOR_ORANGE  = "#F39C12"
COLOR_GRAY    = "#636E72"
FONT_TITLE    = ("Arial", 18, "bold")
# ------------------------------------


class StatsPanel(tk.Frame):
    """
    Κλάση που δημιουργεί ένα Frame με στατιστικά γραφήματα.
    Ενσωματώνεται στο κεντρικό content_frame του MainWindow.
    """

    def __init__(self, parent: tk.Widget, user_profile: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(parent)
        self.configure(bg=COLOR_BG)  # Συγχρονισμός με το background του dashboard
        self.pack(fill="both", expand=True)  # Απαραίτητο: τοποθετεί το Frame στο content_frame

        # =====================================
        # HEADER
        # =====================================
        header_frame = tk.Frame(self, bg=COLOR_BG)
        header_frame.pack(side="top", fill="x", padx=20, pady=(20, 10))

        tk.Label(
            header_frame,
            text="Στατιστικά & Αναφορές",
            font=("Arial", 18, "bold"),
            bg=COLOR_BG,
            fg=COLOR_SIDEBAR,
        ).pack(side="left")

        # =====================================
        # TOP BUTTONS (NAV)
        # =====================================
        nav_frame = tk.Frame(self, bg=COLOR_BG)
        nav_frame.pack(side="top", fill="x", padx=20, pady=10)

        style = ttk.Style()
        style.configure("Stats.TButton", font=("Arial", 10))

        self.btn_daily = ttk.Button(
            nav_frame, text="Ανά Ημέρα", command=self._show_daily, style="Stats.TButton"
        )
        self.btn_daily.pack(side="left", padx=5)

        self.btn_monthly = ttk.Button(
            nav_frame, text="Ανά Μήνα", command=self._show_monthly, style="Stats.TButton"
        )
        self.btn_monthly.pack(side="left", padx=5)

        self.btn_customer = ttk.Button(
            nav_frame, text="Top 10 Πελάτες", command=self._show_by_customer, style="Stats.TButton"
        )
        self.btn_customer.pack(side="left", padx=5)

        self.btn_employee = ttk.Button(
            nav_frame, text="Απόδοση Υπαλλήλων", command=self._show_by_employee, style="Stats.TButton"
        )
        self.btn_employee.pack(side="left", padx=5)


        self.btn_export = ttk.Button(
            nav_frame, text="Εξαγωγή", command=self._show_export_menu, style="Stats.TButton"
        )
        self.btn_export.pack(side="right", padx=5)

        # =====================================
        # CHART CONTAINER
        # =====================================
        # Χρησιμοποιούμε ένα λευκό frame για το γράφημα ώστε να μοιάζει με κάρτα
        self.container = tk.Frame(
            self,
            bg=COLOR_WHITE,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            padx=10,
            pady=10,
        )
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Frame για τα διαδραστικά φίλτρα/widgets
        self.controls_frame = tk.Frame(self.container, bg=COLOR_WHITE)
        self.controls_frame.pack(side="top", fill="x", pady=(0, 10))

        self.canvas = None
        self.current_data = []
        self.current_report_type = ""
        self.current_date_str = ""
        self.current_month_str = ""

        # Προεπιλεγμένο γράφημα κατά την εκκίνηση
        self.after(100, self._show_daily)

    def _clear_controls(self) -> None:
        # Καθαρισμός των widgets φίλτρων από το controls_frame
        for widget in self.controls_frame.winfo_children():
            widget.destroy()

    def _range_times_local(self, start_str: str, end_str: str, step_min: int) -> List[str]:
        # Παραγωγή λίστας με slots ωραρίων
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

    def _draw_chart(self, fig: Figure) -> None:
        """Καθαρίζει το προηγούμενο γράφημα και σχεδιάζει το νέο στο canvas."""
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self.container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _show_daily(self) -> None:
        # Καθαρισμός φίλτρων και δημιουργία DateEntry
        self._clear_controls()

        lbl_date = tk.Label(
            self.controls_frame,
            text="Επιλογή Ημερομηνίας:",
            bg=COLOR_WHITE,
            fg=COLOR_TEXT,
            font=("Arial", 10, "bold")
        )
        lbl_date.pack(side="left", padx=(10, 5))

        self.date_picker = DateEntry(
            self.controls_frame,
            width=12,
            date_pattern="dd/mm/yyyy",
            font=("Arial", 10)
        )
        self.date_picker.pack(side="left", padx=5)
        self.date_picker.bind("<<DateEntrySelected>>", lambda e: self._update_daily_chart())

        # Αρχική εμφάνιση γραφήματος
        self._update_daily_chart()

    def _update_daily_chart(self) -> None:
        # Λήψη επιλεγμένης ημερομηνίας
        selected_date = self.date_picker.get_date()
        date_str_dmy = selected_date.strftime("%d/%m/%Y")
        self.current_date_str = date_str_dmy

        # Ανάκτηση ρυθμίσεων ωραρίου
        try:
            settings = database.get_business_settings()
            weekly_schedule = json.loads(settings.get("weekly_schedule", "{}"))
            slot_duration = int(settings.get("slot_duration", 30))
        except Exception:
            weekly_schedule = {}
            slot_duration = 30

        # Εύρεση ημέρας της εβδομάδας
        weekday_key = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][selected_date.weekday()]
        day_info = weekly_schedule.get(weekday_key, {})

        # Έλεγχος αν η επιχείρηση είναι κλειστή
        if day_info.get("closed") or (not day_info.get("s1_s") and not day_info.get("s2_s")):
            self._show_message(f"Η επιχείρηση είναι κλειστή την ημέρα αυτή ({date_str_dmy})")
            self._save_current_data([], "daily")
            return

        # Παραγωγή slots
        slots = []
        s1_s, s1_e = day_info.get("s1_s"), day_info.get("s1_e")
        if s1_s and s1_e:
            slots.extend(self._range_times_local(s1_s, s1_e, slot_duration))
        s2_s, s2_e = day_info.get("s2_s"), day_info.get("s2_e")
        if s2_s and s2_e:
            slots.extend(self._range_times_local(s2_s, s2_e, slot_duration))

        if not slots:
            self._show_message(f"Δεν υπάρχουν ορισμένα ωράρια για αυτή την ημέρα ({date_str_dmy})")
            self._save_current_data([], "daily")
            return

        # Ανάκτηση ραντεβού
        appointments = database.get_day_appointments(date_str_dmy)

        # Καταμέτρηση ανά slot
        counts = []
        for slot in slots:
            count = sum(1 for appt in appointments if appt.get("start_time") == slot)
            counts.append(count)

        # Σχεδίαση Bar Chart
        fig = Figure(figsize=(8, 5), dpi=100, facecolor="white")
        ax = fig.add_subplot(111)

        ax.bar(slots, counts, color="#1E90FF", edgecolor="#0A3D62", alpha=0.7)
        ax.set_title(f"Ωριαία Κατανομή Ραντεβού — {date_str_dmy}", fontsize=12, pad=15)
        ax.set_ylabel("Πλήθος Ραντεβού")
        ax.grid(axis="y", linestyle="--", alpha=0.3)

        # Αραίωση ετικετών Χ (ανά 2 slots)
        indices = list(range(0, len(slots), 2))
        if (len(slots) - 1) not in indices:
            indices.append(len(slots) - 1)
        ax.set_xticks(indices)
        ax.set_xticklabels([slots[i] for i in indices], rotation=30, ha="right")

        fig.tight_layout()
        self._draw_chart(fig)

        # Αποθήκευση για εξαγωγή
        export_records = [{"date": slot, "count": count} for slot, count in zip(slots, counts)]
        self._save_current_data(export_records, "daily")

    def _show_monthly(self) -> None:
        # Καθαρισμός φίλτρων και δημιουργία Combobox
        self._clear_controls()

        lbl_month = tk.Label(
            self.controls_frame,
            text="Επιλογή Μήνα:",
            bg=COLOR_WHITE,
            fg=COLOR_TEXT,
            font=("Arial", 10, "bold")
        )
        lbl_month.pack(side="left", padx=(10, 5))

        # Ανάκτηση μηνών με κρατήσεις
        chart_records = database.get_appointment_count_by_month()
        months_list = [row["month"] for row in chart_records]

        # Fallback στον τρέχοντα μήνα
        current_month_str = datetime.date.today().strftime("%m/%Y")
        if current_month_str not in months_list:
            months_list.append(current_month_str)

        self.month_picker = ttk.Combobox(
            self.controls_frame,
            values=months_list,
            state="readonly",
            font=("Arial", 10)
        )
        self.month_picker.pack(side="left", padx=5)

        if current_month_str in months_list:
            self.month_picker.set(current_month_str)
        else:
            self.month_picker.current(len(months_list) - 1)

        self.month_picker.bind("<<ComboboxSelected>>", lambda e: self._update_monthly_chart())

        # Αρχική εμφάνιση γραφήματος
        self._update_monthly_chart()

    def _update_monthly_chart(self) -> None:
        # Λήψη επιλεγμένου μήνα
        selected_month = self.month_picker.get()
        self.current_month_str = selected_month

        month_str, year_str = selected_month.split("/")
        m = int(month_str)
        y = int(year_str)

        # Δημιουργία χρονολογίου για όλο το μήνα
        _, num_days = calendar.monthrange(y, m)
        labels = []
        values = []

        # Λήψη δεδομένων
        chart_records = database.get_appointment_count_by_date()
        records_dict = {row["date"]: row["count"] for row in chart_records}

        for day in range(1, num_days + 1):
            iso_date = f"{y:04d}-{m:02d}-{day:02d}"
            labels.append(f"{day:02d}/{m:02d}")
            values.append(records_dict.get(iso_date, 0))

        # Σχεδίαση Wave/Area Chart
        fig = Figure(figsize=(8, 5), dpi=100, facecolor="white")
        ax = fig.add_subplot(111)

        ax.plot(labels, values, color="#1E90FF", linewidth=2)
        ax.fill_between(labels, values, color="#1E90FF", alpha=0.15)

        ax.set_title(f"Τάση Ραντεβού — {selected_month}", fontsize=12, pad=15)
        ax.set_ylabel("Πλήθος Ραντεβού")
        ax.grid(True, linestyle=":", alpha=0.6)

        # Αραίωση ετικετών Χ (ανά 5 ημέρες)
        indices = list(range(0, len(labels), 5))
        if (len(labels) - 1) not in indices:
            indices.append(len(labels) - 1)
        ax.set_xticks(indices)
        ax.set_xticklabels([labels[i] for i in indices], rotation=30, ha="right")

        fig.tight_layout()
        self._draw_chart(fig)

        # Αποθήκευση για εξαγωγή
        export_records = [{"day": label, "count": count} for label, count in zip(labels, values)]
        self._save_current_data(export_records, "monthly")

    def _show_by_customer(self) -> None:
        self._clear_controls()
        # Εμφανίζει οριζόντιο bar chart με τους Top 10 πελάτες με βάση το πλήθος των ραντεβού τους.
        chart_records = database.get_appointment_count_by_customer()

        self._save_current_data(chart_records, "customer")
        # Τα δεδομένα έρχονται ταξινομημένα φθίνουσα, τα αντιστρέφουμε για το barh
        labels = [row["name"] for row in chart_records[:10]][::-1]
        values = [row["count"] for row in chart_records[:10]][::-1]

        fig = Figure(figsize=(8, 5), dpi=100, facecolor="white")
        ax = fig.add_subplot(111)

        ax.barh(labels, values, color="#F39C12", alpha=0.8)
        ax.set_title("Top 10 Πελάτες (Συνολικά Ραντεβού)", fontsize=12, pad=15)
        ax.set_xlabel("Αριθμός Ραντεβού")

        fig.tight_layout()
        self._draw_chart(fig)

    def _show_by_employee(self) -> None:
        self._clear_controls()
        # Εμφανίζει οριζόντιο bar chart με την απόδοση των υπαλλήλων βάσει των συνολικών ραντεβού τους.
        chart_records = database.get_appointment_count_by_employee()

        self._save_current_data(chart_records, "employee")
        # Τα δεδομένα έρχονται ταξινομημένα φθίνουσα, τα αντιστρέφουμε για το barh
        labels = [row["name"] for row in chart_records][::-1]
        values = [row["count"] for row in chart_records][::-1]

        fig = Figure(figsize=(8, 5), dpi=100, facecolor="white")
        ax = fig.add_subplot(111)

        ax.barh(labels, values, color="#1E90FF", alpha=0.8)
        ax.set_title("Απόδοση Υπαλλήλων (Συνολικά Ραντεβού)", fontsize=12, pad=15)
        ax.set_xlabel("Αριθμός Ραντεβού")

        fig.tight_layout()
        self._draw_chart(fig)

    def _show_message(self, message: str) -> None:
        """Εμφανίζει ένα μήνυμα κειμένου αντί για γράφημα."""
        fig = Figure(figsize=(8, 5), dpi=100, facecolor="white")
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=12, color="#636E72")
        ax.set_axis_off()
        self._draw_chart(fig)

    # =====================================
    # EXPORT LOGIC
    # =====================================
    def _show_export_menu(self) -> None:
        """Εμφανίζει μενού επιλογών για την εξαγωγή των στατιστικών."""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Εξαγωγή σε Excel (.xlsx)", command=lambda: self._perform_export("xlsx"))
        menu.add_command(label="Εξαγωγή σε CSV (.csv)", command=lambda: self._perform_export("csv"))
        menu.add_command(label="Εξαγωγή σε PDF (.pdf)", command=lambda: self._perform_export("pdf"))
        menu.post(self.winfo_pointerx(), self.winfo_pointery())

    def _perform_export(self, export_format: str) -> None:
        """Εξάγει τα τρέχοντα στατιστικά δεδομένα."""
        if not self.current_data:
            messagebox.showwarning("Προσοχή", "Δεν υπάρχουν δεδομένα για εξαγωγή.")
            return

        # Προετοιμασία δεδομένων για την export_data.py
        export_list = []
        
        if self.current_report_type == "daily":
            headers = {"col1": "Ώρα", "col2": "Πλήθος Ραντεβού"}
            title = f"Ωριαία Κατανομή Ραντεβού — {self.current_date_str}"
            filename = f"stats_daily_{self.current_date_str.replace('/', '_')}"
        elif self.current_report_type == "monthly":
            headers = {"col1": "Ημερομηνία", "col2": "Πλήθος Ραντεβού"}
            title = f"Στατιστικά Ραντεβού — {self.current_month_str}"
            filename = f"stats_monthly_{self.current_month_str.replace('/', '_')}"
        elif self.current_report_type == "customer":
            headers = {"col1": "Πελάτης", "col2": "Συνολικά Ραντεβού"}
            title = "Στατιστικά: Top 10 Πελάτες"
            filename = "stats_top_customers"
        else: # employee
            headers = {"col1": "Υπάλληλος", "col2": "Συνολικά Ραντεβού"}
            title = "Στατιστικά: Απόδοση Υπαλλήλων"
            filename = "stats_employee_performance"

        for data_row in self.current_data:
            if self.current_report_type == "daily":
                export_list.append({"col1": data_row["date"], "col2": data_row["count"]})
            elif self.current_report_type == "monthly":
                export_list.append({"col1": data_row["day"], "col2": data_row["count"]})
            else: # customer or employee
                export_list.append({"col1": data_row["name"], "col2": data_row["count"]})

        if export_format == "csv":
            export_data.export_to_csv(export_list, headers, filename)
        elif export_format == "xlsx":
            export_data.export_to_xlsx(export_list, headers, filename, "Στατιστικά")
        elif export_format == "pdf":
            export_data.export_to_pdf(export_list, headers, filename, title)

    def _save_current_data(self, chart_records: List[Dict[str, Any]], report_type: str) -> None:
        self.current_data = chart_records
        self.current_report_type = report_type
