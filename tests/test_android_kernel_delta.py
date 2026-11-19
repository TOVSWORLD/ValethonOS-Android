import importlib.util,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('android_kernel_delta',ROOT/'scripts/check_android_kernel_delta.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class KernelDelta(unittest.TestCase):
 def test_source_derived_apex_features_preserve_hardware_and_reject_drift(self):
  hardware={k:'y' for k in ['CONFIG_COMPAT','CONFIG_ARM64_4K_PAGES','CONFIG_DRM_PANFROST','CONFIG_TOUCHSCREEN_GOODIX','CONFIG_DRM_MEDIATEK','CONFIG_SECURITY_SELINUX']}
  required={k:v for f in module.FRAGMENTS for k,v in module.config(f).items()}
  with tempfile.TemporaryDirectory() as d:
   parent=Path(d)/'parent';result=Path(d)/'result'
   def write(path,values):path.write_text(''.join(k+'='+v+'\n' for k,v in values.items()))
   write(parent,hardware);write(result,hardware|required)
   self.assertIn('CONFIG_DM_VERITY',module.check(parent,result))
   for changes in [{'CONFIG_SECURITY_SELINUX':'n'},{'CONFIG_DRM_PANFROST':'m'},{'CONFIG_DEBUG_KERNEL':'y'},{'CONFIG_ANDROID_BINDERFS':'n'}]:
    write(result,hardware|required|changes)
    with self.assertRaises(ValueError):module.check(parent,result)
