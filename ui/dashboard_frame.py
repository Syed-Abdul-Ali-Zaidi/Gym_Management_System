import customtkinter as ctk
from config.ui_config import DATA_FRAME_UI
from services.auth_service import (get_session, get_dashboard_data)
from datetime import datetime

class DashboardFrame(ctk.CTkFrame):
    def __init__(self,content_area):
        super().__init__(content_area,  fg_color=DATA_FRAME_UI['content_bg_color'], border_width=2, corner_radius=10)
        pass

        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=0)  # header, stats row 1, stats row 2
        #self.grid_rowconfigure(3, weight=1)  # quick actions (expands)
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

        # ─── Instance Variables ───────────────────────────────────────────────
        self.user_id  = get_session()['user_id']
        self.username = get_session()['username']
        # getting current and previous month names
        now = datetime.now()
        self.current_month = now.strftime("%B %Y")

        if now.month == 1:
            previous_month = now.replace(
                year=now.year - 1,
                month=12
            )
        else:
            previous_month = now.replace(
                month=now.month - 1
            )
        self.previous_month = previous_month.strftime("%B %Y")

        self._build_header()
        self._build_stats_cards()
        self._load_data()

    def _build_header(self):
        """Header with title and current date"""
        header_frame = ctk.CTkFrame(self, fg_color=DATA_FRAME_UI['card_fg_color'], border_width=1, border_color=DATA_FRAME_UI['card_border_color'])
        header_frame.grid(row=0, column=0, columnspan=8, sticky="ew", padx=20, pady=(20, 10))
        
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        ctk.CTkLabel(
            header_frame,
            text=f"Welcome, {self.username}",
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=34, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Current date
        current_date = datetime.now().strftime("%d %B %Y")
        ctk.CTkLabel(
            header_frame,
            text=f"📅 {current_date}",
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=16),
            text_color=DATA_FRAME_UI['btn_text']
        ).grid(row=0, column=1, padx=2, pady=6, sticky="e")

        # Refresh Botton
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="⭮ Refresh",
            width=DATA_FRAME_UI['topbar_btn_width'],
            height=DATA_FRAME_UI['btn_height'],
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=DATA_FRAME_UI['btn_font_size']),
            fg_color=DATA_FRAME_UI['btn_fg'],
            border_width=DATA_FRAME_UI['btn_border'],
            hover_color=DATA_FRAME_UI['btn_hover'],
            text_color=DATA_FRAME_UI['btn_text'],
            command=self._load_data
        )
        refresh_btn.grid(row=0, column=2, padx=(4, 6), pady=6)


    def _build_stats_cards(self):
        # 1. Active Members  ───────────────────────────────────────────────
        self.active_member = self._create_stat_card(
            row     = 1,
            col     = 0,
            columnspan=2,
            icon    = "👤",
            label   = "Active Members:",
            value   = '---',
            padx    = (20,10),
            pady    = 10
        )

        # 2. Active Memberships  ───────────────────────────────────────────────
        self.active_membership = self._create_stat_card(
            row     = 1,
            col     = 2,
            columnspan=2,
            icon    = "🪪",
            label   = "Active\nMemberships:",
            value   = '---',
            padx    = 10,
            pady    = 10
        )

        # 3. Paid Active Memberships  ───────────────────────────────────────────────
        self.paid_active_membership = self._create_stat_card(
            row     = 1,
            col     = 4,
            columnspan=2,
            icon    = "✔",
            label   = "Paid Active\nMemberships:",
            value   = '---',
            padx    = 10,
            pady    = 10
        )

        # 4. Paid Active Memberships  ───────────────────────────────────────────────
        self.unpaid_active_membership = self._create_stat_card(
            row     = 1,
            col     = 6,
            columnspan=2,
            icon    = "❌",
            label   = "Unpaid Active\nMemberships:",
            value   = '---',
            padx    = (10,20),
            pady    = 10
        )

        # Current Month LABEL  ───────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text=f"This Month ({self.current_month})",
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=14),
            text_color="black"
        ).grid(row=2, column=0, columnspan=8, padx=20, pady=(10,0), sticky='w')

        # 5. Current Revenue
        self.current_revenue = self._create_stat_card(
            row     = 3,
            col     = 1,
            columnspan=2,
            icon    = "💰",
            label   = "Revenue:",
            value   = '---',
            padx    = (20,10),
            pady    = 10
        )

        # 6. Current Expense
        self.current_expense = self._create_stat_card(
            row     = 3,
            col     = 3,
            columnspan=2,
            icon    = "💸",
            label   = "Expense:",
            value   = '---',
            padx    = 10,
            pady    = 10
        )

        # 7. Current Profit
        self.current_pro_loss = self._create_stat_card(
            row     = 3,
            col     = 5,
            columnspan= 2,
            icon    = "💵",
            label   = "Profit / (Loss):",
            value   = '---',
            padx    = (10,20),
            pady    = 10
        )

        # Previous Month LABEL  ───────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text=f"Last Month ({self.previous_month})",
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=14),
            text_color="black"
        ).grid(row=4, column=0, columnspan=8, padx=20, pady=(10,0), sticky='w')

        # 8. Past revenue
        self.past_revenue = self._create_stat_card(
            row     = 5,
            col     = 1,
            columnspan=2,
            icon    = "💰",
            label   = "Revenue:",
            value   = '---',
            padx    = (20,10),
            pady    = 10
        )

        # 9. Past Expense
        self.past_expense = self._create_stat_card(
            row     = 5,
            col     = 3,
            columnspan=2,
            icon    = "💸",
            label   = "Expense:",
            value   = '---',
            padx    = 10,
            pady    = 10
        )

        # 10. Past Profit/Loss
        self.past_pro_loss = self._create_stat_card(
            row     = 5,
            col     = 5,
            columnspan= 2,
            icon    = "💵",
            label   = "Profit / (Loss):",
            value   = '---',
            padx    = (10,20),
            pady    = 10
        )

    


    def _create_stat_card(self, row, col, icon, label, value, color=DATA_FRAME_UI['card_fg_color'], border_color=DATA_FRAME_UI['card_border_color'], padx = 10, pady = 10, columnspan=1):
        """Helper to create a stat card"""
        card = ctk.CTkFrame(
            self,
            fg_color=color,
            corner_radius=10,
            border_width=1,
            border_color= border_color
        )
        card.grid(row=row, column=col, columnspan=columnspan, sticky='nsew', padx=padx, pady=pady)
        
        # Icon
        ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=20)
        ).pack(pady=(15, 5))
        
        # Label
        ctk.CTkLabel(
            card,
            text=label,
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=15),
            text_color=DATA_FRAME_UI['btn_text']
        ).pack()
        
        # Value (store reference for updating)
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(family=DATA_FRAME_UI['btn_font_family'], size=28, weight="bold")
        )
        value_label.pack(pady=(5, 15))
        
        return value_label  # Return label so we can update it later
    
    def _load_data(self):
        data = get_dashboard_data()
                    #f"{row['revenue']:,.0f} PKR"
        active_member = f"{data['active_members']:,.0f}"
        active_membership = f"{data['active_memberships']:,.0f}"
        paid_active_membership = f"{data['paid_active_memberships']:,.0f}"
        unpaid_active_membership = f"{data['unpaid_active_memberships']:,.0f}"

        current_revenue  = f"{data['current_revenue']:,.0f}"
        current_expense  = f"{data['current_expense']:,.0f}"

        raw_current_pro_loss = data['current_pro_loss']
        if int(raw_current_pro_loss) < 0:
            raw_current_pro_loss = float(str(raw_current_pro_loss).replace("-",""))
            current_pro_loss = f"({raw_current_pro_loss:,.0f})"
            current_text_color = DATA_FRAME_UI['delete_text']
        else:
            current_pro_loss = f"{raw_current_pro_loss:,.0f}"
            current_text_color = DATA_FRAME_UI['edit_text']

        past_revenue  = f"{data['past_revenue']:,.0f}"
        past_expense  = f"{data['past_expense']:,.0f}"
        
        raw_past_pro_loss = data['past_pro_loss']
        if int(raw_past_pro_loss) < 0:
            raw_past_pro_loss = float(str(raw_past_pro_loss).replace("-",""))
            past_pro_loss = f"({raw_past_pro_loss:,.0f})"
            past_text_color = DATA_FRAME_UI['delete_text']
        else:
            past_pro_loss = f"{raw_past_pro_loss:,.0f}"
            past_text_color = DATA_FRAME_UI['edit_text']

        self.active_member.configure(text = active_member)
        self.active_membership.configure(text = active_membership)
        self.paid_active_membership.configure(text = paid_active_membership)
        self.unpaid_active_membership.configure(text = unpaid_active_membership)
        self.current_revenue.configure(text = current_revenue)
        self.current_expense.configure(text = current_expense)
        self.current_pro_loss.configure(text = current_pro_loss, text_color = current_text_color)
        self.past_revenue.configure(text = past_revenue)
        self.past_expense.configure(text = past_expense)
        self.past_pro_loss.configure(text = past_pro_loss, text_color = past_text_color)

