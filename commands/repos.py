import json
import subprocess
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent / "orca_repositories"
CONFIG_FILE = REPO_DIR / "orca_repositories.json"

REPO_DIR.mkdir(exist_ok=True)
if not CONFIG_FILE.exists():
    CONFIG_FILE.write_text(json.dumps({"repositories": []}, indent=2))

def load_config():
    with CONFIG_FILE.open("r") as f:
        return json.load(f)

def save_config(data):
    with CONFIG_FILE.open("w") as f:
        json.dump(data, f, indent=2)

def register(subparsers):
    parser = subparsers.add_parser("repos", help="Manage external Orca profile repositories")
    parser.add_argument("action", choices=["add", "list", "remove", "sync"], help="Action to perform")
    parser.add_argument("--name", help="Name of the repository")
    parser.add_argument("--url", help="Git URL of the repository")

def run(args):
    config = load_config()
    repos = config.get("repositories", [])

    if args.action == "list":
        print("Tracked Repositories:")
        for r in repos:
            print(f"- {r['name']}: {r['url']}")

    elif args.action == "add":
        if not args.name or not args.url:
            print("--name and --url are required to add a repository")
            return

        target_path = REPO_DIR / args.name
        if target_path.exists():
            print("❌ Target folder already exists. Choose a different name.")
            return

        print(f"Cloning {args.url} into {target_path}...")
        result = subprocess.run(["git", "clone", args.url, str(target_path)])
        if result.returncode == 0:
            repos.append({"name": args.name, "url": args.url})
            save_config({"repositories": repos})
            print("✅ Repository added.")
        else:
            print("❌ Failed to clone repository.")

    elif args.action == "remove":
        if not args.name:
            print("--name is required to remove a repository")
            return

        updated_repos = [r for r in repos if r["name"] != args.name]
        if len(updated_repos) == len(repos):
            print("❌ Repository not found in config.")
            return

        shutil.rmtree(REPO_DIR / args.name, ignore_errors=True)
        save_config({"repositories": updated_repos})
        print(f"✅ Repository '{args.name}' removed.")

    elif args.action == "sync":
        print("Syncing all repositories...")
        for r in repos:
            path = REPO_DIR / r['name']
            if path.exists():
                print(f"- {r['name']}")
                subprocess.run(["git", "pull"], cwd=path)
            else:
                print(f"⚠️ Missing local folder for {r['name']}")
