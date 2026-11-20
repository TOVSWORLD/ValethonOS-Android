# ARM32 userspace on the physically qualified arm64 maintained kernel.
TARGET_ARCH := arm
# Cortex-A53 uses the ARMv8 instruction set in 32-bit execution mode.
TARGET_ARCH_VARIANT := armv8-a
TARGET_CPU_VARIANT := cortex-a53
TARGET_CPU_ABI := armeabi-v7a
TARGET_BOARD_PLATFORM := mt8163
TARGET_BOOTLOADER_BOARD_NAME := douglas
TARGET_NO_BOOTLOADER := true
TARGET_NO_KERNEL := true
TARGET_NO_RECOVERY := true

# Existing p14, from observed-partitions.json. No repartitioning or super image.
TARGET_USERIMAGES_USE_EXT4 := true
BOARD_SYSTEMIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_SYSTEMIMAGE_PARTITION_SIZE := 1692925952
BOARD_SYSTEMIMAGE_PARTITION_RESERVED_SIZE := 16777216
TARGET_COPY_OUT_VENDOR := system/vendor
TARGET_COPY_OUT_PRODUCT := system/product
TARGET_COPY_OUT_SYSTEM_EXT := system/system_ext
BOARD_AVB_ENABLE := false
BOARD_SEPOLICY_DIRS += device/valethon/douglas/sepolicy
DEVICE_MANIFEST_FILE := device/valethon/douglas/manifest.xml
