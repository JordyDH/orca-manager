# 🐳 Orca Manager CLI

A CLI tool to manage OrcaSlicer profiles using versioned folders and backups.

## 📦 Overview

This tool allows you to:
- Fetch profiles from OrcaSlicer to a Git-tracked folder
- Push profiles back to OrcaSlicer (clean or additive)
- Create and restore backups

Profiles are stored in:
```text
~/.config/OrcaSlicer/user/default/
```

The tool maintains a mirrored folder structure in:
```text
./orca_profiles/default/
```

## 🚀 Example Commands

Run any command like this:
```bash
python orca.py <command>
```

### Common Commands
- `fetch` – Interactively fetch matching profiles from OrcaSlicer
- `push` – Push profiles and clear out old ones first
- `push-clean` – Push profiles without deleting existing ones
- `backup` – Create a timestamped backup of Orca profiles
- `restore` – Interactively restore from a previous backup

---

For up-to-date help and all available commands:
```bash
python orca.py --help
```

---

## 🛠 Installation

To make the CLI available globally:

1. Make sure you have `install.sh` in the same folder as `orca.py`
2. Run the installer:
   ```bash
   ./install.sh
   ```
3. Restart your terminal or run:
   ```bash
   source ~/.bashrc   # or ~/.zshrc
   ```
4. You can now run:
   ```bash
   orca-manager fetch
   ```

The install script will:
- Symlink the CLI as `orca-manager`
- Add its path to your shell config if needed


