from openpyxl import Workbook
from tkinter import filedialog, messagebox

def export_to_excel(tree, default_filename):
    # Ask user where to save file
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        initialfile=default_filename
    )
    
    if not file_path:
        return  # User cancelled

    wb = Workbook()
    ws = wb.active
    ws.title = "Data"

    # Write column headers
    headers = [tree.heading(col)["text"] for col in tree["columns"]]
    ws.append(headers)

    # Write row data
    for row_id in tree.get_children():
        row = tree.item(row_id)['values']
        ws.append(row)

    # Make headers bold
    from openpyxl.styles import Font
    for cell in ws[1]:
        cell.font = Font(bold=True)

    # Auto column width
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        ws.column_dimensions[col_letter].width = max_length + 2

    # Save file
    wb.save(file_path)

    # Show success
    messagebox.showinfo(title="Exported", message=f"Saved to:\n{file_path}")