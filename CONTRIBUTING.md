# Contributing to Otterly Launcher

Thanks for your interest in contributing!

## Project Philosophy

Otterly Launcher is designed to be **minimal and focused**. Before proposing new features, consider:

- Does this add essential functionality?
- Can it be done without adding complexity?
- Does it align with the "quick launcher" purpose?

We prefer simple, well-implemented features over feature bloat.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/launcher.git`
3. Install dependencies: `pip install -r requirements.txt`
4. Read `claude.md` for architecture overview
5. Make your changes
6. Test thoroughly (remember: needs admin privileges on Windows)

## Development Setup

**Requirements:**
- Python 3.8+
- Windows (for now - cross-platform PRs welcome!)
- Administrator privileges for testing

**Testing:**
```bash
# Run as Administrator
python src/launcher.py
```

## Code Style

- Follow PEP 8
- Use type hints where helpful
- Keep functions focused and small
- Comment complex logic, not obvious code
- Maintain the clean architecture (separate concerns)

## Pull Request Process

1. **Create a branch** for your feature/fix
2. **Update documentation** if needed (README, QUICKSTART, claude.md)
3. **Test thoroughly** - launcher must work smoothly
4. **Keep commits focused** - one logical change per commit
5. **Write clear commit messages**

Example:
```
Add fuzzy search filtering to popup window

- Implemented search bar above shortcuts
- Filters as you type
- Escape clears search or closes if empty
```

## Areas We'd Love Help With

- **Cross-platform support** (Linux, macOS)
- **Icon support** (loading .ico files for shortcuts)
- **Alternative trigger methods** (hold key, custom combos)
- **Fuzzy search** in launcher window
- **Auto-start configuration** helper
- **Better error handling** and user feedback
- **Performance improvements**
- **Documentation** improvements

## Bug Reports

When reporting bugs, please include:

- Windows version
- Python version
- Steps to reproduce
- Expected vs actual behavior
- Console output if available
- Config file (with sensitive paths redacted)

## Feature Requests

For feature requests:

- Explain the use case
- Why it fits the minimal philosophy
- How you envision it working
- Whether you're willing to implement it

## Questions?

Open an issue with the "question" label.

## Code of Conduct

Be kind, be constructive, be focused on making the project better.

---

Thank you for contributing! 🦦
