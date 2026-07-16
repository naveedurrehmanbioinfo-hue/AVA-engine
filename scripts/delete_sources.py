"""Delete knowledge-base sources matching a title substring (or an exact
list of IDs), against the running app's /api/sources + /api/sources/{id}.

Usage:
  # preview what would be deleted (no changes made)
  python3 scripts/delete_sources.py <base_url> --title "aiag_website.md"

  # actually delete
  python3 scripts/delete_sources.py <base_url> --title "aiag_website.md" --yes

  # delete an explicit list of IDs from a JSON file (a JSON array of id strings)
  python3 scripts/delete_sources.py <base_url> --ids-file ids.json --yes

Example:
  python3 scripts/delete_sources.py https://ava-engine.vercel.app --title "aiag_website.md" --yes
"""
import argparse
import json
import sys

import requests

parser = argparse.ArgumentParser()
parser.add_argument("base_url")
parser.add_argument("--title", help="substring match against source title (case-insensitive)")
parser.add_argument("--ids-file", help="JSON file containing a list of source IDs to delete")
parser.add_argument("--yes", action="store_true", help="actually delete (default is dry-run preview)")
args = parser.parse_args()

BASE = args.base_url.rstrip("/")

if not args.title and not args.ids_file:
    sys.exit("provide --title or --ids-file")

if args.ids_file:
    with open(args.ids_file) as f:
        ids = json.load(f)
    targets = [{"id": i, "title": "(from ids-file)"} for i in ids]
else:
    sources = requests.get(f"{BASE}/api/sources", timeout=30).json()
    needle = args.title.lower()
    targets = [s for s in sources if needle in s.get("title", "").lower()]

print(f"{len(targets)} source(s) match:")
for t in targets:
    print(" -", t["id"], t.get("title"))

if not args.yes:
    print("\nDry run only. Re-run with --yes to actually delete.")
    sys.exit(0)

ok = 0
for t in targets:
    r = requests.delete(f"{BASE}/api/sources/{t['id']}", timeout=30)
    if r.status_code == 200:
        ok += 1
    else:
        print("FAIL", t["id"], r.status_code, r.text[:150])
print(f"\ndeleted {ok}/{len(targets)}")
