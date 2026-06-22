#!/usr/bin/env python3
"""Migrate legacy publication frontmatter to the structured HugoBlox shape.

The `academic import` BibTeX converter writes publication pages in a legacy
frontmatter format that triggers HugoBlox deprecation warnings at build time.
There is currently no `hugoblox migrate publications` command, so run this
script after every BibTeX (re)import to fix:

  1. flat `publication: '*Name*'`  -> `publication: {name: Name}`
  2. top-level `doi: X`            -> `hugoblox: {ids: {doi: X}}`
  3. `url_pdf: X`                  -> `links: [{type: pdf, url: X}]`

Usage:
    python3 scripts/migrate_pubs.py            # dry run (prints what would change)
    python3 scripts/migrate_pubs.py --write    # apply the changes

A real YAML parser is required because some `publication` values wrap across
multiple lines, so naive line/sed edits would corrupt them.
"""
import sys
import pathlib
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBS = REPO_ROOT / "content" / "publications"
WRITE = "--write" in sys.argv


def split_frontmatter(text):
    """Return (frontmatter, body) or (None, None) if no YAML frontmatter."""
    if not text.startswith("---\n"):
        return None, None
    end = text.find("\n---", 4)
    if end == -1:
        return None, None
    return text[4:end + 1], text[end + 4:]


def migrate(meta):
    """Mutate `meta` in place; return a list of human-readable change notes."""
    changes = []

    pub = meta.get("publication")
    if isinstance(pub, str):
        name = pub.strip().strip("*").strip()
        meta["publication"] = {"name": name}
        changes.append(f"publication -> {{name: {name!r}}}")

    if "doi" in meta:
        doi = meta.pop("doi")
        ids = meta.setdefault("hugoblox", {}).setdefault("ids", {})
        ids["doi"] = doi
        changes.append(f"doi -> hugoblox.ids.doi ({doi})")

    if "url_pdf" in meta:
        url = meta.pop("url_pdf")
        links = meta.get("links")
        if not isinstance(links, list):
            links = []
            meta["links"] = links
        links.append({"type": "pdf", "url": url})
        changes.append(f"url_pdf -> links[type=pdf] ({url})")

    return changes


def main():
    if not PUBS.is_dir():
        sys.exit(f"Publications directory not found: {PUBS}")

    total = 0
    for path in sorted(PUBS.glob("*/index.md")):
        text = path.read_text(encoding="utf-8")
        fm, body = split_frontmatter(text)
        if fm is None:
            print(f"SKIP (no frontmatter): {path.parent.name}")
            continue
        meta = yaml.safe_load(fm)
        if meta is None:
            continue
        changes = migrate(meta)
        if not changes:
            continue
        total += 1
        print(f"\n{path.parent.name}:")
        for c in changes:
            print(f"  - {c}")
        if WRITE:
            new_fm = yaml.safe_dump(
                meta, sort_keys=False, allow_unicode=True,
                default_flow_style=False, width=4096,
            )
            path.write_text(f"---\n{new_fm}---\n{body.lstrip(chr(10))}", encoding="utf-8")

    print(f"\n{'WROTE' if WRITE else 'WOULD CHANGE'} {total} files")
    if not WRITE and total:
        print("Re-run with --write to apply.")


if __name__ == "__main__":
    main()
