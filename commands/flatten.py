import json
from pathlib import Path
import sys
import orca  # Main CLI loader with run_command()

def build_name_index(filament_dir):
    name_map = {}
    profiles = {}

    for file in filament_dir.rglob("*.json"):
        try:
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                name = data.get("name")
                if name:
                    name_map[name] = file
                    profiles[file.name] = data
        except Exception as e:
            print(f"⚠️ Failed to read {file.name}: {e}")
    return name_map, profiles

def flatten_inherited_profiles(name_map, profiles, filament_dir):
    flattened_results = {}
    summary = []

    for filename, profile in profiles.items():
        if "inherits" not in profile:
            continue

        inherits_from = profile["inherits"]
        base_file = name_map.get(inherits_from)

        if not base_file or not base_file.exists():
            print(f"⚠️ Skipping {filename}, base profile not found: {inherits_from}")
            continue

        with base_file.open("r", encoding="utf-8") as bf:
            base_data = json.load(bf)

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
    subparsers.add_parser("flatten", help="Make all inherited filament profiles standalone in OrcaSlicer")

def run(args):
    filament_dir = ORCA_USER_PATH / "filament"
    name_index, profiles = build_name_index(filament_dir)

    summary, results = flatten_inherited_profiles(name_index, profiles, filament_dir)

    if not summary:
        print("✅ No inherited profiles found. Nothing to flatten.")
        return

    print("\nThe following profiles will be flattened directly in OrcaSlicer:\n")
    for item in summary:
        print(f"- {item['target']} (inherits: {item['inherits_from']})")
        if item['added_keys']:
            print(f"  + Will include keys: {', '.join(item['added_keys'])}")

    confirm = input("\nProceed with flattening and overwrite Orca files? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Aborted.")
        return

    # Backup Orca files first
    orca.run_command("backup")

    # Write flattened profiles directly into Orca user dir
    for filename, data in results.items():
        file_path = filament_dir / filename
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    print("\n✅ Flattening complete. All files written directly to OrcaSlicer.")
