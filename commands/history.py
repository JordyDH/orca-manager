import subprocess
from pathlib import Path

def register(subparsers):
    parser = subparsers.add_parser("history", help="Show Git commit history of a profile")
    parser.add_argument("filename", nargs="?", help="Profile filename (optional)")

def run(args):
    if args.filename:
        target_file = args.filename
    else:
        # List all managed files with IDs
        all_profiles = []
        print("📁 Select a profile to view Git history:\n")
        for folder in PROFILE_FOLDERS:
            folder_path = LOCAL_PROFILE_PATH / folder
            files = [f for f in folder_path.rglob("*")
                     if f.is_file() and any(marker in f.name for marker in MANAGED_PROFILE_MARKERS)]
            for f in sorted(files):
                all_profiles.append((folder, f.name))

        if not all_profiles:
            print("❌ No managed profiles found in local folder.")
            return

        for idx, (folder, name) in enumerate(all_profiles):
            print(f"[{idx:02d}] {folder}/{name}")

        try:
            choice = int(input("\nEnter the ID of the profile: "))
            target_file = all_profiles[choice][1]
        except (ValueError, IndexError):
            print("❌ Invalid selection.")
            return

    # Search for the file in known folders
    matches = []
    for folder in PROFILE_FOLDERS:
        full_path = LOCAL_PROFILE_PATH / folder / target_file
        if full_path.exists():
            matches.append((folder, full_path))

    if not matches:
        print(f"❌ File '{target_file}' not found in local folders.")
        return

    for folder, path in matches:
        print(f"\n📜 Git history for: {folder}/{path.name}\n")
        try:
            result = subprocess.run(
                ["git", "log", "--", str(path)],
                cwd=GIT_ROOT_PATH,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.stdout:
                print(result.stdout)
            else:
                print("  No history found.")
        except Exception as e:
            print(f"  Error reading history: {e}")
