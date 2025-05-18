import json
from pathlib import Path

def register(subparsers):
    subparsers.add_parser("validate", help="Validate OrcaSlicer profiles for syntax, structure, and inheritance")

def run(args):
    print("🔍 Validating OrcaSlicer user profile files...\n")
    issues = []

    for profile_type in PROFILE_FOLDERS:
        folder = ORCA_USER_PATH / profile_type
        files = [f for f in folder.rglob("*.json")
                 if any(marker in f.name for marker in MANAGED_PROFILE_MARKERS)]

        if not files:
            print(f"[{profile_type}] ⚠️ No managed profile files found.")
            continue

        print(f"[{profile_type}] Checking {len(files)} managed file(s)...")

        for f in files:
            try:
                with f.open("r", encoding="utf-8") as fp:
                    data = json.load(fp)
            except json.JSONDecodeError as e:
                issues.append((profile_type, f.name, f"Invalid JSON: {str(e)}"))
                continue

            # Basic field checks
            if "name" not in data:
                issues.append((profile_type, f.name, "Missing 'name' field"))

            if profile_type == "filament" and "filament_settings_id" not in data:
                issues.append((profile_type, f.name, "Missing 'filament_settings_id'"))

            if "inherits" in data and data["inherits"].strip():
                issues.append((profile_type, f.name, f"⚠️ Inherits from: {data['inherits']}"))

    # Summary
    if issues:
        print("❌ Issues found:")
        for profile_type, file, msg in issues:
            print(f"- [{profile_type}] {file}: {msg}")
    else:
        print("✅ All managed Orca profiles are valid and standalone.")