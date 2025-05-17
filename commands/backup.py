from datetime import datetime
import shutil
from pathlib import Path

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

def register(subparsers):
    subparsers.add_parser("backup", help="Create a backup of current OrcaSlicer profiles")

def run(args):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_dir = BACKUP_PATH / timestamp / "default"
    print(f"Backing up OrcaSlicer profiles to: {backup_dir}")

    for folder in PROFILE_FOLDERS:
        src = ORCA_USER_PATH / folder
        dst = backup_dir / folder
        copied = copy_folder_recursive(src, dst)
        if copied:
            print(f"[{folder}]")
            print("{:<60} {:<20}".format("Filename", "Status"))
            print("-" * 80)
            for file in copied:
                print("{:<60} {:<20}".format(str(file), "backed up"))
