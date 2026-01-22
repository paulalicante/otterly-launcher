# 🦦 Otterly Launcher

> A minimal, cursor-positioned app launcher for Windows. Think Spotlight or Alfred, but it appears exactly where your cursor is.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

---

## ✨ Features

- 🎯 **Cursor-positioned** - Launcher appears exactly where your cursor is
- ⚡ **Instant activation** - Double-tap Shift (or configure your own trigger)
- 🎨 **Clean design** - Borderless window with soft, pastel colors
- 🔧 **Fully configurable** - JSON-based configuration for everything
- 💾 **Lightweight** - Runs silently in system tray, minimal resources
- 🚀 **Fast** - No delays, no animations, just instant access to your apps

## 🎬 How It Works

1. **Runs in background** with system tray icon
2. **Double-tap Shift** (two quick presses within 300ms)
3. **Launcher appears** at your cursor position
4. **Click an app** to launch it instantly
5. **Disappears** when you click outside or press Escape

## 🚀 Quick Start

### Requirements

- Python 3.8 or higher
- Windows 10/11
- **Administrator privileges** (required for global keyboard hooks)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/launcher.git
   cd launcher
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your shortcuts**

   Edit `default_config.json` with your app paths:
   ```json
   "shortcuts": [
     {
       "name": "VS Code",
       "path": "code",
       "icon": null
     },
     {
       "name": "Your App",
       "path": "C:\\path\\to\\your\\app.exe",
       "icon": null
     }
   ]
   ```

4. **Run the launcher** (as Administrator)
   ```bash
   python src/launcher.py
   ```

5. **Test it** - Double-tap Shift and your launcher appears! 🎉

For detailed setup instructions, see [QUICKSTART.md](QUICKSTART.md).

## ⚙️ Configuration

Configuration is stored in: `%APPDATA%\OtterlyLauncher\config.json`

**Customize:**
- Trigger key (default: Shift)
- Double-tap timeout (default: 300ms)
- Window colors and fonts
- App shortcuts with custom paths

**Example config:**
```json
{
  "trigger": {
    "key": "shift",
    "timeout_ms": 300
  },
  "window": {
    "background_color": "#F5F5F0",
    "button_color": "#E8E8D8"
  },
  "shortcuts": [
    {"name": "VS Code", "path": "code"},
    {"name": "Notepad", "path": "notepad.exe"}
  ]
}
```

Access settings via: Right-click tray icon → **Settings**

## 🏗️ Project Structure

```
launcher/
├── src/
│   ├── launcher.py          # Main entry point & keyboard detection
│   ├── config_manager.py    # Configuration handling
│   ├── tray_icon.py         # System tray functionality
│   └── popup_window.py      # Launcher window UI
├── assets/                  # Icons and images (future)
├── default_config.json      # Default configuration template
├── requirements.txt         # Python dependencies
├── QUICKSTART.md           # Detailed setup guide
├── claude.md               # AI context & architecture docs
└── README.md               # You are here
```

## 🛠️ Tech Stack

- **Python 3.8+** - Core language
- **keyboard** - Global hotkey detection
- **tkinter** - Borderless popup window
- **pystray** - System tray icon
- **Pillow** - Icon image generation

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas we'd love help with:**
- Cross-platform support (Linux, macOS)
- Icon support for shortcuts
- Fuzzy search/filtering
- Alternative trigger methods
- Performance improvements

## 📋 Roadmap

**v0.1** (Current)
- ✅ Double-tap Shift trigger
- ✅ Cursor-positioned window
- ✅ System tray integration
- ✅ JSON configuration

**Future**
- ❌ Custom icons for shortcuts
- ❌ Fuzzy search/filtering
- ❌ Hold-key trigger option
- ❌ GUI settings editor
- ❌ Auto-start configuration
- ❌ Cross-platform support

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Inspired by launchers like Alfred, Spotlight, and Wox - but designed to be minimal and cursor-focused.

---

**Made with ❤️ by developers who want quick access to their apps**
