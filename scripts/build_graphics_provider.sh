#!/usr/bin/env bash
# Source build only. Keep the observed display/touch path; add builtin Panfrost.
set -euo pipefail
export VALETHON_TOUCH_BUILD=1
export VALETHON_GPU_BUILD=1
bash scripts/build_display_provider.sh
