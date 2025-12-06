from fpdf import FPDF
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "test_invoices")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create if not exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ModernInvoice(FPDF):
    def header(self):
        # Looking for font files next to the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(script_dir, "arial.ttf") 
        font_path_bold = os.path.join(script_dir, "arialbd.ttf")

        # Trying to load from script directory, if not found, fallback to Windows fonts
        if os.path.exists(font_path):
            self.add_font("Arial", style="", fname=font_path)
            self.add_font("Arial", style="B", fname=font_path_bold)
        else:
            # Fallback to Windows fonts directory
            self.add_font("Arial", style="", fname=r"C:\Windows\Fonts\arial.ttf")
            self.add_font("Arial", style="B", fname=r"C:\Windows\Fonts\arialbd.ttf")

    def footer(self):
        # Footer: "Thank You For Your Business" + Signature
        self.set_y(-30)
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, "Thank You For Your Business", align="C", ln=True)
        self.ln(2)
        self.set_font("Arial", "", 10)
        # If there is a signer name in data, use it, otherwise default
        self.cell(0, 5, "Lorna Alvarado", align="C")

# ... (A fenti importok és a class ModernInvoice definíció marad) ...

def create_modern_invoice_for_thesis(filename, data):
    # Ez ugyanaz a függvény, csak biztosítjuk, hogy a Dátum is rákerüljön a PDF-re
    # mert a szakdolgozat kéri a "teljesítés dátuma" kinyerését.
    pdf = ModernInvoice()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=35)

    # --- 1. FEJLÉC ---
    # Jobb oldal: INVOICE, ID és DÁTUM
    pdf.set_xy(110, 20)
    pdf.set_font("Arial", "B", 24)
    pdf.cell(90, 10, "INVOICE", align="R", ln=True)
    
    pdf.set_x(110)
    pdf.set_font("Arial", "", 10)
    inv_id = data.get("invoice_id", "#000000")
    pdf.cell(90, 6, f"Invoice Number: {inv_id}", align="R", ln=True)
    
    # ÚJ SOR: Dátum kiírása (Ez kritikus az SAP teszthez!)
    inv_date = data.get("date", "2023.01.01.")
    pdf.cell(90, 6, f"Date: {inv_date}", align="R", ln=True)

    # Bal oldal: INVOICE TO (Vevő/Szállító adatok)
    pdf.set_xy(10, 20)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 6, "INVOICE TO", ln=True)
    
    pdf.set_font("Arial", "", 10)
    # Ha üres a név, akkor üresen hagyjuk (Validation Error teszt)
    pdf.cell(100, 6, str(data.get("customer_name", "")), ln=True)
    pdf.cell(100, 6, str(data.get("customer_phone", "")), ln=True)
    pdf.cell(100, 6, str(data.get("customer_email", "")), ln=True)
    pdf.multi_cell(90, 6, str(data.get("customer_address", "")))

    pdf.ln(15)

    # --- 2. TÁBLÁZAT ---
    cols = [95, 30, 20, 45] 
    headers = ["PRODUCT", "PRICE", "QTY", "TOTAL"]
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 9)
    for i, h in enumerate(headers):
        align = "L" if i == 0 else "C" if i == 2 else "R"
        pdf.cell(cols[i], 10, h, border=0, fill=True, align=align)
    pdf.ln()

    pdf.set_font("Arial", "", 9)
    items = data.get("items", [])
    
    for item in items:
        x_start = pdf.get_x()
        y_start = pdf.get_y()
        
        pdf.multi_cell(cols[0], 8, str(item[0]), align="L")
        y_end = pdf.get_y()
        
        pdf.set_xy(x_start + cols[0], y_start)
        pdf.cell(cols[1], 8, str(item[1]), align="R")
        pdf.cell(cols[2], 8, str(item[2]), align="C")
        pdf.cell(cols[3], 8, str(item[3]), align="R")
        
        pdf.set_xy(10, y_end)
        pdf.set_draw_color(230, 230, 230)
        pdf.line(10, y_end, 200, y_end)
        pdf.set_draw_color(0, 0, 0)

    pdf.ln(5)

    # --- 3. LÁBLÉC (Összesítő) ---
    y_bottom = pdf.get_y()
    
    # Bal oldal: Bank
    pdf.set_xy(10, y_bottom)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(80, 8, "PAYMENT METHOD", ln=True)
    pdf.set_font("Arial", "", 9)
    
    if data.get("bank_name"):
        pdf.cell(20, 6, "Name", align="L")
        pdf.cell(50, 6, f": {data.get('bank_name')}", align="L", ln=True)
    if data.get("bank_id"):
        pdf.cell(20, 6, "ID Bank", align="L")
        pdf.cell(50, 6, f": {data.get('bank_id')}", align="L", ln=True)
    
    # Jobb oldal: Totals
    pdf.set_xy(120, y_bottom)
    
    def total_row(label, value, is_final=False):
        pdf.set_x(120)
        pdf.set_font("Arial", "B" if is_final else "", 10)
        pdf.cell(40, 8, label, align="L")
        pdf.cell(40, 8, value, align="R", ln=True)

    total_row("SUBTOTAL", data.get("subtotal", ""))
    total_row(f"TAX ({data.get('tax_rate', '0%')})", data.get("tax", ""))
    pdf.set_text_color(0, 0, 0) 
    total_row("TOTAL", data.get("grand_total", ""), is_final=True)

    filepath = os.path.join(OUTPUT_DIR, filename)
    pdf.output(filepath)
    print(f"[OK] Teszt PDF Generálva: {filepath}")


