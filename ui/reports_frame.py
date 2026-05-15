import customtkinter as ctk
from tkinter import ttk, messagebox
from config.ui_config import DATA_FRAME_UI, FORM_UI
from services.report_service import (
    active_members_per_plan, trainer_workload,
    monthly_revenue, monthly_expenses, monthly_profit
)
from ui.excel_file_maker import export_to_excel

class ReportsFrame(ctk.CTkFrame):
    def __init__(self, content_area):
        super().__init__(content_area, fg_color=DATA_FRAME_UI['content_bg_color'])

        # Tabview
        self.tabview = ctk.CTkTabview(self,
                            corner_radius=10,
                            border_width=1,
                            fg_color="transparent",          # main body color
                            segmented_button_selected_color="#E1EEF9",
                            segmented_button_selected_hover_color=DATA_FRAME_UI['btn_hover'],
                            segmented_button_unselected_color="white",
                            segmented_button_unselected_hover_color=DATA_FRAME_UI['btn_hover'],
                            text_color=DATA_FRAME_UI['btn_text'],
                            text_color_disabled="gray")
        # self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.tabview.grid(row=0, column=0, sticky='nsew')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add tabs
        self.tabview.add("Plans")
        self.tabview.add("Trainers")
        self.tabview.add("Revenue")
        self.tabview.add("Expenses")
        self.tabview.add("Profit")
        
        # Build each tab
        self._build_plans_tab()
        self._build_trainers_tab()
        self._build_revenue_tab()
        self._build_expenses_tab()
        self._build_profit_tab()

    # ── Tab Builders ──────────────────────────────────────────────────────────────────────────────
    def _build_plans_tab(self):
        # Get the tab container
        tab = self.tabview.tab("Plans")

        tab.grid_rowconfigure(0, weight=0)  # label
        tab.grid_rowconfigure(1, weight=1)  # table expands
        tab.grid_rowconfigure(2, weight=0)  # action bar
        tab.grid_columnconfigure(0, weight=1)

        # ── LABEL ───────────────────────────────────────────────
        ctk.CTkLabel(tab, text="📊 Membership Plans Performance", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']+5)).grid(row=0, column=0, padx=6, pady=4, sticky="ns")

        # ── TABLE ───────────────────────────────────────────────
        cols   = ('plan_id','plan_name', 'active_count', 'revenue')
        heads  = ('Plan ID','Plan Name', 'Paid Active Memberships', 'Revenue')
        widths = (200, 300, 300, 200)
        anchs  = ('center', 'center', 'center', 'center')

        self.plan_table = self._build_table(parent=tab, columns=cols, headers=heads, widths=widths, anchors=anchs)

        # ── ACTION BAR ──────────────────────────────────────────
        self.action_bar = ctk.CTkFrame(tab, height=DATA_FRAME_UI['actionbar_height'])
        self.action_bar.grid(row=2, column=0, sticky="ew", padx=DATA_FRAME_UI['padding_x'], pady=DATA_FRAME_UI['padding_y'])

        self.action_bar.grid_columnconfigure(0, weight=1)
        self.action_bar.grid_columnconfigure((1, 2), weight=0)

        # ── Export button ────────────────────────────────────────
        export_btn = ctk.CTkButton(
            self.action_bar,
            text="📤 Export Plans Report",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=lambda: self._on_export(self.plan_table, "Plans_Report")
        )
        export_btn.grid(row=0, column=1, padx=4, pady=8)

        # ── Refresh button ───────────────────────────────────────
        refresh_btn = ctk.CTkButton(
            self.action_bar,
            text="⭮ Refresh",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=self._on_refresh
        )
        refresh_btn.grid(row=0, column=2, padx=(4, 8), pady=8)

        # Load Data
        self._load_plan_data()


    def _build_trainers_tab(self):
        # Get the tab container
        tab = self.tabview.tab("Trainers")

        tab.grid_rowconfigure(0, weight=0)  # label
        tab.grid_rowconfigure(1, weight=1)  # table expands
        tab.grid_rowconfigure(2, weight=0)  # action bar
        tab.grid_columnconfigure(0, weight=1)

        # ── LABEL ───────────────────────────────────────────────
        ctk.CTkLabel(tab, text="💪 Trainer Workload Analysis", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']+5)).grid(row=0, column=0, padx=6, pady=4, sticky="ns")

        # ── TABLE ───────────────────────────────────────────────
        cols =  ('trainer_id', 'name', 'salary', 'assigned_members', 'trainer_revenue')
        heads = ('Trainer ID', 'Trainer Name', 'Salary', 'Assigned Member', 'Revenue Generated')
        widths = (200, 300, 200, 200, 300)
        anchs = ('center', 'w', 'center', 'center', 'center')

        self.trainer_table = self._build_table(parent=tab, columns=cols, headers=heads, widths=widths, anchors=anchs)

        # ── ACTION BAR ──────────────────────────────────────────
        self.action_bar = ctk.CTkFrame(tab, height=DATA_FRAME_UI['actionbar_height'])
        self.action_bar.grid(row=2, column=0, sticky="ew", padx=DATA_FRAME_UI['padding_x'], pady=DATA_FRAME_UI['padding_y'])

        self.action_bar.grid_columnconfigure(0, weight=1)
        self.action_bar.grid_columnconfigure((1, 2), weight=0)

        # ── Export button ────────────────────────────────────────
        export_btn = ctk.CTkButton(
            self.action_bar,
            text="📤 Export Trianers Report",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=lambda: self._on_export(self.trainer_table, "Trainers_Report")
        )
        export_btn.grid(row=0, column=1, padx=4, pady=8)

        # ── Refresh button ───────────────────────────────────────
        refresh_btn = ctk.CTkButton(
            self.action_bar,
            text="⭮ Refresh",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=self._on_refresh
        )
        refresh_btn.grid(row=0, column=2, padx=(4, 8), pady=8)

        # Load Data
        self._load_trainer_data()


    def _build_revenue_tab(self):
        # Get the tab container
        tab = self.tabview.tab("Revenue")

        tab.grid_rowconfigure(0, weight=0)  # label
        tab.grid_rowconfigure(1, weight=1)  # table expands
        tab.grid_rowconfigure(2, weight=0)  # action bar
        tab.grid_columnconfigure(0, weight=1)

        # ── LABEL ───────────────────────────────────────────────
        ctk.CTkLabel(tab, text="💰 Revenue Analysis", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']+5)).grid(row=0, column=0, padx=6, pady=4, sticky="ns")

        # ── TABLE ───────────────────────────────────────────────
        cols =  ('year', 'month', 'total_revenue', 'no_of_transaction')
        heads = ('Year', 'Month', 'Total Revenue', 'Number of Transactions')
        widths = (200, 200, 200, 300)
        anchs = ('center', 'center', 'center', 'center')

        self.revenue_table = self._build_table(parent=tab, columns=cols, headers=heads, widths=widths, anchors=anchs)

        # ── ACTION BAR ──────────────────────────────────────────
        self.action_bar = ctk.CTkFrame(tab, height=DATA_FRAME_UI['actionbar_height'])
        self.action_bar.grid(row=2, column=0, sticky="ew", padx=DATA_FRAME_UI['padding_x'], pady=DATA_FRAME_UI['padding_y'])

        self.action_bar.grid_columnconfigure(0, weight=1)
        self.action_bar.grid_columnconfigure((1, 2), weight=0)

        # ── Export button ────────────────────────────────────────
        export_btn = ctk.CTkButton(
            self.action_bar,
            text="📤 Export Revenue Report",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=lambda: self._on_export(self.revenue_table, "Revenue_Report")
        )
        export_btn.grid(row=0, column=1, padx=4, pady=8)

        # ── Refresh button ───────────────────────────────────────
        refresh_btn = ctk.CTkButton(
            self.action_bar,
            text="⭮ Refresh",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=self._on_refresh
        )
        refresh_btn.grid(row=0, column=2, padx=(4, 8), pady=8)

        # Load Data
        self._load_revenue_data()


    def _build_expenses_tab(self):
        # Get the tab container
        tab = self.tabview.tab("Expenses")

        tab.grid_rowconfigure(0, weight=0)  # label
        tab.grid_rowconfigure(1, weight=1)  # table expands
        tab.grid_rowconfigure(2, weight=0)  # action bar
        tab.grid_columnconfigure(0, weight=1)

        # ── LABEL ───────────────────────────────────────────────
        ctk.CTkLabel(tab, text="💸 Expense Analysis", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']+5)).grid(row=0, column=0, padx=6, pady=4, sticky="ns")

        # ── TABLE ───────────────────────────────────────────────
        cols =  ('year', 'month', 'total_expense', 'no_of_transaction')
        heads = ('Year', 'Month', 'Total Expense', 'Number of Transactions')
        widths = (200, 200, 200, 300)
        anchs = ('center', 'center', 'center', 'center')

        self.expense_table = self._build_table(parent=tab, columns=cols, headers=heads, widths=widths, anchors=anchs)

        # ── ACTION BAR ──────────────────────────────────────────
        self.action_bar = ctk.CTkFrame(tab, height=DATA_FRAME_UI['actionbar_height'])
        self.action_bar.grid(row=2, column=0, sticky="ew", padx=DATA_FRAME_UI['padding_x'], pady=DATA_FRAME_UI['padding_y'])

        self.action_bar.grid_columnconfigure(0, weight=1)
        self.action_bar.grid_columnconfigure((1, 2), weight=0)

        # ── Export button ────────────────────────────────────────
        export_btn = ctk.CTkButton(
            self.action_bar,
            text="📤 Export Expense Report",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=lambda: self._on_export(self.expense_table, "Expense_Report")
        )
        export_btn.grid(row=0, column=1, padx=4, pady=8)

        # ── Refresh button ───────────────────────────────────────
        refresh_btn = ctk.CTkButton(
            self.action_bar,
            text="⭮ Refresh",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=self._on_refresh
        )
        refresh_btn.grid(row=0, column=2, padx=(4, 8), pady=8)

        # Load Data
        self._load_expense_data()

    def _build_profit_tab(self):
        # Get the tab container
        tab = self.tabview.tab("Profit")

        tab.grid_rowconfigure(0, weight=0)  # label
        tab.grid_rowconfigure(1, weight=1)  # table expands
        tab.grid_rowconfigure(2, weight=0)  # action bar
        tab.grid_columnconfigure(0, weight=1)

        # ── LABEL ───────────────────────────────────────────────
        ctk.CTkLabel(tab, text="📊 Profit Analysis", font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']+5)).grid(row=0, column=0, padx=6, pady=4, sticky="ns")

        # ── TABLE ───────────────────────────────────────────────
        cols =  ('year', 'month', 'revenue', 'expenses', 'profit')
        heads = ('Year', 'Month', 'Revenue', 'Expense', 'Profit / (Loss)')
        widths = (200, 200, 200, 200, 200)
        anchs = ('center', 'center', 'center', 'center', 'center')

        self.profit_table = self._build_table(parent=tab, columns=cols, headers=heads, widths=widths, anchors=anchs)

        # ── ACTION BAR ──────────────────────────────────────────
        self.action_bar = ctk.CTkFrame(tab, height=DATA_FRAME_UI['actionbar_height'])
        self.action_bar.grid(row=2, column=0, sticky="ew", padx=DATA_FRAME_UI['padding_x'], pady=DATA_FRAME_UI['padding_y'])

        self.action_bar.grid_columnconfigure(0, weight=1)
        self.action_bar.grid_columnconfigure((1, 2), weight=0)

        # ── Export button ────────────────────────────────────────
        export_btn = ctk.CTkButton(
            self.action_bar,
            text="📤 Export Profit Report",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=lambda: self._on_export(self.profit_table, "Profit_Report")
        )
        export_btn.grid(row=0, column=1, padx=4, pady=8)

        # ── Refresh button ───────────────────────────────────────
        refresh_btn = ctk.CTkButton(
            self.action_bar,
            text="⭮ Refresh",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=self._on_refresh
        )
        refresh_btn.grid(row=0, column=2, padx=(4, 8), pady=8)

        # Load Data
        self._load_profit_data()

   
    def _load_plan_data(self):
        # Fetch data
        rows = active_members_per_plan() 
        
        # Clear the specific table for this tab
        self.plan_table.delete(*self.plan_table.get_children())

        # Creating Stripped row tags
        self.plan_table.tag_configure('even', background=DATA_FRAME_UI['even'])
        self.plan_table.tag_configure('odd', background=DATA_FRAME_UI['odd'])
        count = 0
        
        # Loop and Insert
        for row in rows:
            if count%2 == 0:
                tag = 'even'
            else:
                tag = 'odd'
            count += 1

            plan_id = row['plan_id']
            formatted_pln_id = f'PLN-{plan_id}'
            plan_name = row['plan_name']
            active_count = row['active_count']
            
            # Format the revenue to look like "225,000 PKR"
            formatted_expense = f"{row['revenue']:,.0f} PKR" 
            
            # The order in 'values' MUST match the order of 'cols' in your _build function
            self.plan_table.insert(parent='', index='end', values=(
                formatted_pln_id,
                plan_name, 
                active_count, 
                formatted_expense),
                tags=(tag,)
            )

    def _load_trainer_data(self):
        # Fetch data
        rows = trainer_workload() 
        
        # Clear the specific table for this tab
        self.trainer_table.delete(*self.trainer_table.get_children())

        # Creating Stripped row tags
        self.trainer_table.tag_configure('even', background=DATA_FRAME_UI['even'])
        self.trainer_table.tag_configure('odd', background=DATA_FRAME_UI['odd'])
        count = 0
        
        # Loop and Insert
        for row in rows:
            if count%2 == 0:
                tag = 'even'
            else:
                tag = 'odd'
            count += 1

            trainer_id = row['trainer_id']
            formatted_trn_id = f'TRN-{trainer_id}'
            trianer_name = row['name']

            # Format the Salary to look like "225,000 PKR"
            formatted_salary = f"{row['salary']:,.0f} PKR" 

            assigned_members = row['assigned_members']

            # Format the Revenue to look like "225,000 PKR"
            formatted_expense = f"{row['trainer_revenue']:,.0f} PKR" 

        
            # The order in 'values' MUST match the order of 'cols' in your _build function
            self.trainer_table.insert(parent='', index='end', values=(
                formatted_trn_id, 
                trianer_name, 
                formatted_salary,
                assigned_members,
                formatted_expense),
                tags=(tag,)
            )

    def _load_revenue_data(self):
        rows = monthly_revenue()
        
        # Clear the specific table for this tab
        self.revenue_table.delete(*self.revenue_table.get_children())

        # Creating Stripped row tags
        self.revenue_table.tag_configure('even', background=DATA_FRAME_UI['even'])
        self.revenue_table.tag_configure('odd', background=DATA_FRAME_UI['odd'])
        count = 0
        
        # Month names for display
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        
        for row in rows:
            if count%2 == 0:
                tag = 'even'
            else:
                tag = 'odd'
            count += 1

            year = row['year']
            month_num = row['month']
            month_name = month_names.get(month_num, str(month_num))
            
            formatted_expense = f"{row['total_revenue']:,.0f} PKR" 
            transactions = row['no_of_transaction']
            
            self.revenue_table.insert(parent='', index='end', values=(
                year,
                month_name,
                formatted_expense,
                transactions),
                tags= (tag,)
            )

    def _load_expense_data(self):
        rows = monthly_expenses()
        
        # Clear the specific table for this tab
        self.expense_table.delete(*self.expense_table.get_children())

        # Creating Stripped row tags
        self.expense_table.tag_configure('even', background=DATA_FRAME_UI['even'])
        self.expense_table.tag_configure('odd', background=DATA_FRAME_UI['odd'])
        count = 0
    
        # Month names for display
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        
        for row in rows:
            if count%2 == 0:
                tag = 'even'
            else:
                tag = 'odd'
            count += 1

            year = row['year']
            month_num = row['month']
            month_name = month_names.get(month_num, str(month_num))
            
            formatted_expense = f"{row['total_expense']:,.0f} PKR" 
            transactions = row['no_of_transaction']
            
            self.expense_table.insert(parent='', index='end', values=(
                year,
                month_name,
                formatted_expense,
                transactions),
                tags= (tag,)
            )

    def _load_profit_data(self):
        rows = monthly_profit()
        
        # Clear the specific table for this tab
        self.profit_table.delete(*self.profit_table.get_children())
        
        # Month names for display
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }

        # Creating Stripped row tags
        self.profit_table.tag_configure('profit', background=DATA_FRAME_UI['profit'])
        self.profit_table.tag_configure('loss', background=DATA_FRAME_UI['loss'])
        
        for row in rows:
            year = row['year']
            month_num = row['month']
            month_name = month_names.get(month_num, str(month_num))
            
            formatted_revenue = f"{row['revenue']:,.0f} PKR" 
            formatted_expense = f"{row['expenses']:,.0f} PKR"

            if int(row['profit']) < 0:
                raw_profit = float(str(row['profit']).replace('-',''))
                tag = 'loss'

                formatted_profit  = f"({raw_profit:,.0f}) PKR"
            else:
                formatted_profit  = f"{row['profit']:,.0f} PKR"
                tag = 'profit'
            self.profit_table.insert(parent='', index='end', values=(
                year,
                month_name,
                formatted_revenue,
                formatted_expense,
                formatted_profit),
                tags= (tag,)
            )
                
    def _on_refresh(self):

        self._load_plan_data()
        self._load_trainer_data()
        self._load_revenue_data()
        self._load_expense_data()
        self._load_profit_data()

    def _on_export(self, table, filename):
        # Check if table has any rows
        if not table.get_children():
            messagebox.showwarning(title="Empty", message="No data to export.")
            return
        
        export_to_excel(tree=table, default_filename=filename)


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

    def _build_table(self, parent, columns : tuple, headers : tuple, widths : tuple, anchors : tuple):
        # ── Table container ───────────────────────────────────────────
        table_frame = ctk.CTkFrame(parent)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=DATA_FRAME_UI['padding_x'], pady=(0, 5))

        table_frame.grid_rowconfigure(0, weight=1)     # row 0 stretches
        table_frame.grid_columnconfigure(0, weight=1)  # col 0 stretches

        # ── Table Styling ───────────────────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview.Heading", font=("Arial", 16, "bold"))
        style.configure("Treeview", font=("Arial", 14), rowheight=35)

        # ── Table Section ───────────────────────────────────────────
        table = ttk.Treeview(table_frame, columns = columns, show= 'headings', selectmode="browse")
        for i in range(len(columns)):
            table.heading(columns[i], text = headers[i])

            # Column widths
            table.column(columns[i], width=widths[i], minwidth=widths[i], anchor=anchors[i])

        #table.bind('<<TreeviewSelect>>', self._on_row_select)

        # Scroll Bar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)

        # Grid both Tree and ScrollBar
        table.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')   # column 1, stretches vertically only

        return table