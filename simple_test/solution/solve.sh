#!/bin/bash

set -euo pipefail

python - <<'PY'
from pathlib import Path

p = Path("/app/main.py")
text = p.read_text(encoding="utf-8")
if "import datetime" not in text:
    text = "import datetime\n" + text
p.write_text(text, encoding="utf-8")
PY