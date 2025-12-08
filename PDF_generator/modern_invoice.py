from fpdf import FPDF
import os

# Mappa beállítása
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "test_invoices")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class BWInvoice(FPDF):
    def header(self):
        # Arial font betöltése
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(script_dir, "arial.ttf") 
        font_path_bold = os.path.join(script_dir, "arialbd.ttf")

        if os.path.exists(font_path):
            self.add_font("Arial", style="", fname=font_path)
            self.add_font("Arial", style="B", fname=font_path_bold)
        else:
            self.add_font("Arial", style="", fname=r"C:\Windows\Fonts\arial.ttf")
            self.add_font("Arial", style="B", fname=r"C:\Windows\Fonts\arialbd.ttf")

def create_bw_invoice(filename, data):
    pdf = BWInvoice()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_text_color(0, 0, 0) 

    # --- 1. FEJLÉC (HEADER) ---
    
    # BAL OLDAL: Cégadatok
    pdf.set_xy(10, 15)
    pdf.set_font("Arial", "B", 14)
    pdf.multi_cell(60, 6, data.get("sender_name", ""), align="L")
    
    pdf.set_font("Arial", "", 9)
    pdf.set_xy(10, 30)
    # A cím multi_cell, mert lehet hosszú
    pdf.multi_cell(60, 5, data.get("sender_address", ""), align="L")
    
    # --- JAVÍTÁS ITT ---
    # Kényszerítjük, hogy az X koordináta visszaálljon 10-re (a bal margóra)
    pdf.set_x(10) 
    pdf.cell(60, 5, data.get("sender_phone", ""), ln=True, align="L")
    # -------------------

    # JOBB OLDAL: INVOICE felirat és adatok
    pdf.set_xy(120, 15)
    pdf.set_font("Arial", "B", 24)
    pdf.cell(80, 10, "INVOICE", align="R", ln=True)
    
    pdf.set_x(120)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 6, "Invoice Number:", align="R")
    pdf.set_font("Arial", "", 10)
    pdf.cell(40, 6, data.get("invoice_no", ""), align="R", ln=True)
    
    pdf.set_x(120)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 6, "Date:", align="R")
    pdf.set_font("Arial", "", 10)
    pdf.cell(40, 6, data.get("date", ""), align="R", ln=True)
    
    pdf.set_x(120)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 6, "Due Date:", align="R")
    pdf.set_font("Arial", "", 10)
    pdf.cell(40, 6, data.get("due_date", ""), align="R", ln=True)

    # --- 2. ÜGYFÉL ÉS FIZETÉSI ADATOK ---
    
    # BILL TO
    pdf.set_xy(10, 55)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(80, 6, "BILL TO:", ln=True)
    
    pdf.set_font("Arial", "B", 11)
    pdf.cell(80, 6, data.get("bill_to_name", ""), ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(80, 5, data.get("bill_to_address", ""), ln=True)
    pdf.cell(80, 5, data.get("bill_to_phone", ""), ln=True)

    # PAYMENT METHOD
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(80, 6, "Payment Method", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(80, 5, data.get("bank_name", ""), ln=True)
    pdf.cell(80, 5, data.get("bank_account_name", ""), ln=True)
    # Itt is biztosítjuk a balra igazítást a biztonság kedvéért
    pdf.set_x(10)
    pdf.cell(80, 5, data.get("bank_account_no", ""), ln=True)

    # --- 3. TÁBLÁZAT ---
    
    table_y = 110
    pdf.set_y(table_y)
    
    col_widths = [15, 90, 30, 20, 35]
    headers = ["NO", "ITEM DESCRIPTION", "PRICE", "QTY", "TOTAL"]
    
    # Fejléc - FEKETE HÁTTÉR, FEHÉR BETŰK
    pdf.set_fill_color(0, 0, 0) 
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 9)
    
    for i, h in enumerate(headers):
        align = "L" if i == 1 else "C"
        pdf.cell(col_widths[i], 8, h, border=0, fill=True, align=align)
    pdf.ln()
    
    # Tételek
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 9)
    
    items = data.get("items", [])
    
    for item in items:
        pdf.set_font("Arial", "B", 10)
        x_start = pdf.get_x()
        y_start = pdf.get_y()
        
        # DESCRIPTION szétszedése
        desc_parts = item[1].split("\n", 1)
        desc_title = desc_parts[0]
        desc_body = desc_parts[1] if len(desc_parts) > 1 else ""
        
        pdf.set_xy(x_start + col_widths[0], y_start)
        
        pdf.set_font("Arial", "B", 9)
        pdf.cell(col_widths[1], 5, desc_title, ln=True, align="L")
        
        pdf.set_font("Arial", "", 8)
        pdf.set_x(x_start + col_widths[0])
        pdf.multi_cell(col_widths[1], 4, desc_body, align="L")
        
        y_end = pdf.get_y()
        row_height = y_end - y_start
        
        # Többi oszlop kitöltése
        pdf.set_xy(x_start, y_start)
        pdf.set_font("Arial", "", 9)
        pdf.cell(col_widths[0], row_height, str(item[0]), align="C")
        
        pdf.set_xy(x_start + col_widths[0] + col_widths[1], y_start)
        pdf.cell(col_widths[2], row_height, str(item[2]), align="C")
        
        pdf.set_xy(x_start + col_widths[0] + col_widths[1] + col_widths[2], y_start)
        pdf.cell(col_widths[3], row_height, str(item[3]), align="C")
        
        pdf.set_xy(x_start + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3], y_start)
        pdf.cell(col_widths[4], row_height, str(item[4]), align="C")
        
        pdf.set_xy(10, y_end + 2)
        pdf.set_draw_color(220, 220, 220)
        pdf.line(10, y_end+1, 200, y_end+1)
        pdf.set_draw_color(0, 0, 0)

    # --- 4. ÖSSZESÍTŐ ---
    pdf.ln(5)
    x_totals = 140
    
    def total_row(label, value, bold=False):
        pdf.set_x(x_totals)
        pdf.set_font("Arial", "B" if bold else "", 10)
        pdf.cell(30, 7, label, align="L")
        pdf.cell(30, 7, value, align="R", ln=True)
    
    total_row("Sub Total", data.get("subtotal", ""))
    total_row("Tax", data.get("tax", ""))
    total_row("Discount", data.get("discount", ""))
    
    pdf.ln(2)
    pdf.set_x(x_totals)
    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(30, 8, "Total", fill=True, align="L")
    pdf.cell(30, 8, data.get("grand_total", ""), fill=True, align="R", ln=True)
    
    pdf.set_text_color(0, 0, 0)

    # --- 5. LÁBLÉC ---
    pdf.set_y(230)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 5, "Term and Conditions:", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(100, 4, data.get("terms", ""), align="L")
    
    pdf.set_xy(140, 230)
    pdf.set_font("Arial", "I", 14) 
    pdf.cell(50, 10, data.get("signer_name", ""), align="C", ln=True)
    
    pdf.set_xy(140, 240)
    pdf.set_font("Arial", "", 10)
    pdf.cell(50, 5, data.get("signer_title", ""), align="C", ln=True)


    filepath = os.path.join(OUTPUT_DIR, filename)
    pdf.output(filepath)
    print(f"[OK] BW Minimalist Számla Generálva: {filepath}")

