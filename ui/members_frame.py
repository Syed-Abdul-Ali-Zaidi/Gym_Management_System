import customtkinter as ctk
from tkinter import ttk, messagebox
from config.ui_config import DATA_FRAME_UI, FORM_UI
from services.member_service import (
    get_all_member, search_member,
    insert_member, update_member
)
from ui.excel_file_maker import export_to_excel

class MembersFrame(ctk.CTkFrame):
    def __init__(self, content_area):
        super().__init__(content_area, fg_color=DATA_FRAME_UI['content_bg_color'])

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
        ctk.CTkLabel(self.topbar_frame, text="Search by MemberID or MemberName", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=10)).grid(row=0, column=0, padx=(6,4), pady=(1,0), sticky="w")

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
        filter_list = ["Active", "Inactive"]
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
        self.table = ttk.Treeview(self.table_frame, columns= ('member_id', 'name', 'phone_no', 'gender', 'status', 'join_date'), show= 'headings', selectmode="browse")
        self.table.heading('member_id', text= 'Member_ID')
        self.table.heading('name',      text= 'Name')
        self.table.heading('phone_no',  text= 'Phone_No')
        self.table.heading('gender',    text= 'Gender')
        self.table.heading('status',    text= 'Status')
        self.table.heading('join_date', text= 'Join Date')

        # Column widths
        self.table.column('member_id', width=150, minwidth=150, anchor='center')
        self.table.column('name',      width=250, minwidth=250)
        self.table.column('phone_no',  width=150, minwidth=150)
        self.table.column('gender',    width=100, minwidth=100, anchor='center')
        self.table.column('status',    width=200, minwidth=200)
        self.table.column('join_date', width=150, minwidth=150, anchor='center')

        self.table.bind('<<TreeviewSelect>>', self._on_row_select)

        # Scroll Bar
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=self.scrollbar.set)

        # Grid both Tree and ScrollBar
        self.table.grid(row=0, column=0, sticky='nsew')
        self.scrollbar.grid(row=0, column=1, sticky='ns')   # column 1, stretches vertically only

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
        self.edit_btn.grid(row=0, column=2, padx=(4, 8), pady=8)




    def load_data(self):
        rows = get_all_member()
        self._refresh_table(rows)

    def _refresh_table(self,rows):
        # Deletes existing rows
        self.table.delete(*self.table.get_children())
        
        # Creating Stripped row tags
        self.table.tag_configure('Active', background=DATA_FRAME_UI['member_active'])
        self.table.tag_configure('Inactive', background=DATA_FRAME_UI['member_inactive'])

        # inserts New Data
        for row in rows:
            tag = row['status']

            formatted_id = f'MEM-{row['member_id']}'
            formatted_date = row['join_date'].strftime("%d-%m-%Y")

            self.table.insert(parent='', index= 'end', values=(
                formatted_id,
                row['name'],
                row['phone_no'] or '',  # if there is a NULL value Tree will show None so replace it with ""
                row['gender'],
                row['status'],
                formatted_date),
                tags= (tag,)
            )
            




    def _on_search(self,  *args):
        search_term = self.searchbar_var.get().strip()
        search_term = search_term.upper()

        # Getting Ticked Filters
        # Create a list of the names of all checked status
        selected_filter = [filter for filter, var in self.filters_var.items() if var.get()]
        

        # if there is no SearchTerm, Load Normal Data
        if search_term.startswith("MEM-"):
                search_term = search_term.replace("MEM-","")
        rows = search_member(search_term, selected_filter)
        self._refresh_table(rows)

        # Clear selection after every search
        self.selected_row = None
        self.selection_label.configure(text='No row selected')
        self.edit_btn.configure(state='disabled')

    def _on_row_select(self, event):
        column_names = ['member_id', 'name', 'phone_no', 'gender', 'status', 'join_date']
        selected = self.table.selection()

        if not selected:
            self.selection_label.configure(text='No Row Selected')
            return None
        
        item_id = selected[0]
        values = self.table.item(item_id)["values"]
        self.selected_row = dict(zip(column_names, values))

        # Updating the Selection Label
        self.selection_label.configure(text= f'ID: {self.selected_row['member_id']} | Name: {self.selected_row['name']}')

        # Enabling the Edit botton
        self.edit_btn.configure(state='normal')



    def _on_add(self):
        self._open_form('add')


    def _on_edit(self):
        if self.selected_row is None:
            return
        self._open_form('edit')

    def _open_form(self, mode):
        popup = ctk.CTkToplevel(self)
        popup.title("Add Member" if mode == "add" else "Edit Member")
        popup.geometry('300x260')
        popup.resizable(False, False) 
        
        # Create StringVars here — they live as long as popup lives
        self.name_var      = ctk.StringVar()
        self.phone_var     = ctk.StringVar(value='+92')
        self.gender_var    = ctk.StringVar()
        self.status_var    = ctk.StringVar()
        self.join_date_var = ctk.StringVar()

        # Filling the date with Current date
        from datetime import datetime

        current_date = datetime.now().strftime("%d-%m-%Y")
        self.join_date_var.set(current_date)
        
        # Pass popup to field builder
        self._build_form_fields(popup)
        self._build_form_buttons(popup, mode)

        if mode == 'edit':
            self.name_var.set(self.selected_row['name'])
            self.phone_var.set(self.selected_row['phone_no'] or '')
            self.gender_var.set(self.selected_row['gender'])
            self.status_var.set(self.selected_row['status'])
            self.join_date_var.set(self.selected_row['join_date'])

            # Disabling the Date_Entry
            self.date_entry.configure(state = 'disabled', text_color="#9E9E9E")
        
        popup.grab_set()    # User CANNOT click anything in the main window until popup closes
        popup.transient(self.winfo_toplevel())    # Popup won't go behind the main window

        

    def _build_form_fields(self, popup):
        form_frame = ctk.CTkFrame(popup)
        form_frame.grid(row=0, column=0, padx=FORM_UI['padx'], pady=FORM_UI['pady'])

        # Row 0 - Name
        ctk.CTkLabel(form_frame, text="Name:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=0, column=0, padx=10, pady=(5,FORM_UI['row_pady']), sticky=FORM_UI["label_sticky"])
        ctk.CTkEntry(form_frame, textvariable=self.name_var).grid(row=0, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

        # Row 1 - Phone
        ctk.CTkLabel(form_frame, text="Phone No:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=1, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        ctk.CTkEntry(form_frame, textvariable=self.phone_var).grid(row=1, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

        # Row 2 - Gender (Dropdown)
        ctk.CTkLabel(form_frame, text="Gender:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=2, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        ctk.CTkOptionMenu(form_frame, variable=self.gender_var, values=["Select Gender", "Male", "Female", "Other"], text_color='black', fg_color= DATA_FRAME_UI['btn_fg'], dropdown_hover_color= DATA_FRAME_UI['btn_hover']).grid(row=2, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

        # Row 3 - Status (Dropdown)
        ctk.CTkLabel(form_frame, text="Status:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=3, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        ctk.CTkOptionMenu(form_frame, variable=self.status_var, values=["Select Status", "Active", "Inactive"], text_color='black', fg_color= DATA_FRAME_UI['btn_fg'], dropdown_hover_color= DATA_FRAME_UI['btn_hover']).grid(row=3, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

        # Row 4 - Join Date
        ctk.CTkLabel(form_frame, text="Join Date\n(DD-MM-YYYY)", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=4, column=0, padx=10, pady=(FORM_UI['row_pady'],5), sticky=FORM_UI["label_sticky"])
        self.date_entry = ctk.CTkEntry(form_frame, textvariable=self.join_date_var)
        self.date_entry.grid(row=4, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

        # Row 5 - Error message
        self.error_label = ctk.CTkLabel(form_frame, text="", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),  text_color=FORM_UI['error_color'])
        self.error_label.grid(row=5, column=0, columnspan=2)

        # Addinh traces to Each Variable. means calling a function whenever variable's value changes
        self.name_var.trace_add("write", self._validate)
        self.phone_var.trace_add("write", self._validate)
        self.gender_var.trace_add("write", self._validate)
        self.status_var.trace_add("write", self._validate)
        self.join_date_var.trace_add("write", self._validate)

    def _build_form_buttons(self, popup, mode):
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=(0, FORM_UI['btn_pady_bottom']))


        self.save_btn = ctk.CTkButton(btn_frame, text="Save", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']), width=FORM_UI['btn_width'], border_width=DATA_FRAME_UI['btn_border'], fg_color=DATA_FRAME_UI['btn_fg'], hover_color=DATA_FRAME_UI['btn_hover'],state='disabled', text_color=DATA_FRAME_UI['btn_text'], command= lambda: self._on_save(popup,mode))
        self.save_btn.pack(side="left", padx=FORM_UI['btn_padx'])

        self.cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']), width=FORM_UI['btn_width'], border_width=DATA_FRAME_UI['btn_border'], fg_color=DATA_FRAME_UI['btn_fg'], hover_color=DATA_FRAME_UI['btn_hover'], text_color=DATA_FRAME_UI['btn_text'], command= popup.destroy)
        self.cancel_btn.pack(side="left", padx=FORM_UI['btn_padx'])

    def _validate(self, *args):
        from datetime import datetime

        name      = self.name_var.get().strip()
        phone     = self.phone_var.get().strip()
        gender    = self.gender_var.get().strip()
        status    = self.status_var.get().strip()
        join_date = self.join_date_var.get().strip()

        # Required: Name
        if not name:
            self._form_error("⚠ Name is required.")
            return
        if len(name) < 2 or len(name) > 50:
            self._form_error("⚠ Name must be 2-50 characters.")
            return
        
        # Required: gender
        if gender not in ('Male', 'Female', 'Other'):
            self._form_error("⚠ Please select a gender.")
            return
        
         # Required: status
        if status not in ('Active', 'Inactive'):
            self._form_error("⚠ Please select a status.")
            return

        # Required: join_date
        if not join_date:
            self._form_error("⚠ Join date is required.")
            return
        try:
            datetime.strptime(join_date, '%d-%m-%Y')   # tries to parse the date
        except ValueError:
            self._form_error("⚠ Date must be valid DD-MM-YYYY.")
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

        name      = self.name_var.get().strip()
        phone     = self.phone_var.get().strip()
        gender    = self.gender_var.get().strip()
        status    = self.status_var.get().strip()
        join_date = self.join_date_var.get().strip()

        formatted_date = datetime.strptime(join_date, "%d-%m-%Y").strftime("%Y-%m-%d")

        if mode == 'add':
            success = insert_member(name, phone, gender, status, formatted_date)
        else:
            member_id = self.selected_row['member_id']
            formatted_id = member_id.replace("MEM-","")
            success = update_member(formatted_id, name, phone, gender, status)
        
        if success:   # Insertion Successful
            popup.destroy()
            # reseting selected row
            self.selected_row = None

            self.load_data()   
            self.selection_label.configure(text='No Row Selected')
            self.edit_btn.configure(state= 'disabled')
        else:
            messagebox.showerror(title="Error",
                                 message=f"Could not {mode} member. Check inputs or DB connection."
                                )


    def _on_export(self):
        # Check if table has any rows
        if not self.table.get_children():
            messagebox.showwarning(title="Empty", message="No data to export.")
            return
        
        export_to_excel(tree=self.table, default_filename="members_export")


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
