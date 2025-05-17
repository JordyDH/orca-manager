import shutil
from pathlib import Path
import sys

# Make sure the main script (orca.py) is importable
import orca  # this is orca.py

def copy_folder_recursive(src: Path, dst: Path):
    if not src.exists():
        return []

    copied_files = []
    for item in src.rglob("*"):
        if item.is_dir():
            continue
        if not any(marker in item.name for marker in MANAGED_PROFILE_MARKERS):
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
                    pass  # Not empty

def register(subparsers):
    subparsers.add_parser("push", help="Backup and push local profiles to OrcaSlicer (cleans destination)")

def run(args):
    print("📤 Pushing local profiles to OrcaSlicer after backup...")
    orca.run_command("backup")  # Dynamically execute the backup command

    for folder in PROFILE_FOLDERS:
        orca_dir = ORCA_USER_PATH / folder
        local_dir = LOCAL_PROFILE_PATH / folder

        delete_all_profiles_in(orca_dir)
        print(f"[{folder}]")
        copied = copy_folder_recursive(local_dir, orca_dir)
        if copied:
            print("{:<60} {:<20}".format("Filename", "Status"))
            print("-" * 80)
            for file in copied:
                print("{:<60} {:<20}".format(str(file), "pushed"))
