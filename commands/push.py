import shutil
from pathlib import Path
import sys
import pandas as pd

# Make sure the main script (orca.py) is importable
import orca  # this is orca.py

RESET = "\033[0m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RED = "\033[91m"

def compare_file_status(src_file: Path, dst_file: Path):
    if not dst_file.exists():
        return "new"
    src_time = src_file.stat().st_mtime
    dst_time = dst_file.stat().st_mtime
    if src_time > dst_time:
        return "updated locally"
    elif dst_time > src_time:
        return "newer in orca"
    else:
        return "same"

def copy_folder_recursive(src: Path, dst: Path, skip_newer=False):
    if not src.exists():
        return []

    copied_files = []
    for item in src.rglob("*.json"):
        if item.is_dir():
            continue
        if not any(marker in item.name for marker in MANAGED_PROFILE_MARKERS):
            continue

        rel_path = item.relative_to(src)
        dst_file = dst / rel_path
        status = compare_file_status(item, dst_file)

        if skip_newer and status == "newer in orca":
            continue

        target_path = dst / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target_path)
        copied_files.append((rel_path, status))
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
                    pass  # Not empty

def register(subparsers):
    parser = subparsers.add_parser("push", help="Backup and push local profiles to OrcaSlicer (cleans destination)")
    parser.add_argument("--force", action="store_true", help="Force push even if OrcaSlicer files are newer")
    parser.add_argument("--skip-newer", action="store_true", help="Skip files that are newer in OrcaSlicer")

def run(args):
    print("\U0001F4E4 Pushing local profiles to OrcaSlicer after backup...")

    push_summary = []
    has_newer_orca = False

    for folder in PROFILE_FOLDERS:
        orca_dir = ORCA_USER_PATH / folder
        local_dir = LOCAL_PROFILE_PATH / folder

        for f in local_dir.rglob("*.json"):
            if not any(marker in f.name for marker in MANAGED_PROFILE_MARKERS):
                continue

            rel_path = f.relative_to(local_dir)
            dst_file = orca_dir / rel_path
            status = compare_file_status(f, dst_file)
            if status == "newer in orca":
                has_newer_orca = True
            push_summary.append({
                "Folder": folder,
                "Filename": str(rel_path),
                "Status": status
            })

    if not push_summary:
        print("❌ No profiles found to push.")
        return

    print("\nThe following profiles will be pushed:\n")
    print(f"{'Folder':<12} {'Filename':<90} {'Status':<20}")
    print("-" * 130)
    for row in push_summary:
        color = ""
        if row['Status'] == "updated locally":
            color = GREEN
        elif row['Status'] == "newer in orca":
            color = RED
        print(f"{color}{row['Folder']:<12} {row['Filename']:<90} {row['Status']:<20}{RESET}")

    if has_newer_orca and not args.force:
        print(f"{RED}⚠️  Warning: Some OrcaSlicer profiles are newer than local ones.")
        print("   Pushing will overwrite these changes and the newer Orca files will be lost.")
        print(f"   If you want to keep those changes, consider fetching or backing up first.{RESET}")
        if not args.skip_newer:
            return

    confirm = input("\nContinue with push? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Aborted.")
        return

    orca.run_command("backup")  # Dynamically execute the backup command
    for folder in PROFILE_FOLDERS:
        orca_dir = ORCA_USER_PATH / folder
        local_dir = LOCAL_PROFILE_PATH / folder

        delete_all_profiles_in(orca_dir)
        print(f"\n[{folder}]")
        copied = copy_folder_recursive(local_dir, orca_dir, skip_newer=args.skip_newer)
        if copied:
            print("{:<60} {:<20}".format("Filename", "Status"))
            print("-" * 80)
            for rel_path, status in copied:
                print("{:<60} {:<20}".format(str(rel_path), "pushed"))
