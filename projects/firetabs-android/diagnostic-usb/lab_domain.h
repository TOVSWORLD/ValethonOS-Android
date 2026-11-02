/* One-way SELinux PID1 transition through the pinned LSM self-context API.
 * No proc writes, arbitrary context, forced label, permissive mode or reload. */
#ifndef VALETHON_LAB_DOMAIN_H
#define VALETHON_LAB_DOMAIN_H
#include "lab_labels.h"
#include "lab_policy_load.h"
#define LL_NR_LSM_GET_SELF_ATTR 459
#define LL_NR_LSM_SET_SELF_ATTR 460
#define LL_LSM_ATTR_CURRENT 100
#define LL_LSM_ID_SELINUX 101
#define LL_LSM_FLAG_SINGLE 1
static inline int ll_enter_init(struct ft_acm_io *io) {
 static const char context[]="system_u:system_r:init_t";
 unsigned long long request[8]={LL_LSM_ID_SELINUX,0,64,sizeof(context),0,0,0,0};
 unsigned char *value=(unsigned char *)request+32;
 for(unsigned long i=0;i<sizeof(context);i++)value[i]=(unsigned char)context[i];
 /* One credential-changing call; no retry or alternate context. */
 long r=ft_call(io,LL_NR_LSM_SET_SELF_ATTR,LL_LSM_ATTR_CURRENT,(long)request,sizeof(request),0,0,0);
 if(r)return r<0?(int)r:-5;
 unsigned long long response[16]={LL_LSM_ID_SELINUX,0};unsigned int size=sizeof(response);
 r=ft_call(io,LL_NR_LSM_GET_SELF_ATTR,LL_LSM_ATTR_CURRENT,(long)response,(long)&size,LL_LSM_FLAG_SINGLE,0,0);
 if(r<0)return (int)r;
 if(r!=1||size<32||size>sizeof(response)||response[0]!=LL_LSM_ID_SELINUX||response[1]||
    response[2]!=size||response[3]!=sizeof(context)||response[2]<32+response[3]||
    !ll_context_equal((const unsigned char *)response+32,(long)response[3],context))return -13;
 struct vp_io vp={io->call,io->ctx};return vp_enforcing(&vp);
}
#endif
