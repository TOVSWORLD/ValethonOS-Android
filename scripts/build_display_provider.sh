#!/usr/bin/env bash
# Full source build only. No DT enabling, firmware packing, install or device test.
set -euo pipefail
[[ "${ARGUMENT_PROFILE:-none}" = none ]] || exit 2
bash scripts/build_ack_baseline.sh first-draft
readonly root="$PWD/work/ack-baseline"
readonly output="$root/output"
python3 scripts/apply_display_port.py "$root/source"
python3 scripts/install_douglas_tpv_panel.py "$root/source"
for symbol in DRM_PANEL_AMAZON_DOUGLAS_TPV BACKLIGHT_CLASS_DEVICE BACKLIGHT_PWM BACKLIGHT_LP855X I2C_MT65XX FRAMEBUFFER_CONSOLE VT VT_CONSOLE LOGO LOGO_LINUX_CLUT224 FONT_8x16; do
  "$root/source/scripts/config" --file "$output/.config" --enable "$symbol"
done
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 olddefconfig
for symbol in DRM_MEDIATEK DRM_PANEL_AMAZON_DOUGLAS_TPV BACKLIGHT_PWM BACKLIGHT_LP855X I2C_MT65XX FRAMEBUFFER_CONSOLE VT_CONSOLE; do
  grep -qx "CONFIG_${symbol}=y" "$output/.config"
done
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$(nproc)" W=1 \
  drivers/gpu/drm/mediatek/mtk_drm_drv.o drivers/gpu/drm/mediatek/mtk_disp_gamma.o \
  drivers/soc/mediatek/mtk-mutex.o drivers/gpu/drm/panel/panel-amazon-douglas-tpv.o \
  drivers/video/backlight/lp855x_bl.o drivers/video/backlight/pwm_bl.o
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$(nproc)" Image vmlinux
gzip -n -9 -c "$output/arch/arm64/boot/Image" > "$output/arch/arm64/boot/Image.gz"
python3 scripts/measure_arm64_image.py --image "$output/arch/arm64/boot/Image" --gzip "$output/arch/arm64/boot/Image.gz" --output "$root/display-image-size-report.json"
python3 - <<'PY'
from pathlib import Path
import hashlib,json
root=Path('work/ack-baseline');output=root/'output';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
artifacts=['arch/arm64/boot/Image','vmlinux','System.map','.config','drivers/gpu/drm/mediatek/mtk_drm_drv.o','drivers/gpu/drm/mediatek/mtk_disp_gamma.o','drivers/soc/mediatek/mtk-mutex.o','drivers/gpu/drm/panel/panel-amazon-douglas-tpv.o','drivers/video/backlight/lp855x_bl.o','drivers/video/backlight/pwm_bl.o']
result={'scope':'Full maintained kernel with MT8163 display pipeline and TPV panel/display-PWM backlight support; no hardware qualification','ack_revision':'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','hardware_execution':False,'display_dt_enabled':False,'physical_execution_admitted':False,'artifacts':{n:{'bytes':(output/n).stat().st_size,'sha256':sha(output/n)} for n in artifacts}}
(root/'display-build-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
PY
echo MT8163_DISPLAY_PROVIDER_IMAGE_COMPLETE_RUNTIME_UNQUALIFIED
