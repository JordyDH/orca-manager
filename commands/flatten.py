import json
from pathlib import Path
import sys
import orca  # Main CLI loader with run_command()
from textwrap import wrap

def build_global_name_index(orca_root: Path):
    """Index all JSON files under ORCA_PATH by their internal 'name' value."""
    name_map = {}
    for file in orca_root.rglob("*.json"):
        try:
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                profile_name = data.get("name")
                if profile_name:
                    name_map[profile_name] = file
        except Exception as e:
            print(f"⚠️ Failed to parse {file}: {e}")
    return name_map

def load_profiles_in_folder(folder: Path):
    profiles = {}
    for file in folder.rglob("*.json"):
        try:
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                profiles[file.name] = data
        except Exception as e:
            print(f"⚠️ Could not load {file.name}: {e}")
    return profiles

def flatten_inherited_profiles(name_map, profiles):
    flattened_results = {}
    summary = []

    for filename, profile in profiles.items():
        if "inherits" not in profile or not profile["inherits"].strip():
            continue

        inherits_from = profile["inherits"]
        base_file = name_map.get(inherits_from)

        if not base_file or not base_file.exists():
            print(f"⚠️ Skipping {filename}, base profile not found: {inherits_from}")
            continue

        try:
            with base_file.open("r", encoding="utf-8") as bf:
                base_data = json.load(bf)
        except Exception as e:
            print(f"⚠️ Cannot read inherited base {base_file}: {e}")
            continue

        flattened = base_data.copy()
        flattened.update(profile)
        flattened.pop("inherits", None)

        flattened_results[filename] = flattened

        added_keys = set(base_data.keys()) - set(profile.keys())
        summary.append({
            "target": filename,
            "inherits_from": inherits_from,
            "added_keys": sorted(added_keys)
        })

    return summary, flattened_results

def register(subparsers):
    subparsers.add_parser("flatten", help="Make inherited profiles standalone in OrcaSlicer")

def run(args):
    print("🔧 Flatten OrcaSlicer Profiles")
    print("Available types: filament, machine, process")
    profile_type = input("Select profile type to flatten: ").strip().lower()

    if profile_type not in PROFILE_FOLDERS:
        print("❌ Invalid profile type selected.")
        return

    # Build global name → file index from all of ORCA_PATH
    name_index = build_global_name_index(orca.ORCA_PATH)

    # Load only profiles of the selected type (user folder only)
    target_folder = ORCA_USER_PATH / profile_type
    profiles = load_profiles_in_folder(target_folder)

    # Identify flattenable profiles
    summary, results = flatten_inherited_profiles(name_index, profiles)

    if not summary:
        print(f"✅ No inherited {profile_type} profiles found. Nothing to flatten.")
        return

    print(f"\nThe following {profile_type} profiles will be flattened directly in OrcaSlicer:\n")
    for item in summary:
        print(f"- {item['target']} (inherits: {item['inherits_from']})")
        if item['added_keys']:
            print("  + Will include keys:")
            for line in wrap(", ".join(item['added_keys']), width=80):
                print(f"    {line}")

    confirm = input("\nProceed with flattening and overwrite Orca files? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Aborted.")
        return

    # Backup all profiles before flattening
    orca.run_command("backup")

    # Write flattened profiles back to original user folder
    for filename, data in results.items():
        file_path = target_folder / filename
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    print(f"\n✅ Flattening complete for {profile_type} profiles.")
