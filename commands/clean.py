from pathlib import Path
import orca  # Main CLI loader with run_command()

def delete_managed_profiles(folder: Path):
    deleted = []
    if folder.exists():
        for item in folder.rglob("*"):
            if item.is_file() and any(marker in item.name for marker in MANAGED_PROFILE_MARKERS):
                deleted.append(item)
                item.unlink()
    return deleted

def register(subparsers):
    subparsers.add_parser("clean", help="Remove all managed profiles from OrcaSlicer user directory")

def run(args):
    print("🧹 Cleaning managed profiles from OrcaSlicer user folder...\n")
    # Backup Orca files first
    orca.run_command("backup")
    for folder in PROFILE_FOLDERS:
        orca_dir = ORCA_USER_PATH / folder
        deleted = delete_managed_profiles(orca_dir)

        if deleted:
            print(f"[{folder}]")
            print("{:<60} {:<20}".format("Filename", "Status"))
            print("-" * 80)
            for file in deleted:
                print("{:<60} {:<20}".format(file.name, "deleted"))
        else:
            print(f"[{folder}] No managed profiles found to delete.")
