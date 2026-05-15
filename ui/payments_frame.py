import customtkinter as ctk
from tkinter import ttk, messagebox
from config.ui_config import DATA_FRAME_UI, FORM_UI
from services.payment_service import (
    get_all_payment, search_payment,
    insert_payment, delete_payment
)
from ui.excel_file_maker import export_to_excel

class PaymentsFrame(ctk.CTkFrame):
    def __init__(self, content_area):
        super().__init__(content_area, fg_color=DATA_FRAME_UI['content_bg_color'], border_width=2)

        self.grid_rowconfigure(0, weight=0)  # topbar
        self.grid_rowconfigure(1, weight=1)  # table expands
        self.grid_rowconfigure(2, weight=0)  # action bar
        self.grid_columnconfigure(0, weight=1)

        # ── Instance variables ─────────────────────────────
        self.selected_row = None  # stores selected row as dict
        self.form_mode    = None  # "add" or "edit"

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

       # ── Vertical Separatoe ───────────────────────────────────────────
        self.create_vertical_separator(self.topbar_frame, column= 2)

        # ── Status Filter Frame ──────────────────────────────────────────

        # Create a small label above the checkboxes
        ctk.CTkLabel(self.topbar_frame, text="Filter by Status:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=10)).grid(row=0, column=3, padx=4, pady=(1,0), sticky="w")

        # Creating a Dict of Filters where each filter name is a BooleanVar()
        filter_s_list = ["Paid", "Unpaid"]
        self.filters_s_var = {}

        for filter in filter_s_list:
            self.filters_s_var[filter] = ctk.BooleanVar(value=True)
        
        filter_s_frame = ctk.CTkFrame(self.topbar_frame, fg_color="transparent")
        filter_s_frame.grid(row=1, column=3, padx=2, pady=0, sticky="nsew")

        # Automatically arrange checkboxes, 2 per col
        for i, filter in enumerate(filter_s_list):
            row_idx = i % 2    # Modulo division:  0, 1, 0, 1
            col_idx = i // 2   # Integer division: 0, 0, 1, 1
            
            chk = ctk.CTkCheckBox(filter_s_frame, text=filter, font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size = 11), checkbox_height=15, checkbox_width=15, variable=self.filters_s_var[filter])
            chk.grid(row=row_idx, column=col_idx, padx=1, sticky=FORM_UI["entry_sticky"])
            
            # Attach trace directly to the checkbox variable
            self.filters_s_var[filter].trace_add("write", self._on_search)

       # ── Vertical Separatoe ───────────────────────────────────────────
        self.create_vertical_separator(self.topbar_frame, column= 4)

        # ── Method Filter Frame ──────────────────────────────────────────

        # Create a small label above the checkboxes
        ctk.CTkLabel(self.topbar_frame, text="Filter by Payment Method:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=10)).grid(row=0, column=5, padx=4, pady=(1,0), sticky="w")

        # Creating a Dict of Filters where each filter name is a BooleanVar()
        filter_m_list = ["Cash", "Card"]
        self.filters_m_var = {}

        for filter in filter_m_list:
            self.filters_m_var[filter] = ctk.BooleanVar(value=True)
        
        filter_m_frame = ctk.CTkFrame(self.topbar_frame, fg_color="transparent")
        filter_m_frame.grid(row=1, column=5, padx=2, pady=0, sticky="nsew")


            
        self.cash_checkbox = ctk.CTkCheckBox(filter_m_frame, text='Cash', font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size = 11), checkbox_height=15, checkbox_width=15, variable=self.filters_m_var['Cash'])
        self.cash_checkbox.grid(row=0, column=0, padx=1, sticky=FORM_UI["entry_sticky"])

        self.card_checkbox = ctk.CTkCheckBox(filter_m_frame, text='Card', font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size = 11), checkbox_height=15, checkbox_width=15, variable=self.filters_m_var['Card'])
        self.card_checkbox.grid(row=1, column=0, padx=1, sticky=FORM_UI["entry_sticky"])
        
        # Attach trace directly to the checkbox variable
        self.filters_m_var['Cash'].trace_add("write", self._on_search)
        self.filters_m_var['Card'].trace_add("write", self._on_search)

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
        self.export_btn.grid(row=0, column=7, padx=(4,6), pady=(6,1))

         # ── Refresh button ───────────────────────────────────────
        refresh_btn = ctk.CTkButton(
            self.topbar_frame,
            text="⭮ Refresh",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=self._on_search
        )
        refresh_btn.grid(row=1, column=7, padx=(4, 6), pady=(1,6))


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
        self.table = ttk.Treeview(self.table_frame, columns= ('member_id', 'member_name', 'plan_id', 'plan_name', 'start_date', 'payment_date', 'method', 'amount', 'payment_status'), show= 'headings', selectmode="browse")
        self.table.heading('member_id',      text= 'Member ID')
        self.table.heading('member_name',    text= 'Member Name')
        self.table.heading('plan_id',        text= 'Plan ID')
        self.table.heading('plan_name',      text= 'Plan Name')
        self.table.heading('start_date',     text= 'Membership Start Date')
        self.table.heading('payment_date',   text= 'Payment Date')
        self.table.heading('method',         text= 'Method')
        self.table.heading('amount',         text= 'Amount')
        self.table.heading('payment_status', text= 'Payment Status')

        # Column widths
        self.table.column('member_id',      width=150, minwidth=150, anchor='center')
        self.table.column('member_name',    width=250, minwidth=250)
        self.table.column('plan_id',        width=150, minwidth=150, anchor='center')
        self.table.column('plan_name',      width=200, minwidth=200)
        self.table.column('start_date',     width=250, minwidth=250, anchor='center')
        self.table.column('payment_date',   width=200, minwidth=200, anchor='center')
        self.table.column('method',         width=100, minwidth=100, anchor='center')
        self.table.column('amount',         width=200, minwidth=200, anchor='center')
        self.table.column('payment_status', width=200, minwidth=200, anchor='center')

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

        self.action_bar.grid_columnconfigure(0, weight=1)
        self.action_bar.grid_columnconfigure(1, weight=0)
        self.action_bar.grid_columnconfigure(2, weight=0)

        self.selection_label = ctk.CTkLabel(self.action_bar, text='No Row Selected')
        self.selection_label.grid(row=0, column=0, sticky="w", padx=10, pady=8)

        # Edit button — disabled by default
        self.edit_btn = ctk.CTkButton(
            self.action_bar,
            text='💵 Receive Payment',
            width=DATA_FRAME_UI['actionbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            state="disabled",
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            hover_color=DATA_FRAME_UI['edit_hover'],
            text_color=DATA_FRAME_UI['edit_text'],
            border_width=DATA_FRAME_UI['btn_border'],
            command=self._on_edit
        )
        self.edit_btn.grid(row=0, column=1, padx=4, pady=8)

        # Delete button — red tint, disabled by default
        self.delete_btn = ctk.CTkButton(
            self.action_bar,
            text='🔄 Void Payment',
            width=DATA_FRAME_UI['actionbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            state="disabled",
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            hover_color=DATA_FRAME_UI['delete_hover'],
            text_color=DATA_FRAME_UI['delete_text'],
            border_width=DATA_FRAME_UI['btn_border'],
            command=self._on_delete
        )
        self.delete_btn.grid(row=0, column=2, padx=(4, 8), pady=8)





    def load_data(self):
        rows = get_all_payment()
        self._refresh_table(rows)

    def _refresh_table(self,rows):
        # Deletes existing rows
        self.table.delete(*self.table.get_children())
        
        # Creating Stripped row tags
        self.table.tag_configure('Paid', background=DATA_FRAME_UI['payment_paid'])
        self.table.tag_configure('Unpaid', background=DATA_FRAME_UI['payment_unpaid'])

        # inserts New Data
        for row in rows:
            tag = row['payment_status']

            formatted_mem_id = f'MEM-{row['member_id']}'
            formatted_pln_id = f'PLN-{row['plan_id']}'
            formatted_start_date = row['start_date'].strftime("%d-%m-%Y")
            if row['payment_date']:
                formatted_payment_date = row['payment_date'].strftime("%d-%m-%Y")
            else:
                formatted_payment_date = row['payment_date']

            self.table.insert(parent='', index= 'end', values=(
                formatted_mem_id,
                row['member_name'],
                formatted_pln_id, 
                row['plan_name'],
                formatted_start_date,
                formatted_payment_date or '',
                row['method'] or '',
                row['amount'],
                row['payment_status']),
                tags= (tag,)
            )
            


    def _on_search(self,  *args):
        search_term = self.searchbar_var.get().strip()
        search_term = search_term.upper()

        # ── If Paid selected → enable Cash/Card ───────
        if self.filters_s_var["Paid"].get():
            
            # Only default-check both when they were previously disabled
            # (i.e. Paid was just turned ON). Preserves user's individual picks.
            if self.cash_checkbox.cget("state") == "disabled":
                self.filters_m_var["Cash"].set(True)
                self.filters_m_var["Card"].set(True)

            self.cash_checkbox.configure(state="normal")
            self.card_checkbox.configure(state="normal")

        else:

            self.filters_m_var["Cash"].set(False)
            self.filters_m_var["Card"].set(False)

            self.cash_checkbox.configure(state="disabled")
            self.card_checkbox.configure(state="disabled")

        # if No Method is Selected then Untick Paid check
        if  not (self.filters_m_var['Cash'].get() or self.filters_m_var['Card'].get()):
            self.filters_s_var['Paid'].set(False)


        # Getting Ticked Filters
        # ── Status filters ────────────────────────────────────
        selected_status_filters = [
            filter_name
            for filter_name, var in self.filters_s_var.items()
            if var.get()
        ]

        # ── Method filters ────────────────────────────────────
        selected_method_filters = [
            filter_name
            for filter_name, var in self.filters_m_var.items()
            if var.get()
        ]


        # if there is no SearchTerm, Load Normal Data
        if search_term.startswith("MEM-"):
                search_term = search_term.replace("MEM-","")

 
        rows = search_payment(search_term, selected_status_filters, selected_method_filters)
        self._refresh_table(rows)

        # Clear selection after every search
        self.selected_row = None
        self.selection_label.configure(text='No Row Selected')
        self.edit_btn.configure(state='disabled')
        self.delete_btn.configure(state='disabled')



    def _on_row_select(self, event):
        column_names = ['member_id', 'member_name', 'plan_id', 'plan_name', 'start_date', 'payment_date', 'method', 'amount', 'payment_status']
        selected = self.table.selection()

        if not selected:
            self.selection_label.configure(text='No Row Selected')
            return None
        
        item_id = selected[0]
        values = self.table.item(item_id)["values"]
        self.selected_row = dict(zip(column_names, values))

        # Updating the Selection Label
        self.selection_label.configure(text= f'Member ID: {self.selected_row['member_id']} | Plan ID: {self.selected_row['plan_id']} | Start Date: {self.selected_row['start_date']}')

        # Enabling the Edit & Delere bottons
        if self.selected_row['payment_status'] == 'Paid':
            self.delete_btn.configure(state='normal')
            self.edit_btn.configure(state='disabled')
        else:
            self.edit_btn.configure(state='normal')
            self.delete_btn.configure(state='disabled')
        


    def _on_delete(self):
        if self.selected_row is None:
            return
        
        from datetime import datetime
        
        # First ask for confirmation on Delete
        confirmed = messagebox.askyesno(title="Confirm", message="Void this Payment?")
        if confirmed:
            mem_id = self.selected_row['member_id'].replace("MEM-","")
            pln_id = self.selected_row['plan_id'].replace("PLN-", "")
            formatted_start_date = self.selected_row['start_date']
            start_date = datetime.strptime(formatted_start_date, "%d-%m-%Y").strftime("%Y-%m-%d")


            success = delete_payment(mem_id, pln_id, start_date)

            if success:   # deletion Successful
                self.load_data()
                # reseting selected row
                self.selected_row = None

                self.selection_label.configure(text='No Row Selected')
                self.delete_btn.configure(state= 'disabled')
                self.edit_btn.configure(state= 'disabled')
            else:
                messagebox.showerror(title="Error",
                                     message="Could not Void the Payment.\nThey may have an active membership."
                                    )



    def _on_edit(self):
        if self.selected_row is None:
            return
        self._open_form('edit')

    def _open_form(self, mode):
        popup = ctk.CTkToplevel(self)
        popup.title("Add payment" if mode == "add" else "Edit payment")
        popup.geometry('270x200')
        popup.resizable(False, False) 
        
        # Create StringVars here — they live as long as popup lives
        self.status_var     = ctk.StringVar(value="Select Method")
        self.payment_date_var = ctk.StringVar()

        
        # Pass popup to field builder
        self._build_form_fields(popup)
        self._build_form_buttons(popup, mode)

         # Set default Payment date for 'add' mode
        from datetime import datetime
        self.payment_date_var.set(datetime.now().strftime("%d-%m-%Y"))

        
        popup.grab_set()    # User CANNOT click anything in the main window until popup closes
        popup.transient(self.winfo_toplevel())    # Popup won't go behind the main window

        

    def _build_form_fields(self, popup):
        form_frame = ctk.CTkFrame(popup)
        form_frame.grid(row=0, column=0, padx=FORM_UI['padx'], pady=FORM_UI['pady'])

        # Row 0 - Name
        ctk.CTkLabel(form_frame, text="Plaese Select Payment Details:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=0, column=0, columnspan = 2, padx=10, pady=(5,FORM_UI['row_pady']), sticky=FORM_UI["label_sticky"])

        # Row 1 - Status (Dropdown)
        ctk.CTkLabel(form_frame, text="Method:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=1, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        ctk.CTkOptionMenu(form_frame, variable=self.status_var, values=["Select Method", "Cash", "Card"], text_color='black', fg_color= DATA_FRAME_UI['btn_fg'], dropdown_hover_color= DATA_FRAME_UI['btn_hover']).grid(row=1, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

        # Row 2 - Dates
        ctk.CTkLabel(form_frame, text="Payment Date:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=2, column=0, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        self.payment_date_entry = ctk.CTkEntry(form_frame, textvariable=self.payment_date_var)
        self.payment_date_entry.grid(row=2, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])


        # Row 3 - Error message
        self.error_label = ctk.CTkLabel(form_frame, text="", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),  text_color=FORM_UI['error_color'])
        self.error_label.grid(row=3, column=0, columnspan=2)

        # Addinh traces to Each Variable. means calling a function whenever variable's value changes
        self.status_var.trace_add("write", self._validate)
        self.payment_date_var.trace_add("write", self._validate)


    def _build_form_buttons(self, popup, mode):
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=(0, FORM_UI['btn_pady_bottom']))


        self.save_btn = ctk.CTkButton(btn_frame, text="Save", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']), width=FORM_UI['btn_width'], border_width=DATA_FRAME_UI['btn_border'], fg_color=DATA_FRAME_UI['btn_fg'], hover_color=DATA_FRAME_UI['btn_hover'],state='disabled', text_color=DATA_FRAME_UI['btn_text'], command= lambda: self._on_save(popup,mode))
        self.save_btn.pack(side="left", padx=FORM_UI['btn_padx'])

        self.cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']), width=FORM_UI['btn_width'], border_width=DATA_FRAME_UI['btn_border'], fg_color=DATA_FRAME_UI['btn_fg'], hover_color=DATA_FRAME_UI['btn_hover'], text_color=DATA_FRAME_UI['btn_text'], command= popup.destroy)
        self.cancel_btn.pack(side="left", padx=FORM_UI['btn_padx'])

    def _validate(self, *args):
        from datetime import datetime
        status         = self.status_var.get().strip()
        payment_date = self.payment_date_var.get().strip()


         # Required: status
        if status not in ('Cash', 'Card'):
            self._form_error("⚠ Please select a method.")
            return
        
        # 3. Start Date Safely Checked
        try:
            datetime.strptime(payment_date, "%d-%m-%Y")
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

        status    = self.status_var.get().strip()
        
        formatted_m_id = self.selected_row['member_id']
        member_id = formatted_m_id.replace("MEM-","")

        formatted_p_id = self.selected_row['plan_id']
        plan_id = formatted_p_id.replace("PLN-","")

        formatted_startdate = self.selected_row['start_date']
        start_date = datetime.strptime(formatted_startdate, "%d-%m-%Y").strftime("%Y-%m-%d")    

        formatted_payment_date = self.payment_date_var.get().strip()
        payment_date = datetime.strptime(formatted_payment_date, "%d-%m-%Y").date()

        success = insert_payment(member_id, plan_id, start_date, payment_date, status)
        
        if success:   # Insertion Successful
            popup.destroy()
            # reseting selected row
            self.selected_row = None

            self.load_data()   
            self.selection_label.configure(text='No Row Selected')
            self.edit_btn.configure(state= 'disabled')
        else:
            messagebox.showerror(title="Error",
                                 message=f"Could not Recieve payment. Check inputs or DB connection."
                                )


    def _on_export(self):
        # Check if table has any rows
        if not self.table.get_children():
            messagebox.showwarning(title="Empty", message="No data to export.")
            return
        
        export_to_excel(tree=self.table, default_filename="payments_export")

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
        