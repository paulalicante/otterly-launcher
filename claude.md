# Claude Context: Otterly Launcher

## Project Overview

Otterly Launcher is a minimal, cursor-positioned app launcher for Windows. Think macOS Spotlight or Alfred, but minimal and appears exactly where your cursor is.

**Core concept:** Double-tap Shift → launcher appears at cursor → click app to launch → done.

## Architecture

### File Structure
```
launcher/
├── src/
│   ├── launcher.py              # Main entry point, keyboard hooks, orchestration
│   ├── config_manager.py        # Config loading/saving (uses %APPDATA%)
│   ├── popup_window.py          # Tkinter borderless window UI
│   ├── shortcut_manager.py      # Manage shortcuts & add hotkeys (tabbed interface)
│   ├── hotkey_monitor.py        # Passive hotkey monitoring (integrated into shortcut_manager)
│   ├── tray_icon.py            # pystray system tray icon
│   ├── hotkey_scanner.py        # (legacy)
│   └── simple_hotkey_setup.py   # (legacy - replaced by shortcut_manager)
├── assets/                      # Icons
├── default_config.json          # Default config template
├── requirements.txt             # Dependencies
└── CHANGELOG.md, CONTRIBUTING.md, README.md, QUICKSTART.md
```

### Component Responsibilities

**launcher.py (Main)**
- Entry point
- Global keyboard hook using `keyboard` library
- Double-tap detection logic (tracks timing between key presses)
- Threading coordination (popup runs in separate thread)
- Tray icon management

**config_manager.py**
- Loads config from `%APPDATA%\OtterlyLauncher\config.json`
- Creates default config on first run
- Provides clean getter interface: `config.get('trigger', 'key')`

**popup_window.py**
- Tkinter borderless window (`overrideredirect(True)`)
- Positions at cursor using `winfo_pointerx/y()`
- Creates buttons dynamically from config shortcuts
- Handles app launching (Python scripts vs executables)
- Focus-out and Escape key to dismiss

**tray_icon.py**
- System tray icon using `pystray`
- Generates simple icon with PIL
- Menu: Settings (opens config in Notepad), Quit

## Configuration System

Config stored in: `%APPDATA%\OtterlyLauncher\config.json`

Structure:
```json
{
  "trigger": {
    "key": "shift",           // Key to watch
    "method": "double-tap",   // Currently only double-tap supported
    "timeout_ms": 300         // Max time between taps
  },
  "window": {
    "width": 200,
    "background_color": "#F5F5F0",
    "button_color": "#E8E8D8",
    "button_hover_color": "#D8D8C8",
    "text_color": "#2C2C2C",
    "font_family": "Segoe UI",
    "font_size": 11
  },
  "shortcuts": [
    {
      "name": "Display Name",
      "path": "executable.exe or full/path/to/script.py",
      "icon": null  // Future feature
    }
  ]
}
```

## Technical Details

### Double-Tap Detection
- Uses `keyboard.hook()` for global keyboard events
- Tracks timestamp of last key press
- If same key pressed within timeout window, increment counter
- Counter >= 2 triggers launcher
- Reset counter when timeout expires

### Threading Model
- Main thread: keyboard hook + tray icon (blocking)
- Popup thread: tkinter window (daemon thread, shows modal window)
- Popup uses `mainloop()` which blocks its thread until closed

### Windows-Specific Requirements
- **Must run as Administrator** for global keyboard hooks
- Uses `%APPDATA%` for config storage
- System tray integration via pystray
- Tkinter for GUI (built into Python on Windows)

## Design Philosophy

**Minimal:** No features beyond core launcher functionality. No plugins, no themes, no complexity.

**Fast:** Instant appearance at cursor. No animations, no delays.

**Clean:** Soft pastel colors, simple buttons, no clutter.

**Unobtrusive:** Lives in tray, no main window. Disappears when not needed.

## Recent Changes (Jan 27, 2026)

1. **Merged Manage Shortcuts & Add Hotkeys**
   - Single window with tabbed interface
   - Removed duplicate menu items
   - Removed old "Add Hotkeys" button from bottom

