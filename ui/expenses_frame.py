import customtkinter as ctk
from tkinter import ttk, messagebox
from config.ui_config import DATA_FRAME_UI, FORM_UI
from services.expense_service import (
    get_all_expense, search_expense, update_expense, get_trainer_data,
    insert_salary, insert_operational, delete_expense
)
from ui.excel_file_maker import export_to_excel

class ExpensesFrame(ctk.CTkFrame):
    def __init__(self, content_area):
        super().__init__(content_area, fg_color="transparent")

        self.grid_rowconfigure(0, weight=0)  # topbar
        self.grid_rowconfigure(1, weight=1)  # table expands
        self.grid_rowconfigure(2, weight=0)  # action bar
        self.grid_columnconfigure(0, weight=1)

        # ── Instance variables ─────────────────────────────
        self.selected_row = None  # stores selected row as dict
        self.form_mode    = None  # "add" or "edit"
        self.is_updating_filters = False    # Flag is True when search is runnig

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
        self.topbar_frame.grid_columnconfigure((1, 2, 3, 4, 5), weight=0)        # buttons fixed


        # ── Search entry ───────────────────────────────────────────────
        ctk.CTkLabel(self.topbar_frame, text="Search by Member ID or Member Name or Plan ID", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=10)).grid(row=0, column=0, padx=(6,4), pady=(1,0), sticky="w")

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
        ctk.CTkLabel(self.topbar_frame, text="Filter by Type:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=10)).grid(row=0, column=2, padx=4, pady=(1,0), sticky="w")

        # Creating a Dict of Filters where each filter name is a BooleanVar()
        filter_s_list = ["Operational", "Salary"]
        self.filters_s_var = {}

        for filter in filter_s_list:
            self.filters_s_var[filter] = ctk.BooleanVar(value=True)
        
        filter_s_frame = ctk.CTkFrame(self.topbar_frame, fg_color="transparent")
        filter_s_frame.grid(row=1, column=2, padx=2, pady=0, sticky="nsew")

        # Automatically arrange checkboxes, 2 per col
        for i, filter in enumerate(filter_s_list):
            row_idx = i % 2    # Modulo division:  0, 1, 0, 1
            col_idx = i // 2   # Integer division: 0, 0, 1, 1
            
            chk = ctk.CTkCheckBox(filter_s_frame, text=filter, font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size = 11), checkbox_height=15, checkbox_width=15, variable=self.filters_s_var[filter])
            chk.grid(row=row_idx, column=col_idx, padx=1, sticky=FORM_UI["entry_sticky"])
            
            # Attach trace directly to the checkbox variable
            self.filters_s_var[filter].trace_add("write", self._on_search)

        # ── Operational_type Filter Frame ──────────────────────────────────────────

        # Create a small label above the checkboxes
        ctk.CTkLabel(self.topbar_frame, text="Filter by expense Method:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=10)).grid(row=0, column=3, padx=4, pady=(1,0), sticky="w")

        # Creating a Dict of Filters where each filter name is a BooleanVar()
        filter_m_list = ["Utility_Bills", "Rent", "Marketing&Sales", "Maintenance&Supplies"]
        self.filters_m_var = {}

        for filter in filter_m_list:
            self.filters_m_var[filter] = ctk.BooleanVar(value=True)
        
        filter_m_frame = ctk.CTkFrame(self.topbar_frame, fg_color="transparent")
        filter_m_frame.grid(row=1, column=3, padx=2, pady=0, sticky="nsew")


            
        self.ub_checkbox = ctk.CTkCheckBox(filter_m_frame, text='Utility_Bills', font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size = 11), checkbox_height=15, checkbox_width=15, variable=self.filters_m_var['Utility_Bills'])
        self.ub_checkbox.grid(row=0, column=0, padx=1, sticky=FORM_UI["entry_sticky"])

        self.rent_checkbox = ctk.CTkCheckBox(filter_m_frame, text='Rent', font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size = 11), checkbox_height=15, checkbox_width=15, variable=self.filters_m_var['Rent'])
        self.rent_checkbox.grid(row=1, column=0, padx=1, sticky=FORM_UI["entry_sticky"])

        self.msales_checkbox = ctk.CTkCheckBox(filter_m_frame, text='Marketing&Sales', font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size = 11), checkbox_height=15, checkbox_width=15, variable=self.filters_m_var['Marketing&Sales'])
        self.msales_checkbox.grid(row=2, column=0, padx=1, sticky=FORM_UI["entry_sticky"])

        self.msupplies_checkbox = ctk.CTkCheckBox(filter_m_frame, text='Maintenance&Supplies', font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size = 11), checkbox_height=15, checkbox_width=15, variable=self.filters_m_var['Maintenance&Supplies'])
        self.msupplies_checkbox.grid(row=3, column=0, padx=1, sticky=FORM_UI["entry_sticky"])

        # Attach trace directly to the checkbox variable
        self.filters_m_var['Utility_Bills'].trace_add("write", self._on_search)
        self.filters_m_var['Rent'].trace_add("write", self._on_search)
        self.filters_m_var['Marketing&Sales'].trace_add("write", self._on_search)
        self.filters_m_var['Maintenance&Supplies'].trace_add("write", self._on_search)

        # ── Add button ─────────────────────────────────────────────────
        self.add_btn = ctk.CTkButton(
            self.topbar_frame,
            text="+ Add New",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=self._on_add
        )
        self.add_btn.grid(row=1, column=4, padx=4, pady=(1,6))

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
        self.export_btn.grid(row=1, column=5, padx=(4,6), pady=(1,6))


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

        # ── Table Section ───────────────────────────────────────
        self.table = ttk.Treeview(self.table_frame, columns= ('expense_id', 'amount', 'expense_date', 'type', 'category', 'trainer_id', 'trainer_name'), show= 'headings', selectmode="browse")
        self.table.heading('expense_id',   text= 'Expense ID')
        self.table.heading('amount',       text= 'Amount')
        self.table.heading('expense_date', text= 'Expense Date')
        self.table.heading('type',         text= 'Expense Type')
        self.table.heading('category',     text= 'Operational Category')
        self.table.heading('trainer_id',   text= 'Trainer ID')
        self.table.heading('trainer_name', text= 'Trainer Name')


        # Column widths
        self.table.column('expense_id',   width=150, minwidth=150, anchor='center')
        self.table.column('amount',       width=200, minwidth=200, anchor='center')
        self.table.column('expense_date', width=150, minwidth=150, anchor='center')
        self.table.column('type',         width=200, minwidth=200, anchor='center')
        self.table.column('category',     width=250, minwidth=250, anchor='center')
        self.table.column('trainer_id',   width=150, minwidth=150, anchor='center')
        self.table.column('trainer_name', width=200, minwidth=200, anchor='center')


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
        self.scrollbarx.grid(row=1, column=0, sticky='ew')   # row 1, stretches horizontal only

        # ── ActionBar Section ──────────────────────────────────────────
        self.action_bar = ctk.CTkFrame(self, height=DATA_FRAME_UI['actionbar_height'])
        self.action_bar.grid(row=2, column=0, sticky="ew", padx=DATA_FRAME_UI['padding_x'], pady=DATA_FRAME_UI['padding_y'])

        self.action_bar.grid_columnconfigure(0, weight=1)
        self.action_bar.grid_columnconfigure(1, weight=0)
        self.action_bar.grid_columnconfigure(2, weight=0)

        self.selection_label = ctk.CTkLabel(self.action_bar, text='No Row Selected')
        self.selection_label.grid(row=0, column=0, sticky="w", padx=10, pady=8)

        # Edit button — disabled by default
        self.edit_btn = ctk.CTkButton(
            self.action_bar,
            text='✏ Edit',
            width=DATA_FRAME_UI['actionbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            state="disabled",
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['edit_fg'],
            hover_color=DATA_FRAME_UI['edit_hover'],
            text_color=DATA_FRAME_UI['edit_text'],
            border_width=DATA_FRAME_UI['btn_border'],
            command=self._on_edit
        )
        self.edit_btn.grid(row=0, column=1, padx=4, pady=8)

        # Delete button — red tint, disabled by default
        self.delete_btn = ctk.CTkButton(
            self.action_bar,
            text='🗑 Void',
            width=DATA_FRAME_UI['actionbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            state="disabled",
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['delete_fg'],
            hover_color=DATA_FRAME_UI['delete_hover'],
            text_color=DATA_FRAME_UI['delete_text'],
            border_width=DATA_FRAME_UI['btn_border'],
            command=self._on_delete
        )
        self.delete_btn.grid(row=0, column=2, padx=(4, 8), pady=8)





    def load_data(self):
        rows = get_all_expense()
        self._refresh_table(rows)

    def _refresh_table(self,rows):
        # Deletes existing rows
        self.table.delete(*self.table.get_children())
        
        # Creating Stripped row tags
        self.table.tag_configure('Operational', background=DATA_FRAME_UI['expense_op'])
        self.table.tag_configure('Salary', background=DATA_FRAME_UI['expense_sal'])

        # inserts New Data
        for row in rows:
            tag = row['type']

            formatted_exp_id = f'EXP-{row['expense_id']}'
            formatted_exp_date = row['expense_date'].strftime("%d-%m-%Y")
            if row['trainer_id'] is not None:
                formatted_trn_id = f'TRN-{row["trainer_id"]}'
            else:
                formatted_trn_id = ''

            self.table.insert(parent='', index= 'end', values=(
                formatted_exp_id,
                row['amount'],
                formatted_exp_date,
                row['type'],
                row['category'],
                formatted_trn_id,
                row['trainer_name'] or ''),
                tags= (tag,)
            )
            




    def _on_search(self,  *args):
        # If we are already in the middle of updating filters, stop here
        if self.is_updating_filters:
            return
        
        search_term = self.searchbar_var.get().strip()
        search_term = search_term.upper()

        # START MUTING TRACES
        self.is_updating_filters = True
        try:
            # 1. Get the current intent of the Master checkbox
            operational_is_checked = self.filters_s_var["Operational"].get()
            
            # 2. If Master is ON -> Make sure sub-types are enabled
            if operational_is_checked:
                # If they were disabled, this was a fresh click on "Operational"
                # so we turn everything on by default.
                if self.ub_checkbox.cget("state") == "disabled":
                    self.filters_m_var["Utility_Bills"].set(True)
                    self.filters_m_var["Rent"].set(True)
                    self.filters_m_var["Marketing&Sales"].set(True)
                    self.filters_m_var["Maintenance&Supplies"].set(True)

                # Ensure they are interactive
                self.ub_checkbox.configure(state="normal")
                self.rent_checkbox.configure(state="normal")
                self.msales_checkbox.configure(state="normal")
                self.msupplies_checkbox.configure(state="normal")
                
                # FINAL SAFETY: If the user manually unchecked every sub-type 
                # WHILE Operational was already normal, then turn Operational OFF
                any_sub_on = any([
                    self.filters_m_var["Utility_Bills"].get(),
                    self.filters_m_var["Rent"].get(),
                    self.filters_m_var["Marketing&Sales"].get(),
                    self.filters_m_var["Maintenance&Supplies"].get()
                ])
                
                if not any_sub_on:
                    self.filters_s_var['Operational'].set(False)
                    self.ub_checkbox.configure(state="disabled")
                    self.rent_checkbox.configure(state="disabled")
                    self.msales_checkbox.configure(state="disabled")
                    self.msupplies_checkbox.configure(state="disabled")

            # 3. If Master is OFF -> Force everything else OFF and Disabled
            else:
                self.filters_m_var["Utility_Bills"].set(False)
                self.filters_m_var["Rent"].set(False)
                self.filters_m_var["Marketing&Sales"].set(False)
                self.filters_m_var["Maintenance&Supplies"].set(False)

                self.ub_checkbox.configure(state="disabled")
                self.rent_checkbox.configure(state="disabled")
                self.msales_checkbox.configure(state="disabled")
                self.msupplies_checkbox.configure(state="disabled")

        finally:
            self.is_updating_filters = False

        # Getting Ticked Filters
        # ── Exp filters ────────────────────────────────────
        selected_exp_filters = [
            filter_name
            for filter_name, var in self.filters_s_var.items()
            if var.get()
        ]

        # ── OP type filters ────────────────────────────────────
        selected_op_type_filters = [
            filter_name
            for filter_name, var in self.filters_m_var.items()
            if var.get()
        ]

        # if there is no SearchTerm, Load Normal Data
        if search_term.startswith("EXP-"):
                search_term = search_term.replace("EXP-","")

        rows = search_expense(search_term, selected_exp_filters, selected_op_type_filters)
        self._refresh_table(rows)

        # Clear selection after every search
        self.selected_row = None
        self.selection_label.configure(text='No row selected')
        self.edit_btn.configure(state='disabled')
        self.delete_btn.configure(state='disabled')



    def _on_row_select(self, event):
        column_names = ['expense_id', 'amount', 'expense_date', 'type', 'category', 'trainer_id', 'trainer_name']
        selected = self.table.selection()

        if not selected:
            self.selection_label.configure(text='No Row Selected')
            return None
        
        item_id = selected[0]
        values = self.table.item(item_id)["values"]
        self.selected_row = dict(zip(column_names, values))

        # Updating the Selection Label
        self.selection_label.configure(text= f'Expense ID: {self.selected_row['expense_id']}')

        # Enabling the Edit & Delere bottons
        self.edit_btn.configure(state='normal')
        self.delete_btn.configure(state='normal')
        


    def _on_delete(self):
        if self.selected_row is None:
            return
        
        # First ask for confirmation on Delete
        confirmed = messagebox.askyesno(title="Confirm", message="Void this expense?")
        if confirmed:
            exp_id = self.selected_row['expense_id'].replace("EXP-","")

            success = delete_expense(exp_id)

            if success:   # deletion Successful
                self.load_data()
                # reseting selected row
                self.selected_row = None

                self.selection_label.configure(text='No Row Selected')
                self.delete_btn.configure(state= 'disabled')
                self.edit_btn.configure(state= 'disabled')
            else:
                messagebox.showerror(title="Error", message="Could not Void the expense.")

    def _on_add(self):
        self._open_form('add')

    def _on_edit(self):
        if self.selected_row is None:
            return
        self._open_form('edit')

    def _open_form(self, mode):
        popup = ctk.CTkToplevel(self)
        popup.title("Add expense" if mode == "add" else "Edit")
        popup.geometry('370x280')
        popup.resizable(False, False) 

        # ── 1. Fetch & Structure Lookups ──────────────────────────────────────
        trainers_list = get_trainer_data()
        # Format: {"5": {"name": "John", "fee": 2000}}
        self.trainers = {str(t['trainer_id']): t for t in trainers_list}
        
        # Create StringVars here — they live as long as popup lives
        self.type_var          = ctk.StringVar(value="Operational")
        self.amount_var        = ctk.StringVar(value="0")
        self.expense_date_var  = ctk.StringVar()
        self.category_var      = ctk.StringVar(value="Select Category")
        self.trn_selection_var = ctk.StringVar(value="Select Trainer")


        
        # Pass popup to field builder
        self._build_form_fields(popup)
        self._build_form_buttons(popup, mode)

        if mode == 'add':
            # Set default expense date for 'add' mode
            from datetime import datetime
            self.expense_date_var.set(datetime.now().strftime("%d-%m-%Y"))

        if mode == 'edit':
            # Type is IMMUTABLE - can't change Operational to Salary
            self.amount_var.set(self.selected_row['amount'])
            self.expense_date_var.set(self.selected_row['expense_date'])

            exp_type = self.selected_row['type']
            self.type_var.set(exp_type)
            self.type_toggle.configure(state='disabled')
           
            
            # Category/Trainer also IMMUTABLE
            if exp_type == 'Salary':
                trn_id = str(self.selected_row['trainer_id']).replace("TRN-","")
                trn_name = self.selected_row['trainer_name']

                self.trn_selection_var.set(f'TRN-{trn_id} - {trn_name}')
                # now disable it
                self.trainer_dropdown.configure(state = 'disabled')
            else:
                category = self.selected_row['category']
                self.category_var.set(category)
                self.category_dropdown.configure(state = 'disabled')
        
        popup.grab_set()    # User CANNOT click anything in the main window until popup closes
        popup.transient(self.winfo_toplevel())    # Popup won't go behind the main window

        

    def _build_form_fields(self, popup):
        form_frame = ctk.CTkFrame(popup)
        form_frame.grid(row=0, column=0, padx=FORM_UI['padx'], pady=FORM_UI['pady'])

        self.type_toggle = ctk.CTkSegmentedButton(form_frame, values=["Operational", "Salary"], variable=self.type_var, command=self._on_type_change)
        self.type_toggle.grid(row=0, column=0, columnspan = 2, padx=10, pady=(5,FORM_UI['row_pady']), sticky='nsew')
        # Row 0 - Name
        ctk.CTkLabel(form_frame, text="Plaese Enter expense Details:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=1, column=0, columnspan = 2, padx=10, pady=(5,FORM_UI['row_pady']), sticky=FORM_UI["label_sticky"])
        
        # Row 1 - Trainer (Dropdown)
        self.trainer_label = ctk.CTkLabel(form_frame, text="Trainer:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']))
        self.trainer_label.grid(row=2, column=0, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        # Create "ID - Name" list for dropdown from your dictionary
        trainer_options = ["Select Trainer"] + [f"{tid} - {t['name']}" for tid, t in self.trainers.items()]
        self.trainer_dropdown = ctk.CTkOptionMenu(form_frame, variable=self.trn_selection_var, values=trainer_options, text_color='black', fg_color= DATA_FRAME_UI['btn_fg'], dropdown_hover_color= DATA_FRAME_UI['btn_hover'])
        self.trainer_dropdown.grid(row=2, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])
        
        # Row 1 - Operational Type (Dropdown)
        self.category_label = ctk.CTkLabel(form_frame, text="Operational Expense\nType:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']))
        self.category_label.grid(row=2, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        self.category_dropdown = ctk.CTkOptionMenu(form_frame, variable=self.category_var, values=["Select Category", "Utility_Bills", "Rent", "Marketing&Sales", "Maintenance&Supplies"], text_color='black', fg_color= DATA_FRAME_UI['btn_fg'], dropdown_hover_color= DATA_FRAME_UI['btn_hover'])
        self.category_dropdown.grid(row=2, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

        # Row 2 - Amount
        ctk.CTkLabel(form_frame, text="Amount:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=3, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        ctk.CTkEntry(form_frame, textvariable=self.amount_var).grid(row=3, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

        # Row 3 - Expense Dates
        ctk.CTkLabel(form_frame, text="expense Date:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=4, column=0, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        self.expense_date_entry = ctk.CTkEntry(form_frame, textvariable=self.expense_date_var)
        self.expense_date_entry.grid(row=4, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

        # Row 4 - Error message
        self.error_label = ctk.CTkLabel(form_frame, text="", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),  text_color=FORM_UI['error_color'])
        self.error_label.grid(row=5, column=0, columnspan=2)

        # Add trainer trace
        self.trn_selection_var.trace_add("write", self._on_trainer_change)

        # Addinh traces to Each Variable. means calling a function whenever variable's value changes
        self.trn_selection_var.trace_add("write", self._validate)
        self.category_var.trace_add("write", self._validate)
        self.amount_var.trace_add("write", self._validate)
        self.expense_date_var.trace_add("write", self._validate)



    def _build_form_buttons(self, popup, mode):
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=(0, FORM_UI['btn_pady_bottom']))


        self.save_btn = ctk.CTkButton(btn_frame, text="Save", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']), width=FORM_UI['btn_width'], border_width=DATA_FRAME_UI['btn_border'], fg_color=DATA_FRAME_UI['btn_fg'], hover_color=DATA_FRAME_UI['btn_hover'],state='disabled', text_color=DATA_FRAME_UI['btn_text'], command= lambda: self._on_save(popup,mode))
        self.save_btn.pack(side="left", padx=FORM_UI['btn_padx'])

        self.cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']), width=FORM_UI['btn_width'], border_width=DATA_FRAME_UI['btn_border'], fg_color=DATA_FRAME_UI['btn_fg'], hover_color=DATA_FRAME_UI['btn_hover'], text_color=DATA_FRAME_UI['btn_text'], command= popup.destroy)
        self.cancel_btn.pack(side="left", padx=FORM_UI['btn_padx'])


    def _on_type_change(self, value):
        """Toggle between category and trainer fields."""
        print("VALUE:",value)
        if value == "Operational":
            # Grid Operational and forget Trainer
            self.category_label.grid(row=2, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
            self.category_dropdown.grid(row=2, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

            self.trainer_label.grid_forget()
            self.trainer_dropdown.grid_forget()

        else:
            self.trainer_label.grid(row=2, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
            self.trainer_dropdown.grid(row=2, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])

            self.category_label.grid_forget()
            self.category_dropdown.grid_forget()

    def _on_trainer_change(self, *args):
        trn_selection = self.trn_selection_var.get()
        if " - " in trn_selection:
            # 1. Extract the ID part (e.g., "TRN-2")
            raw_id = trn_selection.split(" - ")[0]
            # 2. STRIP the prefix to get just the number (e.g., "2")
            trainer_id = raw_id.replace("TRN-", "")

            if trainer_id in self.trainers:
                sal = self.trainers[trainer_id]['salary']
                self.amount_var.set(str(sal))
        else:
            self.amount_var.set('0')


    def _validate(self, *args):
        from datetime import datetime
        amount     = self.amount_var.get().strip()
        expense_date = self.expense_date_var.get().strip()
        exp_type = self.type_var.get().strip()

        if exp_type == "Operational":
            category = self.category_var.get().strip()
            if category not in ['Utility_Bills', 'Rent', 'Marketing&Sales', 'Maintenance&Supplies']:
                self._form_error("⚠ Please select a category")
                return
        else:
            trainer = self.trn_selection_var.get().strip()
            if trainer == "Select Trainer":
                self._form_error("⚠ Please select a trainer")
                return

        # Required: salary
        if not self.is_float(amount):
            self._form_error("⚠ Please enter Salary in numbers only.")
            return

        # Required: Expense Date
        try:
            datetime.strptime(expense_date, "%d-%m-%Y")
        except ValueError:
            self._form_error("⚠ Start Date must be valid DD-MM-YYYY.")
            return

        # All passed
        self._form_ok()

    def _form_error(self, message):
        """Show error and disable Save."""
        self.error_label.configure(text= message)
        self.save_btn.configure(state="disabled")

    def _form_ok(self):
        """Clear error and enable Save."""
        self.error_label.configure(text= '')
        self.save_btn.configure(state="normal")


    def _on_save(self, popup, mode):
        from datetime import datetime
        
        expense_type = self.type_var.get()
        amount = self.amount_var.get()
        formatted_expense_date = self.expense_date_var.get()
        expense_date = datetime.strptime(formatted_expense_date, "%d-%m-%Y").strftime("%Y-%m-%d")   
        

        if mode == 'add':
            if expense_type == "Operational":
                category = self.category_var.get()
                success = insert_operational(amount, expense_date, category)
            else:
                trn_selection = self.trn_selection_var.get()
                # 1. Get "TRN-1"
                raw_trn_id = trn_selection.split(" - ")[0]
                # 2. Convert "TRN-1" -> "1"
                trainer_id = raw_trn_id.replace("TRN-", "")

                success = insert_salary(amount, expense_date, trainer_id)
        else:
            # Edit - type doesn't matter, only update base fields
            formatted_exp_id = self.selected_row['expense_id']
            clean_exp_id = str(formatted_exp_id).replace("EXP-","")
            success = update_expense(clean_exp_id, amount, expense_date)

        if success:
            popup.destroy()
            self.selected_row = None
            self.load_data()   
            self.selection_label.configure(text='No Row Selected')
            self.edit_btn.configure(state='disabled')
        else:
            messagebox.showerror(title="Error", message=f"Could not {mode} expense. Check inputs or DB connection.")

    def is_float(self, value):
        try:
            float(value) and (float(value) > 0)
            return True
        except ValueError:
            return False


    def _on_export(self):
        # Check if table has any rows
        if not self.table.get_children():
            messagebox.showwarning(title="Empty", message="No data to export.")
            return
        
        export_to_excel(tree=self.table, default_filename="expenses_export")
