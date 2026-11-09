#!/usr/bin/env python3
"""Screenshot of a built page for checking the design: preview.py <path> <width> <height> <out.png>.
Rewrites the site's absolute links to local files, so the page renders without a web server."""
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SNAP = os.path.expanduser("~/Documents/StoreScreenshots HowlNight/tools/snap")

path, width, height, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
source = open(os.path.join(ROOT, path.strip("/"), "index.html") if not path.endswith(".html") else os.path.join(ROOT, path.strip("/"))).read()
local = (source.replace('src="/', f'src="file://{ROOT}/').replace('srcset="/', f'srcset="file://{ROOT}/')
         .replace('href="/', f'href="file://{ROOT}/').replace(' loading="lazy"', ''))
tmp = "/tmp/jl-preview.html"
open(tmp, "w").write(local)
subprocess.run([SNAP, tmp, width, height, out], check=True)
