import subprocess
from pathlib import Path

def register(subparsers):
    parser = subparsers.add_parser("git", help="Run Git operations on the orca_profiles repo")
    parser.add_argument("action", choices=["status", "fetch", "pull", "push", "commit", "rebase", "branch", "checkout"],
                        help="Git action to perform")
    parser.add_argument("-m", "--message", help="Commit message (for commit only)")
    parser.add_argument("-b", "--branch", help="Target branch (for checkout)")

def run(args):
    action = args.action
    repo_path = GIT_ROOT_PATH

    def run_git(cmd_args):
        result = subprocess.run(
            ["git"] + cmd_args,
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("⚠️", result.stderr.strip())

    print(f"🔧 Running git {action} in {repo_path}")

    if action == "status":
        run_git(["status"])
    elif action == "fetch":
        run_git(["fetch"])
    elif action == "pull":
        run_git(["pull"])
    elif action == "push":
        run_git(["push"])
    elif action == "commit":
        if not args.message:
            print("❌ Commit message required. Use: -m 'Your message'")
            return
        run_git(["add", "."])
        run_git(["commit", "-a -m", args.message])
    elif action == "rebase":
        run_git(["pull", "--rebase"])
    elif action == "branch":
        run_git(["branch", "-vv"])
    elif action == "checkout":
        if not args.branch:
            print("❌ Branch name required. Use: -b branch-name")
            return
        run_git(["checkout", args.branch])
