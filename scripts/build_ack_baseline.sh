#!/usr/bin/env bash
# Generic compile diagnostic only; does not produce douglas firmware.
set -euo pipefail
readonly revision=d9318bdb4c34e8b2d997b4f67ced56b120b22b87
readonly requested_mode="${1:-generic}"
readonly mode="${requested_mode/lab-retained/lab-log}"
retained_args=()
if [ "$requested_mode" = lab-retained ]; then retained_args=(--retained-mailbox); fi
[[ "$mode" = generic || "$mode" = clocks || "$mode" = clocks-pinctrl || "$mode" = providers || "$mode" = usb-providers || "$mode" = usb-acm-diagnostic || "$mode" = lab-log || "$mode" = diagnostic ]] || exit 2
readonly argument_profile="${ARGUMENT_PROFILE:-none}"
[[ "$argument_profile" = none || "$argument_profile" = generic-force ]] || exit 2
[[ "$argument_profile" = none || "$mode" = diagnostic ]] || exit 2
readonly root="$PWD/work/ack-baseline"
[ "$(uname -s)" = Linux ] || { echo 'A Linux build host is required'; exit 2; }
for tool in git make clang-18 ld.lld-18 llvm-ar-18 bison flex bc openssl pahole; do
  command -v "$tool" || exit 2
done
free -h
df -h .
[ "$(df -Pk . | awk 'END {print $4}')" -ge 15728640 ] || { echo 'Need 15 GiB free'; exit 2; }
[ "$(awk '/MemTotal:/ {print $2}' /proc/meminfo)" -ge 7340032 ] || { echo 'Need 7 GiB RAM'; exit 2; }
mkdir -p "$root"
[ ! -e "$root/source" ] || { echo 'Refusing to overwrite an existing checkout'; exit 2; }
git init "$root/source"
git -C "$root/source" remote add origin https://android.googlesource.com/kernel/common
# A shallow single revision fetch; no tags or full history. Budget is checked
# after transfer; hosted runner timeout also bounds stalled network/build work.
git -C "$root/source" -c http.lowSpeedLimit=1024 -c http.lowSpeedTime=120 fetch --depth=1 --no-tags origin "$revision"
[ "$(du -sk "$root/source/.git" | awk '{print $1}')" -le 3145728 ] || { echo 'Fetch exceeded 3 GiB budget'; exit 2; }
echo "Fetched Git storage (KiB): $(du -sk "$root/source/.git" | awk '{print $1}')"
git -C "$root/source" checkout --detach FETCH_HEAD
echo "Expanded source (KiB): $(du -sk "$root/source" | awk '{print $1}')"
[ "$(git -C "$root/source" rev-parse HEAD)" = "$revision" ]
clang-18 --version
ld.lld-18 --version
make --version | head -1
readonly output="$root/output"
readonly jobs="$(nproc)"
# Start from the reproducible generic ARM64 baseline; diagnostic mode applies
# an explicit restricted fragment. Neither is a qualified Android/board config.
if [ "$mode" != generic ]; then
  python3 scripts/apply_clock_port.py "$root/source"
  if [[ "$mode" = clocks-pinctrl || "$mode" = providers || "$mode" = usb-providers || "$mode" = usb-acm-diagnostic || "$mode" = lab-log || "$mode" = diagnostic ]]; then
    python3 scripts/apply_pinctrl_port.py "$root/source"
  fi
  if [[ "$mode" = providers || "$mode" = usb-providers || "$mode" = usb-acm-diagnostic || "$mode" = lab-log || "$mode" = diagnostic ]]; then
    python3 scripts/apply_power_port.py "$root/source"
    python3 scripts/apply_iommu_port.py "$root/source"
    if [[ "$mode" = usb-providers || "$mode" = usb-acm-diagnostic || "$mode" = lab-log ]]; then python3 scripts/apply_usb_port.py "$root/source"; fi
  fi
fi
if [ "$mode" = lab-log ]; then
  python3 scripts/apply_lab_watchdog.py "$root/source"
  python3 scripts/apply_lab_entry_screen.py "$root/source"
  if [ "$requested_mode" = lab-retained ]; then python3 scripts/apply_lab_retained.py "$root/source"; fi
