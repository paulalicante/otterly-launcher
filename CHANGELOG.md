# Changelog

All notable changes to Otterly Launcher will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Custom icon support for shortcuts
- Fuzzy search/filtering in launcher window
- Hold-key trigger option
- GUI settings editor
- Auto-start configuration helper
- Cross-platform support (Linux, macOS)

## [0.1.0] - 2026-01-22

### Added
- Initial MVP release
- Double-tap Shift trigger for launcher activation
- Cursor-positioned borderless popup window
- System tray icon with Settings/Quit menu
- JSON-based configuration system
  - Stored in `%APPDATA%\OtterlyLauncher\config.json`
  - Configurable trigger key and timeout
  - Customizable window colors and fonts
- Shortcut management
  - Support for executables and Python scripts
  - Simple button-based launcher UI
- Click-outside and Escape key to dismiss launcher
- Comprehensive documentation
  - README with quick start guide
  - QUICKSTART.md for detailed setup
  - claude.md for AI context and architecture
  - CONTRIBUTING.md for contributors

### Technical Details
- Python 3.8+ compatibility
- Windows-only (requires Administrator privileges)
- Dependencies: keyboard, pystray, Pillow, tkinter
- Clean architecture with separated concerns
  - launcher.py: Main orchestration and keyboard hooks
  - config_manager.py: Configuration handling
  - popup_window.py: UI window management
  - tray_icon.py: System tray functionality

---

[Unreleased]: https://github.com/yourusername/launcher/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/launcher/releases/tag/v0.1.0
