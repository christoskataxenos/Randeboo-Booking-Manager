"""
Ο κώδικας του αρχείου συντάχθηκε από τον Βαρθαλίτη Πάνο

=============================================================================
ΑΡΧΕΙΟ: export_data.py
ΣΚΟΠΟΣ: εξαγωγη αποτελεσματων αναζητησης σε excel (.xlsx), csv η pdf
=============================================================================
"""

import os
from tkinter import filedialog, messagebox
from typing import List, Dict, Any, Union, Optional


# -------------------------------------------------------------------
# ΕΞΑΓΩΓΗ ΣΕ EXCEL (.xlsx)
# χρησιμοποιει xlsxwriter για να φτιαξει ενα excel αρχειο με τα δεδομενα

def export_to_xlsx(
    records_list: List[Dict[str, Any]],
    headers_or_filepath: Optional[Union[str, Dict[str, str], List[str]]] = None,
    filepath: Optional[str] = None,
    sheet_name: str = "Ραντεβού"
) -> None:
    # φορτωνουμε τη βιβλιοθηκη τοπικα
    import xlsxwriter

    # ελεγχος αν υπαρχουν δεδομενα
    if not records_list:
        messagebox.showwarning("Εξαγωγη", "Δεν υπαρχουν δεδομενα για εξαγωγη!")
        return

    # διαχωρισμος των παραμετρων για backward compatibility
    headers = None
    filepath_to_use = None

    if isinstance(headers_or_filepath, str):
        # αν το δευτερο ορισμα ειναι string, τοτε ειναι το filepath
        filepath_to_use = headers_or_filepath
    else:
        # αλλιως το δευτερο ορισμα ειναι τα headers και το τριτο το filepath
        headers = headers_or_filepath
        filepath_to_use = filepath

    # αν δεν υπαρχει φακελος στη διαδρομη, ανοιγουμε save as dialog
    if not filepath_to_use or not os.path.dirname(filepath_to_use):
        initial_name = filepath_to_use or "export"
        if not initial_name.lower().endswith(".xlsx"):
            initial_name += ".xlsx"

        filepath_to_use = filedialog.asksaveasfilename(
            title="Αποθηκευση αρχειου Excel",
            initialfile=initial_name,
            defaultextension=".xlsx",
            filetypes=[("Excel αρχειο (*.xlsx)", "*.xlsx")]
        )
        # αν ο χρηστης πατησει ακυρωση
        if not filepath_to_use:
            return

    try:
        # προσδιορισμος των στηλων και των κλειδιων των δεδομενων
        if isinstance(headers, dict):
            keys = list(headers.keys())
            header_labels = list(headers.values())
        elif isinstance(headers, list):
            keys = headers
            header_labels = headers
        else:
            header_labels = ["Ημερομηνια", "Ωρα", "Πελατης", "Τηλεφωνο", "Email", "Υπαλληλος", "Σημειωσεις"]
            keys = ["appt_date", "start_time", "customer_name", "phone", "email", "employee_name", "notes"]

        workbook = xlsxwriter.Workbook(filepath_to_use)
        worksheet = workbook.add_worksheet(sheet_name)

        # στυλ για τα headers (πρωτη γραμμη — σκουρο μπλε, ασπρα γραμματα)
        header_format = workbook.add_format({
            "bold": True,
            "bg_color": "#0A3D62",
            "font_color": "#FFFFFF",
            "border": 1,
            "font_size": 11
        })

        # στυλ για τα κελια δεδομενων
        cell_format = workbook.add_format({
            "border": 1,
            "font_size": 10
        })

        # γραψιμο headers στην πρωτη γραμμη
        for col, header_text in enumerate(header_labels):
            worksheet.write(0, col, header_text, header_format)

        # γραψιμο δεδομενων σειρα-σειρα
        for row_num, row_data in enumerate(records_list, start=1):
            for col_num, key in enumerate(keys):
                value = row_data.get(key, "")
                worksheet.write(row_num, col_num, value or "", cell_format)

        # δυναμικο πλατος στηλων για να φαινονται σωστα τα δεδομενα
        for col_idx, key in enumerate(keys):
            max_len = len(str(header_labels[col_idx]))
            for row_data in records_list:
                val_str = str(row_data.get(key, "") or "")
                if len(val_str) > max_len:
                    max_len = len(val_str)
            col_width = min(max(max_len + 3, 10), 50)
            worksheet.set_column(col_idx, col_idx, col_width)

        workbook.close()
        messagebox.showinfo("Εξαγωγη", f"Το αρχειο αποθηκευτηκε!\n{filepath_to_use}")

    except PermissionError:
        messagebox.showerror("Σφαλμα", "Το αρχειο ειναι ανοιχτο η δεν εχεις δικαιωμα εγγραφης.\nΚλεισε το αρχειο και δοκιμασε ξανα.")
    except Exception as error_msg:
        messagebox.showerror("Σφαλμα", f"Κατι πηγε στραβα:\n{error_msg}")


