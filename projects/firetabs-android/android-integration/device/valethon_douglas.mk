LOCAL_PATH := device/valethon/douglas
$(call inherit-product, $(SRC_TARGET_DIR)/product/aosp_base.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/go_defaults.mk)
$(call inherit-product, vendor/valethon/graphics/graphics-product.mk)

PRODUCT_NAME := valethon_douglas
PRODUCT_DEVICE := douglas
PRODUCT_BRAND := Valethon
PRODUCT_MODEL := Valethon Douglas Engineering
PRODUCT_MANUFACTURER := Valethon
PRODUCT_CHARACTERISTICS := tablet
PRODUCT_USE_DYNAMIC_PARTITIONS := false
PRODUCT_BUILD_SYSTEM_IMAGE := true
PRODUCT_BUILD_RAMDISK_IMAGE := true
PRODUCT_BUILD_BOOT_IMAGE := false
PRODUCT_BUILD_RECOVERY_IMAGE := false
PRODUCT_BUILD_VENDOR_BOOT_IMAGE := false
PRODUCT_BUILD_INIT_BOOT_IMAGE := false
PRODUCT_BUILD_VENDOR_IMAGE := false
PRODUCT_BUILD_PRODUCT_IMAGE := false
PRODUCT_BUILD_SYSTEM_EXT_IMAGE := false
PRODUCT_BUILD_USERDATA_IMAGE := false
PRODUCT_BUILD_CACHE_IMAGE := false

# Android boot container is assembled separately using the qualified LK path.
# Original recovery is never replaced by this product.
# Device adbd is provided by the inherited com.android.adbd APEX.
PRODUCT_PACKAGES += Launcher3QuickStep Provision
# Do not rely on the absent optional frameworks/webview/chromium/chromium.mk.
# external/chromium-webview supplies the pinned ARM32 provider and required JNI.
# These ordinary apps have no new boot service, privileged grant or device-owner role.
PRODUCT_PACKAGES += \
    webview \
    Browser2 \
    LatinIME \
    Settings \
    DocumentsUI \
    DownloadProvider \
    DownloadProviderUi \
    PackageInstaller \
    CertInstaller \
    ValethonReadiness
PRODUCT_VENDOR_PROPERTIES += \
    ro.hardware=douglas \
    ro.sf.lcd_density=160 \
    ro.opengles.version=131072 \
    ro.zygote=zygote32 \
    debug.hwui.renderer=skiagl \
    debug.renderengine.backend=skiaglthreaded

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/media/bootanimation.zip:$(TARGET_COPY_OUT_SYSTEM)/media/bootanimation.zip \
    $(LOCAL_PATH)/init/fstab.douglas:$(TARGET_COPY_OUT_RAMDISK)/fstab.douglas \
    $(LOCAL_PATH)/init/fstab.douglas:$(TARGET_COPY_OUT_VENDOR)/etc/fstab.douglas \
    $(LOCAL_PATH)/init/init.douglas.rc:$(TARGET_COPY_OUT_VENDOR)/etc/init/hw/init.douglas.rc \
    $(LOCAL_PATH)/init/ueventd.douglas.rc:$(TARGET_COPY_OUT_VENDOR)/etc/ueventd.rc
