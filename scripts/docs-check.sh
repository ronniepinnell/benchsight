#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
import os
import re
import sys

root = "docs"
link_re = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

missing = []
for dirpath, _, filenames in os.walk(root):
    for name in filenames:
        if not name.endswith(".md"):
            continue
        path = os.path.join(dirpath, name)
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        for match in link_re.finditer(text):
            link = match.group(2)
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if "://" in link:
                continue
            link = link.split("#", 1)[0].split("?", 1)[0]
            if not link:
                continue
            if link.startswith("/"):
                target = os.path.join(root, link.lstrip("/"))
            else:
                target = os.path.normpath(os.path.join(os.path.dirname(path), link))
            if not os.path.exists(target):
                missing.append((path, link))

if missing:
    print("Missing links:")
    for path, link in missing:
        print(f"{path}: {link}")
    sys.exit(1)

print("Docs link check passed.")
PY
