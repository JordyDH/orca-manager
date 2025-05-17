from datetime import datetime
from pathlib import Path
import subprocess

def get_git_last_editor(file_path: Path):
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%an", str(file_path)],
            cwd=GIT_ROOT_PATH,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        return result.stdout.strip() if result.stdout else "-"
    except Exception:
        return "-"

def register(subparsers):
    subparsers.add_parser("list", help="List all managed profiles in OrcaSlicer")

def run(args):
    print("Listing managed profiles in OrcaSlicer:")

    found = False
    for folder in PROFILE_FOLDERS:
        src = ORCA_USER_PATH / folder
        files = [f for f in src.rglob("*") if f.is_file() and any(marker in f.name for marker in MANAGED_PROFILE_MARKERS)]
        if files:
            found = True
            print(f"\n[{folder}]")
            print("{:<60} {:<20} {:<20}".format("Filename", "Modified", "Last Edited By"))
            print("-" * 100)
            for f in sorted(files):
                modified = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                git_author = get_git_last_editor(LOCAL_PROFILE_PATH / folder / f.name)
                filename = f.name[:57] + "..." if len(f.name) > 60 else f.name
                print("{:<60} {:<20} {:<20}".format(filename, modified, git_author))
    if not found:
        print("\nNo managed profiles found.")
