#Still a work in progress

import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# Configuration paths
CONFIG_DIR = Path(__file__).parent.parent / "orca_repositories"
CONFIG_FILE = CONFIG_DIR / "orca_repositories.json"
INSTALLED_FILE = CONFIG_DIR / "orca_installed.json"
REPO_DIR = CONFIG_DIR

# Ensure config directory and files exist
CONFIG_DIR.mkdir(exist_ok=True)
if not CONFIG_FILE.exists():
    CONFIG_FILE.write_text(json.dumps({"repositories": []}, indent=2))
if not INSTALLED_FILE.exists():
    INSTALLED_FILE.write_text(json.dumps({"installed": []}, indent=2))

# Profile settings
PROFILE_FOLDERS = ["filament", "machine", "process"]
PROFILE_EXTENSIONS = [".json", ".info"]
ORCA_USER_PATH = Path(__file__).parent.parent / "orca_profiles" / "default"

# Console colors
RESET = "\033[0m"
GREEN = "\033[92m"
YELLOW = "\033[93m"

def load_config():
    with CONFIG_FILE.open("r") as f:
        return json.load(f)

def save_config(data):
    with CONFIG_FILE.open("w") as f:
        json.dump(data, f, indent=2)

def load_installed():
    with INSTALLED_FILE.open("r") as f:
        return json.load(f)

def save_installed(data):
    with INSTALLED_FILE.open("w") as f:
        json.dump(data, f, indent=2)

def register(subparsers):
    parser = subparsers.add_parser(
        "repos",
        help="Manage external Orca profile repositories"
    )
    parser.add_argument(
        "action",
        choices=["add", "list", "remove", "sync", "search", "install", "uninstall", "move"],
        help="Action to perform"
    )
    parser.add_argument("--name", help="Repository name")
    parser.add_argument("--url", help="Git URL of the repository")
    parser.add_argument("--profile", help="Profile file name")
    parser.add_argument(
        "--folder",
        help="Folder type (filament, machine, process)"
    )
    parser.add_argument(
        "--target",
        help="Target name or path for move"
    )


