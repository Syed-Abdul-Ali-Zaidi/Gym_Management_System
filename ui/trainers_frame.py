import customtkinter as ctk
from tkinter import ttk, messagebox
from config.ui_config import DATA_FRAME_UI, FORM_UI
from services.trainer_service import (
    get_all_trainer, search_trainer,
    insert_trainer, update_trainer
)
from ui.excel_file_maker import export_to_excel

class TrainersFrame(ctk.CTkFrame):
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
        self.topbar_frame.grid_columnconfigure(1, weight=0)        # buttons fixed
        self.topbar_frame.grid_columnconfigure(2, weight=0)
        self.topbar_frame.grid_columnconfigure(3, weight=0)

        # ── Search entry ───────────────────────────────────────────────
        ctk.CTkLabel(self.topbar_frame, text="Search by trainerID or trainerName", font=ctk.CTkFont(size=10)).grid(row=0, column=0, padx=(6,4), pady=(1,0), sticky="w")

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
        self.add_btn.grid(row=1, column=2, padx=4, pady=(1,6))

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
        self.export_btn.grid(row=1, column=3, padx=(4,6), pady=(1,6))


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
        self.table = ttk.Treeview(self.table_frame, columns= ('trainer_id', 'name', 'phone_no', 'salary', 'specialization', 'status', 'default_fee'), show= 'headings', selectmode="browse")
        self.table.heading('trainer_id',     text= 'Trainer ID')
        self.table.heading('name',           text= 'Name')
        self.table.heading('phone_no',       text= 'Phone No')
        self.table.heading('salary',         text= 'Salary')
        self.table.heading('specialization', text= 'Specialization')
        self.table.heading('status',         text= 'Status')
        self.table.heading('default_fee',    text= 'Default Fee')

        # Column widths
        self.table.column('trainer_id',     width=150, minwidth=150, anchor='center')
        self.table.column('name',           width=250, minwidth=250)
        self.table.column('phone_no',       width=150, minwidth=150, anchor='center')
        self.table.column('salary',         width=150, minwidth=150, anchor='center')
        self.table.column('specialization', width=400, minwidth=400)
        self.table.column('status',         width=150, minwidth=150)
        self.table.column('default_fee',    width=150, minwidth=150, anchor='center')


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
        rows = get_all_trainer()
        self._refresh_table(rows)

    def _refresh_table(self,rows):
        # Deletes existing rows
        self.table.delete(*self.table.get_children())

        # Creating Stripped row tags
        self.table.tag_configure('Active', background=DATA_FRAME_UI['trainer_active'])
        self.table.tag_configure('On-leave', background=DATA_FRAME_UI['trainer_on_leave'])
        self.table.tag_configure('Terminated', background=DATA_FRAME_UI['trainer_terminated'])

        #keys = ['active', 'onleave', 'terminated']('Active', 'On-leave', 'Terminated')

        # inserts New Data
        for row in rows:
            tag = row['status']
        
            self.table.insert(parent='', index= 'end', values=(
                row['trainer_id'],
                row['name'],
                row['phone_no'] or '',  # if there is a NULL value Tree will show None so replace it with ""
                row['salary'],
                row['specialization'] or '',
                row['status'],
                row['default_fee'] or '0'),
                tags= (tag,)
            )





    def _on_search(self,  *args):
        search_term = self.searchbar_var.get().strip()
        # if there is no SearchTerm, Load Normal Data
        if not search_term:
            self.load_data()
        # Else search the Data and load it
        else:
            rows = search_trainer(search_term)
            self._refresh_table(rows)

        # Clear selection after every search
        self.selected_row = None
        self.selection_label.configure(text='No row selected')
        self.edit_btn.configure(state='disabled')

    def _on_row_select(self, event):
        column_names = ['trainer_id', 'name', 'phone_no', 'salary', 'specialization', 'status', 'default_fee']
        selected = self.table.selection()

        if not selected:
            self.selection_label.configure(text='No Row Selected')
            return None
        
        item_id = selected[0]
        values = self.table.item(item_id)["values"]
        self.selected_row = dict(zip(column_names, values))

        # Updating the Selection Label
        self.selection_label.configure(text= f'ID: {self.selected_row['trainer_id']} | Name: {self.selected_row['name']}')

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
        popup.title("Add trainer" if mode == "add" else "Edit trainer")
        popup.geometry('550x420')
        popup.resizable(False, False) 
        
        # Create StringVars here — they live as long as popup lives
        self.name_var           = ctk.StringVar()
        self.phone_var          = ctk.StringVar()
        self.salary_var         = ctk.StringVar()
        self.status_var         = ctk.StringVar()
        self.default_fee_var    = ctk.StringVar()

        # Creating a Dict of Specs where each spec name is a BooleanVar()
        self.spec_list = ["Weight Training", "Cardio Fitness", "Yoga", "CrossFit", "Zumba", "Strength Training"]
        self.specialization_var = {}

        for spec in self.spec_list:
            self.specialization_var[spec] = ctk.BooleanVar(value=False)
        
        # Pass popup to field builder
        self._build_form_fields(popup)
        self._build_form_buttons(popup, mode)

        if mode == 'edit':
            # First checking the ticked boxes
            existing_specs = self.selected_row['specialization'].split(", ")
            for spec in existing_specs:
                clean_spec = spec.strip()
                if clean_spec in self.specialization_var:
                    self.specialization_var[clean_spec].set(True)
                    
            self.name_var.          set(self.selected_row['name'])
            self.phone_var.         set(self.selected_row['phone_no'] or '')
            self.salary_var.        set(self.selected_row['salary'])
            self.status_var.        set(self.selected_row['status'])
            self.default_fee_var.   set(self.selected_row['default_fee'] or '0')
        
        popup.grab_set()    # User CANNOT click anything in the main window until popup closes
        popup.transient(self.winfo_toplevel())    # Popup won't go behind the main window

        

    def _build_form_fields(self, popup):
        form_frame = ctk.CTkFrame(popup)
        form_frame.grid(row=0, column=0, padx=FORM_UI['padx'], pady=FORM_UI['pady'])

        # Row 0 - Name ──────────────────────────────────
        ctk.CTkLabel(form_frame, text="Name:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=0, column=0, padx=10, pady=(5,FORM_UI['row_pady']), sticky=FORM_UI["label_sticky"])
        ctk.CTkEntry(form_frame, textvariable=self.name_var).grid(row=0, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

        # Row 1 - Phone ──────────────────────────────────
        ctk.CTkLabel(form_frame, text="Phone No\n(without spaces):", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=1, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        ctk.CTkEntry(form_frame, textvariable=self.phone_var).grid(row=1, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

        # Row 2 - salary ──────────────────────────────────
        ctk.CTkLabel(form_frame, text="Salary:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=2, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        ctk.CTkEntry(form_frame, textvariable=self.salary_var).grid(row=2, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

        # Row 3 - specialization (Check Boxes)
        ctk.CTkLabel(form_frame, text="Specialization:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=3, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        
        # Creating a Frame in r=3,c=1 for checkboxes
        spec_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        spec_frame.grid(row=3, column=1, padx=10, pady=FORM_UI['row_pady'], sticky="w")

        # Automatically arrange checkboxes, 3 per row
        for i, spec in enumerate(self.spec_list):
            row_idx = i // 3  # Integer division: 0, 0, 0, 1, 1, 1...
            col_idx = i % 3   # Modulo division:  0, 1, 2, 0, 1, 2...
            
            chk = ctk.CTkCheckBox(spec_frame, text=spec, font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size = 11), variable=self.specialization_var[spec])
            chk.grid(row=row_idx, column=col_idx, padx=(0, 10), pady=5, sticky=FORM_UI["entry_sticky"])
            
            # Attach trace directly to the checkbox variable
            self.specialization_var[spec].trace_add("write", self._validate)

        # Row 4 - Status (Dropdown) ──────────────────────────────────
        ctk.CTkLabel(form_frame, text="Status:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=4, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        ctk.CTkOptionMenu(form_frame, variable=self.status_var, values=["Select Status", 'Active', 'On-leave', 'Terminated'], fg_color= DATA_FRAME_UI['btn_fg'], dropdown_hover_color= DATA_FRAME_UI['btn_hover']).grid(row=4, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])
        
        # Row 5 - Default Fee ──────────────────────────────────
        ctk.CTkLabel(form_frame, text="Default Fee:", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size'])).grid(row=5, column=0, padx=10, pady=(FORM_UI['row_pady'],5), sticky=FORM_UI["label_sticky"])
        ctk.CTkEntry(form_frame, textvariable=self.default_fee_var).grid(row=5, column=1, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["entry_sticky"])

        # Row 6 - Error message ──────────────────────────────────
        self.error_label = ctk.CTkLabel(form_frame, text="", text_color=FORM_UI['error_color'])
        self.error_label.grid(row=6, column=0, columnspan=2)

        # Addinh traces to Each Variable. means calling a function whenever variable's value changes
        self.name_var.trace_add("write", self._validate)
        self.phone_var.trace_add("write", self._validate)
        self.salary_var.trace_add("write", self._validate)
        self.status_var.trace_add("write", self._validate)
        self.default_fee_var.trace_add("write", self._validate)

    def _build_form_buttons(self, popup, mode):
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=(0, FORM_UI['btn_pady_bottom']))


        self.save_btn = ctk.CTkButton(btn_frame, text="Save", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']), width=FORM_UI['btn_width'], border_width=DATA_FRAME_UI['btn_border'], fg_color=DATA_FRAME_UI['btn_fg'], hover_color=DATA_FRAME_UI['btn_hover'],state='disabled', text_color=DATA_FRAME_UI['btn_text'], command= lambda: self._on_save(popup,mode))
        self.save_btn.pack(side="left", padx=FORM_UI['btn_padx'])

        self.cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']), width=FORM_UI['btn_width'], border_width=DATA_FRAME_UI['btn_border'], fg_color=DATA_FRAME_UI['btn_fg'], hover_color=DATA_FRAME_UI['btn_hover'], text_color=DATA_FRAME_UI['btn_text'], command= popup.destroy)
        self.cancel_btn.pack(side="left", padx=FORM_UI['btn_padx'])

    def _validate(self, *args):
        name           = self.name_var.get().strip()
        phone          = self.phone_var.get().strip()
        salary         = self.salary_var.get().strip()
        status         = self.status_var.get().strip()
        defaultfee     = self.default_fee_var.get().strip()

        # Check if at least ONE checkbox is ticked
        specialization = False
        for var in self.specialization_var.values():
            specialization = True
            break

        # Required: Name
        if not name:
            self._form_error("⚠ Name is required.")
            return
        elif len(name) < 2 or len(name) > 50:
            self._form_error("⚠ Name must be 2-50 characters.")
            return
        
        # Required: salary
        elif not self.is_float(salary):
            self._form_error("⚠ Please enter Salary in numbers only.")
            return

        # Required: status
        elif status not in ('Active', 'On-leave', 'Terminated'):
            self._form_error("⚠ Status is required.")
            return
        
        elif not specialization:
            self._form_error("Please select a specialization.")
            return

        # Required: Phone
        # have to be done

        if not self.is_float(defaultfee):
            self._form_error("Please enter Default Fee in numbers only.")
    
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
        name           = self.name_var.get().strip()
        phone          = self.phone_var.get().strip()
        salary         = self.salary_var.get().strip()
        status         = self.status_var.get().strip()
        defaultfee     = self.default_fee_var.get().strip() or '0'  # Since DefaultFee is optional so if it is '' so replace it with '0'

        # Create a list of the names of all checked specializations
        selected_specs = [spec for spec, var in self.specialization_var.items() if var.get()]
        
        # Convert list ["Yoga", "Zumba"] -> "Yoga, Zumba"
        specs_string = ", ".join(selected_specs)

        if mode == 'add':
            success = insert_trainer(name, phone, salary, specs_string, status, defaultfee)
        else:
            trainer_id = self.selected_row['trainer_id']
            success = update_trainer(trainer_id, name, phone, salary, specs_string, status, defaultfee)
        
        if success:   # Insertion Successful
            popup.destroy()
            # reseting selected row
            self.selected_row = None

            self.load_data()   
            self.selection_label.configure(text='No Row Selected')
            self.edit_btn.configure(state= 'disabled')
        else:
            messagebox.showerror(title="Error",
                                 message=f"Could not {mode} trainer. Check inputs or DB connection."
                                )

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
        
        export_to_excel(tree=self.table, default_filename="trainers_export")
        
