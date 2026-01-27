"""Shortcut management interface for Otterly Launcher."""
import tkinter as tk
from tkinter import messagebox, ttk
from config_manager import ConfigManager
import subprocess
import sys
import os
import keyboard
from typing import Set
import threading
import time


class ShortcutManager:
    """GUI for managing launcher shortcuts."""

    def __init__(self):
        self.config = ConfigManager()
        self.shortcut_widgets = {}  # {index: {checkbox_var, name_label, delete_btn, frame}}
        
        # Hotkey monitoring state
        self.detected_hotkeys = {}
        self.is_monitoring = False
        self.current_keys = set()
        self.last_combo = None
        self.last_combo_time = 0
        self.hotkey_widgets = {}
        self.monitor_thread = None
        self.monitoring_lock = threading.Lock()
        self.original_shortcuts = None  # Store original state to detect changes

        self.root = tk.Tk()
        self.root.title("Otterly Launcher - Manage Shortcuts")
        self.root.geometry("900x600")
        self.root.minsize(850, 500)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._create_ui()
        self._load_shortcuts()
        self._position_near_cursor()
    
    def _on_close(self):
        """Handle window close - prompt to save if changes were made."""
        # Check if there are unsaved changes
        if self._has_unsaved_changes():
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?"
            )
            if result is True:
                self._save_changes()
                self.root.destroy()
            elif result is False:
                self.root.destroy()
            # If None, cancel close
        else:
            self.root.destroy()
    
    def _has_unsaved_changes(self):
        """Check if there are any unsaved changes."""
        # Check if any shortcuts were deleted
        if self.original_shortcuts and len(self.shortcut_widgets) != len(self.original_shortcuts):
            return True
        
        # Check if any names or enabled status changed
        for idx, widget_data in self.shortcut_widgets.items():
            shortcut = widget_data['shortcut']
            enabled = widget_data['checkbox_var'].get()
            
            # Find the original shortcut
            original = None
            if self.original_shortcuts:
                for s in self.original_shortcuts:
                    if s.get('name') == shortcut.get('name'):
                        original = s
                        break
            
            # Check if enabled status changed
            if original and original.get('enabled', True) != enabled:
                return True
        
        # Check if any hotkeys were added
        if self.hotkey_widgets:
            checked_hotkeys = [w for w in self.hotkey_widgets.values() if w['checkbox_var'].get()]
            if checked_hotkeys:
                return True
        
        return False

    def _create_ui(self):
        """Create the UI with tabs."""
        # Top bar with title and close button
        top_bar = tk.Frame(self.root)
        top_bar.pack(fill=tk.X, padx=10, pady=10)

        # Title
        title = tk.Label(
            top_bar,
            text="Manage Launcher Shortcuts",
            font=('Segoe UI', 16, 'bold')
        )
        title.pack(side=tk.LEFT, padx=10)

        # Close button (X) on the right
        close_btn = tk.Button(
            top_bar,
            text="✕",
            command=self.root.destroy,
            font=('Segoe UI', 16, 'bold'),
            bg='#F44336',
            fg='white',
            padx=15,
            pady=5,
            cursor='hand2',
            relief=tk.FLAT
        )
        close_btn.pack(side=tk.RIGHT, padx=10)

        # Tabbed interface
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Manage Shortcuts
        self.shortcuts_tab = tk.Frame(notebook)
        notebook.add(self.shortcuts_tab, text="Manage Shortcuts")
        self._create_shortcuts_tab()

        # Tab 2: Add Hotkeys
        self.hotkeys_tab = tk.Frame(notebook)
        notebook.add(self.hotkeys_tab, text="Add Hotkeys")
        self._create_hotkeys_tab()

        # Bottom buttons
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=20)

        save_btn = tk.Button(
            bottom_frame,
            text="💾 SAVE CHANGES",
            command=self._save_changes,
            font=('Segoe UI', 12, 'bold'),
            bg='#2196F3',
            fg='white',
            padx=30,
            pady=12,
            cursor='hand2',
            relief=tk.RAISED,
            bd=3
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(
            bottom_frame,
            text="Close",
            command=self.root.destroy,
            font=('Segoe UI', 11),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        close_btn.pack(side=tk.LEFT, padx=5)

    def _create_shortcuts_tab(self):
        """Create the Manage Shortcuts tab."""
        # Instructions
        instructions = tk.Label(
            self.shortcuts_tab,
            text="Check shortcuts to show in launcher. Uncheck to hide. Click Delete to remove.",
            font=('Segoe UI', 10),
            pady=10,
            wraplength=650
        )
        instructions.pack()

        # Scrollable frame for shortcuts
        list_container = tk.Frame(self.shortcuts_tab)
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

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

        tk.Label(header_frame, text="Show", font=('Segoe UI', 9, 'bold'), bg='#E0E0E0', width=6).pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="Name", font=('Segoe UI', 9, 'bold'), bg='#E0E0E0', width=25, anchor='w').pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="Type", font=('Segoe UI', 9, 'bold'), bg='#E0E0E0', width=12, anchor='w').pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="Target", font=('Segoe UI', 9, 'bold'), bg='#E0E0E0', anchor='w', width=30).pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="", font=('Segoe UI', 9, 'bold'), bg='#E0E0E0', width=16).pack(side=tk.LEFT, padx=5)

    def _create_hotkeys_tab(self):
        """Create the Add Hotkeys tab."""
        # Instructions
        instructions = tk.Label(
            self.hotkeys_tab,
            text="Click 'Start Monitoring' and use your applications normally.\n"
                 "Check the boxes for hotkeys you want, edit their names, then they'll be added.",
            font=('Segoe UI', 10),
            pady=10,
            wraplength=650
        )
        instructions.pack()

        # Status area
        status_frame = tk.Frame(self.hotkeys_tab, bg='#F5F5F0', relief=tk.SUNKEN, borderwidth=2)
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
        button_frame = tk.Frame(self.hotkeys_tab)
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
            command=self._clear_hotkey_list,
            font=('Segoe UI', 11),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Detected hotkeys list
        list_label = tk.Label(
            self.hotkeys_tab,
            text="Detected Hotkeys:",
            font=('Segoe UI', 10, 'bold')
        )
        list_label.pack(anchor='w', padx=20, pady=(10, 5))

        # Scrollable frame for hotkeys
        hotkey_list_container = tk.Frame(self.hotkeys_tab)
        hotkey_list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        hotkey_canvas = tk.Canvas(hotkey_list_container, bg='white')
        hotkey_scrollbar = tk.Scrollbar(hotkey_list_container, orient="vertical", command=hotkey_canvas.yview)
        self.hotkey_scrollable_frame = tk.Frame(hotkey_canvas, bg='white')

        self.hotkey_scrollable_frame.bind(
            "<Configure>",
            lambda e: hotkey_canvas.configure(scrollregion=hotkey_canvas.bbox("all"))
        )

        hotkey_canvas.create_window((0, 0), window=self.hotkey_scrollable_frame, anchor="nw")
        hotkey_canvas.configure(yscrollcommand=hotkey_scrollbar.set)

        hotkey_canvas.pack(side="left", fill="both", expand=True)
        hotkey_scrollbar.pack(side="right", fill="y")

        # Header row
        hotkey_header_frame = tk.Frame(self.hotkey_scrollable_frame, bg='#E0E0E0')
        hotkey_header_frame.pack(fill=tk.X, padx=2, pady=2)

        tk.Label(hotkey_header_frame, text="✓", font=('Segoe UI', 9, 'bold'), bg='#E0E0E0', width=3).pack(side=tk.LEFT, padx=2)
        tk.Label(hotkey_header_frame, text="Hotkey", font=('Segoe UI', 9, 'bold'), bg='#E0E0E0', width=20, anchor='w').pack(side=tk.LEFT, padx=2)
        tk.Label(hotkey_header_frame, text="Uses", font=('Segoe UI', 9, 'bold'), bg='#E0E0E0', width=6).pack(side=tk.LEFT, padx=2)
        tk.Label(hotkey_header_frame, text="Button Name", font=('Segoe UI', 9, 'bold'), bg='#E0E0E0', width=30, anchor='w').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

    def _load_shortcuts(self):
        """Load shortcuts from config and display them."""
        shortcuts = self.config.get_shortcuts()
        
        # Store original state to detect changes
        import copy
        self.original_shortcuts = copy.deepcopy(shortcuts)

        if not shortcuts:
            no_shortcuts_label = tk.Label(
                self.scrollable_frame,
                text="No shortcuts configured yet.\nClick 'Add New Hotkeys' to add some!",
                font=('Segoe UI', 11),
                bg='white',
                fg='#666666',
                pady=40
            )
            no_shortcuts_label.pack()
            return

        for idx, shortcut in enumerate(shortcuts):
            self._add_shortcut_row(idx, shortcut)

    def _add_shortcut_row(self, index: int, shortcut: dict):
        """Add a row for a shortcut."""
        row_frame = tk.Frame(self.scrollable_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        row_frame.pack(fill=tk.X, padx=2, pady=1)

        # Checkbox (enabled by default, or use 'enabled' field if it exists)
        enabled = shortcut.get('enabled', True)
        check_var = tk.BooleanVar(value=enabled)
        checkbox = tk.Checkbutton(row_frame, variable=check_var, bg='white')
        checkbox.pack(side=tk.LEFT, padx=5)

        # Name
        name_label = tk.Label(
            row_frame,
            text=shortcut['name'],
            font=('Segoe UI', 10),
            bg='white',
            width=25,
            anchor='w'
        )
        name_label.pack(side=tk.LEFT, padx=5)

        # Type (Application or Hotkey)
        shortcut_type = "Hotkey" if shortcut.get('hotkey') else "Application"
        type_label = tk.Label(
            row_frame,
            text=shortcut_type,
            font=('Segoe UI', 9),
            bg='white',
            fg='#666666',
            width=12,
            anchor='w'
        )
        type_label.pack(side=tk.LEFT, padx=5)

        # Target (path or hotkey)
        target = shortcut.get('hotkey') or shortcut.get('path') or 'N/A'
        target_label = tk.Label(
            row_frame,
            text=target,
            font=('Segoe UI', 9),
            bg='white',
            fg='#666666',
            anchor='w',
            width=30
        )
        target_label.pack(side=tk.LEFT, padx=5)

        # Edit button
        edit_btn = tk.Button(
            row_frame,
            text="Edit",
            command=lambda i=index: self._edit_shortcut_name(i),
            font=('Segoe UI', 9),
            bg='#2196F3',
            fg='white',
            padx=10,
            pady=2,
            cursor='hand2'
        )
        edit_btn.pack(side=tk.LEFT, padx=2)

        # Delete button
        delete_btn = tk.Button(
            row_frame,
            text="Delete",
            command=lambda i=index: self._delete_shortcut(i),
            font=('Segoe UI', 9),
            bg='#F44336',
            fg='white',
            padx=10,
            pady=2,
            cursor='hand2'
        )
        delete_btn.pack(side=tk.LEFT, padx=2)

        # Store references
        self.shortcut_widgets[index] = {
            'checkbox_var': check_var,
            'name_label': name_label,
            'frame': row_frame,
            'shortcut': shortcut
        }

    def _edit_shortcut_name(self, index: int):
        """Edit the name of a shortcut."""
        if index not in self.shortcut_widgets:
            return

        widget_data = self.shortcut_widgets[index]
        shortcut = widget_data['shortcut']
        old_name = shortcut['name']

        # Create a custom dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Shortcut Name")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center on parent
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 75
        dialog.geometry(f"+{x}+{y}")

        # Label
        tk.Label(dialog, text=f"Enter new name for '{old_name}':", font=('Segoe UI', 10)).pack(pady=10)

        # Entry
        entry = tk.Entry(dialog, font=('Segoe UI', 11), width=40)
        entry.pack(pady=10)
        entry.insert(0, old_name)
        entry.focus_set()
        entry.select_range(0, tk.END)

        result_var = tk.StringVar()

        def save():
            result_var.set(entry.get())
            dialog.destroy()

        def cancel():
            result_var.set("")
            dialog.destroy()

        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="OK", command=save, bg='#4CAF50', fg='white', padx=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=cancel, padx=15).pack(side=tk.LEFT, padx=5)

        self.root.wait_window(dialog)

        new_name = result_var.get().strip()
        if new_name and new_name != old_name:
            # Update the shortcut
            shortcut['name'] = new_name
            widget_data['name_label'].config(text=new_name)
            print(f"Shortcut renamed from '{old_name}' to '{new_name}'")

    def _delete_shortcut(self, index: int):
        """Delete a shortcut."""
        if index not in self.shortcut_widgets:
            return

        shortcut = self.shortcut_widgets[index]['shortcut']

        confirm = messagebox.askyesno(
            "Delete Shortcut",
            f"Delete '{shortcut['name']}'?"
        )

        if confirm:
            # Remove from display
            self.shortcut_widgets[index]['frame'].destroy()
            del self.shortcut_widgets[index]

    def _save_changes(self):
        """Save changes to config."""
        # Collect remaining shortcuts with their enabled status
        updated_shortcuts = []

        for idx in sorted(self.shortcut_widgets.keys()):
            widget_data = self.shortcut_widgets[idx]
            shortcut = widget_data['shortcut'].copy()
            shortcut['enabled'] = widget_data['checkbox_var'].get()
            updated_shortcuts.append(shortcut)

        # Add selected hotkeys from the Add Hotkeys tab
        for hotkey, widgets in self.hotkey_widgets.items():
            if widgets['checkbox_var'].get():
                name = widgets['name_entry'].get().strip()
                if name:
                    # Check if this hotkey already exists
                    if not any(s.get('hotkey') == hotkey for s in updated_shortcuts):
                        updated_shortcuts.append({
                            'name': name,
                            'hotkey': hotkey,
                            'path': None,
                            'icon': None
                        })

        # Save to config
        self.config.config['shortcuts'] = updated_shortcuts
        self.config.save_config()

        # Notify user
        messagebox.showinfo(
            "Changes Saved",
            "Changes saved successfully!\n\n"
            "Your shortcuts will update the next time you open the launcher.",
            icon='info'
        )

        self.root.destroy()

    def _toggle_monitoring(self):
        """Toggle monitoring on/off."""
        if self.is_monitoring:
            # Stop monitoring
            with self.monitoring_lock:
                self.is_monitoring = False
            
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
            # Start monitoring
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
            
            # Start keyboard hook in separate thread
            def monitor_loop():
                try:
                    keyboard.hook(self._on_key_event, suppress=False)
                except:
                    pass
            
            self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
            self.monitor_thread.start()

    def _on_key_event(self, event):
        """Handle keyboard events during monitoring."""
        with self.monitoring_lock:
            if not self.is_monitoring:
                return

        try:
            if event.event_type == keyboard.KEY_DOWN:
                self.current_keys.add(event.name)
            elif event.event_type == keyboard.KEY_UP:
                if event.name in self.current_keys:
                    self.current_keys.remove(event.name)

                if len(self.current_keys) >= 1:
                    temp_keys = self.current_keys.copy()
                    temp_keys.add(event.name)

                    if len(temp_keys) >= 2:
                        combo = self._build_hotkey_string(temp_keys)
                        current_time = time.time()

                        if combo != self.last_combo or (current_time - self.last_combo_time) > 0.5:
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
                normalized = key.upper() if len(key) == 1 else key.title()
                regular_keys.append(normalized)

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
            self._update_hotkey_count()

        self.detected_hotkeys[hotkey] += 1

        if hotkey in self.hotkey_widgets:
            self.hotkey_widgets[hotkey]['count_label'].config(text=str(self.detected_hotkeys[hotkey]))

    def _add_hotkey_row(self, hotkey: str):
        """Add a row for a new hotkey."""
        row_frame = tk.Frame(self.hotkey_scrollable_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        row_frame.pack(fill=tk.X, padx=2, pady=1)

        check_var = tk.BooleanVar(value=False)
        checkbox = tk.Checkbutton(row_frame, variable=check_var, bg='white')
        checkbox.pack(side=tk.LEFT, padx=5)

        hotkey_label = tk.Label(
            row_frame,
            text=hotkey,
            font=('Segoe UI', 10, 'bold'),
            bg='white',
            width=20,
            anchor='w'
        )
        hotkey_label.pack(side=tk.LEFT, padx=5)

        count_label = tk.Label(
            row_frame,
            text="1",
            font=('Segoe UI', 9),
            bg='white',
            width=6,
            fg='#666666'
        )
        count_label.pack(side=tk.LEFT, padx=5)

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

        def on_focus_in(e):
            e.widget.config(relief=tk.SUNKEN, bg='#FFFFCC')

        def on_focus_out(e):
            e.widget.config(relief=tk.SOLID, bg='white')

        name_entry.bind('<FocusIn>', on_focus_in)
        name_entry.bind('<FocusOut>', on_focus_out)

        self.hotkey_widgets[hotkey] = {
            'checkbox_var': check_var,
            'name_entry': name_entry,
            'count_label': count_label,
            'frame': row_frame
        }

    def _update_hotkey_count(self):
        """Update the count label."""
        count = len(self.detected_hotkeys)
        self.count_label.config(text=f"{count} unique hotkeys detected")

    def _clear_hotkey_list(self):
        """Clear the detected hotkeys list."""
        if messagebox.askyesno("Clear List", "Clear all detected hotkeys?"):
            for widgets in self.hotkey_widgets.values():
                widgets['frame'].destroy()

            self.hotkey_widgets.clear()
            self.detected_hotkeys.clear()
            self._update_hotkey_count()

    def _position_near_cursor(self):
        """Position window near the cursor."""
        self.root.update_idletasks()

        import ctypes
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        point = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        cursor_x = point.x
        cursor_y = point.y

        width = self.root.winfo_width()
        height = self.root.winfo_height()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = cursor_x + 50
        y = cursor_y + 50

        if x + width > screen_width:
            x = cursor_x - width - 50
        if y + height > screen_height:
            y = cursor_y - height - 50

        self.root.geometry(f"+{x}+{y}")

    def run(self):
        """Run the manager."""
        try:
            self.root.mainloop()
        finally:
            # Clean up keyboard hook when window closes
            with self.monitoring_lock:
                self.is_monitoring = False
            keyboard.unhook_all()


def main():
    """Run the shortcut manager."""
    manager = ShortcutManager()
    manager.run()


if __name__ == '__main__':
    main()