# -------------------------------------------------------------------
# ΕΞΑΓΩΓΗ ΣΕ CSV
# χρησιμοποιει το ενσωματωμενο csv module

def export_to_csv(
    records_list: List[Dict[str, Any]],
    headers_or_filepath: Optional[Union[str, Dict[str, str], List[str]]] = None,
    filepath: Optional[str] = None
) -> None:
    # ελεγχος αν υπαρχουν δεδομενα
    if not records_list:
        messagebox.showwarning("Εξαγωγη", "Δεν υπαρχουν δεδομενα για εξαγωγη!")
        return

    # διαχωρισμος των παραμετρων για backward compatibility
    headers = None
    filepath_to_use = None

    if isinstance(headers_or_filepath, str):
        # αν το δευτερο ορισμα ειναι string, τοτε ειναι το filepath
        filepath_to_use = headers_or_filepath
    else:
        # αλλιως το δευτερο ορισμα ειναι τα headers και το τριτο το filepath
        headers = headers_or_filepath
        filepath_to_use = filepath

    # αν δεν υπαρχει φακελος στη διαδρομη, ανοιγουμε save as dialog
    if not filepath_to_use or not os.path.dirname(filepath_to_use):
        initial_name = filepath_to_use or "export"
        if not initial_name.lower().endswith(".csv"):
            initial_name += ".csv"

        filepath_to_use = filedialog.asksaveasfilename(
            title="Αποθηκευση αρχειου CSV",
            initialfile=initial_name,
            defaultextension=".csv",
            filetypes=[("CSV αρχειο (*.csv)", "*.csv")]
        )
        # αν ο χρηστης πατησει ακυρωση
        if not filepath_to_use:
            return

    try:
        # προσδιορισμος των στηλων και των κλειδιων των δεδομενων
        if isinstance(headers, dict):
            keys = list(headers.keys())
            header_labels = list(headers.values())
        elif isinstance(headers, list):
            keys = headers
            header_labels = headers
        else:
            header_labels = ["Ημερομηνια", "Ωρα", "Πελατης", "Τηλεφωνο", "Email", "Υπαλληλος", "Σημειωσεις"]
            keys = ["appt_date", "start_time", "customer_name", "phone", "email", "employee_name", "notes"]

        # Χρησιμοποιουμε utf-8-sig για να διαβαζει το Excel σωστα τα ελληνικα απευθειας
        with open(filepath_to_use, mode="w", newline="", encoding="utf-8-sig") as file:
            import csv
            writer = csv.writer(file, delimiter=",")
            
            # πρωτη γραμμη - επικεφαλιδες
            writer.writerow(header_labels)
            
            # ολες οι υπολοιπες γραμμες
            for row_data in records_list:
                row = [str(row_data.get(k, "") or "") for k in keys]
                writer.writerow(row)

        messagebox.showinfo("Εξαγωγη", f"Το αρχειο αποθηκευτηκε!\n{filepath_to_use}")

    except PermissionError:
        messagebox.showerror("Σφαλμα", "Το αρχειο ειναι ανοιχτο η δεν εχεις δικαιωμα εγγραφης.\nΚλεισε το αρχειο και δοκιμασε ξανα.")
    except Exception as error_msg:
        messagebox.showerror("Σφαλμα", f"Κατι πηγε στραβα:\n{error_msg}")


# -------------------------------------------------------------------
# ΕΞΑΓΩΓΗ ΣΕ PDF
# χρησιμοποιει reportlab — φτιαχνει πινακα σε landscape A4

