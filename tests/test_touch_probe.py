import shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


class TouchProbe(unittest.TestCase):
    def test_actual_parser_tracks_grid_and_rejects_stale_or_invalid_frames(self):
        code=r'''
#include <stdlib.h>
#include "touch_probe.h"
static void feed(struct tp_state *s,int type,int code,int value){struct tp_event e={0,0,type,code,value};tp_feed(s,&e);}
int main(void){
 struct tp_state s={0};
 feed(&s,3,0x35,400);feed(&s,3,0x36,600);feed(&s,3,0x39,1);feed(&s,0,0,0);if(s.visited)abort();
 for(int y=0;y<3;y++)for(int x=0;x<3;x++){
  feed(&s,3,0x39,y*3+x);feed(&s,3,0x35,133+x*266);feed(&s,3,0x36,213+y*426);feed(&s,0,0,0);feed(&s,3,0x39,-1);
 }
 if(s.visited!=511||s.failed)abort();
 struct tp_state bad={0};feed(&bad,3,0x2f,16);feed(&bad,3,0x35,800);if(bad.failed!=-22||bad.visited)abort();
 bad=(struct tp_state){0};feed(&bad,0,3,0);if(bad.failed!=-75)abort();
 bad=(struct tp_state){0};feed(&bad,3,0x35,801);if(bad.failed!=-34)abort();
 bad=(struct tp_state){0};feed(&bad,3,0x39,3);feed(&bad,3,0x35,800);feed(&bad,3,0x36,1280);feed(&bad,0,0,0);if(bad.visited!=256)abort();
 feed(&bad,3,0x39,4);feed(&bad,0,0,0);if(bad.slots[0].valid)abort();
 return 0;
}
'''
        self.compile_run(code)

    def test_console_write_interrupts_and_partial_writes_are_bounded(self):
        self.compile_run(r'''
#include <stdlib.h>
#include "touch_probe.h"
static int calls,interrupts;
static long mock(void *c,long nr,long a,long b,long n,long d,long e,long f){calls++;return interrupts?-4:1;}
int main(void){struct ft_acm_io io={mock,0};interrupts=1;
 if(tp_write(&io,1,"test",4)!=-110||calls!=256)abort();
 calls=0;interrupts=0;if(tp_write(&io,1,"test",4)||calls!=4)abort();return 0;}
''')

    def compile_run(self,code):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'test.c').write_text(code)
            subprocess.run([shutil.which('clang') or 'cc','-std=c11','-fsanitize=address,undefined','-DFT_ACM_HOST_TEST=1','-I',str(ROOT/'projects/firetabs-android/diagnostic-usb'),str(p/'test.c'),'-o',str(p/'test')],capture_output=True,check=True)
            subprocess.run([str(p/'test')],capture_output=True,check=True)
