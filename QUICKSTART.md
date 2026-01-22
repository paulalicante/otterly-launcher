# Quick Start Guide

## First Time Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Note: The `keyboard` library requires administrator privileges on Windows.

2. **Configure your shortcuts:**
   - Run the launcher once to generate the config file
   - Or manually edit: `default_config.json` before first run
   - After first run, config is at: `%APPDATA%\OtterlyLauncher\config.json`

3. **Update shortcut paths in config:**
   ```json
   "shortcuts": [
     {
       "name": "VS Code",
       "path": "code",
       "icon": null
     },
     {
       "name": "Your App",
       "path": "C:\\full\\path\\to\\your\\app.exe",
       "icon": null
     }
   ]
   ```

## Running the Launcher

**Important:** Must run as Administrator (required for global keyboard hooks on Windows)

```bash
# From project root
python src/launcher.py
```

Or right-click Command Prompt/PowerShell → "Run as Administrator", then run the command.

## Usage

1. Launcher runs in background (check system tray)
2. **Double-tap Shift** (two quick presses within 300ms)
3. Launcher appears at your cursor
4. Click an app to launch it
5. Press Escape or click outside to dismiss

## System Tray

Right-click the tray icon:
- **Settings** - Opens config file in Notepad
- **Quit** - Exits the launcher

## Troubleshooting

**Launcher doesn't appear when I double-tap Shift:**
- Make sure you're running as Administrator
- Check timing - try tapping faster or slower
- Check console output for errors

**"Access denied" or keyboard hook errors:**
- You must run as Administrator on Windows

**Apps don't launch:**
- Check paths in config file
- For Python scripts, ensure full path is correct
- For executables, can use command name if in PATH (like "code" for VS Code)

## Customization

Edit `%APPDATA%\OtterlyLauncher\config.json`:

- Change trigger key (default: "shift")
- Adjust double-tap timeout (default: 300ms)
- Customize colors and fonts
- Add/remove shortcuts

Restart the launcher after config changes.

## Creating a Startup Shortcut

To run launcher on Windows startup:

1. Press `Win + R`, type `shell:startup`, press Enter
2. Right-click → New → Shortcut
3. Location: `pythonw.exe "G:\my drive\launcher\src\launcher.py"`
   (Adjust path to your Python and launcher location)
4. Name it "Otterly Launcher"
5. Right-click shortcut → Properties → Advanced → Run as Administrator

Note: You may need to configure UAC to allow this without prompting.
