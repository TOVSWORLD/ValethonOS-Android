#!/usr/bin/env bash
# Incremental console-only build from the completed Android kernel output.
set -euo pipefail
readonly source_tree="$1"
readonly parent_output="$2"
readonly output_dir="$3"
test ! -e "$output_dir"
cp -a --reflink=auto "$parent_output" "$output_dir"
cp "$output_dir/.config" "$output_dir/../early-console-parent.config"
for symbol in U_SERIAL_CONSOLE USB_G_SERIAL; do
 "$source_tree/scripts/config" --file "$output_dir/.config" --enable "$symbol"
done
make -C "$source_tree" O="$output_dir" ARCH=arm64 LLVM=-18 olddefconfig
python3 - "$output_dir/../early-console-parent.config" "$output_dir/.config" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0,'scripts')
from prepare_android_early_capture import config_values
before,after=[config_values(Path(p).read_bytes()) for p in sys.argv[1:]]
delta={k for k in set(before)|set(after) if before.get(k)!=after.get(k)}
assert delta<={'CONFIG_U_SERIAL_CONSOLE','CONFIG_USB_G_SERIAL','CONFIG_USB_F_SERIAL','CONFIG_USB_F_OBEX'},delta
assert all(after.get(k)=='y' for k in ['CONFIG_U_SERIAL_CONSOLE','CONFIG_USB_G_SERIAL','CONFIG_PSTORE_RAM','CONFIG_PSTORE_CONSOLE'])
PY
make -C "$source_tree" O="$output_dir" ARCH=arm64 LLVM=-18 -j2 Image vmlinux
gzip -n -9 -c "$output_dir/arch/arm64/boot/Image" > "$output_dir/arch/arm64/boot/Image.gz"
