import customtkinter as ctk
from config.ui_config import GLOBAL_UI
from ui.login_frame import LoginFrame


# ── App-wide appearance settings ──────────────────────────────────────────────
# These must be set BEFORE creating the CTk() window
ctk.set_appearance_mode(GLOBAL_UI['theme'])       # "dark" | "light" | "system"
ctk.set_default_color_theme(GLOBAL_UI['theme_color'])  # gives us green accent buttons for free


class App(ctk.CTk):
    """
    Root window. Think of this as the 'shell'.
    It doesn't contain any real UI — it just decides WHAT to show.

    We inherit from CTk (not CTkFrame) because this IS the window itself.

    Responsibilities:
    - biuld Main Root Window
    - Act as an exchanger between login_frame and Main_frame
    """

    def __init__(self):
        super().__init__()

        # ── Window config ──────────────────────────────────────────────────────
        self.title("Gym Management System")
        self.geometry(GLOBAL_UI['window_size'])       # width x height in pixels
        self.minsize(GLOBAL_UI['min_window_size'][0], GLOBAL_UI['min_window_size'][1])          # user can't shrink below this

        # ── Make the window fill its grid cell (1 row, 1 col) ─────────────────
        # This ensures child frames stretch to fill the window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Start with login ───────────────────────────────────────────────────
        # We pass 'self.show_main_app' as a CALLBACK.
        # LoginFrame will call this function when login succeeds.
        # The frame doesn't need to know anything about the main app —
        # it just calls the callback and lets App handle the rest.
        self.login_frame = None
        self.main_app = None    # Initialize both attribute as None to handle any error

        self.login_frame = LoginFrame(
            parent=self,
            on_success=self.show_main_app
        )

        # grid() instead of pack() because we set grid weights above
        # sticky="nsew" means: stretch in all 4 directions (north south east west)
        self.login_frame.grid(row=0, column=0, sticky="nsew")

    def show_main_app(self):
        """
        Called by LoginFrame after successful login.
        Destroys login, shows the main sidebar app.

        We import MainApp HERE (not at top) to avoid circular imports.
        main_app.py will import frames that import services —
        importing it only when needed keeps startup clean.
        """
        # Destroy the login frame after successful login
        self.login_frame.destroy()
        self.login_frame = None


        # Import here to avoid circular import issues at startup
        from ui.main_frame import MainApp

        self.main_app = MainApp(parent=self,on_logout=self.show_login)
        self.main_app.grid(row=0, column=0, sticky="nsew")

    def show_login(self):
        self.main_app.destroy()      # destroy main app
        self.main_app = None         # drop reference
    
        self.login_frame = LoginFrame(parent=self, on_success=self.show_main_app)
        self.login_frame.grid(row=0, column=0, sticky="nsew")


# ── Entry point ────────────────────────────────────────────────────────────────
# This block only runs when you execute THIS file directly (python app.py)
# It won't run if this file is imported by another module
if __name__ == "__main__":
    app = App()
    app.mainloop()   # starts the event loop — app listens for clicks, keypresses etc.