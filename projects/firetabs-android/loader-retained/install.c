/* Install the exact late hook into the already-resident LK. The bootstrap
 * header reloads only LK[0:0x3c8], so changing the embedded tail is ineffective.
 * Called once by resident main before its original whole-LK cache clean/app.
 */
extern const unsigned lbo_hook_word;
int lbo_install_hook(void){
 if(*(volatile unsigned *)0x4bd7c3a0)return -1;
 volatile unsigned *site=(void *)0x4bd3e3e8;
 if(*site!=0x3720f8dfu)return -2;
 if((lbo_hook_word&0xd000f800u)!=0xd000f000u)return -3;
 *site=lbo_hook_word;
 return 0;
}
