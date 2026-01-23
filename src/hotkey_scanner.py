"""
Windows Registered Hotkey Scanner
---------------------------------
Scans for all globally registered hotkeys by attempting to register
each combination and seeing which ones fail (meaning they're taken).

This is the same technique NirSoft's HotKeysList uses.

Requirements: Windows, pywin32 (pip install pywin32)
"""

import ctypes
from ctypes import wintypes
import itertools

# Windows API constants
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008

# Virtual key codes
VK_CODES = {
    # Letters A-Z
    **{chr(i): i for i in range(0x41, 0x5B)},
    # Numbers 0-9
    **{str(i): 0x30 + i for i in range(10)},
    # Function keys F1-F24
    **{f'F{i}': 0x6F + i for i in range(1, 25)},
    # Special keys
    'Space': 0x20,
    'Enter': 0x0D,
    'Tab': 0x09,
    'Escape': 0x1B,
    'Backspace': 0x08,
    'Delete': 0x2E,
    'Insert': 0x2D,
    'Home': 0x24,
    'End': 0x23,
    'PageUp': 0x21,
    'PageDown': 0x22,
    'Up': 0x26,
    'Down': 0x28,
    'Left': 0x25,
    'Right': 0x27,
    'PrintScreen': 0x2C,
    'Pause': 0x13,
    'NumLock': 0x90,
    'ScrollLock': 0x91,
    'CapsLock': 0x14,
    # Numpad
    'Num0': 0x60, 'Num1': 0x61, 'Num2': 0x62, 'Num3': 0x63,
    'Num4': 0x64, 'Num5': 0x65, 'Num6': 0x66, 'Num7': 0x67,
    'Num8': 0x68, 'Num9': 0x69,
    'NumMultiply': 0x6A,
    'NumAdd': 0x6B,
    'NumSubtract': 0x6D,
    'NumDecimal': 0x6E,
    'NumDivide': 0x6F,
    # Punctuation/symbols
    ';': 0xBA, '=': 0xBB, ',': 0xBC, '-': 0xBD,
    '.': 0xBE, '/': 0xBF, '`': 0xC0, '[': 0xDB,
    '\\': 0xDC, ']': 0xDD, "'": 0xDE,
}

# Reverse lookup
VK_NAMES = {v: k for k, v in VK_CODES.items()}

# Modifier combinations to test
MODIFIER_COMBOS = [
    (0, ""),
    (MOD_ALT, "Alt"),
    (MOD_CONTROL, "Ctrl"),
    (MOD_SHIFT, "Shift"),
    (MOD_WIN, "Win"),
    (MOD_ALT | MOD_CONTROL, "Ctrl+Alt"),
    (MOD_ALT | MOD_SHIFT, "Alt+Shift"),
    (MOD_CONTROL | MOD_SHIFT, "Ctrl+Shift"),
    (MOD_ALT | MOD_CONTROL | MOD_SHIFT, "Ctrl+Alt+Shift"),
    (MOD_WIN | MOD_ALT, "Win+Alt"),
    (MOD_WIN | MOD_CONTROL, "Win+Ctrl"),
    (MOD_WIN | MOD_SHIFT, "Win+Shift"),
    (MOD_WIN | MOD_ALT | MOD_CONTROL, "Win+Ctrl+Alt"),
    (MOD_WIN | MOD_ALT | MOD_SHIFT, "Win+Alt+Shift"),
    (MOD_WIN | MOD_CONTROL | MOD_SHIFT, "Win+Ctrl+Shift"),
    (MOD_WIN | MOD_ALT | MOD_CONTROL | MOD_SHIFT, "Win+Ctrl+Alt+Shift"),
]


def scan_hotkeys(verbose=True):
    """
    Scan for all registered global hotkeys.
    Returns a list of tuples: (modifier_name, key_name)
    """
    user32 = ctypes.windll.user32

    registered_hotkeys = []
    test_id = 0x0001  # Arbitrary ID for our test registrations

    total_tests = len(MODIFIER_COMBOS) * len(VK_CODES)
    tested = 0

    if verbose:
        print(f"Scanning {total_tests} hotkey combinations...")
        print("-" * 50)

    for mod_value, mod_name in MODIFIER_COMBOS:
        # Skip bare keys with no modifier (too many false positives)
        if mod_value == 0:
            continue

        for key_name, vk_code in VK_CODES.items():
            tested += 1

            # Try to register the hotkey
            result = user32.RegisterHotKey(None, test_id, mod_value, vk_code)

            if result:
                # Successfully registered - it was free, unregister it
                user32.UnregisterHotKey(None, test_id)
            else:
                # Failed to register - something else has it
                hotkey_str = f"{mod_name}+{key_name}" if mod_name else key_name
                registered_hotkeys.append((mod_name, key_name, hotkey_str))

                if verbose:
                    print(f"  TAKEN: {hotkey_str}")

    if verbose:
        print("-" * 50)
        print(f"Scan complete. Found {len(registered_hotkeys)} registered hotkeys.")

    return registered_hotkeys


def main():
    print("=" * 50)
    print("  Windows Hotkey Scanner")
    print("  (Same technique as NirSoft HotKeysList)")
    print("=" * 50)
    print()

    hotkeys = scan_hotkeys(verbose=True)

    print()
    print("Summary of registered hotkeys:")
    print()

    if hotkeys:
        # Group by modifier
        by_modifier = {}
        for mod, key, full in hotkeys:
            if mod not in by_modifier:
                by_modifier[mod] = []
            by_modifier[mod].append(key)

        for mod in sorted(by_modifier.keys()):
            keys = sorted(by_modifier[mod])
            print(f"  {mod or '(no modifier)'}:")
            print(f"    {', '.join(keys)}")
            print()
    else:
        print("  No registered hotkeys found (unlikely!)")


if __name__ == "__main__":
    main()
