from fpdf import FPDF
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "test_invoices")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ComplexInvoice(FPDF):
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

def create_complex_invoice(filename, data):
    pdf = ComplexInvoice()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- 1. FEJLÉC SZEKCIÓ ---
    
    # BAL OLDAL: Bill To
    pdf.set_xy(10, 10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 5, "Bill To", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(60, 4, data.get("bill_to_text", ""))
    
    # KÖZÉP: Remit To
    pdf.set_xy(80, 10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 5, "Remit to", ln=True)
    pdf.set_xy(80, 15)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(60, 4, data.get("remit_to_text", ""))
    
    # JOBB OLDAL: INVOICE cím és adatok
    pdf.set_xy(140, 10)
    pdf.set_font("Arial", "B", 24)
    pdf.cell(60, 10, "INVOICE", align="R", ln=True)
    
    # Invoice Adattábla (Number, Date, PO)
    pdf.set_xy(140, 25)
    pdf.set_font("Arial", "B", 9)
    
    # Segédfüggvény a kis táblázathoz jobb oldalt
    def right_header_row(label, value):
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.rect(x, y, 25, 6) # Label box
        pdf.rect(x+25, y, 35, 6) # Value box
        pdf.cell(25, 6, label, border=0)
        pdf.set_font("Arial", "", 9)
        pdf.cell(35, 6, str(value), border=0, align="C")
        pdf.set_font("Arial", "B", 9)
        pdf.ln(6)
        pdf.set_x(140)

    pdf.set_x(140)
    right_header_row("Number:", data.get("inv_number", ""))
    right_header_row("Date:", data.get("inv_date", ""))
    right_header_row("PO:", data.get("po_number", ""))

    # --- 2. KÖZÉPSŐ INFORMÁCIÓS SÁV ---

    pdf.ln(10) # Kis hézag
    
    # Source info
    pdf.set_x(10)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"Source: {data.get('source_ref', '')}", ln=True)
    
    # A hosszú vízszintes táblázat
    # Oszlop szélességek
    cols = [15, 25, 30, 30, 30, 20, 15, 25]
    headers = ["Acct.#", "A/R Cust.#", "Acct. ID", "Customer P.O.", "Attn to", "Sales Rep", "Ship Via", "Terms"]
    values = [
        data.get("acct_num", ""),
        data.get("ar_cust", ""),
        data.get("acct_id", ""),
        data.get("cust_po", ""),
        data.get("attn", ""),
        data.get("sales_rep", ""),
        data.get("ship_via", ""),
        data.get("terms", "")
    ]
    
    # Fejléc sor
    pdf.set_font("Arial", "B", 7)
    start_y = pdf.get_y() + 2
    pdf.set_y(start_y)
    
    for i, h in enumerate(headers):
        pdf.cell(cols[i], 5, h, border=1, align="C")
    pdf.ln()
    
    # Adat sor
    pdf.set_font("Arial", "", 7)
    for i, v in enumerate(values):
        # Multi_cell trükk, ha a szöveg túl hosszú lenne a cellába
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.cell(cols[i], 8, str(v), border=1, align="C")
    pdf.ln(12)

    # --- 3. WORK REQUESTED / PERFORMED ---
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 5, "Work Requested:", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 5, data.get("work_requested", ""))
    pdf.ln(2)
    
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 5, "Work Performed:", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 5, data.get("work_performed", ""))
    pdf.ln(5)

    # --- 4. FŐ TÉTEL TÁBLÁZAT (Items) ---

    col_widths = [25, 80, 15, 15, 25, 30]
    table_headers = ["Part Number", "Description", "Qty.", "UOM", "Ea. Price", "Total"]
    
    # Fejléc
    pdf.set_font("Arial", "B", 9)
    for i, h in enumerate(table_headers):
        pdf.cell(col_widths[i], 6, h, border="B", align="L" if i==1 else "C")
    pdf.ln(8)
    
    # Tételek listázása
    pdf.set_font("Arial", "", 9)
    items = data.get("items", [])
    
    grand_total = 0
    
    for item in items:

        line_height = 5
        
        # Mentjük a pozíciót
        x_start = pdf.get_x()
        y_start = pdf.get_y()
        
        # 1. oszlop
        pdf.cell(col_widths[0], line_height, str(item[0]), align="C")
        
        # 2. oszlop (Description) - ez lehet többsoros
        x_desc = pdf.get_x()
        pdf.multi_cell(col_widths[1], line_height, str(item[1]), align="L")
        y_end = pdf.get_y() 
        
        # Visszaállunk a sor tetejére a többi oszlophoz
        pdf.set_xy(x_start + col_widths[0] + col_widths[1], y_start)
        
        # 3. Qty
        pdf.cell(col_widths[2], line_height, str(item[2]), align="C")
        # 4. UOM
        pdf.cell(col_widths[3], line_height, str(item[3]), align="C")
        # 5. Price
        pdf.cell(col_widths[4], line_height, str(item[4]), align="R")
        # 6. Total
        pdf.cell(col_widths[5], line_height, str(item[5]), align="R")
        
        # Következő sor pozíciója
        pdf.set_xy(10, max(y_end, y_start + line_height))
        pdf.ln(1)

    # Vonal a táblázat alján
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)

    # --- 5. ÖSSZESÍTŐ (Totals) ---

    y_totals = pdf.get_y()
    left_margin_totals = 140
    
    # Notes (Bal oldal)
    pdf.set_xy(10, y_totals)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(110, 4, data.get("notes", ""), border=0)
    
    # Számok (Jobb oldal)
    pdf.set_xy(left_margin_totals, y_totals)
    
    def print_total_row(label, value, bold=False):
        pdf.set_x(left_margin_totals)
        pdf.set_font("Arial", "B" if bold else "", 9)
        pdf.cell(35, 6, label, align="R")
        pdf.cell(25, 6, value, align="R", border="B" if bold else 0)
        pdf.ln()

    print_total_row("Item Total:", data.get("total_net", "$ 0.00"))
    print_total_row("Sales Tax:", data.get("tax", "$ 0.00"))
    pdf.ln(1)
    print_total_row("Total Amount Due:", data.get("total_gross", "$ 0.00"), bold=True)

    # Mentés
    filepath = os.path.join(OUTPUT_DIR, filename)
    pdf.output(filepath)
    print(f"[OK] Hagyományos számla Generálva: {filepath}")