def export_to_pdf(
    records_list: List[Dict[str, Any]],
    headers_or_filepath: Optional[Union[str, Dict[str, str], List[str]]] = None,
    filepath: Optional[str] = None,
    title: str = "RandeBoo — Αποτελεσματα"
) -> None:
    # ελεγχος αν υπαρχουν δεδομενα
    if not records_list:
        messagebox.showwarning("Εξαγωγη", "Δεν υπαρχουν δεδομενα για εξαγωγη!")
        return

    # διαχωρισμος των παραμετρων για backward compatibility
    headers = None
    filepath_to_use = None

    if isinstance(headers_or_filepath, str):
        # αν το δευτερο ορισμα ειναι string, τοτε ειναι το filepath
        filepath_to_use = headers_or_filepath
    else:
        # αλλιως το δευτερο ορισμα ειναι τα headers και το τριτο το filepath
        headers = headers_or_filepath
        filepath_to_use = filepath

    # αν δεν υπαρχει φακελος στη διαδρομη, ανοιγουμε save as dialog
    if not filepath_to_use or not os.path.dirname(filepath_to_use):
        initial_name = filepath_to_use or "export"
        if not initial_name.lower().endswith(".pdf"):
            initial_name += ".pdf"

        filepath_to_use = filedialog.asksaveasfilename(
            title="Αποθηκευση αρχειου PDF",
            initialfile=initial_name,
            defaultextension=".pdf",
            filetypes=[("PDF αρχειο (*.pdf)", "*.pdf")]
        )
        # αν ο χρηστης πατησει ακυρωση
        if not filepath_to_use:
            return

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # φορτωνουμε arial απο τα windows fonts — χρειαζεται για ελληνικα
        font_path = "C:/Windows/Fonts/arial.ttf"
        font_name = "Helvetica"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("ArialGR", font_path))
            font_name = "ArialGR"

        # landscape A4 για να χωρανε ολες οι στηλες
        doc = SimpleDocTemplate(filepath_to_use, pagesize=landscape(A4))
        elements = []

        # τιτλος πανω στη σελιδα
        title_style = ParagraphStyle(
            "ExportTitle",
            fontName=font_name,
            fontSize=16,
            leading=20,
            spaceAfter=12
        )
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.5 * cm))

        # προσδιορισμος των στηλων και των κλειδιων των δεδομενων
        if isinstance(headers, dict):
            keys = list(headers.keys())
            header_labels = list(headers.values())
        elif isinstance(headers, list):
            keys = headers
            header_labels = headers
        else:
            header_labels = ["Ημερομηνια", "Ωρα", "Πελατης", "Τηλεφωνο", "Υπαλληλος", "Σημειωσεις"]
            keys = ["appt_date", "start_time", "customer_name", "phone", "employee_name", "notes"]

        table_data = [header_labels]
        for row in records_list:
            table_row = [str(row.get(k, "") or "") for k in keys]
            table_data.append(table_row)

        # δημιουργια πινακα
        table = Table(table_data, repeatRows=1)

        # στυλ πινακα — σκουρο μπλε header, εναλλασσομενα χρωματα γραμμων
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0A3D62")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), font_name),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FC")]),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)
        doc.build(elements)

        messagebox.showinfo("Εξαγωγη", f"Το αρχειο αποθηκευτηκε!\n{filepath_to_use}")

    except PermissionError:
        messagebox.showerror("Σφαλμα", "Το αρχειο ειναι ανοιχτο η δεν εχεις δικαιωμα εγγραφης.\nΚλεισε το αρχειο και δοκιμασε ξανα.")
    except Exception as error_msg:
        messagebox.showerror("Σφαλμα", f"Κατι πηγε στραβα:\n{error_msg}")


# -------------------------------------------------------------------
# ΚΥΡΙΑ ΣΥΝΑΡΤΗΣΗ ΕΞΑΓΩΓΗΣ
# ανοιγει save as dialog — ο χρηστης διαλεγει αν θελει xlsx, csv η pdf
# και σε ποιον φακελο να αποθηκευτει

def export_results(records_list: List[Dict[str, Any]]) -> None:
    # ελεγχος αν εχουμε δεδομενα
    if not records_list:
        messagebox.showwarning("Εξαγωγη", "Δεν υπαρχουν δεδομενα για εξαγωγη!\nΚαντε πρωτα μια αναζητηση.")
        return

    # ανοιγουμε το windows save as dialog
    filepath = filedialog.asksaveasfilename(
        title="Αποθηκευση αρχειου",
        defaultextension=".xlsx",
        filetypes=[
            ("Excel αρχειο (*.xlsx)", "*.xlsx"),
            ("PDF αρχειο (*.pdf)", "*.pdf"),
            ("CSV αρχειο (*.csv)", "*.csv")
        ]
    )

    # αν ο χρηστης πατησε ακυρωση
    if not filepath:
        return

    # αναλογα με την καταληξη αρχειου, καλουμε τη σωστη συναρτηση
    if filepath.lower().endswith(".pdf"):
        export_to_pdf(records_list, filepath=filepath)
    elif filepath.lower().endswith(".csv"):
        export_to_csv(records_list, filepath=filepath)
    else:
        export_to_xlsx(records_list, filepath=filepath)