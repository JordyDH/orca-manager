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
GIT_ROOT_PATH = LOCAL_ROOT
BACKUP_PATH = LOCAL_ROOT / "backups"
PROFILE_FOLDERS = ["filament", "machine", "process"]

def copy_folder_recursive(src: Path, dst: Path, match_filter: str = None):
    if not src.exists():
        return []

    copied_files = []
    for item in src.rglob("*"):
        if item.is_dir():
            continue
        if match_filter and match_filter.lower() not in item.name.lower():
            continue

        target_path = dst / item.relative_to(src)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target_path)
        copied_files.append(item.relative_to(src))
    return copied_files

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
    match = input("Enter a name or part of a profile name to filter (press Enter for all): ").strip()

    all_matches = {}
    for folder in PROFILE_FOLDERS:
        src = ORCA_USER_PATH / folder
        files = [f.relative_to(src) for f in src.rglob("*") if f.is_file() and (match.lower() in f.name.lower() if match else True)]
        if files:
            all_matches[folder] = files

    if not all_matches:
        print("❌ No matching profiles found.")
        return

    print("🔍 The following files will be fetched:")
    for folder, files in all_matches.items():
        print(f"  {folder}/")
        for f in files:
            print(f"    📄 {f}")

    confirm = input("Continue with fetch? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Aborted.")
        return

    for folder in PROFILE_FOLDERS:
        src = ORCA_USER_PATH / folder
        dst = LOCAL_PROFILE_PATH / folder
        copied = copy_folder_recursive(src, dst, match_filter=match)
        if copied:
            print(f"  ✅ Synced {len(copied)} file(s) in {folder}/")

def backup_profiles():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_dir = BACKUP_PATH / timestamp / "default"
    print(f"📦 Backing up OrcaSlicer profiles to: {backup_dir}")

    for folder in PROFILE_FOLDERS:
        src = ORCA_USER_PATH / folder
        dst = backup_dir / folder
        copy_folder_recursive(src, dst)
        print(f"  📁 Backed up: {folder}/")

def restore_backup():
    print("🔁 Restoring a backup to OrcaSlicer...")
    if not BACKUP_PATH.exists():
        print("❌ No backup directory found.")
        return

    backups = sorted([d for d in BACKUP_PATH.iterdir() if d.is_dir()], reverse=True)
    if not backups:
        print("❌ No backups available to restore.")
        return

    print("Available backups:")
    for idx, backup in enumerate(backups):
        print(f"  [{idx}] {backup.name}")

    try:
        choice = int(input("Select a backup to restore by index: "))
        selected_backup = backups[choice] / "default"
    except (ValueError, IndexError):
        print("❌ Invalid selection.")
        return

    print(f"⚠️  This will overwrite current OrcaSlicer profiles. Are you sure? (yes/no)")
    confirm = input().strip().lower()
    if confirm != "yes":
        print("❌ Aborted.")
        return

    for folder in PROFILE_FOLDERS:
        orca_dir = ORCA_USER_PATH / folder
        backup_dir = selected_backup / folder

        delete_all_profiles_in(orca_dir)
        print(f"  🧹 Cleaned: {folder}/")

        copy_folder_recursive(backup_dir, orca_dir)
        print(f"  ✅ Restored: {folder}/")

def orca_push():
    print("📤 Pushing local profiles to OrcaSlicer after backup...")
    backup_profiles()

    for folder in PROFILE_FOLDERS:
        orca_dir = ORCA_USER_PATH / folder
        local_dir = LOCAL_PROFILE_PATH / folder

        delete_all_profiles_in(orca_dir)
        print(f"  🧹 Cleaned: {folder}/")

        copy_folder_recursive(local_dir, orca_dir)
        print(f"  ✅ Pushed: {folder}/")

def orca_push_clean():
    print("📤 Cleaning and pushing ONLY the managed profiles to OrcaSlicer...")
    for folder in PROFILE_FOLDERS:
        orca_dir = ORCA_USER_PATH / folder
        local_dir = LOCAL_PROFILE_PATH / folder

        copy_folder_recursive(local_dir, orca_dir)
        print(f"  ✅ Synced without cleanup: {folder}/")

def git_fetch():
    print("🌐 Running `git fetch` in tool root folder ...")

    if not (GIT_ROOT_PATH / ".git").exists():
        print(f"❌ Not a Git repository: {GIT_ROOT_PATH}")
        return

    try:
        result = subprocess.run(
            ["git", "fetch"],
            cwd=GIT_ROOT_PATH,
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

def main():
    parser = argparse.ArgumentParser(
        description="🐳 Orca Manager CLI",
        usage="orca-manager <command>"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Git-related
    subparsers.add_parser("gitfetch", help="Run 'git fetch' in the repo root")
    subparsers.add_parser("gitpush", help="(Disabled) Placeholder for pushing to Git")

    # Orca operations
    subparsers.add_parser("fetch", help="Fetch profiles from OrcaSlicer to local folder")
    subparsers.add_parser("push", help="Backup and push local profiles to OrcaSlicer (cleans destination)")
    subparsers.add_parser("push-clean", help="Push local profiles to OrcaSlicer without deleting other user files")
    subparsers.add_parser("backup", help="Create a backup of current OrcaSlicer profiles")
    subparsers.add_parser("restore", help="Interactively restore a backup to OrcaSlicer")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "fetch":
        orca_fetch()
    elif args.command == "push":
        orca_push()
    elif args.command == "push-clean":
        orca_push_clean()
    elif args.command == "backup":
        backup_profiles()
    elif args.command == "restore":
        restore_backup()
    elif args.command == "gitfetch":
        git_fetch()
    elif args.command == "gitpush":
        git_push()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()