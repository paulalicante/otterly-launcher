"""System tray icon for Otterly Launcher."""
import pystray
from PIL import Image, ImageDraw
from typing import Callable


class TrayIcon:
    """System tray icon with menu."""

    def __init__(self, on_quit: Callable, on_settings: Callable = None):
        """Initialize tray icon.

        Args:
            on_quit: Callback when user selects Quit
            on_settings: Callback when user selects Settings (optional)
        """
        self.on_quit = on_quit
        self.on_settings = on_settings
        self.icon = None

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

    def run(self):
        """Start the system tray icon."""
        menu_items = []

        if self.on_settings:
            menu_items.append(pystray.MenuItem('Settings', self._on_settings_clicked))

        menu_items.append(pystray.MenuItem('Quit', self._on_quit_clicked))

        self.icon = pystray.Icon(
            "otterly_launcher",
            self.create_image(),
            "Otterly Launcher",
            menu=pystray.Menu(*menu_items)
        )

        self.icon.run()

    def stop(self):
        """Stop the tray icon."""
        if self.icon:
            self.icon.stop()
