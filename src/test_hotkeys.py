from shortcut_scanner import ShortcutScanner

scanner = ShortcutScanner()
results = scanner.scan_all()

with_hotkeys = [s for s in results if s.get('hotkey') and s['hotkey'] != '']

print(f'Total shortcuts: {len(results)}')
print(f'With hotkeys: {len(with_hotkeys)}')
print('\nShortcuts with hotkeys:')
for s in with_hotkeys[:20]:
    print(f'  {s["name"]}: {s["hotkey"]}')
