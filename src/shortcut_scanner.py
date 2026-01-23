"""Scans system for keyboard shortcuts and hotkeys."""
import winreg
import os
from pathlib import Path
from typing import List, Dict, Optional
import subprocess


class ShortcutScanner:
    """Discovers keyboard shortcuts from various sources on Windows."""

    def __init__(self):
        self.shortcuts = []

    def scan_all(self) -> List[Dict]:
        """Scan all sources for shortcuts."""
        self.shortcuts = []

        # Scan different sources
        self.shortcuts.extend(self._scan_start_menu())
        self.shortcuts.extend(self._scan_desktop())
        self.shortcuts.extend(self._scan_taskbar())
        self.shortcuts.extend(self._scan_autohotkey())
        self.shortcuts.extend(self._scan_registry_hotkeys())
        self.shortcuts.extend(self._scan_sharex())
        self.shortcuts.extend(self._get_windows_builtin_shortcuts())

        return self.shortcuts

    def _scan_start_menu(self) -> List[Dict]:
        """Scan Start Menu for .lnk files with hotkeys."""
        shortcuts = []

        # Common Start Menu locations
        start_menu_paths = [
            Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu',
            Path(os.environ.get('PROGRAMDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu',
        ]

        for start_path in start_menu_paths:
            if start_path.exists():
                # Find all .lnk files
                for lnk_file in start_path.rglob('*.lnk'):
                    shortcut_info = self._parse_lnk_file(lnk_file)
                    if shortcut_info:
                        shortcuts.append(shortcut_info)

        return shortcuts

    def _scan_desktop(self) -> List[Dict]:
        """Scan Desktop for shortcuts."""
        shortcuts = []
        desktop = Path.home() / 'Desktop'

        if desktop.exists():
            for lnk_file in desktop.glob('*.lnk'):
                shortcut_info = self._parse_lnk_file(lnk_file)
                if shortcut_info:
                    shortcuts.append(shortcut_info)

        return shortcuts

    def _scan_taskbar(self) -> List[Dict]:
        """Scan taskbar pinned items."""
        shortcuts = []

        # Taskbar shortcuts location
        taskbar_path = Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Internet Explorer' / 'Quick Launch' / 'User Pinned' / 'TaskBar'

        if taskbar_path.exists():
            for lnk_file in taskbar_path.glob('*.lnk'):
                shortcut_info = self._parse_lnk_file(lnk_file)
                if shortcut_info:
                    shortcut_info['source'] = 'Taskbar'
                    shortcuts.append(shortcut_info)

        return shortcuts

    def _scan_autohotkey(self) -> List[Dict]:
        """Scan for AutoHotkey scripts."""
        shortcuts = []

        # Common AutoHotkey locations
        ahk_paths = [
            Path.home() / 'Documents' / 'AutoHotkey',
            Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup',
        ]

        for ahk_path in ahk_paths:
            if ahk_path.exists():
                for ahk_file in ahk_path.rglob('*.ahk'):
                    # Parse AHK file for hotkeys
                    ahk_shortcuts = self._parse_ahk_file(ahk_file)
                    shortcuts.extend(ahk_shortcuts)

        return shortcuts

    def _parse_lnk_file(self, lnk_path: Path) -> Optional[Dict]:
        """Parse a .lnk file to extract target and hotkey."""
        try:
            # Use PowerShell to read .lnk file properties
            # Output format: TARGET|HOTKEY
            ps_script = f"""
            $sh = New-Object -ComObject WScript.Shell
            $lnk = $sh.CreateShortcut('{lnk_path}')
            $target = $lnk.TargetPath
            $hotkey = $lnk.Hotkey
            Write-Output "$target|$hotkey"
            """

            result = subprocess.run(
                ['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode != 0:
                return None

            output = result.stdout.strip()
            if '|' in output:
                parts = output.split('|', 1)
                target = parts[0].strip()
                hotkey = parts[1].strip() if len(parts) > 1 else ''

                if target and os.path.exists(target):
                    return {
                        'name': lnk_path.stem,
                        'path': target,
                        'hotkey': hotkey if hotkey else None,
                        'source': 'Start Menu' if 'Start Menu' in str(lnk_path) else 'Desktop',
                        'type': 'shortcut'
                    }
        except Exception as e:
            pass

        return None

    def _parse_ahk_file(self, ahk_path: Path) -> List[Dict]:
        """Parse AutoHotkey file for hotkey definitions."""
        shortcuts = []

        try:
            with open(ahk_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple regex to find hotkey patterns like "^!s::" (Ctrl+Alt+S)
            import re
            hotkey_pattern = r'^([^\s:]+)::\s*(.*)$'

            for line in content.split('\n'):
                line = line.strip()
                if '::' in line and not line.startswith(';'):
                    match = re.match(hotkey_pattern, line)
                    if match:
                        hotkey_combo = match.group(1)
                        action = match.group(2) or 'Custom Action'

                        shortcuts.append({
                            'name': f"AHK: {hotkey_combo}",
                            'path': str(ahk_path),
                            'hotkey': hotkey_combo,
                            'source': 'AutoHotkey',
                            'type': 'ahk_script',
                            'action': action
                        })
        except Exception as e:
            print(f"Error parsing AHK file {ahk_path}: {e}")

        return shortcuts

    def get_shortcuts_with_hotkeys(self) -> List[Dict]:
        """Return only shortcuts that have hotkeys defined."""
        return [s for s in self.shortcuts if s.get('hotkey')]

    def get_all_applications(self) -> List[Dict]:
        """Return all discovered applications, with or without hotkeys."""
        return self.shortcuts

    def _scan_registry_hotkeys(self) -> List[Dict]:
        """Scan Windows Registry for hotkey definitions."""
        shortcuts = []

        try:
            # Common registry paths for hotkeys
            registry_paths = [
                r'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\AppKey',
                r'HKCU\Software\Classes\Applications',
            ]

            for reg_path in registry_paths:
                try:
                    result = subprocess.run(
                        ['reg', 'query', reg_path, '/s'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )

                    if result.returncode == 0:
                        # Parse registry output for hotkey entries
                        lines = result.stdout.split('\n')
                        current_key = None
                        for line in lines:
                            if line.startswith('HKEY'):
                                current_key = line.strip()
                            elif 'ShellExecute' in line or 'Hotkey' in line:
                                parts = line.split('REG_SZ')
                                if len(parts) >= 2:
                                    value = parts[1].strip()
                                    if value:
                                        shortcuts.append({
                                            'name': f'Registry: {Path(current_key).name}',
                                            'path': value,
                                            'hotkey': 'Registry defined',
                                            'source': 'Registry',
                                            'type': 'registry'
                                        })
                except Exception:
                    pass

        except Exception as e:
            print(f"Error scanning registry: {e}")

        return shortcuts

    def _scan_sharex(self) -> List[Dict]:
        """Scan ShareX configuration for hotkeys."""
        shortcuts = []

        try:
            # ShareX settings locations
            sharex_paths = [
                Path(os.environ.get('USERPROFILE', '')) / 'Documents' / 'ShareX',
                Path(os.environ.get('APPDATA', '')) / 'ShareX',
            ]

            for sharex_path in sharex_paths:
                if sharex_path.exists():
                    # Look for HotkeysConfig.json
                    hotkey_file = sharex_path / 'HotkeysConfig.json'
                    if hotkey_file.exists():
                        try:
                            import json
                            with open(hotkey_file, 'r', encoding='utf-8') as f:
                                config = json.load(f)

                            # Parse ShareX hotkeys
                            if 'Hotkeys' in config:
                                for hotkey in config['Hotkeys']:
                                    # Get task name from Job field or Description
                                    task_settings = hotkey.get('TaskSettings', {})
                                    task_name = task_settings.get('Description', '')
                                    if not task_name:
                                        # Use Job field and make it more readable
                                        job = task_settings.get('Job', 'Unknown')
                                        task_name = job.replace('_', ' ')

                                    hotkey_str = hotkey.get('HotkeyInfo', {}).get('Hotkey', '')

                                    if hotkey_str:
                                        # Clean up hotkey string: "PrintScreen, Control" -> "Ctrl+PrintScreen"
                                        parts = [p.strip() for p in hotkey_str.split(',')]
                                        # Remap common key names
                                        key_map = {'Control': 'Ctrl', 'PrintScreen': 'PrtScn'}
                                        mapped_parts = [key_map.get(p, p) for p in parts]
                                        hotkey_display = '+'.join(mapped_parts)

                                        shortcuts.append({
                                            'name': f'ShareX: {task_name}',
                                            'path': 'ShareX',
                                            'hotkey': hotkey_display,
                                            'source': 'ShareX',
                                            'type': 'app_hotkey'
                                        })
                        except Exception as e:
                            print(f"Error parsing ShareX config: {e}")

        except Exception as e:
            print(f"Error scanning ShareX: {e}")

        return shortcuts

    def _get_windows_builtin_shortcuts(self) -> List[Dict]:
        """Return list of common Windows built-in keyboard shortcuts."""
        shortcuts = []

        # Common Windows keyboard shortcuts
        windows_shortcuts = [
            ('Windows: Show Desktop', 'Win+D'),
            ('Windows: File Explorer', 'Win+E'),
            ('Windows: Lock PC', 'Win+L'),
            ('Windows: Settings', 'Win+I'),
            ('Windows: Task View', 'Win+Tab'),
            ('Windows: Run Dialog', 'Win+R'),
            ('Windows: Quick Link Menu', 'Win+X'),
            ('Windows: Screenshot', 'Win+PrintScreen'),
            ('Windows: Snipping Tool', 'Win+Shift+S'),
            ('Windows: Task Manager', 'Ctrl+Shift+Esc'),
            ('Windows: Clipboard History', 'Win+V'),
            ('Windows: Emoji Picker', 'Win+.'),
            ('Windows: Project/Display', 'Win+P'),
            ('Windows: Action Center', 'Win+A'),
            ('Windows: Search', 'Win+S'),
            ('Windows: Notification Center', 'Win+N'),
            ('Windows: Magnifier', 'Win++'),
            ('Windows: Game Bar', 'Win+G'),
            ('Windows: Connect', 'Win+K'),
            ('Windows: Switch Apps', 'Alt+Tab'),
            ('Windows: Virtual Desktop Left', 'Win+Ctrl+Left'),
            ('Windows: Virtual Desktop Right', 'Win+Ctrl+Right'),
            ('Windows: New Virtual Desktop', 'Win+Ctrl+D'),
            ('Windows: Close Virtual Desktop', 'Win+Ctrl+F4'),
        ]

        for name, hotkey in windows_shortcuts:
            shortcuts.append({
                'name': name,
                'path': 'windows_builtin',
                'hotkey': hotkey,
                'source': 'Windows Built-in',
                'type': 'system_shortcut'
            })

        return shortcuts
