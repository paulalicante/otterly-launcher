"""Setup wizard to discover and add hotkey shortcuts to launcher."""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from hotkey_scanner import scan_hotkeys
from config_manager import ConfigManager
from typing import List, Dict
import json
import os
from pathlib import Path


class SetupWizard:
    """GUI wizard for discovering and selecting hotkey shortcuts."""

    def __init__(self):
        self.config = ConfigManager()
        self.hotkeys = []
        self.hotkey_names = {}  # Maps hotkey string to user-friendly name

        # Cache file location
        self.cache_file = Path(os.environ.get('APPDATA', '')) / 'OtterlyLauncher' / 'hotkey_cache.json'

        self.root = tk.Tk()
        self.root.title("Otterly Launcher - Setup Wizard")
        self.root.geometry("700x500")

        self._create_ui()

        # Load cached results if available
        self._load_cache()

    def _create_ui(self):
        """Create the wizard UI."""
        # Title
        title = tk.Label(
            self.root,
            text="Discover Your Hotkeys",
            font=('Segoe UI', 16, 'bold'),
            pady=20
        )
        title.pack()

        # Instructions
        instructions = tk.Label(
            self.root,
            text="Scanning for registered system hotkeys...\n"
                 "Select which ones you want as buttons in your launcher and give them names.",
            font=('Segoe UI', 10),
            pady=10
        )
        instructions.pack()

        # Scan button
        scan_frame = tk.Frame(self.root)
        scan_frame.pack(pady=10)

        self.scan_btn = tk.Button(
            scan_frame,
            text="Scan for Hotkeys",
            command=self._scan_hotkeys,
            font=('Segoe UI', 11),
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.scan_btn.pack()

        # Progress label
        self.progress_label = tk.Label(
            self.root,
            text="",
            font=('Segoe UI', 9),
            fg='gray'
        )
        self.progress_label.pack()

        # Search and filter box
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=20, pady=5)

        search_label = tk.Label(
            search_frame,
            text="Search:",
            font=('Segoe UI', 10)
        )
        search_label.pack(side=tk.LEFT, padx=5)

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_changed)

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Segoe UI', 10),
            state=tk.DISABLED
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Shortcuts list frame
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview for hotkeys
        columns = ('hotkey', 'name')
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='tree headings',
            yscrollcommand=scrollbar.set,
            selectmode='extended'
        )

        self.tree.heading('#0', text='✓')
        self.tree.heading('hotkey', text='Hotkey')
        self.tree.heading('name', text='Button Name (click to edit)')

        self.tree.column('#0', width=40)
        self.tree.column('hotkey', width=200)
        self.tree.column('name', width=400)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        # Add checkboxes and edit support
        self.tree.tag_configure('unchecked', image='')
        self.tree.bind('<Button-1>', self._on_tree_click)
        self.tree.bind('<Double-Button-1>', self._on_tree_double_click)

        # Bottom buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        self.add_btn = tk.Button(
            button_frame,
            text="Add Selected to Launcher",
            command=self._add_selected,
            font=('Segoe UI', 11),
            bg='#2196F3',
            fg='white',
            padx=20,
            pady=10,
            state=tk.DISABLED,
            cursor='hand2'
        )
        self.add_btn.pack(side=tk.LEFT, padx=10)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.root.destroy,
            font=('Segoe UI', 11),
            padx=20,
            pady=10,
            cursor='hand2'
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)

    def _scan_hotkeys(self):
        """Scan system for registered hotkeys."""
        self.progress_label.config(text="Scanning for hotkeys...")
        self.scan_btn.config(state=tk.DISABLED)
        self.root.update()

        try:
            # Perform scan (verbose=False to avoid console spam)
            hotkey_results = scan_hotkeys(verbose=False)

            # Convert to simpler format: list of hotkey strings
            self.hotkeys = [result[2] for result in hotkey_results]  # result[2] is the full hotkey string

            # Sort alphabetically
            self.hotkeys.sort()

            # Initialize names dict with default names (same as hotkey)
            for hotkey in self.hotkeys:
                if hotkey not in self.hotkey_names:
                    self.hotkey_names[hotkey] = hotkey

            # Save to cache
            self._save_cache()

            # Populate tree
            self._populate_tree()

            self.progress_label.config(
                text=f"Found {len(self.hotkeys)} registered hotkeys",
                fg='green'
            )
            self.add_btn.config(state=tk.NORMAL)
            self.search_entry.config(state=tk.NORMAL)
            self.search_entry.focus()

        except Exception as e:
            messagebox.showerror("Scan Error", f"Error scanning hotkeys: {e}")
            self.progress_label.config(text="Scan failed", fg='red')
            self.scan_btn.config(state=tk.NORMAL)

    def _populate_tree(self, filter_text=''):
        """Populate tree with discovered hotkeys."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Filter hotkeys based on search text
        filter_lower = filter_text.lower()

        filtered_hotkeys = [
            (idx, hotkey) for idx, hotkey in enumerate(self.hotkeys)
            if filter_lower in hotkey.lower() or filter_lower in self.hotkey_names.get(hotkey, '').lower()
        ]

        # Add hotkeys to tree
        for idx, hotkey in filtered_hotkeys:
            name = self.hotkey_names.get(hotkey, hotkey)

            self.tree.insert(
                '',
                'end',
                iid=str(idx),
                text='☐',  # Unchecked checkbox
                values=(
                    hotkey,
                    name
                ),
                tags=('unchecked',)
            )

    def _on_search_changed(self, *args):
        """Handle search text change."""
        search_text = self.search_var.get()
        self._populate_tree(search_text)

    def _on_tree_click(self, event):
        """Handle tree item click to toggle checkbox."""
        region = self.tree.identify('region', event.x, event.y)
        if region == 'tree':
            item = self.tree.identify_row(event.y)
            if item:
                # Toggle checkbox
                tags = self.tree.item(item, 'tags')
                if 'unchecked' in tags:
                    self.tree.item(item, text='☑', tags=('checked',))
                else:
                    self.tree.item(item, text='☐', tags=('unchecked',))

    def _on_tree_double_click(self, event):
        """Handle double-click to edit name."""
        region = self.tree.identify('region', event.x, event.y)
        if region == 'cell':
            column = self.tree.identify_column(event.x)
            if column == '#2':  # Name column
                item = self.tree.identify_row(event.y)
                if item:
                    idx = int(item)
                    hotkey = self.hotkeys[idx]
                    current_name = self.hotkey_names.get(hotkey, hotkey)

                    # Simple dialog to get new name
                    new_name = tk.simpledialog.askstring(
                        "Edit Button Name",
                        f"Enter name for {hotkey}:",
                        initialvalue=current_name,
                        parent=self.root
                    )

                    if new_name:
                        self.hotkey_names[hotkey] = new_name
                        self.tree.item(item, values=(hotkey, new_name))
                        self._save_cache()

    def _add_selected(self):
        """Add selected hotkeys to launcher config."""
        selected_items = []

        # Get all checked items
        for item in self.tree.get_children():
            tags = self.tree.item(item, 'tags')
            if 'checked' in tags:
                idx = int(item)
                hotkey = self.hotkeys[idx]
                name = self.hotkey_names.get(hotkey, hotkey)
                selected_items.append({'name': name, 'hotkey': hotkey})

        if not selected_items:
            messagebox.showwarning("No Selection", "Please select at least one hotkey to add.")
            return

        # Add to config
        current_shortcuts = self.config.get_shortcuts()

        for item in selected_items:
            # Check if already exists
            if not any(s.get('name') == item['name'] for s in current_shortcuts):
                current_shortcuts.append({
                    'name': item['name'],
                    'hotkey': item['hotkey'],
                    'path': None,  # No path for hotkey shortcuts
                    'icon': None
                })

        # Save config
        self.config.config['shortcuts'] = current_shortcuts
        self.config.save_config()

        messagebox.showinfo(
            "Success",
            f"Added {len(selected_items)} hotkey buttons to launcher!\n\n"
            f"Restart the launcher to see your new buttons."
        )

        self.root.destroy()

    def _save_cache(self):
        """Save hotkeys to cache file."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_data = {
                'hotkeys': self.hotkeys,
                'hotkey_names': self.hotkey_names
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save cache: {e}")

    def _load_cache(self):
        """Load hotkeys from cache file if available."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)

                self.hotkeys = cache_data.get('hotkeys', [])
                self.hotkey_names = cache_data.get('hotkey_names', {})

                if self.hotkeys:
                    self._populate_tree()
                    self.progress_label.config(
                        text=f"Loaded {len(self.hotkeys)} hotkeys from cache",
                        fg='blue'
                    )
                    self.add_btn.config(state=tk.NORMAL)
                    self.search_entry.config(state=tk.NORMAL)
                    self.search_entry.focus()
            except Exception as e:
                print(f"Failed to load cache: {e}")

    def run(self):
        """Run the wizard."""
        self.root.mainloop()


def main():
    """Run the setup wizard."""
    wizard = SetupWizard()
    wizard.run()


if __name__ == '__main__':
    main()
