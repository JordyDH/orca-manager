#!/usr/bin/env python3

import argparse
import importlib.util
import os
import sys
from pathlib import Path

# Constants
ORCA_PATH = Path.home() / ".config" / "OrcaSlicer"
ORCA_USER_ROOT = Path.home() / ".config" / "OrcaSlicer" / "user"
ORCA_USER_PATH = ORCA_USER_ROOT / "default"
LOCAL_ROOT = Path(__file__).parent
LOCAL_PROFILE_PATH = LOCAL_ROOT / "orca_profiles" / "default"
GIT_ROOT_PATH = LOCAL_PROFILE_PATH
BACKUP_PATH = LOCAL_ROOT / "backups"
PROFILE_FOLDERS = ["filament", "machine", "process"]
MANAGED_PROFILE_MARKERS = ["ODG_", "(ON)"]
#MANAGED_PROFILE_MARKERS = [""]

COMMANDS_DIR = LOCAL_ROOT / "commands"

BACKUP_WARNING_LIMIT = 25
RED = "\033[91m"
RESET = "\033[0m"

def load_commands(parser):
    subparsers = parser.add_subparsers(dest="command")

    command_funcs = {}

    for file in sorted(COMMANDS_DIR.glob("*.py")):
        module_name = file.stem
        spec = importlib.util.spec_from_file_location(module_name, file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.ORCA_USER_ROOT = ORCA_USER_ROOT
        mod.ORCA_USER_PATH = ORCA_USER_PATH
        mod.LOCAL_ROOT = LOCAL_ROOT
        mod.LOCAL_PROFILE_PATH = LOCAL_PROFILE_PATH
        mod.GIT_ROOT_PATH = GIT_ROOT_PATH
        mod.BACKUP_PATH = BACKUP_PATH
        mod.PROFILE_FOLDERS = PROFILE_FOLDERS
        mod.MANAGED_PROFILE_MARKERS = MANAGED_PROFILE_MARKERS

        if hasattr(mod, "register") and hasattr(mod, "run"):
            mod.register(subparsers)
            command_funcs[module_name] = mod.run

    return command_funcs

def check_backup_count():
    if BACKUP_PATH.exists():
        backup_folders = [d for d in BACKUP_PATH.iterdir() if d.is_dir()]
        if len(backup_folders) > BACKUP_WARNING_LIMIT:
            print(f"{RED}⚠️  Warning: You have {len(backup_folders)} backups stored.")
            print("   Consider cleaning up old backups to save disk space.", RESET)

def run_command(command_name: str, args_dict: dict = {}):
    """Run another command from within a command script."""
    parser = argparse.ArgumentParser()
    command_funcs = load_commands(parser)

    if command_name not in command_funcs:
        print(f"❌ Command '{command_name}' not found.")
        return

    class Args:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    args = Args(**args_dict)
    command_funcs[command_name](args)

def main():
    parser = argparse.ArgumentParser(
        description="🐳 Orca Manager CLI",
        usage="orca-manager <command>"
    )

    command_funcs = load_commands(parser)

    check_backup_count()

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command in command_funcs:
        command_funcs[args.command](args)
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main()
