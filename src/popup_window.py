"""Popup launcher window for Otterly Launcher."""
import tkinter as tk
import subprocess
import sys
import keyboard
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

        # Bind focus loss to close (double-tap Shift also closes via toggle)
        self.root.bind('<FocusOut>', lambda e: self.hide())

        # Force focus and grab keyboard
        self.root.focus_set()
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

        # Filter to only enabled shortcuts
        enabled_shortcuts = [s for s in shortcuts if s.get('enabled', True)]

        if not enabled_shortcuts:
            # No shortcuts configured or all disabled
            label = tk.Label(
                self.root,
                text="No shortcuts enabled",
                bg=self.config.get('window', 'background_color', default='#F5F5F0'),
                fg=self.config.get('window', 'text_color', default='#2C2C2C'),
                font=(self.config.get('window', 'font_family', default='Segoe UI'),
                      self.config.get('window', 'font_size', default=11)),
                pady=10,
                padx=20
            )
            label.pack()
            return

        # Create a button for each enabled shortcut
        for shortcut in enabled_shortcuts:
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
                  self.config.get('window', 'font_size', default=9)),
            relief=tk.FLAT,
            cursor='hand2',
            anchor='w',
            padx=5,
            pady=2
        )
        button.pack(fill=tk.X, padx=2, pady=1)

        # Hover effects
        def on_enter(e):
            button['background'] = self.config.get('window', 'button_hover_color', default='#D8D8C8')

        def on_leave(e):
            button['background'] = self.config.get('window', 'button_color', default='#E8E8D8')

        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        
        # Right-click to edit name
        def on_right_click(e):
            self._show_edit_menu(e, shortcut, button)
        
        button.bind('<Button-3>', on_right_click)

    def _show_edit_menu(self, event, shortcut: Dict, button):
        """Show context menu to edit the shortcut name."""
        import tkinter.simpledialog as simpledialog
        
        # Ask user for new name
        new_name = simpledialog.askstring(
            "Edit Shortcut Name",
            f"Enter new name for '{shortcut['name']}':",
            initialvalue=shortcut['name']
        )
        
        if new_name and new_name != shortcut['name']:
            # Update the shortcut name
            shortcut['name'] = new_name
            button.config(text=new_name)
            
            # Save to config
            shortcuts = self.config.get_shortcuts()
            for s in shortcuts:
                if s.get('hotkey') == shortcut.get('hotkey') or s.get('path') == shortcut.get('path'):
                    s['name'] = new_name
                    break
            
            self.config.config['shortcuts'] = shortcuts
            self.config.save_config()
            print(f"Shortcut renamed to: {new_name}")

    def _launch_app(self, shortcut: Dict):
        """Launch the application or trigger hotkey specified in the shortcut."""
        try:
            # Check if this is a hotkey shortcut
            if 'hotkey' in shortcut and shortcut['hotkey']:
                print(f"Triggering hotkey: {shortcut['hotkey']}")
                # Convert hotkey to lowercase format that keyboard library expects
                # e.g., "Ctrl+Shift+R" -> "ctrl+shift+r"
                hotkey = shortcut['hotkey'].lower()
                print(f"Converted to: {hotkey}")

                # Hide window first to restore focus
                self.hide()

                # Wait briefly for focus to restore, then trigger hotkey
                import threading
                def trigger_delayed():
                    import time
                    time.sleep(0.15)  # 150ms delay
                    keyboard.press_and_release(hotkey)
                    print("Hotkey triggered after delay")

                threading.Thread(target=trigger_delayed, daemon=True).start()
                return

            # Otherwise, launch as an application
            path = shortcut.get('path')
            if not path:
                print(f"Error: No path or hotkey for {shortcut['name']}")
                return

            # Check if it's a Python script
            if path.endswith('.py'):
                subprocess.Popen([sys.executable, path])
            else:
                # Try to launch as executable or command
                subprocess.Popen(path, shell=True)

            self.hide()
        except Exception as e:
            print(f"Error launching {shortcut['name']}: {e}")
            # Don't hide on error so user can see something is wrong

    def _position_at_cursor(self):
        """Position window at current cursor location."""
        self.root.update_idletasks()  # Update to get accurate size

        # Get actual cursor position using Windows API (more reliable than winfo_pointer)
        import ctypes
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        point = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        cursor_x = point.x
        cursor_y = point.y

        # Get window size
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # Get screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Position window slightly offset from cursor (10px right, 10px down)
        # so the window appears next to the cursor, not under it
        x = cursor_x + 10
        y = cursor_y + 10

        # Adjust position to keep window on screen
        if x + width > screen_width:
            x = cursor_x - width - 10  # Place to the left instead
        if y + height > screen_height:
            y = cursor_y - height - 10  # Place above instead

        self.root.geometry(f"+{x}+{y}")

    def hide(self):
        """Hide and destroy the window (thread-safe)."""
        print(f"hide() called. root={self.root}, is_visible={self.is_visible}")

        if not self.root:
            self.is_visible = False
            if self.on_close:
                self.on_close()
            return

        # Schedule destruction in the tkinter thread
        def destroy_window():
            print("Destroying window in tkinter thread...")
            if self.root:
                self.root.quit()
                self.root.destroy()
                self.root = None
            self.is_visible = False

            print(f"About to call on_close callback: {self.on_close}")
            if self.on_close:
                self.on_close()
            print("hide() complete")

        try:
            self.root.after(0, destroy_window)
        except:
            # If after() fails, do it directly
            destroy_window()
