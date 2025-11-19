from fpdf import FPDF
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "Test_Invoices")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Létrehozzuk, ha nem létezik
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ModernInvoice(FPDF):
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

    def footer(self):
        # Lábléc: "Thank You For Your Business" + Aláírás
        self.set_y(-30)
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, "Thank You For Your Business", align="C", ln=True)
        self.ln(2)
        self.set_font("Arial", "", 10)
        # Ha a data-ban van aláíró név, azt használjuk, különben alapértelmezett
        self.cell(0, 5, "Lorna Alvarado", align="C")

def create_modern_invoice(filename, data):
    pdf = ModernInvoice()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=35) # Nagyobb margó alul a láblécnek

    # --- 1. FEJLÉC SZEKCIÓ ---
    
    # Jobb oldal: INVOICE felirat és ID
    pdf.set_xy(110, 20)
    pdf.set_font("Arial", "B", 24)
    pdf.cell(90, 10, "INVOICE", align="R", ln=True)
    
    pdf.set_x(110)
    pdf.set_font("Arial", "", 10)
    # Ha nincs ID, akkor placeholder
    inv_id = data.get("invoice_id", "#000000")
    pdf.cell(90, 6, f"Invoice ID: {inv_id}", align="R", ln=True)

    # Bal oldal: INVOICE TO adatok
    # Visszaugrunk a bal oldalra fentre
    pdf.set_xy(10, 20)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 6, "INVOICE TO", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(100, 6, str(data.get("customer_name", "")), ln=True)
    pdf.cell(100, 6, str(data.get("customer_phone", "")), ln=True)
    pdf.cell(100, 6, str(data.get("customer_email", "")), ln=True)
    # Multi_cell a címnek, ha hosszú lenne
    pdf.multi_cell(90, 6, str(data.get("customer_address", "")))

    pdf.ln(15) # Nagyobb térköz a táblázat előtt

    # --- 2. TERMÉK TÁBLÁZAT (Minimalista stílus) ---
    
    # Oszlop szélességek: Product, Price, Qty, Total
    # A kép alapján a Product széles, a többi keskenyebb
    cols = [95, 30, 20, 45] 
    headers = ["PRODUCT", "PRICE", "QTY", "TOTAL"]
    
    # Táblázat fejléce (Szürke háttérrel, hogy modern legyen)
    pdf.set_fill_color(240, 240, 240) # Világosszürke
    pdf.set_font("Arial", "B", 9)
    
    for i, h in enumerate(headers):
        # Align: Product balra, számok jobbra vagy középre
        align = "L" if i == 0 else "C" if i == 2 else "R"
        pdf.cell(cols[i], 10, h, border=0, fill=True, align=align)
    pdf.ln()

    # Tételek kiírása
    pdf.set_font("Arial", "", 9)
    items = data.get("items", [])
    
    # Váltakozó sorszínezés vagy csak sima fehér? A kép fehér. Maradjunk a fehérnél.
    for item in items:
        # item = [Name, Price, Qty, Total]
        
        # Mentjük a pozíciót a multi_cell miatt
        x_start = pdf.get_x()
        y_start = pdf.get_y()
        
        # 1. PRODUCT (Multi_cell, ha hosszú a név)
        pdf.multi_cell(cols[0], 8, str(item[0]), align="L")
        y_end = pdf.get_y()
        
        # Visszaállunk a sor tetejére a többi oszlophoz
        pdf.set_xy(x_start + cols[0], y_start)
        
        # 2. PRICE
        pdf.cell(cols[1], 8, str(item[1]), align="R")
        # 3. QTY
        pdf.cell(cols[2], 8, str(item[2]), align="C")
        # 4. TOTAL
        pdf.cell(cols[3], 8, str(item[3]), align="R")
        
        # Következő sor pozíciója
        pdf.set_xy(10, y_end)
        
        # Opcionális: vékony elválasztó vonal minden sor alá (nagyon halvány)
        pdf.set_draw_color(230, 230, 230)
        pdf.line(10, y_end, 200, y_end)
        pdf.set_draw_color(0, 0, 0) # Vissza feketére

    pdf.ln(5)

    # --- 3. LÁBLÉC INFÓK (Bank + Összesítő) ---
    
    y_bottom = pdf.get_y()
    
    # BAL OLDAL: PAYMENT METHOD
    pdf.set_xy(10, y_bottom)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(80, 8, "PAYMENT METHOD", ln=True)
    
    pdf.set_font("Arial", "", 9)
    # Kis segédfüggvény a banki adatokhoz (Label: Value)
    def bank_row(label, value):
        pdf.set_font("Arial", "B", 9)
        pdf.cell(20, 6, label, align="L")
        pdf.set_font("Arial", "", 9)
        pdf.cell(50, 6, f":  {value}", align="L", ln=True)

    bank_row("Name", data.get("bank_name", ""))
    bank_row("ID Bank", data.get("bank_id", ""))
    bank_row("Bank", data.get("bank_institute", ""))

    # JOBB OLDAL: TOTALS (Sub-total, Tax, Total)
    # Kiszámoljuk, hol kezdődjön (pl. 120-as x koordináta)
    pdf.set_xy(120, y_bottom)
    
    def total_row(label, value, is_final=False):
        pdf.set_x(120)
        pdf.set_font("Arial", "B" if is_final else "", 10)
        # Címke
        pdf.cell(40, 8, label, align="L")
        # Érték
        pdf.cell(40, 8, value, align="R", ln=True)

    total_row("SUB-TOTAL", data.get("subtotal", "$ 0.00"))
    total_row("TAX (20%)", data.get("tax", "$ 0.00"))
    
    # Vastag betűs végösszeg, esetleg kék színnel, vagy marad fekete
    pdf.set_text_color(0, 0, 0) 
    total_row("TOTAL", data.get("grand_total", "$ 0.00"), is_final=True)


    # Mentés
    filepath = os.path.join(OUTPUT_DIR, filename)
    pdf.output(filepath)
    print(f"[OK] Modern PDF Generálva: {filepath}")

# --- ADATOK A KÉPRŐL ---

modern_data = {
    "invoice_id": "#1234567890",
    "customer_name": "Marceline Anderson",
    "customer_phone": "+123-456-7890",
    "customer_email": "hello@reallygreatsite.com",
    "customer_address": "123 Anywhere St., Any City",
    
    "items": [
        ["Logo Design", "$ 100.00", "1", "$ 100.00"],
        ["Business Magazine Design", "$ 60.00", "2", "$ 120.00"],
        ["Business Card", "$ 125.00", "1", "$ 125.00"],
        ["Website Page (Extra long description test)", "$ 30.00", "4", "$ 120.00"]
    ],
    
    "bank_name": "Kim Chun Hei",
    "bank_id": "123-456-7890",
    "bank_institute": "Fauget",
    
    "subtotal": "$ 465.00",
    "tax": "$ 93.00",
    "grand_total": "$ 558.00"
}

# Futtatás
create_modern_invoice("modern_invoice_01.pdf", modern_data)

# Tesztelés rossz adatokkal (elcsúszott formázás)
bad_data = modern_data.copy()
bad_data["items"] = [
    ["Túl hosszú terméknév " * 10, "$ 0.00", "10000", "$ 0.00"],
    ["Normál tétel", "$ 10.00", "1", "$ 10.00"]
]
create_modern_invoice("modern_invoice_broken.pdf", bad_data)