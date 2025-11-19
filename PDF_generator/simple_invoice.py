from fpdf import FPDF
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "Test_Invoices")
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
    
    # Y pozíció mentése a kezdéshez
    start_y = 20
    pdf.set_y(start_y)

    # --- BAL OSZLOP (Issued To & Pay To) ---
    pdf.set_x(10)
    
    # ISSUED TO
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 5, "ISSUED TO:", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(100, 5, str(data.get("issued_to_name", "")), ln=True)
    pdf.cell(100, 5, str(data.get("issued_to_company", "")), ln=True)
    pdf.multi_cell(90, 5, str(data.get("issued_to_address", "")))
    
    pdf.ln(5) # Kis térköz

    # PAY TO
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 5, "PAY TO:", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(100, 5, str(data.get("pay_to_bank", "")), ln=True)
    pdf.cell(100, 5, f"Account Name: {data.get('pay_to_acc_name', '')}", ln=True)
    pdf.cell(100, 5, f"Account No.: {data.get('pay_to_acc_no', '')}", ln=True)

    # Mentjük, hol végződött a bal oldal
    left_column_end_y = pdf.get_y()

    # --- JOBB OSZLOP (INVOICE felirat és dátumok) ---
    # Visszaállunk a tetejére, de jobbra toljuk az X-et
    pdf.set_xy(120, start_y)
    
    # INVOICE cím
    pdf.set_font("Arial", "B", 24)
    pdf.cell(70, 10, "INVOICE", align="R", ln=True)
    
    # Adatok (Invoice No, Date, Due Date)
    pdf.set_font("Arial", "B", 10)
    
    def right_data_row(label, value):
        pdf.set_x(120) # Mindig innen kezdjük a sort
        pdf.set_font("Arial", "B", 10)
        pdf.cell(35, 6, label, align="L")
        pdf.set_font("Arial", "", 10)
        pdf.cell(35, 6, value, align="R", ln=True)

    pdf.ln(5)
    right_data_row("INVOICE NO:", data.get("invoice_no", ""))
    right_data_row("DATE:", data.get("date", ""))
    right_data_row("DUE DATE:", data.get("due_date", ""))

    # --- 2. TÁBLÁZAT ---
    
    # A táblázatnak a két oszlop közül a lejjebb lévő alatt kell kezdődnie
    table_start_y = max(left_column_end_y, pdf.get_y()) + 15
    pdf.set_y(table_start_y)

    # Oszlopok: Description, Unit Price, Qty, Total
    cols = [90, 35, 25, 40]
    headers = ["DESCRIPTION", "UNIT PRICE", "QTY", "TOTAL"]

    # Fejléc
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(255, 255, 255) # Fehér háttér (minimalista)
    
    for i, h in enumerate(headers):
        align = "L" if i == 0 else "R"
        pdf.cell(cols[i], 8, h, border="B", align=align) # Csak alsó vonal
    pdf.ln(10)

    # Tételek
    pdf.set_font("Arial", "", 9)
    items = data.get("items", [])

    for item in items:
        # item = [Desc, Price, Qty, Total]
        
        # Mentés a multi_cell miatt
        x_start = pdf.get_x()
        y_start = pdf.get_y()

        # 1. Description (ez lehet többsoros)
        pdf.multi_cell(cols[0], 6, str(item[0]), align="L")
        y_end = pdf.get_y()

        # Visszaállunk a sor tetejére
        pdf.set_xy(x_start + cols[0], y_start)

        # 2. Unit Price
        pdf.cell(cols[1], 6, str(item[1]), align="R")
        # 3. Qty
        pdf.cell(cols[2], 6, str(item[2]), align="R")
        # 4. Total
        pdf.cell(cols[3], 6, str(item[3]), align="R")

        # Következő sor pozíciója
        pdf.set_xy(10, y_end)
        pdf.ln(2) # Kis sorköz

    # --- 3. ÖSSZESÍTŐ (Totals) ---
    pdf.ln(5)
    
    # Csak a jobb oldalra írunk, igazítva a táblázat széléhez
    x_totals = 135 
    
    def total_line(label, value, bold=False):
        pdf.set_x(x_totals)
        pdf.set_font("Arial", "B" if bold else "", 10)
        pdf.cell(25, 6, label, align="L") # Label
        pdf.cell(30, 6, value, align="R", ln=True) # Value

    total_line("SUBTOTAL", data.get("subtotal", ""))
    total_line("Tax", data.get("tax", ""))
    pdf.ln(2)
    # Végösszeg vastagon
    pdf.set_font("Arial", "B", 12)
    pdf.set_x(x_totals)
    pdf.cell(25, 8, "TOTAL", align="L")
    pdf.cell(30, 8, data.get("total_amount", ""), align="R", ln=True)

    # --- 4. ALÁÍRÁS / LÁBLÉC ---
    # Bal oldalra, alulra
    pdf.ln(15)
    pdf.set_x(10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 5, str(data.get("signer_name", "")), ln=True)
    
    # Mentés
    filepath = os.path.join(OUTPUT_DIR, filename)
    pdf.output(filepath)
    print(f"[OK] Simple Invoice Generálva: {filepath}")


# --- ADATOK A FELTÖLTÖTT KÉP ALAPJÁN ---

simple_data = {
    # Bal oldal
    "issued_to_name": "Richard Sanchez",
    "issued_to_company": "Thynk Unlimited",
    "issued_to_address": "123 Anywhere St., Any City",
    
    "pay_to_bank": "Borcele Bank",
    "pay_to_acc_name": "Adeline Palmerston",
    "pay_to_acc_no": "0123 4567 8901",
    
    # Jobb oldal
    "invoice_no": "01234",
    "date": "11.02.2030",
    "due_date": "11.03.2030",
    
    # Tételek
    "items": [
        ["Brand consultation", "100", "1", "$100"],
        ["Logo design", "100", "1", "$100"],
        ["Website design", "100", "1", "$100"],
        ["Social media templates", "100", "1", "$100"],
        ["Brand photography", "100", "1", "$100"],
        ["Brand guide", "100", "1", "$100"]
    ],
    
    # Összesítő
    "subtotal": "$400", # (Megj: a képen 6 tétel van, de a subtotal 400. Ez furcsa a képen, de mi lemásoljuk :))
    "tax": "10%",
    "total_amount": "$440",
    
    "signer_name": "Atlee Petersen"
}

# 1. Valid generálás
create_simple_invoice("simple_invoice_01.pdf", simple_data)

# 2. "Stressz teszt" adatokkal
stress_data = simple_data.copy()
stress_data["issued_to_name"] = "Dr. Very Long Name " * 5
stress_data["items"] = [
    ["Extrém hosszú szolgáltatás megnevezés, ami biztosan sortörést fog okozni a táblázatban, és meg kell nézni, hogy rácsúszik-e az árra.", "9999", "10", "$99999"],
    ["Normál tétel", "10", "1", "$10"]
]
stress_data["tax"] = "ÁFA mentes" # Szám helyett szöveg
create_simple_invoice("simple_invoice_stress_test.pdf", stress_data)