# --- SZAKDOLGOZAT TESZT ESETEK ---

# 1. ESET: "Belföldi számla" (Valid, HUF, 27% ÁFA)
# Cél: Tesztelni a sikeres adatkinyerést és a 27%-os ÁFA felismerését.
case_1_domestic = {
    "invoice_id": "123456789",
    "date": "2025. 12. 06.", # Teljesítés dátuma
    "customer_name": "Servicios en Daganzo",
    "customer_phone": "+36-1-123-4567",
    "customer_email": "info@daganzosercios.hu",
    "customer_address": "74214 Daganzo, Lindenstrasse 55",
    
    "items": [
        ["Bicycle", "1000 €", "1", "1000 €"],
        ["Bicycle part", "500 €", "2", "1000 €"]
    ],
    
    "bank_name": "Magyar Bank Zrt.",
    "bank_id": "11773333-12345678",
    
    "subtotal": "2000 €",
    "tax_rate": "27%",
    "tax": "540 €",
    "grand_total": "2540 €"
}
create_modern_invoice_for_thesis("modern_01_valid.pdf", case_1_domestic)


# 2. ESET: "Duplikált számlaszám" teszthez (Valid tartalom, de ismétlődő ID)
# Cél: Ezt a fájlt másodikként kell feltölteni az SAP-ba. A rendszernek dobnia kell egy hibát,
# hogy az "INV-HU-2024-001" már létezik a rendszerben.
# (A tartalom kicsit más, de az ID ugyanaz, ez a lényeg)
case_2_duplicate = case_1_domestic.copy()
case_2_duplicate["items"] = [["Other one", "10 €", "1", "10 €"]]
case_2_duplicate["grand_total"] = "12,7 €"
# AZ ID UGYANAZ MARAD!
create_modern_invoice_for_thesis("modern_02_duplicate_id_check.pdf", case_2_duplicate)


# 4. ESET: "Hiányzó Kötelező Adat" (Missing Mandatory Field)
# Cél: A "customer_name" üres. Az SAP automatizációnak ezt észre kell vennie, 
# és a validációs lépésnél el kell utasítania vagy manuális javításra küldenie (Human in the Loop).
case_4_invalid = {
    "invoice_id": "987654321",
    "date": "2025. 12. 06.",
    "customer_name": "", # <--- HIBA! Hiányzik a szállító neve.
    "customer_phone": "",
    "customer_address": "",
    
    "items": [
        ["Unknow product", "100 €", "1", "100 €"]
    ],
    
    "bank_name": "Bank",
    "bank_id": "1234",
    
    "subtotal": "100 €",
    "tax_rate": "27%",
    "tax": "27 F€",
    "grand_total": "127 €"
}
create_modern_invoice_for_thesis("modern_04_missing_vendor_error.pdf", case_4_invalid)