from fpdf import FPDF
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "test_invoices")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class SimpleInvoice(FPDF):
    def header(self):
        # Megkeressük a font fájlt a script mellett
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(script_dir, "arial.ttf") 
        font_path_bold = os.path.join(script_dir, "arialbd.ttf")

        # Megpróbáljuk betölteni a script mellől, ha nincs ott, akkor a Windowsból
        if os.path.exists(font_path):
            self.add_font("Arial", style="", fname=font_path)
            self.add_font("Arial", style="B", fname=font_path_bold)
        else:
            # Fallback a Windows rendszermappára
            self.add_font("Arial", style="", fname=r"C:\Windows\Fonts\arial.ttf")
            self.add_font("Arial", style="B", fname=r"C:\Windows\Fonts\arialbd.ttf")

def create_simple_invoice(filename, data):
    pdf = SimpleInvoice()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # --- 1. FEJLÉC SZEKCIÓ (Két oszlopos elrendezés) ---
    
    start_y = 20
    pdf.set_y(start_y)

    # --- BAL OSZLOP (Issued To & Pay To) ---
    pdf.set_x(10)
    
    # ISSUED TO
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 5, "ISSUED TO:", ln=True)
    
    pdf.set_font("Arial", "", 10)
    # Ha üres az adat, üreset írunk (Validációs hiba teszteléséhez)
    pdf.cell(100, 5, str(data.get("issued_to_name", "")), ln=True)
    pdf.cell(100, 5, str(data.get("issued_to_company", "")), ln=True)
    pdf.multi_cell(90, 5, str(data.get("issued_to_address", "")))
    
    pdf.ln(5)

    # PAY TO
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 5, "PAY TO:", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(100, 5, str(data.get("pay_to_bank", "")), ln=True)
    pdf.cell(100, 5, f"Account Name: {data.get('pay_to_acc_name', '')}", ln=True)
    pdf.cell(100, 5, f"Account No.: {data.get('pay_to_acc_no', '')}", ln=True)

    left_column_end_y = pdf.get_y()

    # --- JOBB OSZLOP (INVOICE felirat és dátumok) ---
    pdf.set_xy(120, start_y)
    
    pdf.set_font("Arial", "B", 24)
    pdf.cell(70, 10, "INVOICE", align="R", ln=True)
    
    pdf.set_font("Arial", "B", 10)
    
    def right_data_row(label, value):
        pdf.set_x(120)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(35, 6, label, align="L")
        pdf.set_font("Arial", "", 10)
        pdf.cell(35, 6, value, align="R", ln=True)

    pdf.ln(5)
    right_data_row("INVOICE NO:", data.get("invoice_no", ""))
    right_data_row("DATE:", data.get("date", ""))
    right_data_row("DUE DATE:", data.get("due_date", ""))

    # --- 2. TÁBLÁZAT ---
    
    table_start_y = max(left_column_end_y, pdf.get_y()) + 15
    pdf.set_y(table_start_y)

    cols = [90, 35, 25, 40]
    headers = ["DESCRIPTION", "UNIT PRICE", "QTY", "TOTAL"]

    # Fejléc
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(255, 255, 255)
    
    for i, h in enumerate(headers):
        align = "L" if i == 0 else "R"
        pdf.cell(cols[i], 8, h, border="B", align=align)
    pdf.ln(10)

    # Tételek
    pdf.set_font("Arial", "", 9)
    items = data.get("items", [])

    for item in items:
        x_start = pdf.get_x()
        y_start = pdf.get_y()

        pdf.multi_cell(cols[0], 6, str(item[0]), align="L")
        y_end = pdf.get_y()

        pdf.set_xy(x_start + cols[0], y_start)

        pdf.cell(cols[1], 6, str(item[1]), align="R")
        pdf.cell(cols[2], 6, str(item[2]), align="R")
        pdf.cell(cols[3], 6, str(item[3]), align="R")

        pdf.set_xy(10, y_end)
        pdf.ln(2)

    # --- 3. ÖSSZESÍTŐ (Totals) ---
    pdf.ln(5)
    
    x_totals = 135 
    
    def total_line(label, value, bold=False):
        pdf.set_x(x_totals)
        pdf.set_font("Arial", "B" if bold else "", 10)
        pdf.cell(25, 6, label, align="L")
        pdf.cell(30, 6, value, align="R", ln=True)

    total_line("SUBTOTAL", data.get("subtotal", ""))
    total_line("Tax", data.get("tax", ""))
    pdf.ln(2)
    
    pdf.set_font("Arial", "B", 12)
    pdf.set_x(x_totals)
    pdf.cell(25, 8, "TOTAL", align="L")
    pdf.cell(30, 8, data.get("total_amount", ""), align="R", ln=True)

    # --- 4. ALÁÍRÁS ---
    pdf.ln(15)
    pdf.set_x(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 5, str(data.get("signer_name", "")), ln=True)
    
    filepath = os.path.join(OUTPUT_DIR, filename)
    pdf.output(filepath)
    print(f"[OK] Simple Invoice Generálva: {filepath}")


