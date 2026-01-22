"""Configuration manager for Otterly Launcher."""
import json
import os
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manages loading, saving, and accessing configuration."""

    APP_NAME = "OtterlyLauncher"
    CONFIG_FILENAME = "config.json"

    def __init__(self):
        """Initialize config manager and load configuration."""
        self.config_dir = self._get_config_directory()
        self.config_path = self.config_dir / self.CONFIG_FILENAME
        self.config = self._load_config()

    def _get_config_directory(self) -> Path:
        """Get the configuration directory path (creates if doesn't exist)."""
        appdata = os.getenv('APPDATA')
        if not appdata:
            raise RuntimeError("APPDATA environment variable not found")

        config_dir = Path(appdata) / self.APP_NAME
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using default configuration.")
                return self._create_default_config()
        else:
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """Create and save default configuration."""
        # Load from default_config.json in project root
        default_config_path = Path(__file__).parent.parent / "default_config.json"

        if default_config_path.exists():
            with open(default_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            # Fallback inline default
            config = {
                "trigger": {
                    "key": "shift",
                    "method": "double-tap",
                    "timeout_ms": 300
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
                    {"name": "VS Code", "path": "code", "icon": None},
                    {"name": "Notepad", "path": "notepad.exe", "icon": None}
                ]
            }

        self.save_config(config)
        return config

    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file."""
        if config is not None:
            self.config = config

        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get(self, *keys, default=None):
        """Get a configuration value by nested keys.

        Example: config.get('trigger', 'timeout_ms') returns 300
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def get_shortcuts(self):
        """Get the list of configured shortcuts."""
        return self.config.get('shortcuts', [])
