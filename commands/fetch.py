import shutil
from pathlib import Path
from datetime import datetime
import pandas as pd

def copy_folder_recursive(src: Path, dst: Path, match_filter: str = None):
    if not src.exists():
        return []

    copied_files = []
    for item in src.rglob("*.json"):
        if item.is_dir():
            continue
        if not any(marker in item.name for marker in MANAGED_PROFILE_MARKERS):
            continue
        if match_filter and match_filter.lower() not in item.name.lower():
            continue

        target_path = dst / item.relative_to(src)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target_path)
        copied_files.append(item.relative_to(src))
    return copied_files

def compare_file_status(src_file: Path, dst_file: Path):
    if not dst_file.exists():
        return "new"
    orca_time = src_file.stat().st_mtime
    local_time = dst_file.stat().st_mtime
    if orca_time > local_time:
        return "updated in orca"
    elif local_time > orca_time:
        return "newer locally"
    else:
        return "same"

def register(subparsers):
    parser = subparsers.add_parser("fetch", help="Fetch profiles from OrcaSlicer to local folder")
    parser.add_argument("--filter", help="Optional string to match part of profile filename")
    parser.add_argument("--force", action="store_true", help="Force fetch even if local files are newer")
    parser.add_argument("--skip-newer", action="store_true", help="Skip files that are newer locally")

def run(args):
    match = args.filter or ""
    fetch_summary = []

    for folder in PROFILE_FOLDERS:
        src = ORCA_USER_PATH / folder
        dst = LOCAL_PROFILE_PATH / folder

        for f in src.rglob("*.json"):
            if not any(marker in f.name for marker in MANAGED_PROFILE_MARKERS):
                continue
            if match and match.lower() not in f.name.lower():
                continue

            rel_path = f.relative_to(src)
            dst_file = dst / rel_path
            status = compare_file_status(f, dst_file)

            fetch_summary.append({
                "Folder": folder,
                "Filename": str(rel_path),
                "Status": status
            })

    if not fetch_summary:
        print("❌ No matching profiles found.")
        return

    # Show preview table
    df = pd.DataFrame(fetch_summary)
    print("\nThe following profiles will be fetched:\n")
    RESET = "\033[0m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    RED = "\033[91m"
    newer_local = False
    print(f"{'Folder':<12} {'Filename':<90} {'Status':<20}")
    print("-" * 130)
    for row in fetch_summary:
        color = ""
        status = row['Status']
        if status == "newer locally":
            color = RED
            newer_local = True
        elif status == "updated in orca":
            color = BLUE

        print(f"{color}{row['Folder']:<12} {row['Filename']:<90} {status:<20}{RESET}")

    if newer_local and not args.force:
        print(f"{RED}⚠️  Warning: Some local profiles are newer than the versions in OrcaSlicer.")
        print("   Fetching will overwrite these changes and the newer local versions will be lost.")
        print(f"   If you want to keep your local edits, consider pushing or backing up before proceeding.{RESET}")
        if not args.skip_newer:
            return

    confirm = input("\nContinue with fetch? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Aborted.")
        return

    for folder in PROFILE_FOLDERS:
        src = ORCA_USER_PATH / folder
        dst = LOCAL_PROFILE_PATH / folder
        copied = []
        for f in src.rglob("*.json"):
            if not any(marker in f.name for marker in MANAGED_PROFILE_MARKERS):
                continue
            if match and match.lower() not in f.name.lower():
                continue

            rel_path = f.relative_to(src)
            dst_file = dst / rel_path
            status = compare_file_status(f, dst_file)

            if args.skip_newer and status == "newer locally":
                continue

            target_path = dst / rel_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target_path)
            copied.append(rel_path)

        if copied:
            print("\n{:<60} {:<20}".format("Filename", "Status"))
            print("-" * 80)
            for file in copied:
                print("{:<60} {:<20}".format(str(file), "fetched"))
