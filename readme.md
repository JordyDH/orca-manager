# 🐳 Orca Manager CLI

`orca-manager` is a command-line utility to manage OrcaSlicer profiles in a Git-based workflow. It allows teams to safely edit, track, sync, and distribute print profiles with automated validation, backups, and profile flattening logic.

## Features

- Fetch profiles from OrcaSlicer into a local Git folder
- Push local profiles to OrcaSlicer (with validation and conflict detection)
- Backup and restore full OrcaSlicer profile states
- Flatten inherited profiles to standalone JSON files
- Show diffs between OrcaSlicer and local profiles
- List and validate managed profiles
- Git control commands (`fetch`, `commit`, `push`, etc.) from CLI

## Usage

Run with:
```bash
orca-manager <command> [options]
```

Call with no arguments or `--help` to view all commands.

## Install

To make `orca-manager` accessible globally:
```bash
./install.sh
```
This adds an alias to your shell (`~/.bashrc` or `~/.zshrc`).

## Commands

- `fetch` – Fetch profiles from OrcaSlicer to local folder
- `push` – Push profiles from local folder to OrcaSlicer
- `push-clean` – Push without cleaning existing files
- `backup` – Backup current OrcaSlicer profiles
- `restore` – Interactively restore a previous backup
- `list` – List all managed profiles currently in OrcaSlicer
- `diff` – Show differences between local and OrcaSlicer profiles
- `flatten` – Flatten inherited profiles into standalone ones
- `validate` – Validate profile structure and inheritance
- `clone` – Clone a profile into a new one
- `git` – Perform Git actions (`status`, `commit`, etc.)

## Adding New Commands

All commands live in the `commands/` directory and follow a simple structure.
Each command is a Python file that implements two functions:

```python
def register(subparsers):
    parser = subparsers.add_parser("yourcommand", help="Describe the command")
    parser.add_argument(...)  # optional CLI arguments

def run(args):
    # logic that runs when the command is invoked
    print("Running your command")
```

### Rules:
- File must be placed in the `commands/` folder.
- File name becomes the command name (e.g. `hello.py` → `orca-manager hello`).
- Globals such as `ORCA_USER_PATH`, `LOCAL_PROFILE_PATH`, etc. are auto-injected.

You can also call another command internally using:
```python
import orca
orca.run_command("backup")
```

## Notes

- Only files containing `ODG_` or `(ON)` in the filename are considered "managed"
- All backups are stored in `./backups/`
- Git operations work on the `./orca_profiles/` folder

## License

This project is internal tooling and currently distributed without a license.

---

For more details, consult the inline help:
```bash
orca-manager <command> --help
```
