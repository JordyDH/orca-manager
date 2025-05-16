#!/usr/bin/env python3

import argparse
import shutil
from pathlib import Path
import sys
from datetime import datetime
import subprocess

# Constants
ORCA_USER_ROOT = Path.home() / ".config" / "OrcaSlicer" / "user"
ORCA_USER_PATH = ORCA_USER_ROOT / "default"
LOCAL_ROOT = Path(__file__).parent
LOCAL_PROFILE_PATH = LOCAL_ROOT / "orca_profiles" / "default"
BACKUP_PATH = LOCAL_ROOT / "backups"
PROFILE_FOLDERS = ["filament", "machine", "process"]

def copy_folder_recursive(src: Path, dst: Path):
    if not src.exists():
        return
    for item in src.rglob("*"):
        target_path = dst / item.relative_to(src)
        if item.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target_path)
            print(f"    📄 Copied: {item.relative_to(src)}")

def delete_all_profiles_in(folder: Path):
    if folder.exists():
        for item in folder.rglob("*"):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                try:
                    item.rmdir()
                except OSError:
                    pass  # not empty

def orca_fetch():
    print("📅 Fetching profiles from OrcaSlicer to local git folder...")
    for folder in PROFILE_FOLDERS:
        src = ORCA_USER_PATH / folder
        dst = LOCAL_PROFILE_PATH / folder
        copy_folder_recursive(src, dst)
        print(f"  ✅ Synced: {folder}/")

def backup_profiles():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_dir = BACKUP_PATH / timestamp / "default"
    print(f"📦 Backing up OrcaSlicer profiles to: {backup_dir}")

    for folder in PROFILE_FOLDERS:
        src = ORCA_USER_PATH / folder
        dst = backup_dir / folder
        copy_folder_recursive(src, dst)
        print(f"  📁 Backed up: {folder}/")

def orca_push():
    print("📤 Pushing local profiles to OrcaSlicer after backup...")
    backup_profiles()

    for folder in PROFILE_FOLDERS:
        orca_dir = ORCA_USER_PATH / folder
        local_dir = LOCAL_PROFILE_PATH / folder

        # Clean all existing files
        delete_all_profiles_in(orca_dir)
        print(f"  🧹 Cleaned: {folder}/")

        # Push new files
        copy_folder_recursive(local_dir, orca_dir)
        print(f"  ✅ Pushed: {folder}/")

def git_fetch():
    print("🌐 Running `git fetch` in orca_profiles/default ...")

    git_folder = LOCAL_PROFILE_PATH
    if not (git_folder / ".git").exists():
        print(f"❌ Not a Git repository: {git_folder}")
        return

    try:
        result = subprocess.run(
            ["git", "fetch"],
            cwd=git_folder,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("⚠️", result.stderr)
    except Exception as e:
        print(f"❌ Git fetch failed: {e}")

def git_push():
    print("🔒 Git push placeholder – this operation is disabled for safety.")
    # This is where you'd later allow automated git pushes if needed

def main():
    parser = argparse.ArgumentParser(
        description="🐳 Orca Manager CLI",
        usage="orca-manager <command>"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Git-related
    subparsers.add_parser("gitfetch", help="Run 'git fetch' in the orca_profiles folder")
    subparsers.add_parser("gitpush", help="(Disabled) Placeholder for pushing to Git")

    # Orca operations
    subparsers.add_parser("fetch", help="Fetch profiles from OrcaSlicer to local folder")
    subparsers.add_parser("push", help="Backup and push local profiles to OrcaSlicer")
    subparsers.add_parser("backup", help="Create a backup of current OrcaSlicer profiles")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "fetch":
        orca_fetch()
    elif args.command == "push":
        orca_push()
    elif args.command == "backup":
        backup_profiles()
    elif args.command == "gitfetch":
        git_fetch()
    elif args.command == "gitpush":
        git_push()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
