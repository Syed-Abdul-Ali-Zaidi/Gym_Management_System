import customtkinter as ctk
from tkinter import ttk, messagebox
from config.ui_config import DATA_FRAME_UI, FORM_UI
from services.audit_service import (
    get_all_audit, search_audit,
    get_by_date_audit
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
        self.topbar_frame.grid_columnconfigure((1, 2, 3, 4), weight=0)        # buttons fixed

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

        # ── Status Filter Frame ──────────────────────────────────────────

        # Create a small label above the checkboxes
        ctk.CTkLabel(self.topbar_frame, text="Filter by Action:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=10)).grid(row=0, column=2, padx=4, pady=(1,0), sticky="w")

        # Creating a Dict of Filters where each filter name is a BooleanVar()
        filter_list = ["Insert", "Update", "Delete"]
        self.filters_var = {}

        for filter in filter_list:
            self.filters_var[filter] = ctk.BooleanVar(value=True)
        
        filter_frame = ctk.CTkFrame(self.topbar_frame, fg_color="transparent")
        filter_frame.grid(row=1, column=2, padx=2, pady=0, sticky="nsew")

        # Automatically arrange checkboxes, 2 per col
        for i, filter in enumerate(filter_list):
            row_idx = i % 2    # Modulo division:  0, 1, 0, 1
            col_idx = i // 2   # Integer division: 0, 0, 1, 1
            
            chk = ctk.CTkCheckBox(filter_frame, text=filter, font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size = 11), checkbox_height=15, checkbox_width=15, variable=self.filters_var[filter])
            chk.grid(row=row_idx, column=col_idx, padx=1, sticky=FORM_UI["entry_sticky"])
            
            # Attach trace directly to the checkbox variable
            self.filters_var[filter].trace_add("write", self._on_search)

        # # ── Add button ─────────────────────────────────────────────────
        # self.add_btn = ctk.CTkButton(
        #     self.topbar_frame,
        #     text="+ Add New",
        #     width=DATA_FRAME_UI['topbar_btn_width'],
        #     height=DATA_FRAME_UI['btn_height'],
        #     font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
        #     fg_color=DATA_FRAME_UI['btn_fg'],
        #     border_width=DATA_FRAME_UI['btn_border'],
        #     hover_color=DATA_FRAME_UI['btn_hover'],
        #     text_color=DATA_FRAME_UI['btn_text'],
        #     command=self._on_add
        # )
        # self.add_btn.grid(row=1, column=2, padx=4, pady=(1,6))

        # ── Date Filter Section (Replaces Add Button) ──────────────────
        self.date_filter_frame = ctk.CTkFrame(self.topbar_frame, fg_color="transparent")
        self.date_filter_frame.grid(row=0, column=3, rowspan=2, padx=2, pady=(1,6))

        # Variables
        self.from_date_var = ctk.StringVar()
        self.to_date_var = ctk.StringVar()

        ctk.CTkLabel(self.date_filter_frame, text="From Date:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=1)
        ctk.CTkLabel(self.date_filter_frame, text="To Date:", font=ctk.CTkFont(size=12)).grid(row=1, column=0, padx=1)       


        # From Date Entry
        self.from_entry = ctk.CTkEntry(
            self.date_filter_frame,
            width=100,
            height=DATA_FRAME_UI['btn_height'],
            placeholder_text="DD-MM-YYYY",
            textvariable=self.from_date_var
        )
        self.from_entry.grid(row=0, column=1, padx=1)


        # To Date Entry
        self.to_entry = ctk.CTkEntry(
            self.date_filter_frame,
            width=100,
            height=DATA_FRAME_UI['btn_height'],
            placeholder_text="DD-MM-YYYY",
            textvariable=self.to_date_var
        )
        self.to_entry.grid(row=1, column=1, padx=1)

        # Apply Filter Button (Small icon version to save space)
        self.apply_date_btn = ctk.CTkButton(
            self.date_filter_frame,
            text="📅 Filter",
            width=70,
            height=DATA_FRAME_UI['btn_height'],
            fg_color=DATA_FRAME_UI['btn_fg'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            command=self._on_date_filter
        )
        self.apply_date_btn.grid(row=0, column=3, padx=(1, 2))

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
        self.export_btn.grid(row=1, column=4, padx=(4,6), pady=(1,6))


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
            




    def _on_search(self,  *args):
        search_term = self.searchbar_var.get().strip()
        search_term = search_term.upper()

        # Getting Ticked Filters
        # Create a list of the names of all checked status
        selected_filter = [filter for filter, var in self.filters_var.items() if var.get()]
        
        # if there is no SearchTerm, Load Normal Data
        if not search_term:
            rows = search_audit(search_term, selected_filter)
            self._refresh_table(rows)
        # Else search the Data and load it
        else:
            if search_term.startswith("USR-"):
                search_term = search_term.replace("USR-","")
            rows = search_audit(search_term, selected_filter)
            self._refresh_table(rows)

        # Clear selection after every search
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


    # def _on_add(self):
    #     pass
        

    def _on_date_filter(self):
        from_date = self.from_date_var.get().strip()
        to_date = self.to_date_var.get().strip()

        # 1. Basic validation: If both are empty, just reload all
        if not from_date and not to_date:
            self.load_data()
            return

        # 2. Simple format check (you can make this more robust with datetime)
        if len(from_date) != 10 or len(to_date) != 10:
            messagebox.showwarning("Invalid Date", "Please use DD-MM-YYYY format.")
            return

        # 3. Call service
        # Note: Your service 'get_by_date_audit' should handle the DB query
        rows = get_by_date_audit(from_date, to_date)
        
        if rows is not None:
            self._refresh_table(rows)
            self.selection_label.configure(text=f"Showing results from {from_date} to {to_date}")
        else:
            messagebox.showerror("Error", "Could not fetch data for these dates.")


            