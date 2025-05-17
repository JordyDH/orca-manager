import shutil
from pathlib import Path

def copy_folder_recursive(src: Path, dst: Path, match_filter: str = None):
    if not src.exists():
        return []

    copied_files = []
    for item in src.rglob("*"):
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

def register(subparsers):
    parser = subparsers.add_parser("fetch", help="Fetch profiles from OrcaSlicer to local folder")
    parser.add_argument("--filter", help="Optional string to match part of profile filename")

def run(args):
    match = args.filter or ""
    all_matches = {}

    for folder in PROFILE_FOLDERS:
        src = ORCA_USER_PATH / folder
        files = [f.relative_to(src) for f in src.rglob("*")
                 if f.is_file()
                 and any(marker in f.name for marker in MANAGED_PROFILE_MARKERS)
                 and (match.lower() in f.name.lower() if match else True)]
        if files:
            all_matches[folder] = files

    if not all_matches:
        print("❌ No matching profiles found.")
        return

    print("The following files will be fetched:")
    for folder, files in all_matches.items():
        print(f"  {folder}/")
        for f in files:
            print(f"    {f}")

    confirm = input("Continue with fetch? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Aborted.")
        return

    for folder in PROFILE_FOLDERS:
        src = ORCA_USER_PATH / folder
        dst = LOCAL_PROFILE_PATH / folder
        copied = copy_folder_recursive(src, dst, match_filter=match)
        if copied:
            print("{:<60} {:<20}".format("Filename", "Status"))
            print("-" * 80)
            for file in copied:
                print("{:<60} {:<20}".format(str(file), "fetched"))