"""Passive hotkey monitoring tool - listens and records hotkeys as they're used."""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import keyboard
from config_manager import ConfigManager
from typing import List, Dict, Set
import threading
import time
import subprocess
import sys
import os


class HotkeyMonitor:
    """GUI for monitoring and capturing hotkeys passively."""

    def __init__(self):
        self.config = ConfigManager()
        self.detected_hotkeys = {}  # {hotkey_string: count}
        self.is_monitoring = False
        self.current_keys = set()
        self.last_combo = None
        self.last_combo_time = 0
        self.hotkey_widgets = {}  # {hotkey: {checkbox_var, name_entry, count_label}}
        self.monitor_thread = None
        self.monitoring_lock = threading.Lock()

        self.root = tk.Tk()
        self.root.title("Otterly Launcher - Hotkey Monitor")
        self.root.geometry("750x700")
        self.root.minsize(700, 650)

        self._create_ui()

    def _create_ui(self):
        """Create the UI."""
        # Title
        title = tk.Label(
            self.root,
            text="Monitor Your Hotkeys",
            font=('Segoe UI', 16, 'bold'),
            pady=20
        )
        title.pack()

        # Instructions
        instructions = tk.Label(
            self.root,
            text="Click 'Start Monitoring' and use your applications normally.\n"
                 "Check the boxes for hotkeys you want, edit their names, then click 'Add to Launcher'.",
            font=('Segoe UI', 10),
            pady=10,
            wraplength=650
        )
        instructions.pack()

        # Status area
        status_frame = tk.Frame(self.root, bg='#F5F5F0', relief=tk.SUNKEN, borderwidth=2)
        status_frame.pack(pady=10, padx=20, fill=tk.X)

        self.status_label = tk.Label(
            status_frame,
            text="Ready to monitor",
            font=('Segoe UI', 12, 'bold'),
            bg='#F5F5F0',
            fg='#666666',
            pady=15
        )
        self.status_label.pack()

        self.count_label = tk.Label(
            status_frame,
            text="0 hotkeys detected",
            font=('Segoe UI', 10),
            bg='#F5F5F0',
            fg='#999999',
            pady=5
        )
        self.count_label.pack()

        # Control buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.toggle_btn = tk.Button(
            button_frame,
            text="Start Monitoring",
            command=self._toggle_monitoring,
            font=('Segoe UI', 11),
            bg='#4CAF50',
            fg='white',
            padx=30,
            pady=10,
            cursor='hand2'
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(
            button_frame,
            text="Clear List",
            command=self._clear_list,
            font=('Segoe UI', 11),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Detected hotkeys list
        list_label = tk.Label(
            self.root,
            text="Detected Hotkeys:",
            font=('Segoe UI', 10, 'bold')
        )
        list_label.pack(anchor='w', padx=20, pady=(10, 5))

        # Scrollable frame for hotkeys
        list_container = tk.Frame(self.root)
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        canvas = tk.Canvas(list_container, bg='white')
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='white')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Header row
        header_frame = tk.Frame(self.scrollable_frame, bg='#E0E0E0')
        header_frame.pack(fill=tk.X, padx=2, pady=2)

        tk.Label(header_frame, text="✓", font=('Segoe UI', 9, 'bold'), bg='#E0E0E0', width=3).pack(side=tk.LEFT, padx=2)
        tk.Label(header_frame, text="Hotkey", font=('Segoe UI', 9, 'bold'), bg='#E0E0E0', width=20, anchor='w').pack(side=tk.LEFT, padx=2)
        tk.Label(header_frame, text="Uses", font=('Segoe UI', 9, 'bold'), bg='#E0E0E0', width=6).pack(side=tk.LEFT, padx=2)
        tk.Label(header_frame, text="Button Name", font=('Segoe UI', 9, 'bold'), bg='#E0E0E0', width=30, anchor='w').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        # Bottom buttons
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=20)

        self.save_btn = tk.Button(
            bottom_frame,
            text="Add Selected to Launcher",
            command=self._save_hotkeys,
            font=('Segoe UI', 11),
            bg='#2196F3',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(
            bottom_frame,
            text="Cancel",
            command=self._quit,
            font=('Segoe UI', 11),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def _setup_keyboard_hook(self):
        """Set up keyboard hook for monitoring."""
        # Don't hook immediately - wait for monitoring to start
        pass

    def _on_key_event(self, event):
        """Handle keyboard events during monitoring."""
        # Quick early exit if not monitoring
        with self.monitoring_lock:
            if not self.is_monitoring:
                return

        try:
            if event.event_type == keyboard.KEY_DOWN:
                self.current_keys.add(event.name)
            elif event.event_type == keyboard.KEY_UP:
                # Remove the released key
                if event.name in self.current_keys:
                    self.current_keys.remove(event.name)

                # Only process if we have a potential hotkey combo
                if len(self.current_keys) >= 1:
                    temp_keys = self.current_keys.copy()
                    temp_keys.add(event.name)

                    if len(temp_keys) >= 2:  # Must have modifier + key
                        combo = self._build_hotkey_string(temp_keys)
                        current_time = time.time()

                        # Avoid duplicate registrations (debounce 500ms)
                        if combo != self.last_combo or (current_time - self.last_combo_time) > 0.5:
                            # Schedule UI update in main thread
                            try:
                                self.root.after(0, lambda c=combo: self._register_hotkey(c))
                            except:
                                pass
                            self.last_combo = combo
                            self.last_combo_time = current_time
        except:
            pass

    def _build_hotkey_string(self, keys: Set[str]) -> str:
        """Build a normalized hotkey string from a set of keys."""
        modifiers = []
        regular_keys = []

        for key in keys:
            key_lower = key.lower()
            if key_lower in ['ctrl', 'left ctrl', 'right ctrl']:
                if 'Ctrl' not in modifiers:
                    modifiers.append('Ctrl')
            elif key_lower in ['alt', 'left alt', 'right alt']:
                if 'Alt' not in modifiers:
                    modifiers.append('Alt')
            elif key_lower in ['shift', 'left shift', 'right shift']:
                if 'Shift' not in modifiers:
                    modifiers.append('Shift')
            elif key_lower in ['win', 'left windows', 'right windows']:
                if 'Win' not in modifiers:
                    modifiers.append('Win')
            else:
                # Normalize key names
                normalized = key.upper() if len(key) == 1 else key.title()
                regular_keys.append(normalized)

        # Sort for consistency
        modifiers.sort()
        regular_keys.sort()

        parts = modifiers + regular_keys
        return '+'.join(parts)

    def _register_hotkey(self, hotkey: str):
        """Register a detected hotkey."""
        is_new = hotkey not in self.detected_hotkeys

        if is_new:
            self.detected_hotkeys[hotkey] = 0
            self._add_hotkey_row(hotkey)
            self._update_count()  # Only update count when new hotkey added

        self.detected_hotkeys[hotkey] += 1

        # Update count label for this specific hotkey
        if hotkey in self.hotkey_widgets:
            self.hotkey_widgets[hotkey]['count_label'].config(text=str(self.detected_hotkeys[hotkey]))

    def _add_hotkey_row(self, hotkey: str):
        """Add a row for a new hotkey."""
        row_frame = tk.Frame(self.scrollable_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        row_frame.pack(fill=tk.X, padx=2, pady=1)

        # Checkbox
        check_var = tk.BooleanVar(value=False)
        checkbox = tk.Checkbutton(row_frame, variable=check_var, bg='white')
        checkbox.pack(side=tk.LEFT, padx=5)

        # Hotkey label
        hotkey_label = tk.Label(
            row_frame,
            text=hotkey,
            font=('Segoe UI', 10, 'bold'),
            bg='white',
            width=20,
            anchor='w'
        )
        hotkey_label.pack(side=tk.LEFT, padx=5)

        # Count label
        count_label = tk.Label(
            row_frame,
            text="1",
            font=('Segoe UI', 9),
            bg='white',
            width=6,
            fg='#666666'
        )
        count_label.pack(side=tk.LEFT, padx=5)

        # Name entry
        name_entry = tk.Entry(
            row_frame,
            font=('Segoe UI', 10),
            width=35,
            relief=tk.SOLID,
            borderwidth=1,
            bg='white',
            insertbackground='black'
        )
        name_entry.insert(0, hotkey)
        name_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Simple visual feedback when editing
        def on_focus_in(e):
            e.widget.config(relief=tk.SUNKEN, bg='#FFFFCC')

        def on_focus_out(e):
            e.widget.config(relief=tk.SOLID, bg='white')

        name_entry.bind('<FocusIn>', on_focus_in)
        name_entry.bind('<FocusOut>', on_focus_out)

        # Store references
        self.hotkey_widgets[hotkey] = {
            'checkbox_var': check_var,
            'name_entry': name_entry,
            'count_label': count_label,
            'frame': row_frame
        }

    def _update_count(self):
        """Update the count label."""
        count = len(self.detected_hotkeys)
        self.count_label.config(text=f"{count} unique hotkeys detected")

    def _toggle_monitoring(self):
        """Toggle monitoring on/off."""
        if self.is_monitoring:
            # Stop monitoring
            with self.monitoring_lock:
                self.is_monitoring = False
            
            # Give the hook thread a moment to exit
            time.sleep(0.1)
            keyboard.unhook_all()
            
            self.toggle_btn.config(
                text="Start Monitoring",
                bg='#4CAF50'
            )
            self.status_label.config(
                text="Monitoring stopped",
                fg='#666666'
            )
        else:
            # Start monitoring in a background thread
            with self.monitoring_lock:
                self.is_monitoring = True
            
            self.toggle_btn.config(
                text="Stop Monitoring",
                bg='#FF9800'
            )
            self.status_label.config(
                text="🔴 MONITORING - Use your apps normally",
                fg='#FF9800'
            )
            
            # Start keyboard hook in separate thread with minimal overhead
            def monitor_loop():
                try:
                    keyboard.hook(self._on_key_event, suppress=False)
                except:
                    pass
            
            self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
            self.monitor_thread.start()

    def _clear_list(self):
        """Clear the detected hotkeys list."""
        if messagebox.askyesno("Clear List", "Clear all detected hotkeys?"):
            # Destroy all widgets
            for widgets in self.hotkey_widgets.values():
                widgets['frame'].destroy()

            self.hotkey_widgets.clear()
            self.detected_hotkeys.clear()
            self._update_count()

    def _save_hotkeys(self):
        """Save selected hotkeys to config."""
        selected_items = []

        for hotkey, widgets in self.hotkey_widgets.items():
            if widgets['checkbox_var'].get():
                name = widgets['name_entry'].get().strip()
                if name:
                    selected_items.append({'name': name, 'hotkey': hotkey})

        if not selected_items:
            messagebox.showwarning("No Selection", "Please check at least one hotkey to add.")
            return

        # Add to config
        current_shortcuts = self.config.get_shortcuts()

        for item in selected_items:
            if not any(s.get('name') == item['name'] for s in current_shortcuts):
                current_shortcuts.append({
                    'name': item['name'],
                    'hotkey': item['hotkey'],
                    'path': None,
                    'icon': None
                })

        self.config.config['shortcuts'] = current_shortcuts
        self.config.save_config()

        # Notify user
        messagebox.showinfo(
            "Success",
            f"Added {len(selected_items)} hotkey buttons!\n\n"
            f"They'll appear the next time you open the launcher.",
            icon='info'
        )

        self._quit()

    def _quit(self):
        """Clean up and quit."""
        with self.monitoring_lock:
            self.is_monitoring = False
        keyboard.unhook_all()
        self.root.destroy()

    def run(self):
        """Run the monitor."""
        self.root.mainloop()


def main():
    """Run the hotkey monitor."""
    monitor = HotkeyMonitor()
    monitor.run()


if __name__ == '__main__':
    main()
