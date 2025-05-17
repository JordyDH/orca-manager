from pathlib import Path
import shutil

def copy_folder_recursive(src: Path, dst: Path):
    if not src.exists():
        return []

    copied_files = []
    for item in src.rglob("*"):
        if item.is_dir():
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

def register(subparsers):
    subparsers.add_parser("restore", help="Interactively restore a backup to OrcaSlicer")

def run(args):
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

    print("⚠️  This will overwrite current OrcaSlicer profiles. Are you sure? (yes/no)")
    confirm = input().strip().lower()
    if confirm != "yes":
        print("❌ Aborted.")
        return

    for folder in PROFILE_FOLDERS:
        orca_dir = ORCA_USER_PATH / folder
        backup_dir = selected_backup / folder

        delete_all_profiles_in(orca_dir)
        print(f"[{folder}]")
        copied = copy_folder_recursive(backup_dir, orca_dir)
        if copied:
            print("{:<60} {:<20}".format("Filename", "Status"))
            print("-" * 80)
            for file in copied:
                print("{:<60} {:<20}".format(str(file), "restored"))
