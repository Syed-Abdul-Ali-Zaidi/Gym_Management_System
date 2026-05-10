import customtkinter as ctk
from tkinter import ttk, messagebox
from config.ui_config import DATA_FRAME_UI, FORM_UI
from services.membership_service import (
    get_all_membership, search_membership, insert_membership,
    update_membership, delete_membership, get_membership_form_data
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
        self.topbar_frame.grid_columnconfigure((1, 2, 3, 4), weight=0)        # buttons fixed


        # ── Search entry ───────────────────────────────────────────────
        ctk.CTkLabel(self.topbar_frame, text="Search by MembershipID or membershipmember_name", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=10)).grid(row=0, column=0, padx=(6,4), pady=(1,0), sticky="w")

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

        # ── start_date Filter Frame ──────────────────────────────────────────

        # Create a small label above the checkboxes
        ctk.CTkLabel(self.topbar_frame, text="Filter by start_date:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=10)).grid(row=0, column=2, padx=4, pady=(1,0), sticky="w")

        # Creating a Dict of Filters where each filter member_name is a BooleanVar()
        filter_list = ['Active', 'Expired', 'Cancelled', 'Upcoming']
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
        self.add_btn.grid(row=1, column=3, padx=4, pady=(1,6))

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
        self.table.column('agreed_plan_fee',    width=150, minwidth=150, anchor='center')
        self.table.column('trainer_id',         width=150, minwidth=150, anchor='center')
        self.table.column('trainer_name',       width=250, minwidth=250)
        self.table.column('agreed_trainer_fee', width=150, minwidth=150, anchor='center')


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
        rows = get_all_membership()
        self._refresh_table(rows)

    def _refresh_table(self,rows):
        # Deletes existing rows
        self.table.delete(*self.table.get_children())
        
        # Creating Stripped row tags
        self.table.tag_configure('Active', background=DATA_FRAME_UI['membership_active'])
        self.table.tag_configure('Expired', background=DATA_FRAME_UI['membership_expired'])
        self.table.tag_configure('Cancelled', background=DATA_FRAME_UI['membership_cancelled'])
        self.table.tag_configure('Upcoming', background=DATA_FRAME_UI['membership_cancelled'])

        # inserts New Data
        for row in rows:
            tag = row['status']

            formatted_mem_id = f'MEM-{row['member_id']}'
            formatted_pln_id = f'PLN-{row['plan_id']}'
            formatted_trn_id = f'TRN-{row['trainer_id']}'

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
                                     message="Could not delete member.\nThey may have an active membership."
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
        popup.geometry('500x600')
        popup.resizable(False, False) 
        
        # ── 1. Fetch & Structure Lookups ──────────────────────────────────────
        from services.membership_service import get_membership_form_data
        m_list, p_list, t_list = get_membership_form_data()

        # Structured as: {"ID": {'name': NAME, ...}}
        self.members = {str(m['member_id']): m for m in m_list}
        self.plans   = {str(p['plan_id']): p for p in p_list}
        self.trainers = {str(t['trainer_id']): t for t in t_list}

        # ── 2. Initialize Variables ───────────────────────────────────────────
        self.mem_id_var             = ctk.StringVar()
        self.mem_name_var           = ctk.StringVar(value="Not Found")
        self.pln_selection_var      = ctk.StringVar(value="Select Plan")
        self.start_date_var         = ctk.StringVar()
        self.end_date_var           = ctk.StringVar()
        self.status_var             = ctk.StringVar(value="Active")
        self.agreed_plan_fee_var    = ctk.StringVar(value="0")
        self.trn_selection_var      = ctk.StringVar(value="No Trainer")
        self.agreed_trainer_fee_var = ctk.StringVar(value="0")

        # Set default start date for 'add' mode
        from datetime import datetime
        self.start_date_var.set(datetime.now().strftime("%d-%m-%Y"))

        # ── 3. Build UI ───────────────────────────────────────────────────────
        self._build_form_fields(popup)
        self._build_form_buttons(popup, mode)

        # ── 4. Edit Mode Logic ───────────────────────────────────────────────
        if mode == 'edit':
            # Pre-fill variables from the selected row dictionary
            self.mem_id_var.set(str(self.selected_row['member_id']).replace("MEM-", ""))
            self.mem_name_var.set(self.selected_row['member_name'])
            
            formatted_plan_name = f'{self.selected_row['plan_id']} - {self.selected_row['plan_name']}'
            self.pln_selection_var.set(formatted_plan_name)
            
            self.start_date_var.set(self.selected_row['start_date'])
            self.end_date_var.set(self.selected_row['end_date'])
            self.status_var.set(self.selected_row['status'])
            self.agreed_plan_fee_var.set(str(self.selected_row['agreed_plan_fee']))
            
            if self.selected_row.get('trainer_id'):
                formatted_trainer_name = f'{self.selected_row['trainer_id']} - {self.selected_row['name']}'
                self.trn_selection_var.set(formatted_trainer_name)
                self.agreed_trainer_fee_var.set(str(self.selected_row['agreed_trainer_fee']))

            # DISABLE specified fields in Edit Mode
            # Ensure these names match the widget references in _build_form_fields
            self.mem_id_entry.configure(state='disabled', text_color="#9E9E9E")
            self.pln_dropdown.configure(state='disabled', text_color="#9E9E9E")
            self.start_date_entry.configure(state='disabled', text_color="#9E9E9E")
            # Note: end_date_entry should be disabled in BOTH modes (auto-filled only)
        
        # # End Date is always disabled as it's auto-calculated
        # self.end_date_entry.configure(state='disabled', text_color="#9E9E9E")

        popup.grab_set()
        popup.transient(self.winfo_toplevel())
        

    def _build_form_fields(self, popup):
            form_frame = ctk.CTkFrame(popup)
            form_frame.grid(row=0, column=0, padx=20, pady=10)

            # Member Selection
            ctk.CTkLabel(form_frame, text="Member ID:").grid(row=0, column=0, sticky="e", pady=5)
            self.mem_entry = ctk.CTkEntry(form_frame, textvariable=self.mem_id_var, width=80)
            self.mem_entry.grid(row=0, column=1, sticky="w", padx=10)
            # Name label next to ID
            ctk.CTkLabel(form_frame, textvariable=self.mem_name_var, text_color="#4DA6FF").grid(row=0, column=1, sticky="e")

            # Plan Dropdown
            ctk.CTkLabel(form_frame, text="Plan:").grid(row=1, column=0, sticky="e", pady=5)
            # Create "ID - Name" list for dropdown from your dictionary
            plan_options = [f"{pid} - {p['plan_name']}" for pid, p in self.plans.items()]
            self.plan_menu = ctk.CTkOptionMenu(form_frame, variable=self.pln_selection_var, values=plan_options)
            self.plan_menu.grid(row=1, column=1, sticky="w", padx=10)

            # Dates
            ctk.CTkLabel(form_frame, text="Start Date:").grid(row=2, column=0, sticky="e", pady=5)
            self.start_entry = ctk.CTkEntry(form_frame, textvariable=self.start_date_var)
            self.start_entry.grid(row=2, column=1, sticky="w", padx=10)

            ctk.CTkLabel(form_frame, text="End Date:").grid(row=3, column=0, sticky="e", pady=5)
            # This is the disabled entry you requested
            self.end_entry = ctk.CTkEntry(form_frame, textvariable=self.end_date_var, state="disabled", text_color="#9E9E9E")
            self.end_entry.grid(row=3, column=1, sticky="w", padx=10)

            # Row 3 - Status (Dropdown)
            ctk.CTkLabel(form_frame, text="Status:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=3, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
            ctk.CTkOptionMenu(form_frame, variable=self.status_var, values=["Select Status", "Active", "Inactive"], text_color='black', fg_color= DATA_FRAME_UI['btn_fg'], dropdown_hover_color= DATA_FRAME_UI['btn_hover']).grid(row=3, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])
                
            # Agreed_plan_fee
            ctk.CTkLabel(form_frame, text="Agreed Plan Fee:").grid(row=5, column=0, sticky="e", pady=5)
            self.agreed_plnfee_entry = ctk.CTkEntry(form_frame, textvariable=self.agreed_plan_fee_var)
            self.agreed_plnfee_entry.grid(row=5, column=1, sticky="w", padx=10)

            # Trainer Dropdown
            ctk.CTkLabel(form_frame, text="Trainer:").grid(row=6, column=0, sticky="e", pady=5)
            # Create "ID - Name" list for dropdown from your dictionary
            trainer_options = [f"{pid} - {p['name']}" for pid, p in self.plans.items()]
            self.trainer_menu = ctk.CTkOptionMenu(form_frame, variable=self.trn_selection_var, values=trainer_options)
            self.trainer_menu.grid(row=6, column=1, sticky="w", padx=10)

            # Agreed_trainer_fee
            ctk.CTkLabel(form_frame, text="Agreed Trainer Fee:").grid(row=7, column=0, sticky="e", pady=5)
            self.agreed_plnfee_entry = ctk.CTkEntry(form_frame, textvariable=self.agreed_trainer_fee_var)
            self.agreed_plnfee_entry.grid(row=7, column=1, sticky="w", padx=10)


            # Attach Traces
            self.mem_id_var.trace_add("write", self._on_mem_id_change)
            self.pln_selection_var.trace_add("write", self._on_plan_change)
            self.start_date_var.trace_add("write", self._on_plan_change) # Updates end_date if user changes start_date
            self.agreed_plan_fee_var.trace_add("write", self._on_plan_change)
            self.status_var.trace_add("write", self._validate)
            self.trn_selection_var.trace_add("write",self.on_trainer_change)
            self.agreed_trainer_fee_var.trace_add("write", self.on_trainer_change)

    def _build_form_buttons(self, popup, mode):
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=(0, FORM_UI['btn_pady_bottom']))


        self.save_btn = ctk.CTkButton(btn_frame, text="Save", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']), width=FORM_UI['btn_width'], border_width=DATA_FRAME_UI['btn_border'], fg_color=DATA_FRAME_UI['btn_fg'], hover_color=DATA_FRAME_UI['btn_hover'],state='disabled', text_color=DATA_FRAME_UI['btn_text'], command= lambda: self._on_save(popup,mode))
        self.save_btn.pack(side="left", padx=FORM_UI['btn_padx'])

        self.cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']), width=FORM_UI['btn_width'], border_width=DATA_FRAME_UI['btn_border'], fg_color=DATA_FRAME_UI['btn_fg'], hover_color=DATA_FRAME_UI['btn_hover'], text_color=DATA_FRAME_UI['btn_text'], command= popup.destroy)
        self.cancel_btn.pack(side="left", padx=FORM_UI['btn_padx'])

    def _on_mem_id_change(self, *args):
            """Find member name instantly using the ID key."""
            uid = self.mem_id_var.get().strip().replace("MEM-", "")
            if uid in self.members:
                self.mem_name_var.set(self.members[uid]['name'])
            else:
                self._form_error("❌ Member Not Found")

    def _on_plan_change(self, *args):
        """Auto-fill Fee and calculate End Date using dictionary lookup."""
        selection = self.plan_selection_var.get()
        if " - " in selection:
            plan_id = selection.split(" - ")[0]
            
            # Access the dictionary directly using the ID!
            plan_data = self.plans[plan_id]
            
            # Set Fee
            self.agreed_plan_fee_var.set(str(plan_data['fee']))
            
            # Calculate End Date
            from datetime import datetime, timedelta
            try:
                start_dt = datetime.strptime(self.start_date_var.get(), "%d-%m-%Y")
                # Add duration from your dictionary
                end_dt = start_dt + timedelta(days=int(plan_data['duration_days']))
                self.end_date_var.set(end_dt.strftime("%d-%m-%Y"))
            except:
                self.end_date_var.set("Invalid Start Date")

    def _on_trainer_change(self, *args):
        """Auto-fill Fee and calculate End Date using dictionary lookup."""
        selection = self.trn_selection_var.get()
        if " - " in selection:
            trainer_id = selection.split(" - ")[0]
            
            # Access the dictionary directly using the ID!
            trainer_data = self.trainers[trainer_id]
            
            # Set Fee
            self.agreed_trainer_fee_var.set(str(trainer_data['default_fee']))

            return True
            
    def _validate(self, *args):
        status       = self.status_var.get().strip()

        # Required: status
        if status not in ('Active', 'Inactive'):
            self._form_error("⚠ Please select a status.")
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

        member_name      = self.member_name_var.get().strip()
        phone     = self.phone_var.get().strip()
        plan_name    = self.plan_name_var.get().strip()
        start_date    = self.start_date_var.get().strip()
        end_date = self.end_date_var.get().strip()

        formatted_date = datetime.strptime(end_date, "%d-%m-%Y").strftime("%Y-%m-%d")

        if mode == 'add':
            success = insert_membership(member_name, phone, plan_name, start_date, formatted_date)
        else:
            member_id = self.selected_row['member_id']
            formatted_id = member_id.replace("MEM-","")
            success = update_membership(formatted_id, member_name, phone, plan_name, start_date)
        
        if success:   # Insertion Successful
            popup.destroy()
            # reseting selected row
            self.selected_row = None

            self.load_data()   
            self.selection_label.configure(text='No Row Selected')
            self.edit_btn.configure(state= 'disabled')
        else:
            messagebox.showerror(title="Error",
                                 message=f"Could not {mode} membership. Check inputs or DB connection."
                                )


    def _on_export(self):
        # Check if table has any rows
        if not self.table.get_children():
            messagebox.showwarning(title="Empty", message="No data to export.")
            return
        
        export_to_excel(tree=self.table, default_filemember_name="memberships_export")
        


















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

