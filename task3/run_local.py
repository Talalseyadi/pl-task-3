"""Run Lambda-style handler locally against JSON event files."""
import argparse
import json
from pathlib import Path
from handler import handler


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--event", help="Path to a single event JSON file")
    p.add_argument("--all", action="store_true", help="Run all events in ./events")
    args = p.parse_args()

    events_dir = Path("events")

    paths = []
    if args.all:
        if not events_dir.exists():
            print("ERROR: events/ folder not found.")
            return
        paths = sorted([p for p in events_dir.glob("*.json")])
    elif args.event:
        paths = [Path(args.event)]
    else:
        print("Usage: python run_local.py --event events/01_user_signup_valid.json")
        print("   or: python run_local.py --all")
        return

    for path in paths:
        try:
            event = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"--- {path.name} ---")
            print(f"ERROR reading JSON: {e}")
            continue

        print(f"--- {path.name} ---")
        result = handler(event, context={"source": "local"})
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print()

if __name__ == "__main__":
    main()
