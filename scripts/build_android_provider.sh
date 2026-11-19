#!/usr/bin/env bash
# Integrated Android kernel source build. No boot container, install or device test.
set -euo pipefail
if [[ "${1:-}" = --reuse-graphics ]]; then
  python3 - <<'CHECK_PARENT'
from pathlib import Path
import hashlib,json
r=Path('work/ack-baseline');p=r/'android-parent.config'
report=json.loads((r/'display-build-result.json').read_text())
assert hashlib.sha256(p.read_bytes()).hexdigest()==report['artifacts']['.config']['sha256']
(r/'output/.config').write_bytes(p.read_bytes())
CHECK_PARENT
else
  bash scripts/build_graphics_provider.sh
fi
readonly root="$PWD/work/ack-baseline"
readonly output="$root/output"
python3 scripts/apply_android_fuse_guard.py "$root/source" --report "$root/android-fuse-source-fix.json"
cp "$output/.config" "$root/android-parent.config"
python3 - <<'PARENT_IMAGE'
from pathlib import Path
import json
r=Path('work/ack-baseline')
report=json.loads((r/'display-build-result.json').read_text())
(r/'android-parent-image.sha256').write_text(report['artifacts']['arch/arm64/boot/Image']['sha256']+'  graphics-parent-Image\n')
PARENT_IMAGE
while IFS= read -r line; do
  [[ "$line" = CONFIG_*=y ]] || continue
  symbol="${line#CONFIG_}"; symbol="${symbol%=y}"
  "$root/source/scripts/config" --file "$output/.config" --enable "$symbol"
done < <(cat projects/firetabs-android/android-integration/kernel.fragment projects/firetabs-android/android-integration/kernel-apex.fragment)
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 olddefconfig
python3 scripts/check_android_kernel_delta.py --parent "$root/android-parent.config" --result "$output/.config" --output "$root/android-config-delta.json"
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$(nproc)" Image vmlinux
gzip -n -9 -c "$output/arch/arm64/boot/Image" > "$output/arch/arm64/boot/Image.gz"
python3 scripts/measure_arm64_image.py --image "$output/arch/arm64/boot/Image" --gzip "$output/arch/arm64/boot/Image.gz" --output "$root/android-image-size-report.json"
python3 - <<'PY'
from pathlib import Path
import hashlib,json
root=Path('work/ack-baseline');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result={'scope':'Integrated Android kernel compile only; no device execution','ack_revision':'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','source_fixes':[json.loads((root/'android-fuse-source-fix.json').read_text())],'config_changes':json.loads((root/'android-config-delta.json').read_text()),'size':json.loads((root/'android-image-size-report.json').read_text()),'hardware_execution':False,'android_boot_qualified':False,'artifacts':{n:{'bytes':(root/'output'/n).stat().st_size,'sha256':sha(root/'output'/n)} for n in ['arch/arm64/boot/Image','arch/arm64/boot/Image.gz','.config','System.map']}}
(root/'android-build-result.json').write_text(json.dumps(result,indent=2)+'\n')
print('Integrated Android kernel source compilation complete; runtime unqualified.')
PY
