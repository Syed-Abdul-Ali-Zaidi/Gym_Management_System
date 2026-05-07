# import customtkinter as ctk

# class PlansFrame(ctk.CTkFrame):
#     def __init__(self, content_area):
#         super().__init__(content_area, fg_color="transparent")


import customtkinter as ctk
from tkinter import ttk, messagebox
from config.ui_config import DATA_FRAME_UI, FORM_UI
from services.plan_service import (
    get_all_plan, search_plan,
    insert_plan, update_plan, delete_plan
)
from ui.excel_file_maker import export_to_excel

class PlansFrame(ctk.CTkFrame):
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
        ctk.CTkLabel(self.topbar_frame, text="Search by PlanID or PlanName", font=ctk.CTkFont(size=10)).grid(row=0, column=0, padx=(6,4), pady=(1,0), sticky="w")

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
        self.table = ttk.Treeview(self.table_frame, columns= ('plan_id', 'plan_name', 'duration_days', 'fee'), show= 'headings', selectmode="browse")
        self.table.heading('plan_id',       text= 'Plan ID')
        self.table.heading('plan_name',     text= 'Plan Name')
        self.table.heading('duration_days', text= 'Duration Days')
        self.table.heading('fee',           text= 'Fee')

        # Column widths
        self.table.column('plan_id',       width=150, minwidth=150, anchor='center')
        self.table.column('plan_name',     width=250, minwidth=250)
        self.table.column('duration_days', width=100, minwidth=100, anchor='center')
        self.table.column('fee',           width=150, minwidth=150, anchor='center')

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

    def load_data(self):
        rows = get_all_plan()
        self._refresh_table(rows)

    def _refresh_table(self,rows):
        # Deletes existing rows
        self.table.delete(*self.table.get_children())

        # Creating Stripped row tags
        self.table.tag_configure('oddrow', background=DATA_FRAME_UI['odd'])
        self.table.tag_configure('evenrow', background=DATA_FRAME_UI['even'])
        
        count = 0
        keys = ['evenrow', 'oddrow']

        # inserts New Data
        for row in rows:
            tag = keys[count % 2]
            self.table.insert(parent='', index= 'end', values=(
                row['plan_id'],
                row['plan_name'],
                row['duration_days'],
                row['fee']),
                tags= (tag,)
            )

            count += 1




    def _on_search(self,  *args):
        search_term = self.searchbar_var.get().strip()
        # if there is no SearchTerm, Load Normal Data
        if not search_term:
            self.load_data()
        # Else search the Data and load it
        else:
            rows = search_plan(search_term)
            self._refresh_table(rows)

        # Clear selection after every search
        self.selected_row = None
        self.selection_label.configure(text='No row selected')
        self.edit_btn.configure(state='disabled')
        self.delete_btn.configure(state='disabled')

    def _on_row_select(self, event):
        column_names = ['plan_id', 'plan_name', 'duration_days', 'fee']
        selected = self.table.selection()

        if not selected:
            self.selection_label.configure(text='No Row Selected')
            return None
        
        item_id = selected[0]
        values = self.table.item(item_id)["values"]
        self.selected_row = dict(zip(column_names, values))

        # Updating the Selection Label
        self.selection_label.configure(text= f'ID: {self.selected_row['plan_id']} | Name: {self.selected_row['plan_name']}')

        # Enabling the Edit and Delete bottons
        self.delete_btn.configure(state='normal')
        self.edit_btn.configure(state='normal')


            

    def _on_delete(self):
        if self.selected_row is None:
            return
        
        # First ask for confirmation on Delete
        confirmed = messagebox.askyesno(title="Confirm", message="Delete this planget_all_plan?")
        if confirmed:
            item_id = self.selected_row['plan_id']
            success = delete_plan(item_id)

            if success:   # deletion Successful
                self.load_data()
                # reseting selected row
                self.selected_row = None

                self.selection_label.configure(text='No Row Selected')
                self.delete_btn.configure(state= 'disabled')
                self.edit_btn.configure(state= 'disabled')
            else:
                messagebox.showerror(title="Error",
                                     message="Could not delete plan.\nThey may have an active planget_all_planship."
                                    )




    def _on_add(self):
        self._open_form('add')


    def _on_edit(self):
        if self.selected_row is None:
            return
        self._open_form('edit')

    def _open_form(self, mode):
        popup = ctk.CTkToplevel(self)
        popup.title("Add Plan" if mode == "add" else "Edit Plan")
        popup.geometry('400x280')
        popup.resizable(False, False) 
        
        # Create StringVars here — they live as long as popup lives
        self.name_var     = ctk.StringVar()
        self.days_var    = ctk.StringVar()
        self.fee_var    = ctk.StringVar()

        
        # Pass popup to field builder
        self._build_form_fields(popup)
        self._build_form_buttons(popup, mode)

        if mode == 'edit':
            self.name_var.set(self.selected_row['plan_name'])
            self.days_var.set(self.selected_row['duration_days'])
            self.fee_var.set(self.selected_row['fee'])
        
        popup.grab_set()    # User CANNOT click anything in the main window until popup closes
        popup.transient(self.winfo_toplevel())    # Popup won't go behind the main window

        

    def _build_form_fields(self, popup):
        form_frame = ctk.CTkFrame(popup)
        form_frame.grid(row=0, column=0, padx=FORM_UI['padx'], pady=FORM_UI['pady'])

        # Row 0 - Name
        ctk.CTkLabel(form_frame, text="Name:").grid(row=0, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        ctk.CTkEntry(form_frame, textvariable=self.name_var).grid(row=0, column=1, padx=10, pady=FORM_UI['row_pady'])

        # Row 1 - days
        ctk.CTkLabel(form_frame, text="Duration (days):").grid(row=1, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        ctk.CTkEntry(form_frame, textvariable=self.days_var).grid(row=1, column=1, padx=10, pady=FORM_UI['row_pady'])

        # Row 2 - fee
        ctk.CTkLabel(form_frame, text="Fee:").grid(row=2, column=0, padx=10, pady=FORM_UI['row_pady'], sticky=FORM_UI["label_sticky"])
        ctk.CTkEntry(form_frame, textvariable=self.fee_var).grid(row=2, column=1, padx=10, pady=FORM_UI['row_pady'])

        # Row 3 - Error message
        self.error_label = ctk.CTkLabel(form_frame, text="", text_color=FORM_UI['error_color'])
        self.error_label.grid(row=5, column=0, columnspan=2)

        # Adding traces to Each Variable. means calling a function whenever variable's value changes
        self.name_var.trace_add("write", self._validate)
        self.days_var.trace_add("write", self._validate)
        self.fee_var.trace_add("write", self._validate)

    def _build_form_buttons(self, popup, mode):
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.grid(row=1, column=0, pady=(0, FORM_UI['btn_pady_bottom']))


        self.save_btn = ctk.CTkButton(btn_frame, text="Save", width=FORM_UI['btn_width'], border_width=DATA_FRAME_UI['btn_border'], fg_color=DATA_FRAME_UI['btn_fg'], hover_color=DATA_FRAME_UI['btn_hover'],state='disabled', text_color=DATA_FRAME_UI['btn_text'], command= lambda: self._on_save(popup,mode))
        self.save_btn.pack(side="left", padx=FORM_UI['btn_padx'])

        self.cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", width=FORM_UI['btn_width'], border_width=DATA_FRAME_UI['btn_border'], fg_color=DATA_FRAME_UI['btn_fg'], hover_color=DATA_FRAME_UI['btn_hover'], text_color=DATA_FRAME_UI['btn_text'], command= popup.destroy)
        self.cancel_btn.pack(side="left", padx=FORM_UI['btn_padx'])

    def _validate(self, *args):
        name      = self.name_var.get().strip()
        days     = self.days_var.get().strip()
        fee     = self.fee_var.get().strip()

        # Required: Name
        if not name:
            self._form_error("⚠ Plan Name is required.")
            return
        if len(name) < 2 or len(name) > 50:
            self._form_error("⚠ Plan Name must be 2-50 characters.")
            return
        
        # Required: days
        if not days.isdigit():
            self._form_error("⚠ Please enter Dauration in numbers only.")
            return

        # Required: fees
        if not self.is_float(fee):
            self._form_error("⚠ Please enter Fee in numbers only.")
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
        days     = self.days_var.get().strip()
        fee     = self.fee_var.get().strip()

        if mode == 'add':
            success = insert_plan(name, days, fee)
        else:
            plan_id = self.selected_row['plan_id']
            success = update_plan(plan_id, name, days, fee)
        
        if success:   # Insertion Successful
            popup.destroy()
            # reseting selected row
            self.selected_row = None

            self.load_data()   
            self.selection_label.configure(text='No Row Selected')
            self.delete_btn.configure(state= 'disabled')
            self.edit_btn.configure(state= 'disabled')
        else:
            messagebox.showerror(title="Error",
                                 message=f"Could not {mode} planget_all_plan. Check inputs or DB connection."
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
        
        export_to_excel(tree=self.table, default_filename="planget_all_planship_plans_export")
        


