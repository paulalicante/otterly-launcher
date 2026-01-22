"""Popup launcher window for Otterly Launcher."""
import tkinter as tk
import subprocess
import sys
from typing import List, Dict, Callable


class PopupWindow:
    """Borderless popup window that shows app shortcuts."""

    def __init__(self, config_manager, on_close_callback: Callable = None):
        """Initialize popup window.

        Args:
            config_manager: ConfigManager instance
            on_close_callback: Optional callback when window closes
        """
        self.config = config_manager
        self.on_close = on_close_callback
        self.root = None
        self.is_visible = False

    def show(self):
        """Show the launcher window at cursor position."""
        if self.is_visible:
            return

        self.is_visible = True
        self.root = tk.Tk()
        self._setup_window()
        self._create_ui()
        self._position_at_cursor()

        # Bind click outside to close
        self.root.bind('<FocusOut>', lambda e: self.hide())
        self.root.bind('<Escape>', lambda e: self.hide())

        self.root.focus_force()
        self.root.mainloop()

    def _setup_window(self):
        """Configure window properties."""
        self.root.overrideredirect(True)  # Borderless
        self.root.attributes('-topmost', True)  # Always on top

        # Try to make rounded corners (Windows 11)
        try:
            self.root.attributes('-transparentcolor', 'white')
        except:
            pass

        bg_color = self.config.get('window', 'background_color', default='#F5F5F0')
        self.root.configure(bg=bg_color)

    def _create_ui(self):
        """Create the UI elements."""
        shortcuts = self.config.get_shortcuts()

        if not shortcuts:
            # No shortcuts configured
            label = tk.Label(
                self.root,
                text="No shortcuts configured",
                bg=self.config.get('window', 'background_color', default='#F5F5F0'),
                fg=self.config.get('window', 'text_color', default='#2C2C2C'),
                font=(self.config.get('window', 'font_family', default='Segoe UI'),
                      self.config.get('window', 'font_size', default=11)),
                pady=10,
                padx=20
            )
            label.pack()
            return

        # Create a button for each shortcut
        for shortcut in shortcuts:
            self._create_shortcut_button(shortcut)

    def _create_shortcut_button(self, shortcut: Dict):
        """Create a button for a single shortcut."""
        button = tk.Button(
            self.root,
            text=shortcut['name'],
            command=lambda s=shortcut: self._launch_app(s),
            bg=self.config.get('window', 'button_color', default='#E8E8D8'),
            fg=self.config.get('window', 'text_color', default='#2C2C2C'),
            activebackground=self.config.get('window', 'button_hover_color', default='#D8D8C8'),
            font=(self.config.get('window', 'font_family', default='Segoe UI'),
                  self.config.get('window', 'font_size', default=11)),
            relief=tk.FLAT,
            cursor='hand2',
            anchor='w',
            padx=15,
            pady=8
        )
        button.pack(fill=tk.X, padx=5, pady=2)

        # Hover effects
        def on_enter(e):
            button['background'] = self.config.get('window', 'button_hover_color', default='#D8D8C8')

        def on_leave(e):
            button['background'] = self.config.get('window', 'button_color', default='#E8E8D8')

        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)

    def _launch_app(self, shortcut: Dict):
        """Launch the application specified in the shortcut."""
        try:
            # Check if it's a Python script
            if shortcut['path'].endswith('.py'):
                subprocess.Popen([sys.executable, shortcut['path']])
            else:
                # Try to launch as executable or command
                subprocess.Popen(shortcut['path'], shell=True)

            self.hide()
        except Exception as e:
            print(f"Error launching {shortcut['name']}: {e}")
            # Don't hide on error so user can see something is wrong

    def _position_at_cursor(self):
        """Position window at current cursor location."""
        self.root.update_idletasks()  # Update to get accurate size

        # Get cursor position
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()

        # Get window size
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # Get screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Adjust position to keep window on screen
        if x + width > screen_width:
            x = screen_width - width - 10
        if y + height > screen_height:
            y = screen_height - height - 10

        self.root.geometry(f"+{x}+{y}")

    def hide(self):
        """Hide and destroy the window."""
        if self.root:
            self.root.quit()
            self.root.destroy()
            self.root = None
        self.is_visible = False

        if self.on_close:
            self.on_close()