def run(args):
    config = load_config()
    repos = config.get("repositories", [])
    installed = load_installed()

    if args.action == "list":
        print("Tracked Repositories:")
        for r in repos:
            print(f"- {r['name']}: {r['url']}")
        return

    if args.action == "add":
        if not args.name or not args.url:
            print("--name and --url are required to add a repository")
            return
        target_path = REPO_DIR / args.name
        if target_path.exists():
            print("❌ Target folder already exists.")
            return
        print(f"Cloning {args.url} into {target_path}...")
        result = subprocess.run(
            ["git", "clone", args.url, str(target_path)]
        )
        if result.returncode == 0:
            repos.append({"name": args.name, "url": args.url})
            save_config({"repositories": repos})
            print("✅ Repository added.")
        else:
            print("❌ Failed to clone repository.")
        return

    if args.action == "remove":
        if not args.name:
            print("--name is required to remove a repository")
            return
        updated = [r for r in repos if r["name"] != args.name]
        if len(updated) == len(repos):
            print("❌ Repository not found.")
            return
        shutil.rmtree(REPO_DIR / args.name, ignore_errors=True)
        save_config({"repositories": updated})
        print(f"✅ Removed repository: {args.name}")
        return

    if args.action == "sync":
        print("Comparing local and repository profiles...")
        sync_plan = []
        for r in repos:
            repo_path = REPO_DIR / r["name"]
            for folder in PROFILE_FOLDERS:
                repo_dir = repo_path / folder
                local_dir = ORCA_USER_PATH / folder
                if not repo_dir.exists():
                    print(f"⚠️ Missing folder '{folder}' in repo '{r['name']}'")
                    continue
                # Build maps of relative paths to file Paths
                repo_files = {}
                for p in repo_dir.rglob("*"):
                    if p.is_file() and p.suffix in PROFILE_EXTENSIONS:
                        rel = p.relative_to(repo_dir)
                        repo_files[str(rel)] = p
                local_files = {}
                if local_dir.exists():
                    for p in local_dir.rglob("*"):
                        if p.is_file() and p.suffix in PROFILE_EXTENSIONS:
                            rel = p.relative_to(local_dir)
                            local_files[str(rel)] = p
                # Compare sets
                for rel_path in sorted(set(repo_files) | set(local_files)):
                    in_repo = rel_path in repo_files
                    in_local = rel_path in local_files
                    if in_repo and not in_local:
                        status = "repo -> local (new)"
                    elif in_local and not in_repo:
                        status = "local -> repo (new)"
                    else:
                        rt = repo_files[rel_path].stat().st_mtime
                        lt = local_files[rel_path].stat().st_mtime
                        if rt > lt:
                            status = "repo -> local (newer)"
                        elif lt > rt:
                            status = "local -> repo (newer)"
                        else:
                            status = "same"
                    if status != "same":
                        sync_plan.append({
                            "repo": r['name'],
                            "folder": folder,
                            "rel_path": rel_path,
                            "status": status
                        })
        # Print plan
        if not sync_plan:
            print("No changes detected.")
            return
        print("\nPlanned sync actions:")
        print(f"{'Repo':<20} {'Folder':<10} {'Path':<50} {'Action'}")
        print("-" * 95)
        for item in sync_plan:
            print(
                f"{item['repo']:<20} {item['folder']:<10} "
                f"{item['rel_path']:<50} {item['status']}"
            )
        if input("\nProceed? (yes/no): ").strip().lower() != "yes":
            print("Aborted.")
            return
        # Execute sync
        for item in sync_plan:
            repo_dir = REPO_DIR / item['repo'] / item['folder']
            local_dir = ORCA_USER_PATH / item['folder']
            rel = item['rel_path']
            if item['status'].startswith("repo -> local"):
                src = repo_dir / rel
                dst = local_dir / rel
            else:
                src = local_dir / rel
                dst = repo_dir / rel
            # Log copy action
            print(f"Copying '{rel}' [{item['status']}] from '{src}' to '{dst}'")
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        print("✅ Sync complete.")
        return

    if args.action == "search":
        print("Available profiles in repositories:")
        for r in repos:
            print(f"\n[{r['name']}]'")
            for folder in PROFILE_FOLDERS:
                path = REPO_DIR / r['name'] / folder
                if path.exists():
                    for p in path.rglob("*"):
                        if p.is_file() and p.suffix in PROFILE_EXTENSIONS:
                            print(f"  {folder}/{p.relative_to(path)}")
        return

    if args.action == "install":
        if not args.name:
            print("--name is required to install profiles")
            return
        repo_path = REPO_DIR / args.name
        if not repo_path.exists():
            print("❌ Repository not found.")
            return
        count = 0
        for folder in PROFILE_FOLDERS:
            for rel, p in {
                str(p.relative_to(repo_path / folder)): p
                for p in (repo_path / folder).rglob("*") if p.is_file() and p.suffix in PROFILE_EXTENSIONS
            }.items():
                dst = ORCA_USER_PATH / folder / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dst)
                installed['installed'].append({
                    'repo': args.name, 'folder': folder, 'profile': rel
                })
                print(f"{GREEN}Installed: {folder}/{rel}{RESET}")
                count += 1
        save_installed(installed)
        print(f"✅ Installed {count} profiles.")
        return

    if args.action == "uninstall":
        if not args.name or not args.profile:
            print("--name and --profile are required to uninstall a profile")
            return
        rem = []
        removed = False
        for e in installed['installed']:
            if e['repo']==args.name and e['profile']==args.profile:
                path = ORCA_USER_PATH / e['folder'] / e['profile']
                if path.exists(): path.unlink()
                removed = True
            else:
                rem.append(e)
        if removed:
            save_installed({'installed': rem})
            print(f"✅ Uninstalled: {args.profile}")
        else:
            print("❌ Profile not found in installed list.")
        return

    if args.action == "move":
        if not all([args.name, args.folder, args.profile, args.target]):
            print("--name, --folder, --profile, and --target are required to move a profile")
            return
        src = REPO_DIR / args.name / args.folder / args.profile
        dst = REPO_DIR / args.name / args.folder / args.target
        if not src.exists():
            print("❌ Source profile not found.")
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        print(f"✅ Moved {args.profile} to {args.target}")
        return

    print("Unknown action. Use --help.")
