import difflib
from pathlib import Path

def register(subparsers):
    parser = subparsers.add_parser("diff", help="Show differences between OrcaSlicer and local profiles")
    parser.add_argument("--all", action="store_true", help="Show all files, including identical ones")
    parser.add_argument("--details", action="store_true", help="Show line-by-line file diffs for differing files")

def run(args):
    show_all = args.all
    show_diff = args.details

    print("Comparing OrcaSlicer profiles with local git-tracked profiles:")
    print("{:<60} {:<20}".format("Filename", "Status"))
    print("-" * 80)

    for folder in PROFILE_FOLDERS:
        orca_dir = ORCA_USER_PATH / folder
        local_dir = LOCAL_PROFILE_PATH / folder

        orca_files = {f.name: f for f in orca_dir.rglob("*") if f.is_file() and any(m in f.name for m in MANAGED_PROFILE_MARKERS)}
        local_files = {f.name: f for f in local_dir.rglob("*") if f.is_file() and any(m in f.name for m in MANAGED_PROFILE_MARKERS)}

        all_filenames = set(orca_files.keys()).union(local_files.keys())

        for filename in sorted(all_filenames):
            status = []
            orca_file = orca_files.get(filename)
            local_file = local_files.get(filename)

            if orca_file and not local_file:
                status.append("only in Orca")
            elif local_file and not orca_file:
                status.append("only in Git")
            elif orca_file and local_file:
                if orca_file.read_bytes() != local_file.read_bytes():
                    status.append("differs")
                else:
                    status.append("same")

            if not show_all and "same" in status:
                continue

            print("{:<60} {:<20}".format(filename, ", ".join(status)))

            if "differs" in status and show_diff and orca_file and local_file:
                print("    --- Git version vs Orca version ---")
                try:
                    git_lines = local_file.read_text(errors='ignore').splitlines()
                    orca_lines = orca_file.read_text(errors='ignore').splitlines()
                    diff = difflib.unified_diff(
                        git_lines,
                        orca_lines,
                        fromfile=f"git/{folder}/{filename}",
                        tofile=f"orca/{folder}/{filename}",
                        lineterm=""
                    )
                    for line in diff:
                        if line.startswith("+") and not line.startswith("+++"):
                            print("    \033[32m" + line + "\033[0m")  # green
                        elif line.startswith("-") and not line.startswith("---"):
                            print("    \033[31m" + line + "\033[0m")  # red
                        elif line.startswith("@@"):
                            print("    \033[33m" + line + "\033[0m")  # yellow
                        else:
                            print("    " + line)
                except Exception as e:
                    print(f"    [Error showing diff: {e}]")
