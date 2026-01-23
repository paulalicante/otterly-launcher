"""Main entry point for Otterly Launcher."""
import keyboard
import time
import threading
import sys
from config_manager import ConfigManager
from popup_window import PopupWindow
from tray_icon import TrayIcon
from setup_wizard import SetupWizard


class OtterlyLauncher:
    """Main launcher application."""

    def __init__(self):
        """Initialize the launcher."""
        self.config = ConfigManager()
        self.popup = None
        self.is_running = True
        self.last_key_time = 0
        self.key_press_count = 0
        self.key_is_down = False

        # Get trigger settings
        self.trigger_key = self.config.get('trigger', 'key', default='shift')
        self.trigger_timeout = self.config.get('trigger', 'timeout_ms', default=300) / 1000.0

        print(f"Otterly Launcher starting...")
        print(f"Trigger: Double-tap {self.trigger_key.upper()} (within {int(self.trigger_timeout * 1000)}ms)")
        print(f"Config location: {self.config.config_path}")

    def _on_key_event(self, event):
        """Handle keyboard events for trigger detection."""
        # Check for Escape key to close popup
        if event.name.lower() == 'esc' and event.event_type == keyboard.KEY_DOWN:
            if self.popup and self.popup.is_visible:
                print("Escape detected, closing launcher...")
                self.popup.hide()
            return

        if event.name.lower() != self.trigger_key.lower():
            return

        current_time = time.time()

        # Track key down
        if event.event_type == keyboard.KEY_DOWN:
            # Ignore if key is already down (auto-repeat)
            if self.key_is_down:
                return

            self.key_is_down = True
            print(f"Shift pressed. Count: {self.key_press_count + 1}, Time diff: {current_time - self.last_key_time:.3f}s")

            # Check if this is within the timeout window
            if current_time - self.last_key_time <= self.trigger_timeout:
                self.key_press_count += 1

                if self.key_press_count >= 2:
                    # Double-tap detected!
                    print("Double-tap detected!")
                    self._show_launcher()
                    self.key_press_count = 0
                    self.last_key_time = 0
            else:
                # Start new detection window
                self.key_press_count = 1
                self.last_key_time = current_time

        # Track key up
        elif event.event_type == keyboard.KEY_UP:
            self.key_is_down = False

    def _show_launcher(self):
        """Show the launcher popup window."""
        if self.popup and self.popup.is_visible:
            print(f"Launcher already visible, skipping. popup={self.popup}, is_visible={self.popup.is_visible}")
            return

        print("Showing launcher...")

        # Create and show popup in a separate thread
        def show_window():
            self.popup = PopupWindow(self.config, on_close_callback=self._on_popup_closed)
            self.popup.show()

        threading.Thread(target=show_window, daemon=True).start()

    def _on_popup_closed(self):
        """Callback when popup window closes."""
        print("Popup closed callback - resetting popup to None")
        self.popup = None

    def _open_settings(self):
        """Open settings (placeholder for now)."""
        print("Settings not yet implemented. Config file location:")
        print(f"  {self.config.config_path}")
        # In future, could open the config file in default editor
        import subprocess
        try:
            subprocess.Popen(['notepad.exe', str(self.config.config_path)])
        except Exception as e:
            print(f"Could not open settings: {e}")

    def _open_setup_wizard(self):
        """Open the setup wizard to discover and add shortcuts."""
        print("Opening Setup Wizard...")

        def run_wizard():
            wizard = SetupWizard()
            wizard.run()

        threading.Thread(target=run_wizard, daemon=True).start()

    def _quit(self):
        """Quit the application."""
        print("Quitting Otterly Launcher...")
        self.is_running = False
        keyboard.unhook_all()
        sys.exit(0)

    def run(self):
        """Start the launcher application."""
        # Set up keyboard hook
        keyboard.hook(self._on_key_event)

        # Create system tray icon
        tray = TrayIcon(on_quit=self._quit, on_settings=self._open_settings, on_setup_wizard=self._open_setup_wizard)

        print("Otterly Launcher is running. Check system tray.")
        print(f"Press {self.trigger_key.upper()} twice quickly to show launcher.")

        # Run tray icon (this blocks)
        try:
            tray.run()
        except KeyboardInterrupt:
            self._quit()


def main():
    """Main entry point."""
    launcher = OtterlyLauncher()
    launcher.run()


if __name__ == '__main__':
    main()
