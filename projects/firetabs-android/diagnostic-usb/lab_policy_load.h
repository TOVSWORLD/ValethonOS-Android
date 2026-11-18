/* Initial-policy bootstrap for a fresh isolated guest only. No runtime reload.
 * Input must be the immutable compiler-verified embedded policy blob. This code
 * does not activate a gadget or change enforcement. RAM callback tests only until
 * a complete exact trial image is separately reviewed. */
#ifndef VALETHON_LAB_POLICY_LOAD_H
#define VALETHON_LAB_POLICY_LOAD_H
#define VP_NR_MOUNT 40
#define VP_NR_OPENAT 56
#define VP_NR_CLOSE 57
#define VP_NR_READ 63
#define VP_NR_WRITE 64
#define VP_AT_FDCWD -100
#define VP_NOFOLLOW 0100000
#define VP_CLOEXEC 02000000
struct vp_io {long (*call)(void *,long,long,long,long,long,long,long);void *ctx;};
struct vp_state {int attempted,mounted,loaded,readonly;};
static inline long vp_call(struct vp_io *io,long n,long a,long b,long c,long d,long e,long f) {
 return io->call(io->ctx,n,a,b,c,d,e,f);
}
static inline int vp_enforcing(struct vp_io *io) {
 char value[2],extra;
 long fd=vp_call(io,VP_NR_OPENAT,VP_AT_FDCWD,(long)"/security/enforce",VP_NOFOLLOW|VP_CLOEXEC,0,0,0);
 if(fd<0)return (int)fd;
 long n=vp_call(io,VP_NR_READ,fd,(long)value,2,0,0,0);
 long end=n==1?vp_call(io,VP_NR_READ,fd,(long)&extra,1,0,0,0):-1;
 long closed=vp_call(io,VP_NR_CLOSE,fd,0,0,0,0,0); /* Never retry close. */
 return n==1&&value[0]=='1'&&end==0&&closed==0?0:-1;
}
static inline int vp_bootstrap(struct vp_io *io,const unsigned char *policy,unsigned long n,struct vp_state *state) {
 const unsigned char magic[16]={0x8c,0xff,0x7c,0xf9,8,0,0,0,'S','E',' ','L','i','n','u','x'};
 if(!io||!io->call||!policy||!state||n<24||n>65536)return -22;
 if(state->attempted||state->mounted||state->loaded||state->readonly)return -16;
 for(int i=0;i<16;i++)if(policy[i]!=magic[i])return -22;
 if(policy[16]!=33||policy[17]||policy[18]||policy[19])return -22;
 state->attempted=1;
 long r=vp_call(io,VP_NR_MOUNT,(long)"selinuxfs",(long)"/security",(long)"selinuxfs",14,0,0);
 if(r)return (int)r;
 state->mounted=1;
 int enforced=vp_enforcing(io);if(enforced)return enforced;
 /* Exact pinned ACK security_read_policy returns -EINVAL only without policy.
  * Existing readable policy or any other error refuses replacement. */
 long probe=vp_call(io,VP_NR_OPENAT,VP_AT_FDCWD,(long)"/security/policy",VP_NOFOLLOW|VP_CLOEXEC,0,0,0);
 if(probe>=0){vp_call(io,VP_NR_CLOSE,probe,0,0,0,0,0);return -17;}
 if(probe!=-22)return (int)probe;
 long fd=vp_call(io,VP_NR_OPENAT,VP_AT_FDCWD,(long)"/security/load",1|VP_NOFOLLOW|VP_CLOEXEC,0,0,0);
 if(fd<0)return (int)fd;
 /* One store only: no short-store splitting and no EINTR load retry. */
 long wrote=vp_call(io,VP_NR_WRITE,fd,(long)policy,n,0,0,0);
 long closed=vp_call(io,VP_NR_CLOSE,fd,0,0,0,0,0);
 if(wrote<0)return (int)wrote;
 if((unsigned long)wrote!=n)return -5;
 state->loaded=1;
 if(closed<0)return (int)closed;
 enforced=vp_enforcing(io);if(enforced)return enforced;
 r=vp_call(io,VP_NR_MOUNT,0,(long)"/security",0,47,0,0); /* RO remount, same virtual FS. */
 if(r)return (int)r;
 state->readonly=1;
 return vp_enforcing(io);
}
#endif
