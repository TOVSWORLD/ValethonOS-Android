# Valethon intercom-derived boot animation

Uses the owner's exact Valethon G3 Intercom background, found through the ChatGPT
chat **Valethon G3 Background Design** and its matching downloaded PNG. The
source artwork is retained as intercom-background.png, with hashes/derivation in
artwork-source.json. Canonical Valethon brand/brand_bible and brand/tokens specify
white knockout on dark surfaces, optional #1FB6FF accents, unchanged logo geometry
and clearspace. The artwork's existing white/blue logo and lettering are preserved;
no replacement symbol or font is generated. The earlier improvised V is superseded.

The circuit field reveals upwards, then the real mark/name fade into place;
a subtle blue activity sequence loops in the empty header. No percentage or
claimed milestone timing is invented. First reveal: 1.5 seconds at 24 fps;
activity cycle: one second. Both Android `p` parts are interruptible when boot
finishes. No custom service, sound, minimum playback time or diagnostic dependency.
The animation begins after Android graphics starts, not during LK/early kernel.

60 RGB frames at 300x512 preserve the portrait aspect ratio while bounding decoded
RGBA frame payload at about 35.2 MiB (actual GL/process overhead and scaling still
need runtime measurement). Archive about 10.3 MiB; source raster is the high-quality
CoreGraphics downsample of the exact 600x1024 PNG, stored compressed for portable,
standard-library-only generation. The 300x512 render is an engineering tradeoff;
full-panel animation would have substantially larger texture footprint.

Regenerate deterministically:

```
python3 scripts/build_bootanimation.py --output projects/firetabs-android/android-integration/branding/bootanimation.zip
```

stage_android_product.py regenerates this from hash-checked source artwork into
the device media directory; the generated ZIP is not checked into Git. The product
copies it to /system/media/bootanimation.zip. This is source/package integration,
not a full Android build or tablet playback pass. Include image/memory fit and
actual animation playback in the shared integrated test, without another boot.

Format: https://github.com/aosp-mirror/platform_frameworks_base/blob/master/cmds/bootanimation/FORMAT.md
