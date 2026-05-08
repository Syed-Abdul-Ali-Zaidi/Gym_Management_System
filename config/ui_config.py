# ══════════════════════════════════════════════════════════════════════════════
# UI CONFIGURATION — Single source of truth for all UI values
# Rule: APP_THEME is only used INSIDE this file.
#       Other files import the specific dict they need.
# ══════════════════════════════════════════════════════════════════════════════

# ── Base Theme Colors ──────────────────────────────────────────────────────────
APP_THEME = {
    # ── Accent (active sidebar, brand) ────────────────────────────────────────
    "primary_green":       "#1a3a5c",
    "hover_green":         "#4DA6FF",

    # ── Danger (delete, logout, errors) ───────────────────────────────────────
    "danger_red":          "#FF6B6B",
    "danger_hover":        "#4a1a1a",

    # ── Success (edit button) ──────────────────────────────────────────────────
    "success_green":       "#22C55E",
    "success_hover":       "#1B4332",

    # ── Neutral (standard buttons) ────────────────────────────────────────────
    "primary_color":       "#344E61",
    "primary_color_hover": "#D2EBFF",

    # ── Sidebar ───────────────────────────────────────────────────────────────
    "dark_bg":             "#0d1b2a",
    "border_color":        "#1a2e45",
}

# ── Global App Config ──────────────────────────────────────────────────────────
GLOBAL_UI = {
    "theme":           "light",
    "theme_color":     "blue",
    "window_size":     "1100x600",
    "min_window_size": (900, 550),
    "font_family":     "Georgia",
    "Data_font":       "Georgia"
}

# ── Login Frame ────────────────────────────────────────────────────────────────
LOGIN_UI = {
    # Layout
    "card_width":         380,
    "card_height":        480,
    "card_corner_radius": 16,
    "label_width":        300,
    "entry_width":        300,
    "entry_height":       40,

    # Font
    "font_family":    GLOBAL_UI["font_family"],
    "data_font":      GLOBAL_UI["Data_font"],
    "title_font_size":    22,
    "subtitle_font_size": 13,
    "button_font_size":   14,
    "label_font_size":    12,
    "emoji_size":         48,

    # Colors
    "subtitle_color":     "gray",
    "error_color":        APP_THEME["danger_red"],

    # ── Style: Login button ────────────────────────────────────────────────────
    "btn_fg":             APP_THEME["primary_color_hover"],
    "btn_border":         1,
    "btn_hover":          APP_THEME["primary_color"],
}

# ── Sidebar ────────────────────────────────────────────────────────────────────
SIDEBAR_UI = {
    # Layout
    "width":            210,
    "btn_height":       38,
    "btn_corner_radius":8,

    # Font
    "font_family":      GLOBAL_UI["font_family"],
    "title_font_size":  15,
    "btn_font_size":    13,
    "info_font_size":   11,

    # Colors
    "bg_color":         APP_THEME["dark_bg"],
    "divider_color":    APP_THEME["border_color"],
    "text_color":       "#ffffff",
    "info_color":       "gray",
    "brand_accent":     APP_THEME["hover_green"],

    # ── Style: Nav buttons ────────────────────────────────────────────────────
    "btn_active_color": APP_THEME["primary_green"],
    "btn_hover_color":  APP_THEME["hover_green"],

    # ── Style: Logout ─────────────────────────────────────────────────────────
    "logout_text":      APP_THEME["danger_red"],
    "logout_hover":     APP_THEME["danger_hover"],
}

# ── Main Content Container ─────────────────────────────────────────────────────
CONTENT_CONTAINER_UI = {
    "content_bg": "transparent",
    "padding_x":  0,
    "padding_y":  0,
}

# ══════════════════════════════════════════════════════════════════════════════
# DATA FRAME UI — Used by EVERY module frame (Members, Trainers, Plans...)
# ══════════════════════════════════════════════════════════════════════════════
DATA_FRAME_UI = {
    # Layout
    "padding_x":             10,
    "padding_y":             10,
    "topbar_height":         60,
    "actionbar_height":      50,
    "btn_height":            38,
    "topbar_btn_width":      110,
    "actionbar_btn_width":   100,

    # Font
    "btn_font_family":    GLOBAL_UI["font_family"],
    "data_font":          GLOBAL_UI["Data_font"],
    "btn_font_size":      13,

    # ── Style: Standard (Search, Add, Export, Save, Cancel) ───────────────────
    "btn_fg":             "#FFFFFF",
    "btn_border":         1,
    "btn_hover":          APP_THEME["primary_color_hover"],
    "btn_text":           APP_THEME["primary_color"],

    # ── Style: Edit ───────────────────────────────────────────────────────────
    "edit_fg":            "transparent",
    "edit_text":          APP_THEME["success_green"],
    "edit_hover":         APP_THEME["success_hover"],

    # ── Style: Delete ─────────────────────────────────────────────────────────
    "delete_fg":          "transparent",
    "delete_text":        APP_THEME["danger_red"],
    "delete_hover":       APP_THEME["danger_hover"],

    # ── Error label ───────────────────────────────────────────────────────────
    "error_text":         APP_THEME["danger_red"],

    # ── Table strips ──────────────────────────────────────────────────────────
    "even":               "#f5f5f5",
    "odd":                "#ffffff",

    # ── Trainer status row colors ─────────────────────────────
    "trainer_active":      "#DCFCE7",   # soft green
    "trainer_on_leave":    "#FEF3C7",   # soft yellow
    "trainer_terminated":  "#FEE2E2",   # soft red

    # ── Member status row colors ─────────────────────────────
    "member_active":      "#DCFCE7",   # soft green
    "member_inactive":    "#FEE2E2",   # soft red

    # ── Plan status row colors ─────────────────────────────
    "plan_active":      "#DCFCE7",   # soft green
    "plan_discontinued":    "#FEE2E2",   # soft red

    # ── User status row colors ─────────────────────────────
    "user_active":      "#DCFCE7",   # soft green
    "user_inactive":    "#FEE2E2",   # soft red

    }

# ── Popup Form UI — Used by every frame's popup ────────────────────────────────
FORM_UI = {
    # Layout
    "data_font":      GLOBAL_UI["Data_font"],
    "padx":             10,
    "pady":             10,
    "frame_padx":       20,
    "frame_pady":       20,
    "row_pady":         2.5,
    "label_padx":       10,
    "entry_padx":       10,
    "label_sticky":     "e",
    "entry_sticky":     "w",
    "btn_width":        100,
    "btn_padx":         10,
    "btn_pady_bottom":  20,

    # ── Error label ───────────────────────────────────────────────────────────
    "error_color":      APP_THEME["danger_red"]
}