#!/usr/bin/env python3
"""Repair pinned ACK FUSE dentry cleanup guards without enabling FUSE BPF."""
import argparse,hashlib,json
from pathlib import Path
SHA='eb418bedbd82e70bb58162faead79d2e225ed2fa0a62dccd738f205d9c5861d5'
PATCHED_SHA='7ee5e69d51e4ddf2f71cf3bf978cb1e950ddb7b93ec9e34673dd17ec5800d77a'
BEFORE='''static void fuse_dentry_release(struct dentry *dentry)
{
\tstruct fuse_dentry *fd = dentry->d_fsdata;

#if BITS_PER_LONG < 64 || defined(CONFIG_FUSE_BPF)
\tif (fd && fd->backing_path.dentry)
\t\tpath_put(&fd->backing_path);

\tif (fd && fd->bpf)
\t\tbpf_prog_put(fd->bpf);
#endif

\tkfree_rcu(fd, rcu);
}
'''
AFTER=BEFORE.replace('{\n\tstruct fuse_dentry', '{\n#if BITS_PER_LONG < 64 || defined(CONFIG_FUSE_BPF)\n\tstruct fuse_dentry').replace('\n#if BITS_PER_LONG < 64 || defined(CONFIG_FUSE_BPF)\n\tif', '\n#ifdef CONFIG_FUSE_BPF\n\tif').replace('\tkfree_rcu(fd, rcu);\n}', '\tkfree_rcu(fd, rcu);\n#endif\n}')
def apply(root):
    p=Path(root)/'fs/fuse/dir.c';data=p.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
    if sha(data) not in [SHA,PATCHED_SHA]:raise ValueError('Exact pinned ACK FUSE source required')
    if sha(data)==PATCHED_SHA:
        return {'path':'fs/fuse/dir.c','before_sha256':SHA,'after_sha256':PATCHED_SHA,'scope':'Conditional cleanup only; no FUSE BPF enablement or hardware changes'}
    text=data.decode()
    if text.count(BEFORE)!=1:raise ValueError('Unique pinned cleanup function required')
    patched=text.replace(BEFORE,AFTER).encode()
    if sha(patched)!=PATCHED_SHA:raise ValueError('Patched FUSE source identity mismatch')
    p.write_bytes(patched)
    return {'path':'fs/fuse/dir.c','before_sha256':SHA,'after_sha256':sha(patched),'scope':'Conditional cleanup only; no FUSE BPF enablement or hardware changes'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args();r=apply(a.source);a.report.write_text(json.dumps(r,indent=2)+'\n');print('Pinned FUSE conditional cleanup repaired.')
