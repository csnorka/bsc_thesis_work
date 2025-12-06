from fpdf import FPDF
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "test_invoices")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ComplexInvoice(FPDF):
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

def create_complex_invoice(filename, data):
    pdf = ComplexInvoice()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- 1. HEADER SECTION ---
    
    # LEFT SIDE: Bill To
    pdf.set_xy(10, 10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 5, "Bill To", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(60, 4, data.get("bill_to_text", ""))
    
    # CENTER: Remit To
    pdf.set_xy(80, 10)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 5, "Remit to", ln=True)
    pdf.set_xy(80, 15)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(60, 4, data.get("remit_to_text", ""))
    
    # RIGHT SIDE: INVOICE title and details
    pdf.set_xy(140, 10)
    pdf.set_font("Arial", "B", 24)
    pdf.cell(60, 10, "INVOICE", align="R", ln=True)
    
    # Invoice Data Table (Number, Date, PO)
    pdf.set_xy(140, 25)
    pdf.set_font("Arial", "B", 9)
    
    # Helper function for the small table on the right
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

    # --- 2. MIDDLE INFORMATION BAND ---

    pdf.ln(10) # Small gap
    
    # Source info
    pdf.set_x(10)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"Source: {data.get('source_ref', '')}", ln=True)
    
    # The long horizontal table
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
    
    # Header row
    pdf.set_font("Arial", "B", 7)
    start_y = pdf.get_y() + 2
    pdf.set_y(start_y)
    
    for i, h in enumerate(headers):
        pdf.cell(cols[i], 5, h, border=1, align="C")
    pdf.ln()
    
    # Data row
    pdf.set_font("Arial", "", 7)
    for i, v in enumerate(values):
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

    # --- 4. MAIN ITEMS TABLE ---

    col_widths = [25, 80, 15, 15, 25, 30]
    table_headers = ["Part Number", "Description", "Qty.", "UOM", "Ea. Price", "Total"]
    
    # Header
    pdf.set_font("Arial", "B", 9)
    for i, h in enumerate(table_headers):
        pdf.cell(col_widths[i], 6, h, border="B", align="L" if i==1 else "C")
    pdf.ln(8)
    
    # Listing items
    pdf.set_font("Arial", "", 9)
    items = data.get("items", [])
    
    for item in items:
        line_height = 5
        x_start = pdf.get_x()
        y_start = pdf.get_y()
        
        pdf.cell(col_widths[0], line_height, str(item[0]), align="C")
        
        # Description multiline
        pdf.multi_cell(col_widths[1], line_height, str(item[1]), align="L")
        y_end = pdf.get_y() 
        
        pdf.set_xy(x_start + col_widths[0] + col_widths[1], y_start)
        
        pdf.cell(col_widths[2], line_height, str(item[2]), align="C")
        pdf.cell(col_widths[3], line_height, str(item[3]), align="C")
        pdf.cell(col_widths[4], line_height, str(item[4]), align="R")
        pdf.cell(col_widths[5], line_height, str(item[5]), align="R")
        
        pdf.set_xy(10, max(y_end, y_start + line_height))
        pdf.ln(1)

    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)

    # --- 5. TOTALS ---

    y_totals = pdf.get_y()
    left_margin_totals = 140
    
    pdf.set_xy(10, y_totals)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(110, 4, data.get("notes", ""), border=0)
    
    pdf.set_xy(left_margin_totals, y_totals)
    
    def print_total_row(label, value, bold=False):
        pdf.set_x(left_margin_totals)
        pdf.set_font("Arial", "B" if bold else "", 9)
        pdf.cell(35, 6, label, align="R")
        pdf.cell(25, 6, value, align="R", border="B" if bold else 0)
        pdf.ln()

    print_total_row("Item Total:", data.get("total_net", "€ 0.00"))
    print_total_row("Sales Tax:", data.get("tax", "€ 0.00"))
    pdf.ln(1)
    print_total_row("Total Amount Due:", data.get("total_gross", "€ 0.00"), bold=True)

    filepath = os.path.join(OUTPUT_DIR, filename)
    pdf.output(filepath)
    print(f"[OK] Generálva: {filepath}")


# --- GENERATING TEST CASES ---

# 1. BASE CASE (Valid, USD)
base_data = {
    "bill_to_text": "ABC Communication\n3451 NE Willoughby Blvd.\nSturt, FL 5494 U.S.A",
    "remit_to_text": "Sixt GmbH & Co.\nZugspitzstrasse 1\n82049",
    "inv_number": "174221",
    "inv_date": "6/12/2025",
    "po_number": "1258-0854",
    "source_ref": "S.O. #687250",
    "acct_num": "860",
    "ar_cust": "Std Products",
    "acct_id": "Ft. Lenderdale",
    "cust_po": "285058-5848",
    "attn": "Curtis V. Brown",
    "sales_rep": "Smith",
    "ship_via": "Email",
    "terms": "Net 30",
    "work_requested": "Customer advised that incoming phone calls now ring throughout the store.",
    "work_performed": "Lines had programming glitch. Tested all lines incoming OK.",
    
    # Items (PartNo, Desc, Qty, UOM, Price, Total)
    "items": [
        ["2001", "Labor Service", "2.00", "HR", "€ 55.00", "€ 110.00"],
        ["3001", "Extra Fee", "1.00", "MD", "€ 70.00", "€ 70.00"],
        ["9001", "Travel costs", "1.00", "TR", "€ 40.00", "€ 40.00"]
    ],
    "notes": "Thank you for your business!",
    "total_net": "€ 220.00",
    "tax": "$ 0.00",
    "total_gross": "€ 220.00"
}

# File 1: Perfect condition
create_complex_invoice("general_invoice_01_valid.pdf", base_data)


# 2. MISSING INVOICE NUMBER (Missing Number)
missing_id_data = base_data.copy()
missing_id_data["inv_number"] = "" # Leave empty
missing_id_data["po_number"] = "" # Remove the PO number for testing purposes:

create_complex_invoice("general_invoice_02_missing_id.pdf", missing_id_data)


# 3. DIFFERENT CURRENCY (USD Currency)
# Copy the base
usd_data = base_data.copy()
# Rewrite the text values where there was a € sign
usd_data["items"] = [
    ["2001", "Labor Service (EU)", "2.00", "HR", "$ 50.00", "$ 100.00"],
    ["3001", "Extra Fee", "1.00", "MD", "$ 60.00", "$ 60.00"],
    ["9001", "Travel costs", "1.00", "TR", "$ 35.00", "$ 35.00"]
]
usd_data["total_net"] = "$ 195.00"
usd_data["tax"] = "$ 39.00"      # Let's put 20% VAT since it's Europe
usd_data["total_gross"] = "$ 234.00"

create_complex_invoice("general_invoice_03_currency_usd.pdf", usd_data)