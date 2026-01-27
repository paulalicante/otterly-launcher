"""System tray icon for Otterly Launcher."""
import pystray
from PIL import Image, ImageDraw
from typing import Callable
import uuid


class TrayIcon:
    """System tray icon with menu."""

    def __init__(self, on_quit: Callable, on_settings: Callable = None, on_setup_wizard: Callable = None, on_manage_shortcuts: Callable = None):
        """Initialize tray icon.

        Args:
            on_quit: Callback when user selects Quit
            on_settings: Callback when user selects Settings (optional)
            on_setup_wizard: Callback when user selects Setup Wizard (optional)
            on_manage_shortcuts: Callback when user selects Manage Shortcuts (optional)
        """
        self.on_quit = on_quit
        self.on_settings = on_settings
        self.on_setup_wizard = on_setup_wizard
        self.on_manage_shortcuts = on_manage_shortcuts
        self.icon = None
        # Use a unique ID for this instance to avoid conflicts with old icons
        self.icon_id = f"otterly_launcher_{uuid.uuid4().hex[:8]}"

    def create_image(self):
        """Create a simple icon image."""
        # Create a simple circular icon with an "O" for Otterly
        width = 64
        height = 64
        color1 = '#8BC6EC'  # Light blue
        color2 = '#2C2C2C'  # Dark text

        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)

        # Draw a circle
        dc.ellipse([8, 8, width-8, height-8], fill=color1, outline=color2, width=3)

        # Draw "O" in the center (simplified)
        dc.ellipse([20, 20, width-20, height-20], outline=color2, width=4)

        return image

    def _on_quit_clicked(self, icon, item):
        """Handle quit menu item click."""
        icon.stop()
        if self.on_quit:
            self.on_quit()

    def _on_settings_clicked(self, icon, item):
        """Handle settings menu item click."""
        if self.on_settings:
            self.on_settings()

    def _on_setup_wizard_clicked(self, icon, item):
        """Handle setup wizard menu item click."""
        if self.on_setup_wizard:
            self.on_setup_wizard()

    def _on_manage_shortcuts_clicked(self, icon, item):
        """Handle manage shortcuts menu item click."""
        if self.on_manage_shortcuts:
            self.on_manage_shortcuts()

    def run(self):
        """Start the system tray icon."""
        menu_items = []

        if self.on_manage_shortcuts:
            menu_items.append(pystray.MenuItem('Manage Shortcuts', self._on_manage_shortcuts_clicked))

        if self.on_settings:
            menu_items.append(pystray.MenuItem('Settings', self._on_settings_clicked))

        menu_items.append(pystray.MenuItem('Quit', self._on_quit_clicked))

        self.icon = pystray.Icon(
            self.icon_id,
            self.create_image(),
            "Otterly Launcher",
            menu=pystray.Menu(*menu_items)
        )

        self.icon.run()

    def stop(self):
        """Stop the tray icon."""
        if self.icon:
            self.icon.stop()
