import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DEVICE=ROOT/'projects/firetabs-android/android-integration/device'
class DouglasSourceGuard(unittest.TestCase):
 def test_system_capacity_matches_observed_partition_without_new_slots(self):
  observed=json.loads((ROOT/'evidence/douglas-original-route/observed-partitions.json').read_text());size=next(p['bytes'] for p in observed['partitions'] if p['number']==14)
  board=(DEVICE/'BoardConfig.mk').read_text();self.assertRegex(board,rf'BOARD_SYSTEMIMAGE_PARTITION_SIZE := {size}\b')
  self.assertNotIn('BOARD_SUPER_PARTITION_SIZE',board)
 def test_first_home_fstab_never_mounts_original_userdata_or_cache(self):
  rows=[x.split() for x in (DEVICE/'init/fstab.douglas').read_text().splitlines() if x.strip() and not x.startswith('#')]
  self.assertEqual(len(rows),1);self.assertEqual(rows[0][:4],['/dev/block/mmcblk0p14','/system','ext4','ro,barrier=1']);self.assertEqual(rows[0][4],'wait,first_stage_mount')
  init=(DEVICE/'init/init.douglas.rc').read_text();self.assertIn('mount tmpfs tmpfs /data',init);self.assertNotRegex(init,r'\b(format|wipe|mke2fs|mkfs)\b')
 def test_build_does_not_emit_flashable_recovery_or_userdata_images(self):
  product=(DEVICE/'valethon_douglas.mk').read_text()
  for name in ['BOOT','RECOVERY','VENDOR_BOOT','INIT_BOOT','USERDATA','CACHE']:
   self.assertIn('PRODUCT_BUILD_'+name+'_IMAGE := false',product)
 def test_enforcing_and_authenticated_adb_are_not_overridden(self):
  text='\n'.join(p.read_text() for p in DEVICE.rglob('*') if p.is_file() and p.name!='README.md')
  self.assertNotIn('androidboot.selinux=permissive',text);self.assertNotIn('ro.adb.secure=0',text);self.assertNotIn('permissive ',text)
  fragment=(ROOT/'projects/firetabs-android/android-integration/kernel.fragment').read_text();self.assertIn('CONFIG_ANDROID_BINDERFS=y',fragment);self.assertIn('CONFIG_USB_CONFIGFS_F_FS=y',fragment)