# --- SZAKDOLGOZAT TESZT ESETEK (UPDATED VENDORS) ---

# 1. BASE CASE (Valid, USD) - Vendor: Inland-Lohnbearbeiter A, DE
# Ez lesz az alapértelmezett, hibátlan számla.
thesis_bw_1 = {
    # Szállító 1
    "sender_name": "Inland-Lohnbearbeiter A, DE",
    "sender_address": "Hauptstraße 12\n39343 Alleringersleben",
    "sender_phone": "+49 123 456 789",
    
    "invoice_no": "#1234",
    "date": "June 13, 2021",
    "due_date": "June 16, 2021",
    
    "bill_to_name": "Murad Naser",
    "bill_to_address": "123 Anywhere st., Any City",
    "bill_to_phone": "+123-456-7890",
    
    "bank_name": "Central Bank",
    "bank_account_name": "Samira Hadid",
    "bank_account_no": "DE89 3704 0044 0532 0130 00",
    
    "items": [
        ["1", "Branding Design\nLogo and Identity", "$1000", "1", "$1000"],
        ["2", "Web Design\nHomepage and Landing Page", "$3000", "1", "$3000"],
        ["3", "Brochure\nPrint ready version", "$800", "1", "$800"]
    ],
    "subtotal": "$4800",
    "tax": "$0",
    "discount": "$0",
    "grand_total": "$4800",
    "terms": "Thank you for your business.",
    "signer_name": "Samira Hadid",
    "signer_title": "Manager"
}
create_bw_invoice("modern_invoice_01_valid.pdf", thesis_bw_1)


# 2. ESET: Duplikáció teszt - Vendor: Inlandslieferant DE 2
# Ugyanaz a számlaszám (#1234), de másik szállító és tartalom.
# Megjegyzés: Ha az SAP szállítónként vizsgálja a duplikációt, ez átmehet. 
# Ha globálisan, vagy ha a Vevő ugyanaz, akkor fennakadhat.
thesis_bw_2 = thesis_bw_1.copy()

# Szállító 2
thesis_bw_2["sender_name"] = "Inlandslieferant DE 2"
thesis_bw_2["sender_address"] = "Kirchhög 78\n99867 Gotha"

thesis_bw_2["items"] = [["1", "Consulting", "$500", "1", "$500"]]
thesis_bw_2["grand_total"] = "$500"
thesis_bw_2["subtotal"] = "$500"
# AZ ID MARAD #1234 -> Teszteljük, hogy a rendszer észreveszi-e
create_bw_invoice("modern_invoice_02_duplicate.pdf", thesis_bw_2)


# 3. ESET: Hiányzó Vendor Név teszt - Eredetileg: Inlandslieferant DE15
# Itt a feladat az volt, hogy HIÁNYZIK a név, ezért a 'sender_name'-t üresre állítjuk,
# de a címből (sender_address) az SAP megpróbálhatja kitalálni, hogy ez a DE15-ös szállító.
thesis_bw_3 = thesis_bw_1.copy()

# Szállító 3 (Név nélkül, csak címmel)
thesis_bw_3["sender_name"] = "" # <--- ÜRES, EZ A TESZT LÉNYEGE!
thesis_bw_3["sender_address"] = "Hullerner Straße 85\n45721 Haltern am See" # Ez alapján lehetne Inlandslieferant DE15

thesis_bw_3["invoice_no"] = "ERR-NO-VENDOR" 
thesis_bw_3["grand_total"] = "$1500"
thesis_bw_3["subtotal"] = "$1500"
thesis_bw_3["items"] = [["1", "Service Fee", "$1500", "1", "$1500"]]

create_bw_invoice("modern_invoice_03_missing_vendor.pdf", thesis_bw_3)