2. **Improved Shortcut Editing**
   - Added Edit button next to Delete in Manage Shortcuts tab
   - Right-click on shortcut in popup to edit name
   - Custom dialog for name editing (not simple dialog)

3. **Performance & Responsiveness**
   - Moved keyboard hook to separate thread
   - Non-blocking hook prevents UI freezing
   - Fixed keyboard interference with text input fields
   - Performance issues with hotkey monitoring resolved

4. **User Experience**
   - Made "Save Changes" button prominent (larger, bold, emoji)
   - Added unsaved changes warning on close
   - Changes detection for deletions, edits, and new hotkeys
   - Proper save/cancel flow

5. **Window Management**
   - Larger default window size (900x600)
   - Better button layout with improved widths
   - Fixed Delete button visibility issue by narrowing Target field

6. **Tray Icon Improvements**
   - Unique icon IDs per instance prevent duplicates
   - Proper cleanup when quitting
   - Fixed SystemExit exception from tray callback

## Current Status

**v0.2+ Features Implemented:**
- ✅ Double-tap Shift trigger
- ✅ Cursor positioning
- ✅ System tray with menu
- ✅ Config system with hot-reload
- ✅ Manage Shortcuts window (tabbed interface)
  - ✅ View/hide/delete shortcuts
  - ✅ Edit shortcut names (Edit button + right-click in popup)
  - ✅ Support for both hotkeys and applications
- ✅ Add Hotkeys tab (passive monitoring)
  - ✅ Detect hotkeys by monitoring keyboard usage
  - ✅ Name hotkeys before adding
  - ✅ Integrated into Shortcut Manager (no separate window)
- ✅ Changes prompt on close (save confirmation)
- ✅ Right-click edit names in popup launcher
- ✅ Tray icon management (unique IDs per instance)
- ✅ Performance optimizations (non-blocking keyboard hook)

**v0.1 MVP Features:**
- ✅ Double-tap Shift trigger
- ✅ Cursor positioning
- ✅ System tray
- ✅ Config system

**Future Enhancements:**
- ❌ Custom icons (path in config, not implemented)
- ❌ Fuzzy search/filtering
- ❌ Auto-start on Windows login
- ❌ Advanced hotkey customization

## Common Development Tasks

### Testing the Trigger
Run as admin, watch console output:
```bash
python src/launcher.py
```
Console shows "Showing launcher..." when double-tap detected.

### Modifying Trigger Logic
See `launcher.py` → `_on_key_event()` method. The double-tap logic is ~20 lines.

### Changing Window Appearance
See `popup_window.py` → `_create_ui()` and `_create_shortcut_button()`.
Colors pulled from config, so can test by editing config JSON.

### Adding New Trigger Methods
1. Add to config schema in `default_config.json`
2. Implement in `launcher.py` → `_on_key_event()`
3. Load setting in `__init__` alongside existing trigger settings

## Dependencies

- `keyboard` - Global keyboard hooks (REQUIRES ADMIN on Windows)
- `pystray` - System tray icon
- `Pillow` (PIL) - Image creation for tray icon
- `tkinter` - GUI (built-in with Python)

## User's Preferences

The user (Honey) has these preferences from other projects:
- Pastel, soft colors (implemented: #F5F5F0, #E8E8D8 palette)
- Clean, minimal design (no clutter)
- Functional over flashy
- Proper project structure from the start
- Comprehensive docs (README, QUICKSTART, this file)

## Development Context

This was built as a "stomach feeling" project - something the user wanted immediately and viscerally. The goal was to create an MVP quickly that actually works, then iterate.

Built in one session, designed to be taken into VS Code for testing and refinement.

## When Making Changes

**Do:**
- Keep it minimal
- Test with double-tap Shift trigger
- Remember it needs admin privileges
- Update config schema if adding settings
- Preserve the clean architecture

**Don't:**
- Add features not explicitly requested
- Complicate the UI
- Break the cursor positioning
- Require external dependencies beyond current list
- Make config file complex

## Git & GitHub

This project is ready for GitHub:
- Clean structure
- Comprehensive README
- .gitignore configured
- No secrets or personal paths in tracked files
- Default config is template only
