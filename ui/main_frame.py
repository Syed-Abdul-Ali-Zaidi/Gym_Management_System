import customtkinter as ctk
from config.ui_config import SIDEBAR_UI, CONTENT_CONTAINER_UI
from services.auth_service import is_admin, get_session, current_session

# ── Import all content frames ──────────────────────────────────────────────────
# We import them all here so _build_frames() can create them
from ui.dashboard_frame import DashboardFrame
from ui.members_frame import MembersFrame
from ui.plans_frame import PlansFrame
from ui.trainers_frame import TrainersFrame
from ui.memberships_frame import MembershipsFrame
from ui.payments_frame import PaymentsFrame
from ui.expenses_frame import ExpensesFrame
from ui.reports_frame import ReportsFrame
from ui.admin.users_frame import UsersFrame
from ui.admin.audit_frame import AuditFrame


class MainApp(ctk.CTkFrame):
    """
    The main shell after login.
    Contains sidebar (left) and content area (right).
    
    Responsibilities:
    - Build sidebar with nav buttons
    - Build all content frames and stack them
    - Switch between frames on button click
    - Handle logout
    
    Does NOT contain any business logic — that lives in each frame.
    """
    def __init__(self, parent, on_logout):
        super().__init__(parent, fg_color=CONTENT_CONTAINER_UI['content_bg'])

        # Store logout callback — called when user clicks logout
        self.on_logout = on_logout

        # Track which sidebar button is currently highlighted
        # Starts as None — will be set when first frame is shown
        self.active_button = None

        # ── Grid: 1 row, 2 columns ─────────────────────────────────────────────
        # column 0 = sidebar (fixed width, doesn't grow)
        # column 1 = content area (grows to fill remaining space)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)   # sidebar: fixed
        self.grid_columnconfigure(1, weight=1)   # content: stretches

        # ── Build the two zones ────────────────────────────────────────────────
        self._build_sidebar()
        self._build_content_area()

        # ── Create all frames and stack them in content area ───────────────────
        self._build_frames()

        # ── Show Dashboard as the default screen ──────────────────────────────
        # This also highlights the Dashboard button
        self.show_frame("dashboard", self.dashboard_btn)

    # ══════════════════════════════════════════════════════════════════════════
    # SIDEBAR
    # ══════════════════════════════════════════════════════════════════════════

    def _build_sidebar(self):
        """
        Creates the left sidebar panel.
        Uses pack() internally because it's a vertical stack of widgets.
        """

        # ── Sidebar container ──────────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(
            self,
            width=SIDEBAR_UI['width'],
            fg_color=SIDEBAR_UI['bg_color'],
            corner_radius=0      # no rounded corners — flush with window edge
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Prevent sidebar from shrinking to fit children
        self.sidebar.pack_propagate(False)

        # ── Title / Logo area ──────────────────────────────────────────────────
        ctk.CTkLabel(
            self.sidebar,
            text="🏋️  GYM MANAGER",
            font=ctk.CTkFont(family=SIDEBAR_UI['font_family'], size=SIDEBAR_UI['title_font_size'], weight="bold"),
            text_color=SIDEBAR_UI['brand_accent']     # green accent for brand feel
        ).pack(pady=(24, 4), padx=16, anchor="w")

        # Session info: "Logged in as Ali | Admin"
        session = get_session()
        ctk.CTkLabel(
            self.sidebar,
            text=f"👤 {session['username']}  |  {session['role']}",
            font=ctk.CTkFont(size=SIDEBAR_UI['info_font_size']),
            text_color=SIDEBAR_UI['info_color']
        ).pack(padx=16, anchor="w")

        # Thin horizontal line as divider
        ctk.CTkFrame(self.sidebar, height=1, fg_color=SIDEBAR_UI['divider_color']).pack(
            fill="x", padx=12, pady=(16, 8)
        )

        # ── Navigation buttons ─────────────────────────────────────────────────
        # Each tuple: (display text, frame key, button attribute name)
        # Button attribute name lets us reference each button later (for highlighting)
        nav_items = [
            ("🗂️Dashboard",    "dashboard",    "dashboard_btn"),
            ("👥    Members",      "members",      "members_btn"),
            ("🏷️Plans",        "plans",        "plans_btn"),
            ("💪    Trainers",     "trainers",     "trainers_btn"),
            ("📋    Memberships",  "memberships",  "memberships_btn"),
            ("💳    Payments",     "payments",     "payments_btn"),
            ("💸    Expenses",     "expenses",     "expenses_btn"),
            ("📊    Reports",      "reports",      "reports_btn"),
        ]

        # Using loop to create bottons and assign them to thier respective varible name
        for label, frame_key, btn_attr in nav_items:
            btn = self._make_nav_button(label, frame_key)
            # Store button as instance attribute using setattr
            # e.g. setattr(self, "members_btn", btn) = self.members_btn = btn
            # We need this so show_frame() can highlight the right button
            setattr(self, btn_attr, btn)

        # ── Admin-only section ─────────────────────────────────────────────────
        # is_admin() reads current_session — already set during login
        if is_admin():
            # Thin Horizontal Divider line
            ctk.CTkFrame(self.sidebar, height=1, fg_color=SIDEBAR_UI['divider_color']).pack(
                fill="x", padx=12, pady=(12, 4)
            )

            # Making 2 extra bottons for admin
            btn = self._make_nav_button("👤   Users", "users")
            setattr(self, "users_btn", btn)

            btn = self._make_nav_button("🔍   Audit Log", "audit")
            setattr(self, "audit_btn", btn)

        # ── Logout button — pinned to bottom ───────────────────────────────────
        # Thin Horizontal Divider line
        ctk.CTkFrame(self.sidebar, height=1, fg_color=SIDEBAR_UI['divider_color']).pack(
            fill="x", padx=12, pady=(0, 8)
        )

        ctk.CTkButton(
            self.sidebar,
            text="🚪   Logout",
            anchor="w",
            font=ctk.CTkFont(family=SIDEBAR_UI['font_family'], size=SIDEBAR_UI['btn_font_size']),
            fg_color="transparent",
            hover_color=SIDEBAR_UI['logout_hover'],       # dark red hover for logout
            text_color=SIDEBAR_UI['logout_text'],        # red tint to signal danger action
            command=self._handle_logout
        ).pack(fill="x", padx=8, pady=(0, 16), side = 'bottom')

    def _make_nav_button(self, label, frame_key):
        """
        Helper that creates one sidebar nav button.
        Extracted to a method to avoid repeating the same CTkButton config 8+ times.
        
        Why lambda here?
            command=self.show_frame("members") would call show_frame immediately
            command=lambda: self.show_frame(...) defers the call until click
        
        But there's a classic Python closure bug with lambdas in loops:
            lambda: self.show_frame(frame_key, btn)
            All lambdas would capture the LAST value of frame_key and btn
        
        Fix: use default argument to capture current value at creation time:
            lambda fk=frame_key, b=btn: self.show_frame(fk, b)
        """
        btn = ctk.CTkButton(
            self.sidebar,
            text=label,
            anchor="w",                         # left-align text
            font=ctk.CTkFont(family=SIDEBAR_UI['font_family'], size=SIDEBAR_UI['btn_font_size']),
            fg_color="transparent",             # no background by default
            hover_color=SIDEBAR_UI['btn_hover_color'],
            text_color=SIDEBAR_UI['text_color'],
            corner_radius=SIDEBAR_UI['btn_corner_radius'],
            height=SIDEBAR_UI['btn_height'],
        )
        btn.pack(fill="x", padx=8, pady=2)

        # Set command AFTER creation so we can reference btn itself
        # Default argument trick explained in docstring above
        btn.configure(command=lambda fk=frame_key, b=btn: self.show_frame(fk, b))

        return btn

    # ══════════════════════════════════════════════════════════════════════════
    # CONTENT AREA
    # ══════════════════════════════════════════════════════════════════════════

    def _build_content_area(self):
        """
        Creates the right side container where all frames will live.
        All frames are stacked here — only one visible at a time.
        """
        self.content_area = ctk.CTkFrame(self, fg_color=CONTENT_CONTAINER_UI['content_bg'])
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=CONTENT_CONTAINER_UI['padding_x'], pady=CONTENT_CONTAINER_UI['padding_y'])

        # Content area itself needs to stretch to fill its space
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

    def _build_frames(self):
        """
        Creates ALL content frames and places them in the same grid cell.
        They stack on top of each other — tkraise() brings one to the front.
        
        Think of it like a deck of cards all placed at position (0,0).
        """
        # All frames go in row=0, col=0 of content_area
        # sticky="nsew" makes each frame fill the entire content area
        frame_classes = {
            "dashboard":   DashboardFrame,
            "members":     MembersFrame,
            "plans":       PlansFrame,
            "trainers":    TrainersFrame,
            "memberships": MembershipsFrame,
            "payments":    PaymentsFrame,
            "expenses":    ExpensesFrame,
            "reports":     ReportsFrame,
        }

        # Admin frames added only if user is admin
        if is_admin():
            frame_classes["users"] = UsersFrame
            frame_classes["audit"] = AuditFrame

        # Create each frame and store in self.frames dict
        self.frames = {}
        for key, FrameClass in frame_classes.items():
            frame = FrameClass(self.content_area)
            frame.grid(row=0, column=0, sticky="nsew")  # .grid() used to stack frame on each other
            self.frames[key] = frame

        # At this point all frames exist but are stacked
        # show_frame() will lift the right one to the top

    # ══════════════════════════════════════════════════════════════════════════
    # FRAME SWITCHING
    # ══════════════════════════════════════════════════════════════════════════

    def show_frame(self, name, button):
        """
        Brings the named frame to the front and highlights its sidebar button.
        
        tkraise() lifts a widget to the top of the stacking order.
        It doesn't destroy or hide others — just covers them.
        
        Args:
            name   : key in self.frames dict e.g. "members"
            button : the CTkButton that was clicked (for highlighting)
        """

        # ── Reset previously active button ─────────────────────────────────────
        if self.active_button:
            self.active_button.configure(fg_color="transparent")

        # ── Highlight new active button ────────────────────────────────────────
        button.configure(fg_color=SIDEBAR_UI['btn_active_color'])
        self.active_button = button   # remember it for next switch

        # ── Bring frame to front ───────────────────────────────────────────────
        self.frames[name].tkraise()

    # ══════════════════════════════════════════════════════════════════════════
    # LOGOUT
    # ══════════════════════════════════════════════════════════════════════════

    def _handle_logout(self):
        """
        1. Clear the session (security — don't leave user data in memory)
        2. Call on_logout callback → App.show_login() runs
        """

        # Clear session data so no frame can accidentally use stale user info
        current_session.update({
            "user_id":  None,
            "username": None,
            "role":     None
        })

        # App will set self.main_app = None after this
        self.on_logout()