# --- SZAKDOLGOZAT TESZT ESETEK (SAP Automation) ---

# 1. ESET: Belföldi (HUF, 27% ÁFA) - "Happy Path"
# Ez a standard eset, aminek csont nélkül át kell mennie a rendszeren.
thesis_simple_1 = {
    "issued_to_name": "Kovács Informatikai Kft.",
    "issued_to_company": "Beszerzési Osztály",
    "issued_to_address": "1117 Budapest, Irinyi József u. 42.",
    
    "pay_to_bank": "OTP Bank",
    "pay_to_acc_name": "Tech Solutions Zrt.",
    "pay_to_acc_no": "11700001-22223333",
    
    "invoice_no": "SIM-HU-2024-001",
    "date": "2024.11.25",
    "due_date": "2024.12.25",
    
    "items": [
        ["Rendszerkarbantartás - November", "100 000 Ft", "1", "100 000 Ft"],
        ["Szerver hosting díj", "50 000 Ft", "1", "50 000 Ft"]
    ],
    
    "subtotal": "150 000 Ft",
    "tax": "27% (40 500 Ft)",
    "total_amount": "190 500 Ft",
    "signer_name": "Szabó Péter ügyvezető"
}
create_simple_invoice("thesis_simple_01_valid_huf.pdf", thesis_simple_1)


# 2. ESET: Duplikáció teszt (Ugyanaz az Invoice NO, mint az 1-esnél!)
# Tartalom kicsit más, de a számlaszám ütközik. Az SAP-nak ezt el kell kapnia.
thesis_simple_2 = thesis_simple_1.copy()
thesis_simple_2["items"] = [["Extra kiszállás", "10 000 Ft", "1", "10 000 Ft"]]
thesis_simple_2["total_amount"] = "12 700 Ft"
# A SZÁMLASZÁM MARAD AZ EREDETI:
thesis_simple_2["invoice_no"] = "SIM-HU-2024-001" 
create_simple_invoice("thesis_simple_02_duplicate_error.pdf", thesis_simple_2)


# 3. ESET: Külföldi / Devizás (EUR, 0% ÁFA)
# Teszteli a deviza felismerést és a fordított adózást.
thesis_simple_3 = {
    "issued_to_name": "Global Tech GmbH",
    "issued_to_company": "Headquarters",
    "issued_to_address": "Munich, Industrial Park 4.",
    
    "pay_to_bank": "Deutsche Bank",
    "pay_to_acc_name": "Tech Sol. EU Branch",
    "pay_to_acc_no": "DE89 3704 0044 0532 0130 00",
    
    "invoice_no": "SIM-EU-2024-999",
    "date": "2024.12.01",
    "due_date": "2025.01.01",
    
    "items": [
        ["Software License Fee", "€ 500.00", "2", "€ 1000.00"],
        ["Remote Support", "€ 100.00", "5", "€ 500.00"]
    ],
    
    "subtotal": "€ 1500.00",
    "tax": "0% (Reverse Charge)",
    "total_amount": "€ 1500.00",
    "signer_name": "John Doe, Regional Manager"
}
create_simple_invoice("thesis_simple_03_foreign_eur.pdf", thesis_simple_3)


# 4. ESET: Hiányzó kötelező adat (Validation Error)
# Hiányzik a Vevő neve ("issued_to_name").
# Ezt a "Human in the Loop" folyamat tesztelésére használjuk (kézi javításra kell esnie).
thesis_simple_4 = {
    "issued_to_name": "", # <--- ÜRES MEZŐ HIBA!
    "issued_to_company": "Ismeretlen Kft.",
    "issued_to_address": "Budapest, Váci út 1.",
    
    "pay_to_bank": "K&H Bank",
    "pay_to_acc_name": "Tech Solutions Zrt.",
    "pay_to_acc_no": "10404040-00000000",
    
    "invoice_no": "SIM-ERR-MISSING",
    "date": "2024.10.10",
    "due_date": "2024.10.20",
    
    "items": [
        ["Teszt tétel", "1000 Ft", "1", "1000 Ft"]
    ],
    
    "subtotal": "1000 Ft",
    "tax": "270 Ft",
    "total_amount": "1270 Ft",
    "signer_name": "Automata Rendszer"
}
create_simple_invoice("thesis_simple_04_missing_data.pdf", thesis_simple_4)