fi
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 defconfig
if [ "$mode" != generic ]; then
  # ACK forbids a built-in MMSYS with modular CMDQ. Keep this generic parent
  # compile isolated from command-queue operation rather than enabling that I/O.
  "$root/source/scripts/config" --file "$output/.config" --disable MTK_CMDQ
  for symbol in MTK_MMSYS COMMON_CLK_MT8163 COMMON_CLK_MT8163_AUDSYS COMMON_CLK_MT8163_IMGSYS COMMON_CLK_MT8163_MFGCFG COMMON_CLK_MT8163_MMSYS COMMON_CLK_MT8163_VDECSYS COMMON_CLK_MT8163_VENCSYS; do
    "$root/source/scripts/config" --file "$output/.config" --enable "$symbol"
  done
  if [[ "$mode" = clocks-pinctrl || "$mode" = providers || "$mode" = usb-providers || "$mode" = usb-acm-diagnostic || "$mode" = lab-log || "$mode" = diagnostic ]]; then
    "$root/source/scripts/config" --file "$output/.config" --enable PINCTRL_MT8163
  fi
  if [[ "$mode" = providers || "$mode" = usb-providers || "$mode" = usb-acm-diagnostic || "$mode" = lab-log || "$mode" = diagnostic ]]; then
    for symbol in MTK_PMIC_WRAP MTK_SCPSYS_PM_DOMAINS MTK_IOMMU MTK_SMI; do
      "$root/source/scripts/config" --file "$output/.config" --enable "$symbol"
    done
  fi
  if [[ "$mode" = usb-providers || "$mode" = usb-acm-diagnostic || "$mode" = lab-log ]]; then
    for symbol in USB USB_GADGET USB_PHY NOP_USB_XCEIV USB_MUSB_HDRC USB_MUSB_MEDIATEK USB_MUSB_DUAL_ROLE USB_INVENTRA_DMA PHY_MTK_TPHY; do
      "$root/source/scripts/config" --file "$output/.config" --enable "$symbol"
    done
    "$root/source/scripts/config" --file "$output/.config" --disable USB_MUSB_HOST --disable USB_MUSB_GADGET --disable MUSB_PIO_ONLY
  fi
  if [ "$mode" = diagnostic ]; then
    python3 scripts/diagnostic_config.py apply "$output/.config" --source "$root/source"
    if [ "$argument_profile" = generic-force ]; then
      python3 scripts/check_diagnostic_commandline.py "$output/.config" --apply --source "$root/source" --profile generic-force
    fi
  fi
  if [[ "$mode" = usb-acm-diagnostic || "$mode" = lab-log ]]; then
    python3 scripts/usb_acm_config.py apply "$output/.config" --source "$root/source"
  fi
  if [ "$mode" = lab-log ]; then
    python3 scripts/lab_log_config.py apply "$output/.config" --source "$root/source" "${retained_args[@]}"
  fi
  make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 olddefconfig
  if [ "$argument_profile" = generic-force ]; then
    python3 scripts/check_diagnostic_commandline.py "$output/.config" --profile generic-force
  fi
  if [ "$mode" = diagnostic ]; then
    if ! python3 scripts/diagnostic_config.py check "$output/.config"; then
      cat "$output/.config" # Retain rejected resolved config in logs.
      exit 1
    fi
  fi
  if [[ "$mode" = usb-acm-diagnostic || "$mode" = lab-log ]]; then
    if ! python3 scripts/usb_acm_config.py check "$output/.config"; then
      cat "$output/.config"
      exit 1
    fi
  fi
  if [ "$mode" = lab-log ]; then
    python3 scripts/lab_log_config.py check "$output/.config" "${retained_args[@]}"
  fi
  for symbol in MTK_MMSYS COMMON_CLK_MT8163 COMMON_CLK_MT8163_AUDSYS COMMON_CLK_MT8163_IMGSYS COMMON_CLK_MT8163_MFGCFG COMMON_CLK_MT8163_MMSYS COMMON_CLK_MT8163_VDECSYS COMMON_CLK_MT8163_VENCSYS; do
    grep -qx "CONFIG_${symbol}=y" "$output/.config"
  done
  grep -qx "# CONFIG_MTK_CMDQ is not set" "$output/.config"
  make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$jobs" W=1 drivers/clk/mediatek/
  make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$jobs" W=1 drivers/soc/mediatek/mtk-mmsys.o
  echo MT8163_MMSYS_PARENT_OBJECT_COMPILE_COMPLETE
  echo MT8163_CLOCK_OBJECT_COMPILE_COMPLETE
  if [[ "$mode" = clocks-pinctrl || "$mode" = providers || "$mode" = usb-providers || "$mode" = usb-acm-diagnostic || "$mode" = lab-log || "$mode" = diagnostic ]]; then
    grep -qx CONFIG_PINCTRL_MT8163=y "$output/.config"
    make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$jobs" W=1 drivers/pinctrl/mediatek/
    echo MT8163_PINCTRL_OBJECT_COMPILE_COMPLETE
  fi
  if [[ "$mode" = providers || "$mode" = usb-providers || "$mode" = usb-acm-diagnostic || "$mode" = lab-log || "$mode" = diagnostic ]]; then
    for symbol in MTK_PMIC_WRAP MTK_SCPSYS_PM_DOMAINS MTK_IOMMU MTK_SMI; do grep -qx "CONFIG_${symbol}=y" "$output/.config"; done
    make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$jobs" W=1 drivers/soc/mediatek/mtk-pmic-wrap.o drivers/pmdomain/mediatek/mtk-pm-domains.o
    echo MT8163_POWER_OBJECT_COMPILE_COMPLETE
    make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$jobs" W=1 drivers/iommu/mtk_iommu.o drivers/memory/mtk-smi.o
    sha256sum "$output/drivers/iommu/mtk_iommu.o" "$output/drivers/memory/mtk-smi.o"
    echo MT8163_IOMMU_SMI_OBJECT_COMPILE_COMPLETE
  fi
  if [[ "$mode" = usb-providers || "$mode" = usb-acm-diagnostic || "$mode" = lab-log ]]; then
    for symbol in USB USB_GADGET USB_PHY NOP_USB_XCEIV USB_MUSB_HDRC USB_MUSB_MEDIATEK USB_MUSB_DUAL_ROLE USB_INVENTRA_DMA PHY_MTK_TPHY; do
      grep -qx "CONFIG_${symbol}=y" "$output/.config"
    done
    make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$jobs" W=1 drivers/usb/musb/mediatek.o drivers/phy/mediatek/phy-mtk-tphy.o
    sha256sum "$output/drivers/usb/musb/mediatek.o" "$output/drivers/phy/mediatek/phy-mtk-tphy.o"
    grep -qx '# CONFIG_MUSB_PIO_ONLY is not set' "$output/.config"
    echo MT8163_USB_PROVIDER_OBJECT_COMPILE_COMPLETE
    if [[ "$mode" = usb-acm-diagnostic || "$mode" = lab-log ]]; then
      # Builtin composites are flattened; probe their actual translation units.
      acm_targets="$(python3 scripts/usb_acm_config.py objects)"
      readarray -t acm_objects <<< "$acm_targets"
      make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$jobs" W=1 "${acm_objects[@]}"
      for object in "${acm_objects[@]}"; do sha256sum "$output/$object"; done
      echo USB_ACM_BUILTIN_OBJECT_COMPILE_COMPLETE
    fi
  fi
