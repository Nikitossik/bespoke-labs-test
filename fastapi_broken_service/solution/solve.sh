#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$SCRIPT_DIR/01_fix_models.sh"
bash "$SCRIPT_DIR/02_fix_main.sh"
bash "$SCRIPT_DIR/03_reset_db.sh"