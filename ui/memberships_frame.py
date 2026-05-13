import customtkinter as ctk
from tkinter import ttk, messagebox
from config.ui_config import DATA_FRAME_UI, FORM_UI
from services.membership_service import (
    get_all_membership, search_membership, insert_membership,
    update_membership, delete_membership, get_membership_form_data, sync_statuses_membership
)
from ui.excel_file_maker import export_to_excel

class MembershipsFrame(ctk.CTkFrame):
    def __init__(self, content_area):
        super().__init__(content_area, fg_color="transparent")

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
        self.topbar_frame.grid_columnconfigure((1, 2, 3, 4, 5, 6), weight=0)        # buttons fixed


        # ── Search entry ───────────────────────────────────────────────
        ctk.CTkLabel(self.topbar_frame, text="Search by MembershipID or Member Name or PlanID or TrianerID", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=10)).grid(row=0, column=0, padx=(6,4), pady=(1,0), sticky="w")

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

        # ── start_date Filter Frame ──────────────────────────────────────────

        # Create a small label above the checkboxes
        ctk.CTkLabel(self.topbar_frame, text="Filter by start_date:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=10)).grid(row=0, column=3, padx=4, pady=(1,0), sticky="w")

        # Creating a Dict of Filters where each filter member_name is a BooleanVar()
        filter_list = ['Active', 'Expired', 'Cancelled', 'Upcoming']
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
            chk.grid(row=row_idx, column=col_idx, padx=1, sticky=FORM_UI["entry_sticky"])
            
            # Attach trace directly to the checkbox variable
            self.filters_var[filter].trace_add("write", self._on_search)

       # ── Vertical Separatoe ───────────────────────────────────────────
        self.create_vertical_separator(self.topbar_frame, column= 4)

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
        self.add_btn.grid(row=1, column=5, padx=4, pady=(1,6))

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
        self.export_btn.grid(row=1, column=6, padx=(4,6), pady=(1,6))


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
        self.table = ttk.Treeview(self.table_frame, columns= ('member_id', 'member_name', 'plan_id', 'plan_name', 'start_date', 'end_date', 'status', 'agreed_plan_fee', 'trainer_id', 'trainer_name', 'agreed_trainer_fee'), show= 'headings', selectmode="browse")
        self.table.heading('member_id',          text= 'Member ID')
        self.table.heading('member_name',        text= 'Member Name')
        self.table.heading('plan_id',            text= 'Plan ID')
        self.table.heading('plan_name',          text= 'Plan Name')
        self.table.heading('start_date',         text= 'Start Date')
        self.table.heading('end_date',           text= 'End Date')
        self.table.heading('status',             text= 'Status')
        self.table.heading('agreed_plan_fee',    text= 'Agreed Plan Fee')
        self.table.heading('trainer_id',         text= 'Trainer ID')
        self.table.heading('trainer_name',       text= 'Trainer Name')
        self.table.heading('agreed_trainer_fee', text= 'Agreed Trainer Fee')


        # Column widths
        self.table.column('member_id',          width=150, minwidth=150, anchor='center')
        self.table.column('member_name',        width=250, minwidth=250)
        self.table.column('plan_id',            width=150, minwidth=150, anchor='center')
        self.table.column('plan_name',          width=200, minwidth=200)
        self.table.column('start_date',         width=150, minwidth=150, anchor='center')
        self.table.column('end_date',           width=150, minwidth=150, anchor='center')
        self.table.column('status',             width=150, minwidth=150, anchor='center')
        self.table.column('agreed_plan_fee',    width=200, minwidth=200, anchor='center')
        self.table.column('trainer_id',         width=150, minwidth=150, anchor='center')
        self.table.column('trainer_name',       width=250, minwidth=250)
        self.table.column('agreed_trainer_fee', width=200, minwidth=200, anchor='center')


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
            text='🗑 Delete',
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
        sync_statuses_membership()
        rows = get_all_membership()
        self._refresh_table(rows)

    def _refresh_table(self,rows):
        # Deletes existing rows
        self.table.delete(*self.table.get_children())
        sync_statuses_membership()
        
        # Creating Stripped row tags
        self.table.tag_configure('Active', background=DATA_FRAME_UI['membership_active'])
        self.table.tag_configure('Expired', background=DATA_FRAME_UI['membership_expired'])
        self.table.tag_configure('Cancelled', background=DATA_FRAME_UI['membership_cancelled'])
        self.table.tag_configure('Upcoming', background=DATA_FRAME_UI['membership_upcoming'])

        # inserts New Data
        for row in rows:
            tag = row['status']

            formatted_mem_id = f'MEM-{row['member_id']}'
            formatted_pln_id = f'PLN-{row['plan_id']}'
            if row['trainer_id'] is not None:
                formatted_trn_id = f'TRN-{row["trainer_id"]}'
            else:
                formatted_trn_id = ''

            formatted_start_date = row['start_date'].strftime("%d-%m-%Y")
            formatted_end_date = row['end_date'].strftime("%d-%m-%Y")            

            self.table.insert(parent='', index= 'end', values=(
                formatted_mem_id,
                row['member_name'],
                formatted_pln_id,
                row['plan_name'],
                formatted_start_date,
                formatted_end_date,
                row['status'],
                row['agreed_plan_fee'],
                formatted_trn_id or '',  # if there is a NULL value Tree will show None so replace it with ""
                row['trainer_name'] or '',
                row['agreed_trainer_fee'] or ''),
                tags= (tag,)
            )
            




    def _on_search(self,  *args):
        search_term = self.searchbar_var.get().strip()
        search_term = search_term.upper()

        # Getting Ticked Filters
        # Create a list of the member_names of all checked start_date
        selected_filter = [filter for filter, var in self.filters_var.items() if var.get()]
        

        # if there is no SearchTerm, Load Normal Data
        if not search_term:
            rows = search_membership(search_term, selected_filter)
            self._refresh_table(rows)
        # Else search the Data and load it
        else:
            if search_term.startswith("MEM-"):
                search_term = search_term.replace("MEM-","")
            elif search_term.startswith("PLN-"):
                search_term = search_term.replace("PLN-","")
            elif search_term.startswith("TRN-"):
                search_term = search_term.replace("TRN-","")
            rows = search_membership(search_term, selected_filter)
            self._refresh_table(rows)

        # Clear selection after every search
        self.selected_row = None
        self.selection_label.configure(text='No row selected')
        self.edit_btn.configure(state='disabled')
        self.delete_btn.configure(state='disabled')

    def _on_row_select(self, event):
        column_member_names = ['member_id', 'member_name', 'plan_id', 'plan_name', 'start_date', 'end_date', 'status', 'agreed_plan_fee', 'trainer_id', 'trainer_name', 'agreed_trainer_fee']
        selected = self.table.selection()

        if not selected:
            self.selection_label.configure(text='No Row Selected')
            return None
        
        item_id = selected[0]
        values = self.table.item(item_id)["values"]
        self.selected_row = dict(zip(column_member_names, values))

        # Updating the Selection Label
        self.selection_label.configure(text= f'Member ID: {self.selected_row['member_id']} | Plan ID: {self.selected_row['plan_id']} | Start Date: {self.selected_row['start_date']}')

        # Enabling the Edit & Delere bottons
        self.edit_btn.configure(state='normal')
        self.delete_btn.configure(state='normal')


    def _on_delete(self):
        if self.selected_row is None:
            return
        
        from datetime import datetime
        
        # First ask for confirmation on Delete
        confirmed = messagebox.askyesno(title="Confirm", message="Delete this Member?")
        if confirmed:
            mem_id = self.selected_row['member_id'].replace("MEM-","")
            pln_id = self.selected_row['plan_id'].replace("PLN-", "")
            formatted_start_date = self.selected_row['start_date']
            start_date = datetime.strptime(formatted_start_date, "%d-%m-%Y").strftime("%Y-%m-%d")


            success = delete_membership(mem_id, pln_id, start_date)

            if success:   # deletion Successful
                self.load_data()
                # reseting selected row
                self.selected_row = None

                self.selection_label.configure(text='No Row Selected')
                self.delete_btn.configure(state= 'disabled')
                self.edit_btn.configure(state= 'disabled')
            else:
                messagebox.showerror(title="Error",
                                     message="Could not delete membership.\nKindly Void its payment first."
                                    )


    def _on_add(self):
        self._open_form('add')


    def _on_edit(self):
        if self.selected_row is None:
            return
        self._open_form('edit')

    def _open_form(self, mode):
        popup = ctk.CTkToplevel(self)
        popup.title("Add membership" if mode == "add" else "Edit membership")
        popup.geometry('400x370')
        popup.resizable(False, False) 
        
        # ── 1. Fetch & Structure Lookups ──────────────────────────────────────
        members_list, plans_list, trainers_list = get_membership_form_data()

       # 2. Build your specialized Lookups
        # Format: {"1": {"name": "Ali", ...}}
        self.members = {str(m['member_id']): m for m in members_list}
        
        # Format: {"101": {"plan_name": "Gold", "fee": 5000, "duration_days": 30}}
        self.plans = {str(p['plan_id']): p for p in plans_list}
        
        # Format: {"5": {"name": "John", "fee": 2000}}
        self.trainers = {str(t['trainer_id']): t for t in trainers_list}

        # ── 2. Initialize Variables ───────────────────────────────────────────
        self.mem_id_var             = ctk.StringVar()
        self.mem_name_var           = ctk.StringVar(value="Not Found")
        self.pln_selection_var      = ctk.StringVar(value="Select Plan")
        self.start_date_var         = ctk.StringVar()
        self.end_date_var           = ctk.StringVar()
        self.status_var             = ctk.StringVar()
        self.agreed_plan_fee_var    = ctk.StringVar(value="0")
        self.trn_selection_var      = ctk.StringVar(value="No Trainer")
        self.agreed_trainer_fee_var = ctk.StringVar(value="0")

        # Set default start date for 'add' mode
        from datetime import datetime
        self.start_date_var.set(datetime.now().strftime("%d-%m-%Y"))

        # ── 3. Build UI ───────────────────────────────────────────────────────
        self._build_form_fields(popup)
        self._build_form_buttons(popup, mode)

        self.form_mode = mode

        if mode == 'add':
            self.status_menu.configure(state='disabled')
            self.status_var.set('Auto')

        # ── 4. Edit Mode Logic ───────────────────────────────────────────────
        if mode == 'edit':
            # Pre-fill variables from the selected row dictionary
            self.mem_id_var.set(str(self.selected_row['member_id']))
            self.mem_name_var.set(self.selected_row['member_name'])
            
            formatted_plan_name = f'{self.selected_row['plan_id']} - {self.selected_row['plan_name']}'
            self.pln_selection_var.set(formatted_plan_name)
            
            self.start_date_var.set(self.selected_row['start_date'])
            self.end_date_var.set(self.selected_row['end_date'])
            if self.selected_row['status'] == "Cancelled":
                self.status_var.set("Cancelled")
            else:
                self.status_var.set("Current Status")
            self.agreed_plan_fee_var.set(str(self.selected_row['agreed_plan_fee']) or '0')
            
            if self.selected_row.get('trainer_id'):
                formatted_trainer_name = f'{self.selected_row['trainer_id']} - {self.selected_row['trainer_name']}'
                self.trn_selection_var.set(formatted_trainer_name)
                self.agreed_trainer_fee_var.set(str(self.selected_row['agreed_trainer_fee']) or '0')

            # DISABLE specified fields in Edit Mode
            # Ensure these names match the widget references in _build_form_fields
            self.mem_entry.configure(state='disabled', text_color="#9E9E9E")
            self.plan_menu.configure(state='disabled', text_color="#9E9E9E")
            self.start_entry.configure(state='disabled', text_color="#9E9E9E")
            # Note: end_date_entry should be disabled in BOTH modes (auto-filled only)
        
        # # End Date is always disabled as it's auto-calculated
        # self.end_date_entry.configure(state='disabled', text_color="#9E9E9E")

        popup.grab_set()
        popup.transient(self.winfo_toplevel())
        

    def _build_form_fields(self, popup):
            form_frame = ctk.CTkFrame(popup)
            form_frame.grid(row=0, column=0, padx=20, pady=10)

            # Row 0 - Member Selection
            ctk.CTkLabel(form_frame, text="Member ID:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=0, column=0, padx=10, pady=(5,FORM_UI['row_pady']), sticky=FORM_UI["label_sticky"])
            self.mem_entry = ctk.CTkEntry(form_frame, textvariable=self.mem_id_var, width=80)
            self.mem_entry.grid(row=0, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])
            # Name label next to ID
            ctk.CTkLabel(form_frame, textvariable=self.mem_name_var, font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=11, slant="italic")).grid(row=0, column=2, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

            # Row 1 - Plan Dropdown
            ctk.CTkLabel(form_frame, text="Plan:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=1, column=0, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
            # Create "ID - Name" list for dropdown from your dictionary
            plan_options = ["No plan"] + [f"{pid} - {p['plan_name']}" for pid, p in self.plans.items()]
            self.plan_menu = ctk.CTkOptionMenu(form_frame, variable=self.pln_selection_var, values=plan_options, text_color='black', fg_color= DATA_FRAME_UI['btn_fg'], dropdown_hover_color= DATA_FRAME_UI['btn_hover'])
            self.plan_menu.grid(row=1, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

            # Row 2 3 - Dates
            ctk.CTkLabel(form_frame, text="Start Date:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=2, column=0, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
            self.start_entry = ctk.CTkEntry(form_frame, textvariable=self.start_date_var)
            self.start_entry.grid(row=2, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

            ctk.CTkLabel(form_frame, text="End Date:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=3, column=0, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
            # This is the disabled entry you requested
            self.end_entry = ctk.CTkEntry(form_frame, textvariable=self.end_date_var, state="disabled", text_color="#9E9E9E")
            self.end_entry.grid(row=3, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

            # Row 4 - Status (Dropdown)
            ctk.CTkLabel(form_frame, text="Status:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=4, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
            self.status_menu = ctk.CTkOptionMenu(form_frame, variable=self.status_var, values=["Current Status", "Cancelled"], text_color='black', fg_color= DATA_FRAME_UI['btn_fg'], dropdown_hover_color= DATA_FRAME_UI['btn_hover'])
            self.status_menu.grid(row=4, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])
                
            # Row 5 - Agreed_plan_fee
            ctk.CTkLabel(form_frame, text="Agreed Plan Fee:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=5, column=0, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
            self.agreed_plnfee_entry = ctk.CTkEntry(form_frame,state='disabled', text_color="#9E9E9E", textvariable=self.agreed_plan_fee_var)
            self.agreed_plnfee_entry.grid(row=5, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

            # Row 6 - Trainer (Dropdown)
            ctk.CTkLabel(form_frame, text="Trainer:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=6, column=0, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
            # Create "ID - Name" list for dropdown from your dictionary
            trainer_options = ["No Trainer"] + [f"{tid} - {t['name']}" for tid, t in self.trainers.items()]
            self.trainer_menu = ctk.CTkOptionMenu(form_frame, variable=self.trn_selection_var, values=trainer_options, text_color='black', fg_color= DATA_FRAME_UI['btn_fg'], dropdown_hover_color= DATA_FRAME_UI['btn_hover'])
            self.trainer_menu.grid(row=6, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

            # Row 7 - Agreed_trainer_fee
            ctk.CTkLabel(form_frame, text="Agreed Trainer Fee:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=7, column=0, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
            self.agreed_trnfee_entry = ctk.CTkEntry(form_frame,state='disabled', text_color="#9E9E9E", textvariable=self.agreed_trainer_fee_var)
            self.agreed_trnfee_entry.grid(row=7, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

            # Row 8 - Error message ──────────────────────────────────
            self.error_label = ctk.CTkLabel(form_frame, text="", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']), text_color=FORM_UI['error_color'])
            self.error_label.grid(row=8, column=0, columnspan=2)

            # ── Action Traces (Auto-filling) ──────────────────────────────────────
            self.mem_id_var.trace_add("write", self._on_mem_change)
            self.pln_selection_var.trace_add("write", self._on_plan_change)
            self.start_date_var.trace_add("write", self._on_date_change)
            self.trn_selection_var.trace_add("write", self._on_trainer_change)

            # ── Validation Traces (Checking rules) ────────────────────────────────
            # Everything triggers validate so the Save button updates in real-time
            self.mem_id_var.trace_add("write", self._validate)
            self.pln_selection_var.trace_add("write", self._validate)
            self.start_date_var.trace_add("write", self._validate) 
            self.agreed_plan_fee_var.trace_add("write", self._validate)
            self.status_var.trace_add("write", self._validate)
            self.trn_selection_var.trace_add("write", self._validate)
            self.agreed_trainer_fee_var.trace_add("write", self._validate)


    def _build_form_buttons(self, popup, mode):
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=(0, FORM_UI['btn_pady_bottom']))


        self.save_btn = ctk.CTkButton(btn_frame, text="Save", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']), width=FORM_UI['btn_width'], border_width=DATA_FRAME_UI['btn_border'], fg_color=DATA_FRAME_UI['btn_fg'], hover_color=DATA_FRAME_UI['btn_hover'],state='disabled', text_color=DATA_FRAME_UI['btn_text'], command= lambda: self._on_save(popup,mode))
        self.save_btn.pack(side="left", padx=FORM_UI['btn_padx'])

        self.cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']), width=FORM_UI['btn_width'], border_width=DATA_FRAME_UI['btn_border'], fg_color=DATA_FRAME_UI['btn_fg'], hover_color=DATA_FRAME_UI['btn_hover'], text_color=DATA_FRAME_UI['btn_text'], command= popup.destroy)
        self.cancel_btn.pack(side="left", padx=FORM_UI['btn_padx'])
   


    def _on_mem_change(self, *args):
        memid = self.mem_id_var.get().strip().upper().replace("MEM-", "")

        if memid in self.members:
            self.mem_name_var.set(self.members[memid]['name'])
        else:
            self.mem_name_var.set("❌ Not Found")

    def _on_plan_change(self, *args):
        pln_selection = self.pln_selection_var.get()
        if " - " in pln_selection:
            # 1. Extract the ID part (e.g., "PLN-2")
            raw_id = pln_selection.split(" - ")[0]
            
            # 2. STRIP the prefix to get just the number (e.g., "2")
            plan_id = raw_id.replace("PLN-", "")
            self.agreed_plan_fee_var.set(str(self.plans[plan_id]['fee']))

            # Enable the entry
            self.agreed_plnfee_entry.configure(state='normal', text_color="black")
        else:   # reset the fee and disable entry
            self.agreed_plan_fee_var.set("0")
            self.agreed_plnfee_entry.configure(state='disabled', text_color="#9E9E9E" )
            
        self._on_date_change() # Trigger date calculation

    def _on_date_change(self, *args):
        from datetime import datetime, timedelta
        pln_selection = self.pln_selection_var.get()
        start_date_str = self.start_date_var.get().strip()

        if " - " in pln_selection:
            # 1. Extract the ID part (e.g., "PLN-2")
            raw_id = pln_selection.split(" - ")[0]
            
            # 2. STRIP the prefix to get just the number (e.g., "2")
            plan_id = raw_id.replace("PLN-", "")
            try:
                start_dt = datetime.strptime(start_date_str, "%d-%m-%Y")
                end_dt = start_dt + timedelta(days=int(self.plans[plan_id]['duration_days']))
                self.end_date_var.set(end_dt.strftime("%d-%m-%Y"))
            except ValueError:
                self.end_date_var.set("Invalid Start Date")

    def _on_trainer_change(self, *args):
        trn_selection = self.trn_selection_var.get()
        if " - " in trn_selection:
            # 1. Extract the ID part (e.g., "TRN-2")
            raw_id = trn_selection.split(" - ")[0]
            # 2. STRIP the prefix to get just the number (e.g., "2")
            trainer_id = raw_id.replace("TRN-", "")

            if trainer_id in self.trainers:
                fee = self.trainers[trainer_id]['default_fee']
                self.agreed_trainer_fee_var.set(str(fee))
                self.agreed_trnfee_entry.configure(state='normal', text_color="black")
        else:
            self.agreed_trainer_fee_var.set('0')
            self.agreed_trnfee_entry.configure(state='disabled', text_color="#9E9E9E")

    def _validate(self, *args):
        from datetime import datetime

        memid = self.mem_id_var.get().strip().upper().replace("MEM-", "")
        pln_selection = self.pln_selection_var.get()
        start_date_str = self.start_date_var.get().strip()
        status = self.status_var.get().strip()
        pln_fee = self.agreed_plan_fee_var.get().strip()
        trn_selection = self.trn_selection_var.get()
        trn_fee = self.agreed_trainer_fee_var.get().strip()

        # 1. Member
        if memid not in self.members:
            self._form_error("⚠ Please enter a valid Member ID.")
            return
        
        # 2. Plan
        if " - " not in pln_selection:
            self._form_error("⚠ Please select a Membership Plan.")
            return

        # 3. Start Date Safely Checked
        try:
            datetime.strptime(start_date_str, "%d-%m-%Y")
        except ValueError:
            self._form_error("⚠ Start Date must be valid DD-MM-YYYY.")
            return

        # 4. Status validation (Edit mode only)
        if self.form_mode == "edit":
            if status not in ("Current Status", "Cancelled"):
                self._form_error("⚠ Please select a valid status.")
                return
        
        # 5. Plan Fee
        if not self.is_float(pln_fee):
            self._form_error("⚠ Plan Fee must be a number.")
            return
        
        # 6. Trainer Fee
        if " - " in trn_selection and not self.is_float(trn_fee):
            self._form_error("⚠ Trainer Fee must be a number.")
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

        member_id = self.mem_id_var.get().strip().upper().replace("MEM-", "")
        
        pln_selection = self.pln_selection_var.get()
        f_plan_id = pln_selection.split(" - ")[0]
        plan_id = str(f_plan_id).replace("PLN-","")
        
        formatted_startdate = self.start_date_var.get()
        start_date = datetime.strptime(formatted_startdate, "%d-%m-%Y").strftime("%Y-%m-%d")
        
        # Preparing dates as date object for status function
        start_dt = datetime.strptime(formatted_startdate, "%d-%m-%Y").date()
        formatted_enddate = self.end_date_var.get()
        end_dt = datetime.strptime(formatted_enddate, "%d-%m-%Y").date()
        
        if mode == "add":
            status = self.calculate_membership_status(start_dt, end_dt)

        else:
            if self.status_var.get() == "Cancelled":
                status = "Cancelled"
            else:
                status = self.calculate_membership_status(start_dt, end_dt)
                agreed_plnfee = self.agreed_plan_fee_var.get().strip()
        
        agreed_plnfee = self.agreed_plan_fee_var.get().strip()

        # Safely handle the Trainer ID
        trn_selection = self.trn_selection_var.get()
        trainer_id = None  # Default to None
        if " - " in trn_selection:
            # 1. Get "TRN-1"
            raw_trn_id = trn_selection.split(" - ")[0]
            # 2. Convert "TRN-1" -> "1"
            trainer_id = raw_trn_id.replace("TRN-", "")
            
        agreed_trnfee = self.agreed_trainer_fee_var.get().strip()

        if mode == 'add':
            success = insert_membership(member_id, plan_id, start_date, status, agreed_plnfee, trainer_id, agreed_trnfee)
        else:
            # Safely grab the membership's unique key if needed, or use member_id depending on your schema
            formatted_mem_id = self.selected_row['member_id']
            clean_mem_id = str(formatted_mem_id).replace("MEM-","")
            formatted_pln_id = self.selected_row['plan_id']
            clean_pln_id = str(formatted_pln_id).replace("PLN-","")

            success = update_membership(clean_mem_id, clean_pln_id, start_date, status, agreed_plnfee, trainer_id, agreed_trnfee)
        
        if success:
            popup.destroy()
            self.selected_row = None
            self.load_data()   
            self.selection_label.configure(text='No Row Selected')
            self.edit_btn.configure(state='disabled')
        else:
            messagebox.showerror(title="Error", message=f"Could not {mode} membership. Check inputs or DB connection.")

    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _on_export(self):
        # Check if table has any rows
        if not self.table.get_children():
            messagebox.showwarning(title="Empty", message="No data to export.")
            return
        
        export_to_excel(tree=self.table, default_filename="memberships_export")
        

    def calculate_membership_status(self, start_date, end_date):
        from datetime import date

        today = date.today()

        if end_date < today:
            return "Expired"
        elif start_date > today:
            return "Upcoming"
        else:
            return "Active"

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
















# # Delete button — red tint, disabled by default
# self.delete_btn = ctk.CTkButton(
#     self.action_bar,
#     text='🗑 Delete',
#     width=DATA_FRAME_UI['actionbar_btn_width'],
#     height=DATA_FRAME_UI['btn_height'],
#     state="disabled",
#     font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
#     fg_color=DATA_FRAME_UI['delete_fg'],
#     hover_color=DATA_FRAME_UI['delete_hover'],
#     text_color=DATA_FRAME_UI['delete_text'],
#     border_width=DATA_FRAME_UI['btn_border'],
#     command=self._on_delete
# )
# self.delete_btn.grid(row=0, column=2, padx=(4, 8), pady=8)