fi
if [ "$mode" = lab-log ]; then
  make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$jobs" W=1 drivers/watchdog/mtk_wdt.o drivers/watchdog/watchdog_dev.o
  sha256sum "$output/drivers/watchdog/mtk_wdt.o" "$output/drivers/watchdog/watchdog_dev.o"
  echo LAB_BOOT_WATCHDOG_OBJECT_COMPILE_COMPLETE
fi
if [ "$requested_mode" = lab-retained ]; then
  make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$jobs" W=1 drivers/misc/valethon_mailbox.o drivers/mmc/host/mtk-sd.o
  sha256sum "$output/drivers/misc/valethon_mailbox.o" "$output/drivers/mmc/host/mtk-sd.o"
  echo LAB_RETAINED_MAILBOX_EMMC_OBJECT_COMPILE_COMPLETE
fi
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$jobs" Image vmlinux
if [[ "$mode" = diagnostic || "$mode" = lab-log ]]; then
  gzip -n -9 -c "$output/arch/arm64/boot/Image" > "$output/arch/arm64/boot/Image.gz"
  python3 scripts/measure_arm64_image.py --image "$output/arch/arm64/boot/Image" --gzip "$output/arch/arm64/boot/Image.gz" --output "$root/image-size-report.json"
  if [ "$mode" = lab-log ]; then
    python3 -c 'import json; r=json.load(open("work/ack-baseline/image-size-report.json")); assert r["decoded_file_fits_lk_capacity"], "Image exceeds exact selected loader capacity"'
  fi
  sha256sum "$output/arch/arm64/boot/Image.gz"
  wc -c "$output/arch/arm64/boot/Image.gz"
fi
file "$output/vmlinux" "$output/arch/arm64/boot/Image"
llvm-readelf-18 -h "$output/vmlinux"
sha256sum "$output/.config" "$output/vmlinux" "$output/arch/arm64/boot/Image"
wc -c "$output/vmlinux" "$output/arch/arm64/boot/Image"
grep -E '^CONFIG_(ARM64|ARM64_4K_PAGES|COMPAT|ARCH_MEDIATEK|SECURITY_SELINUX|BPF_SYSCALL|ANDROID_BINDER_IPC)=' "$output/.config"
# Emit complete resolved configuration in CI logs for this first experiment.
cat "$output/.config"
echo "ARM64_COMPILE_COMPLETE mode=$mode; DOUGLAS_BOOT_UNTESTED"