# --- ADATOK ÉS FUTTATÁS ---

# Ez az adatstruktúra pont úgy néz ki, mint a feltöltött PDF-ed
sample_data = {
    # Fejléc adatok
    "bill_to_text": "ABC Communication\n3451 NE Willoughby Blvd.\nSturt, FL 5494 U.S.A\nPhone: (72) 288-2250\nEmail: dispatch@abcms.com",
    "remit_to_text": "Standard Products\n3150 SW 9th Street\nMiami, FL 3218 U.S.A.\nPhone: (306) 461-003",
    "inv_number": "174221",
    "inv_date": "2/18/2019",
    "po_number": "1258-0854",
    
    # Középső sáv
    "source_ref": "S.O. #687250",
    "acct_num": "860",
    "ar_cust": "Std Products",
    "acct_id": "Ft. Lenderdale",
    "cust_po": "285058-5848",
    "attn": "Curtis V. Brown",
    "sales_rep": "",
    "ship_via": "Email",
    "terms": "Due upon receipt",
    
    # Munka leírás
    "work_requested": "02/01/2016 11:39 AM, Gary: Per phone call from Ben: Customer advised that incoming phone calls now ring throughout the store over the speaker.",
    "work_performed": "2/16/16 Lines had programming glitch, ring over page to group 5011. Deleted Lisa out of MC 7224. Tested all lines incoming OK.",
    
    # Tételek (PartNo, Desc, Qty, UOM, Price, Total)
    "items": [
        ["2001", "Professional Service 1-Labor", "2.00", "HR", "$ 55.00", "$ 110.00"],
        ["3001", "Extra Fee - 24h Service", "1.00", "MD", "$ 70.00", "$ 70.00"],
        ["9001", "Travel costs", "1.00", "TR", "$ 40.00", "$ 40.00"]
    ],
    
    # Összesítés
    "notes": "There should be no calls coming in on these lines.\nThank you for your business!",
    "total_net": "$ 220.00",
    "tax": "$ 0.00",
    "total_gross": "$ 220.00"
}

# 1. Generáljunk egy tökéletes másolatot
create_complex_invoice("general_invoice_01.pdf", sample_data)

# 2. Generáljunk egy "TÖRÖTT" teszt verziót (hosszú szöveggel, hogy lásd, mit bír)
broken_data = sample_data.copy()
broken_data["inv_number"] = "ERROR-999"
broken_data["items"] = [
    ["ERR", "Ez egy extrém hosszú tétel leírás, ami biztosan el fogja törni a táblázatot, ha nem kezeli jól a sortörést a program...", "999", "db", "$ 1.00", "$ 999.00"],
    ["NaN", "Hibás ár", "-1", "db", "ingyen", "Végtelen"]
]
create_complex_invoice("general_invoice_broken_01.pdf", broken_data)