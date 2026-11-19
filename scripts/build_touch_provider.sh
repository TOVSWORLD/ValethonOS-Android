#!/usr/bin/env bash
# Source build only; retains the observed display path and adds builtin Goodix.
set -euo pipefail
export VALETHON_TOUCH_BUILD=1
bash scripts/build_display_provider.sh
