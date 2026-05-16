import customtkinter as ctk
from config.ui_config import LOGIN_UI
from services.auth_service import login
from PIL import Image

class LoginFrame(ctk.CTkFrame):
    """
    The login screen.

    Inherits from CTkFrame — so this object IS a frame.
    We pass it a 'parent' (the root window) and an 'on_success' callback.

    Responsibilities:
    - build login Frame
    - validate login credentials
    """

    def __init__(self, parent, on_success):
        # Initialize the CTkFrame with black bg so root window color shows
        super().__init__(parent, fg_color="black")

        # Store the callback — we'll call it after successful login
        # Parameter on_success is a Reference of app.py func that destroys login page and opens MainApp
        self.on_success = on_success

        # ── Background Image ─────────────────────────────
        bg_image = Image.open("background3_1.png")

        self.bg_photo = ctk.CTkImage(
            light_image=bg_image,
            dark_image=bg_image,
            size=(1400, 900)
        )

        self.bg_label = ctk.CTkLabel(
            self,
            image=self.bg_photo,
            text=""
        )

        # Fill whole frame
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        # ── Center the card on screen ──────────────────────────────────────────
        # We make this frame's grid have 3 rows and 3 cols
        # and give all weight to the middle row/col
        # This pushes the card to the center
        self.grid_rowconfigure((0, 2), weight=1)     # top and bottom rows expand
        self.grid_rowconfigure(1, weight=0)           # middle row stays fixed (our card)
        self.grid_columnconfigure((0, 2), weight=1)   # left and right cols expand
        self.grid_columnconfigure(1, weight=0)        # middle col stays fixed

       
        # ── Build the card contents ────────────────────────────────────────────
        self._build_card()

    def _build_card(self):
        """
        Builds the Card and all widgets inside the card.
        We use a separate method to keep __init__ clean.

        Using pack() here because it's a simple top-to-bottom layout.
        padx/pady add spacing around each widget.
        """

        # Create the 'Box' itself first
        self.card = ctk.CTkFrame(self,
                        width=LOGIN_UI['card_width'],
                        height=LOGIN_UI['card_height'],
                        corner_radius=LOGIN_UI['card_corner_radius'])
        self.card.grid(row=1, column=1, padx=20, pady=20)
        self.card.grid_propagate(False)

        # ── Logo / Icon label (emoji as placeholder) ───────────────────────────
        ctk.CTkLabel(
            self.card,
            text="     🏋️",
            font=ctk.CTkFont(family=LOGIN_UI['font_family'], size=LOGIN_UI['emoji_size'])
        ).pack(pady=(40, 0), anchor='center')

        # ── App title ──────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self.card,
            text="Gym Management System",
            font=ctk.CTkFont(family=LOGIN_UI['font_family'], size=LOGIN_UI['title_font_size'], weight="bold")
        ).pack(pady=(8, 0))

        ctk.CTkLabel(
            self.card,
            text="Sign in to continue",
            font=ctk.CTkFont(family=LOGIN_UI['font_family'], size=LOGIN_UI['subtitle_font_size']),
            text_color=LOGIN_UI['subtitle_color']
        ).pack(pady=(2, 20))

        # ── Username ───────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self.card,
            text="Username",
            anchor="w",              # anchor="w" aligns text to the left
            width=LOGIN_UI['label_width'],
            font=ctk.CTkFont(family=LOGIN_UI['font_family'], size=LOGIN_UI['subtitle_font_size'])
        ).pack(padx=40, fill="x")   # fill="x" stretches label to full card width

        # StringVar: live variable that holds what user types
        # We read it later with .get()
        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()

        self.username_entry = ctk.CTkEntry(
            self.card,
            width=LOGIN_UI['entry_width'],
            height=LOGIN_UI['entry_height'],
            placeholder_text="Enter username",
            textvariable=self.username_var   # link entry to our StringVar
        )
        self.username_entry.pack(padx=40, pady=(4, 12))

        # ── Password ───────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self.card,
            text="Password",
            anchor="w",
            width=LOGIN_UI['label_width'],
            font=ctk.CTkFont(family=LOGIN_UI['font_family'], size=LOGIN_UI['subtitle_font_size'])
        ).pack(padx=40, fill="x")

        self.password_entry = ctk.CTkEntry(
            self.card,
            width=LOGIN_UI['entry_width'],
            height=LOGIN_UI['entry_height'],
            placeholder_text="Enter password",
            textvariable=self.password_var,
            show="*"        # THIS is what masks the password with asterisks
        )
        self.password_entry.pack(padx=40, pady=(4, 4))

        # ── Show/Hide password toggle ──────────────────────────────────────────
        # CTkCheckBox calls a command when toggled
        self.show_pass_var = ctk.BooleanVar(value=False)  # starts unchecked
        ctk.CTkCheckBox(
            self.card,
            text="Show password",
            variable=self.show_pass_var,
            command=self._toggle_password,   # called on every toggle
            height=20,
            font=ctk.CTkFont(family=LOGIN_UI['font_family'], size=LOGIN_UI['label_font_size'])
        ).pack(padx=40, anchor="w", pady=(0, 16))

        # ── Error label ────────────────────────────────────────────────────────
        # Always present, starts empty.
        # We update its text when login fails.
        # Never crash — always show a message instead.
        self.error_label = ctk.CTkLabel(
            self.card,
            text="",                    # empty initially
            text_color=LOGIN_UI['error_color'],       # soft red
            font=ctk.CTkFont(family=LOGIN_UI['font_family'], size=LOGIN_UI['label_font_size'])
        )
        self.error_label.pack(pady=(0, 8))

        # ── Login button ───────────────────────────────────────────────────────
        self.login_btn = ctk.CTkButton(
            self.card,
            text="Login",
            text_color=LOGIN_UI['btn_text'],
            width=LOGIN_UI['entry_width'],
            height=LOGIN_UI['entry_height'] + 2,
            font=ctk.CTkFont(family=LOGIN_UI['font_family'], size=LOGIN_UI['button_font_size'], weight="bold"),
            fg_color=LOGIN_UI['btn_fg'],
            hover_color=LOGIN_UI['btn_hover'],
            border_width=1,
            command=self._handle_login    # called when button is clicked
        )
        self.login_btn.pack(padx=40, pady=5)

        # ── Bind Enter key to login ────────────────────────────────────────────
        # Users expect Enter to submit — bind it to the whole window
        # "<Return>" is tkinter's name for the Enter key
        self.master.bind("<Return>", lambda event: self._handle_login())

    def _toggle_password(self):
        """
        Called when Show Password checkbox is toggled.
        show="" means visible text, show="*" means masked.
        """
        if self.show_pass_var.get():    # if checkbox is NOW checked
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")

    def _handle_login(self):
        """
        Main login logic. Called on button click or Enter key.

        Flow:
        1. Read username and password from StringVars
        2. Basic validation (empty check)
        3. Call auth_service.login()
        4. On success → log it → call on_success callback
        5. On failure → show error message
        """

        # .get() reads current value of the StringVar
        # .strip() removes accidental leading/trailing spaces
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        # ── Step 1: Client-side validation ────────────────────────────────────
        # Check empty fields before even hitting the database
        if not username or not password:
            self._show_error("Please enter both username and password.")
            return   # stop here, don't proceed
        
        elif len(password) < 8:
            self._show_error("Length of Password should be minimum 8 characters.")
            return   # stop here, don't proceed

        # ── Step 2: Disable button while processing ────────────────────────────
        # Prevents double-clicking while DB query runs
        self.login_btn.configure(state="disabled", text="Logging in...")

        # ── Step 3: Call the auth service ─────────────────────────────────────
        # login() returns a dict row if found, None if not found
        result = login(username, password)

        if result:
            # ── Success path ───────────────────────────────────────────────────
            # Log the login event into audit_log
            #log_login()

            # Unbind Enter key so it doesn't trigger login logic in main app
            self.master.unbind("<Return>")

            # Call the callback — App.show_main_app() runs now
            self.on_success()

        else:
            # ── Failure path ───────────────────────────────────────────────────
            self._show_error("Invalid username or password.")

            # Re-enable button so user can try again
            self.login_btn.configure(state="normal", text="Login")

            # Clear password field for security — don't leave it filled
            self.password_var.set("")

    def _show_error(self, message: str):
        """Updates the error label text. Single place to change error styling."""
        self.error_label.configure(text=message)

# Currently LOGIN LOG IS COMMENTED OUT

# if __name__ == "__main__":
#     import customtkinter as ctk

#     app = ctk.CTk()   # ✅ THIS is your parent (root window)

#     def dummy_success():
#         print("Login successful!")

#     loginn = LoginFrame(app, dummy_success)
#     loginn.pack(fill="both", expand=True)

#     app.mainloop()
