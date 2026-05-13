import customtkinter as ctk
from tkinter import ttk, messagebox
from config.ui_config import DATA_FRAME_UI, FORM_UI
from services.audit_service import (
    get_all_audit, search_audit
)
from ui.excel_file_maker import export_to_excel

class AuditFrame(ctk.CTkFrame):
    def __init__(self, content_area):
        super().__init__(content_area, fg_color="transparent")

        self.grid_rowconfigure(0, weight=0)  # topbar
        self.grid_rowconfigure(1, weight=1)  # table expands
        self.grid_rowconfigure(2, weight=0)  # action bar
        self.grid_columnconfigure(0, weight=1)

        # ── Instance variables ─────────────────────────────
        self.selected_row = None  # stores selected row as dict
        self.correct_dates_flag = False

        # ── Build UI ───────────────────────────────────────
        self._build_topbar()
        self._build_table()

        # ── Load data on open ──────────────────────────────
        self.load_data()

    def _build_topbar(self):
        # ── Topbar container ───────────────────────────────────────────
        self.topbar_frame = ctk.CTkFrame(self, height=DATA_FRAME_UI['topbar_height'])
        self.topbar_frame.grid(row=0, column=0, sticky="ew", padx=DATA_FRAME_UI['padding_x'], pady=DATA_FRAME_UI['padding_y'])

        # Give topbar 4 columns: search entry | search btn | add btn | export
        self.topbar_frame.grid_rowconfigure(0, weight=0)
        self.topbar_frame.grid_rowconfigure(1, weight=1)
        self.topbar_frame.grid_columnconfigure(0, weight=1)        # search entry stretches
        self.topbar_frame.grid_columnconfigure((1, 2, 3, 4, 5, 6, 7), weight=0)        # buttons fixed

        # ── Search entry ───────────────────────────────────────────────
        ctk.CTkLabel(self.topbar_frame, text="Search by UserID or Username or TableName", font=ctk.CTkFont(size=10)).grid(row=0, column=0, padx=(6,4), pady=(1,0), sticky="w")

        # ── Search entry ───────────────────────────────────────────────
        self.searchbar_var = ctk.StringVar(value="")
        self.search_bar_entry = ctk.CTkEntry(
            self.topbar_frame,
            height=DATA_FRAME_UI['btn_height'],
            border_width=1,
            border_color=DATA_FRAME_UI['btn_text'],
            textvariable=self.searchbar_var
        )
        self.search_bar_entry.grid(row=1, column=0, padx=(6,4), pady=(0,6), sticky="ew")

        # Adding trace to Variable. means calling a function whenever variable's value changes
        self.searchbar_var.trace_add("write", self._on_search)

        # ── Search button ──────────────────────────────────────────────
        self.search_btn = ctk.CTkButton(
            self.topbar_frame,
            text="🔍 Search",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=self._on_search
        )
        self.search_btn.grid(row=1, column=1, padx=4, pady=(1,6))

       # ── Vertical Separatoe ───────────────────────────────────────────
        self.create_vertical_separator(self.topbar_frame, column= 2)

        # ── Status Filter Frame ──────────────────────────────────────────

        # Create a small label above the checkboxes
        ctk.CTkLabel(self.topbar_frame, text="Filter by Action:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=10)).grid(row=0, column=3, padx=4, pady=(1,0), sticky="w")

        # Creating a Dict of Filters where each filter name is a BooleanVar()
        filter_list = ["Insert", "Update", "Delete"]
        self.filters_var = {}

        for filter in filter_list:
            self.filters_var[filter] = ctk.BooleanVar(value=True)
        
        filter_frame = ctk.CTkFrame(self.topbar_frame, fg_color="transparent")
        filter_frame.grid(row=1, column=3, padx=2, pady=0, sticky="nsew")

        # Automatically arrange checkboxes, 2 per col
        for i, filter in enumerate(filter_list):
            row_idx = i % 2    # Modulo division:  0, 1, 0, 1
            col_idx = i // 2   # Integer division: 0, 0, 1, 1
            
            chk = ctk.CTkCheckBox(filter_frame, text=filter, font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size = 11), checkbox_height=15, checkbox_width=15, variable=self.filters_var[filter])
            chk.grid(row=row_idx, column=col_idx, padx=(1,0), sticky=FORM_UI["entry_sticky"])
            
            # Attach trace directly to the checkbox variable
            self.filters_var[filter].trace_add("write", self._on_search)

       # ── Vertical Separatoe ───────────────────────────────────────────
        self.create_vertical_separator(self.topbar_frame, column= 4)

        # ── Date Filter Section ──────────────────
        self.date_filter_frame = ctk.CTkFrame(self.topbar_frame, fg_color="transparent")
        self.date_filter_frame.grid(row=0, column=5, rowspan=2, pady=(1,6))

        # Variables
        self.from_date_var = ctk.StringVar()
        self.to_date_var = ctk.StringVar()

        ctk.CTkLabel(self.date_filter_frame, text="From Date:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=10)).grid(row=0, column=0, padx=4, pady=(1,0), sticky="w")
        ctk.CTkLabel(self.date_filter_frame, text="To Date:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=10)).grid(row=1, column=0, padx=4, pady=(1,0), sticky="w")       


        # From Date Entry
        self.from_entry = ctk.CTkEntry(
            self.date_filter_frame,
            height=DATA_FRAME_UI['btn_height']-10,
            width=DATA_FRAME_UI['topbar_btn_width'],
            border_width=1,
            border_color=DATA_FRAME_UI['btn_text'],
            textvariable=self.from_date_var
        )
        self.from_entry.grid(row=0, column=1, padx=1, pady=(0,2))


        # To Date Entry
        self.to_entry = ctk.CTkEntry(
            self.date_filter_frame,
            height=DATA_FRAME_UI['btn_height']-10,
            width=DATA_FRAME_UI['topbar_btn_width'],
            border_width=1,
            border_color=DATA_FRAME_UI['btn_text'],
            textvariable=self.to_date_var
        )
        self.to_entry.grid(row=1, column=1, padx=1, pady=(2,0))

        # Apply Filter Button (Small icon version to save space)
        self.apply_date_btn = ctk.CTkButton(
            self.date_filter_frame,
            text="📅 Filter",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height']-10,
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=self._on_date_filter
        )
        self.apply_date_btn.grid(row=0, column=2, rowspan=2, padx=(1, 2))

       # ── Vertical Separatoe ───────────────────────────────────────────
        self.create_vertical_separator(self.topbar_frame, column= 6)

        # ── Export button ──────────────────────────────────────────────
        self.export_btn = ctk.CTkButton(
            self.topbar_frame,
            text="📤 Export",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=self._on_export
        )
        self.export_btn.grid(row=1, column=7, padx=(4,6), pady=(1,6))


    def _build_table(self):
        # ── Table container ───────────────────────────────────────────
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=DATA_FRAME_UI['padding_x'], pady=(0, 5))

        self.table_frame.grid_rowconfigure(0, weight=1)     # row 0 stretches
        self.table_frame.grid_columnconfigure(0, weight=1)  # col 0 stretches

        # ── Table Styling ───────────────────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))
        style.configure("Treeview", font=("Arial", 14), rowheight=35)

        # ── Table Section ───────────────────────────────────────────
        self.table = ttk.Treeview(self.table_frame, columns= ('user_id', 'username', 'timestamp', 'action', 'table_name', 'old_value', 'new_value'), show= 'headings', selectmode="browse")
        self.table.heading('user_id',    text= 'User ID')
        self.table.heading('username',   text= 'Username')
        self.table.heading('timestamp',  text= 'Timestamp')
        self.table.heading('action',     text= 'Action')
        self.table.heading('table_name', text= 'Table Name')
        self.table.heading('old_value',  text= 'Old Value')
        self.table.heading('new_value',  text= 'New Value')

        # Column widths
        self.table.column('user_id',    width=150, minwidth=150, anchor='center')
        self.table.column('username',   width=200, minwidth=200)
        self.table.column('timestamp',  width=200, minwidth=200, anchor='center')
        self.table.column('action',     width=100, minwidth=100, anchor='center')
        self.table.column('table_name', width=200, minwidth=200, anchor='center')
        self.table.column('old_value',  width=750, minwidth=750)
        self.table.column('new_value',  width=750, minwidth=750)

        self.table.bind('<<TreeviewSelect>>', self._on_row_select)

        # Scroll Bar
        self.scrollbary = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=self.scrollbary.set)

        # Scroll Bar
        self.scrollbarx = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.table.xview)
        self.table.configure(xscrollcommand=self.scrollbarx.set)

        # Grid both Tree and ScrollBar
        self.table.grid(row=0, column=0, sticky='nsew')
        self.scrollbary.grid(row=0, column=1, sticky='ns')   # column 1, stretches vertically only
        self.scrollbarx.grid(row=1, column=0, sticky='ew')   # column 1, stretches horizontal only

        # ── ActionBar Section ──────────────────────────────────────────
        self.action_bar = ctk.CTkFrame(self, height=DATA_FRAME_UI['actionbar_height'])
        self.action_bar.grid(row=2, column=0, sticky="ew", padx=DATA_FRAME_UI['padding_x'], pady=DATA_FRAME_UI['padding_y'])

        #self.action_bar.grid_columnconfigure(0, weight=1)

        self.selection_label = ctk.CTkLabel(self.action_bar, text='No Row Selected')
        self.selection_label.grid(row=0, column=0, sticky="w", padx=10, pady=8)




    def load_data(self):
        rows = get_all_audit()
        self._refresh_table(rows)

    def _refresh_table(self,rows):
        # Deletes existing rows
        self.table.delete(*self.table.get_children())
        
        # Creating Stripped row tags
        self.table.tag_configure('Insert', background=DATA_FRAME_UI['audit_insert'])
        self.table.tag_configure('Update', background=DATA_FRAME_UI['audit_update'])
        self.table.tag_configure('Delete', background=DATA_FRAME_UI['audit_delete'])

        # inserts New Data
        for row in rows:
            tag = row['action']

            formatted_id = f'USR-{row['user_id']}'

            self.table.insert(parent='', index= 'end', values=(
                formatted_id,
                row['username'],
                row['timestamp'],  # if there is a NULL value Tree will show None so replace it with ""
                row['action'],
                row['table_name'],
                row['old_value'],
                row['new_value']),
                tags= (tag,)
            )
            


    def _on_search(self, *args):
        """Called by: search text change, filter checkboxes change, OR date filter button."""
        search_term = self.searchbar_var.get().strip().upper()
        if search_term.startswith("USR-"):
            search_term = search_term.replace("USR-", "")

        # ── Get action filters ─────────────────────────────────
        selected_filter = [f for f, var in self.filters_var.items() if var.get()]

        # ── Try to parse dates (silently fail if invalid) ──────
        from_date = None
        to_date = None
        
        from_str = self.from_date_var.get().strip()
        to_str = self.to_date_var.get().strip()
        
        # Only apply date filter if BOTH dates are provided
        if from_str and to_str:
            try:
                from datetime import datetime
                from_dt = datetime.strptime(from_str, "%d-%m-%Y")
                to_dt = datetime.strptime(to_str, "%d-%m-%Y")

                if from_dt > to_dt:
                    messagebox.showwarning(
                        "Invalid Date Range",
                        "From date must be before or equal to To date."
                    )
                    return
                
                # Convert to MySQL format
                from_date = from_dt.strftime("%Y-%m-%d")
                to_date = to_dt.strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showwarning(
                "Incomplete Date Range",
                "Please provide both From and To dates, or leave both empty."
                )
                return

        # ── Execute search ─────────────────────────────────────
        rows = search_audit(search_term, selected_filter, start_date=from_date, end_date=to_date)
        self._refresh_table(rows)
        
        # Clear selection
        self.selected_row = None
        self.selection_label.configure(text='No row selected')

    def _on_row_select(self, event):
        column_usernames = ['user_id', 'username', 'timestamp', 'action', 'table_name', 'old_value', 'new_value']
        selected = self.table.selection()

        if not selected:
            self.selection_label.configure(text='No Row Selected')
            return None
        
        item_id = selected[0]
        values = self.table.item(item_id)["values"]
        self.selected_row = dict(zip(column_usernames, values))

        # Updating the Selection Label
        self.selection_label.configure(text= f'ID: {self.selected_row['user_id']} | Username: {self.selected_row['username']} | Timestamp: {self.selected_row['timestamp']}')



    def _on_export(self):
        # Check if table has any rows
        if not self.table.get_children():
            messagebox.showwarning(title="Empty", message="No data to export.")
            return
        
        export_to_excel(tree=self.table, default_filename="audits_export")

    def create_vertical_separator(self, parent, column):
        ctk.CTkFrame(
            parent,
            width=1,
            height=1,
            fg_color="gray"
        ).grid(
            row=0,
            column=column,
            rowspan=2,
            padx=1,
            pady=4,
            sticky="ns"
        )

    def _on_date_filter(self):
        """Called when user clicks the Filter button explicitly."""
        from_str = self.from_date_var.get().strip()
        to_str = self.to_date_var.get().strip()
        
        # ── Case 1: Both empty → Clear filter ──────────────────
        if not from_str and not to_str:
            self._on_search()  # Search without date filter
            return
        

        # ── Case 2: Both provided → Validate ───────────────────
        if from_str and to_str:
            try:
                from datetime import datetime
                from_dt = datetime.strptime(from_str, "%d-%m-%Y")
                to_dt = datetime.strptime(to_str, "%d-%m-%Y")
                
                # Verify range logic
                if from_dt > to_dt:
                    messagebox.showwarning(
                        "Invalid Date Range",
                        "From date must be before or equal to To date."
                    )
                    return
                
                # Valid dates - trigger search
                self._on_search()
                
            except ValueError:
                messagebox.showwarning(
                    "Invalid Date Format",
                    "Please use DD-MM-YYYY format.\nExample: 01-01-2024"
                )

        # ── Case 3: Only one provided → Error ──────────────────
        else:
            messagebox.showwarning(
                "Incomplete Date Range",
                "Please provide both From and To dates, or leave both empty."
            )
            return
    
                