import importlib.util,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('android_fuse_guard',ROOT/'scripts/apply_android_fuse_guard.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class FuseConditionalCleanup(unittest.TestCase):
 def test_actual_cleanup_c_handles_32_and_64_bit_with_and_without_bpf(self):
  compiler=shutil.which('clang') or shutil.which('cc');self.assertIsNotNone(compiler)
  prefix='''#include <stdlib.h>
struct dentry {void *d_fsdata;};
static int freed,paths,programs;
#if BITS_PER_LONG < 64 || defined(CONFIG_FUSE_BPF)
struct fuse_dentry {
 int rcu;
#ifdef CONFIG_FUSE_BPF
 struct {void *dentry;} backing_path;void *bpf;
#endif
};
#define kfree_rcu(ptr, field) do {if(ptr)freed++;} while(0)
#endif
#ifdef CONFIG_FUSE_BPF
#define path_put(ptr) do {paths++;} while(0)
#define bpf_prog_put(ptr) do {programs++;} while(0)
#endif
'''
  main='''int main(void){struct dentry entry={0};
#if BITS_PER_LONG < 64 || defined(CONFIG_FUSE_BPF)
 struct fuse_dentry fd={0};entry.d_fsdata=&fd;
#ifdef CONFIG_FUSE_BPF
 fd.backing_path.dentry=&entry;fd.bpf=&entry;
#endif
#endif
 fuse_dentry_release(&entry);
#if BITS_PER_LONG < 64 || defined(CONFIG_FUSE_BPF)
 if(freed!=1)abort();
#else
 if(freed)abort();
#endif
#ifdef CONFIG_FUSE_BPF
 if(paths!=1||programs!=1)abort();
#else
 if(paths||programs)abort();
#endif
 entry.d_fsdata=0;fuse_dentry_release(&entry);return 0;}
'''
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'test.c').write_text(prefix+module.AFTER+main)
   for bits in [32,64]:
    for bpf in [False,True]:
     with self.subTest(bits=bits,bpf=bpf):
      args=[compiler,'-std=c11','-Werror','-DBITS_PER_LONG='+str(bits)]+(['-DCONFIG_FUSE_BPF=1'] if bpf else [])+[str(p/'test.c'),'-o',str(p/'test')]
      r=subprocess.run(args,capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
      subprocess.run([str(p/'test')],check=True)
 def test_patch_rejects_unpinned_source_before_writing(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'fs/fuse/dir.c';p.parent.mkdir(parents=True);p.write_text(module.BEFORE)
   with self.assertRaises(ValueError):module.apply(Path(d))
   self.assertEqual(p.read_text(),module.BEFORE)
