/* SPDX-License-Identifier: GPL-2.0-only
 * Standalone GPU/KMS trial. No storage, networking, input injection or reboot.
 */
#define _GNU_SOURCE
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES2/gl2.h>
#include <gbm.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <errno.h>
#include <fcntl.h>
#include <math.h>
#include <poll.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <time.h>
#include <unistd.h>
#include "touch_probe.h"

static unsigned long milliseconds(void){struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t))return 0;return (unsigned long)t.tv_sec*1000+(unsigned long)t.tv_nsec/1000000;}
__attribute__((noreturn)) static void idle(void){for(;;){struct timespec t={1,0};nanosleep(&t,NULL);}}
static void multiply(float out[16],const float a[16],const float b[16]){
 float r[16]={0};for(int c=0;c<4;c++)for(int row=0;row<4;row++)for(int k=0;k<4;k++)r[c*4+row]+=a[k*4+row]*b[c*4+k];memcpy(out,r,sizeof(r));
}
static void matrix(float out[16],float angle,float x,float y,float aspect){
 float c=cosf(angle),s=sinf(angle),cx=cosf(angle*.7f),sx=sinf(angle*.7f);
 float ry[16]={c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1};
 float rx[16]={1,0,0,0,0,cx,sx,0,0,-sx,cx,0,0,0,0,1};
 float tr[16]={1,0,0,0,0,1,0,0,0,0,1,0,x*.4f,y*.4f,-4.5f,1};
 float p[16]={2.41421356f/aspect,0,0,0,0,2.41421356f,0,0,0,0,-1.020202f,-1,0,0,-.2020202f,0},r[16];
 multiply(r,ry,rx);multiply(r,tr,r);multiply(out,p,r);
}
static GLuint shader(GLenum kind,const char *source){
 GLuint result=glCreateShader(kind);glShaderSource(result,1,&source,NULL);glCompileShader(result);GLint okay=0;glGetShaderiv(result,GL_COMPILE_STATUS,&okay);return okay?result:0;
}
static void flip_done(int fd,unsigned int sequence,unsigned int seconds,unsigned int useconds,void *data){(void)fd;(void)sequence;(void)seconds;(void)useconds;*(int *)data=0;}
static int framebuffer(int fd,struct gbm_bo *bo,uint32_t *id){return drmModeAddFB(fd,gbm_bo_get_width(bo),gbm_bo_get_height(bo),24,32,gbm_bo_get_stride(bo),gbm_bo_get_handle(bo).u32,id);}
static void error_number(unsigned int number){
 static const unsigned char digits[10][7]={{14,17,19,21,25,17,14},{4,12,4,4,4,4,14},{14,17,1,2,4,8,31},{30,1,1,14,1,1,30},{2,6,10,18,31,2,2},{31,16,16,30,1,1,30},{14,16,16,30,17,17,14},{31,1,2,4,8,8,8},{14,17,17,14,17,17,14},{14,17,17,15,1,1,14}};
 for(unsigned int row=0;row<7;row++)for(unsigned int y=0;y<4;y++){printf("\033[%u;43H",20+row*4+y);for(unsigned int x=0;x<5;x++)printf("\033[%um   ",(digits[number%10][row]&(1U<<(4-x)))?47:41);}
 printf("\033[0m");
}
static int touch_open(void){
 for(unsigned int i=0;i<16;i++){
  char path[80],name[80]={0};tp_path(path,"/sys/class/input/event",i,"/device/name");int fd=open(path,O_RDONLY|O_NOFOLLOW|O_CLOEXEC);if(fd<0)continue;
  ssize_t n=read(fd,name,sizeof(name)-1);close(fd);if(n<=0||strcmp(name,"Goodix Capacitive TouchScreen\n"))continue;
  tp_path(path,"/dev/input/event",i,"");fd=open(path,O_RDONLY|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC);
  if(fd<0)return -1;struct stat st;if(fstat(fd,&st)||!S_ISCHR(st.st_mode)||major(st.st_rdev)!=13||minor(st.st_rdev)!=64+i){close(fd);return -1;}return fd;
 }
 return -1;
}

/* A late arrival sees an explicit prompt; GPU work waits for the first tap. */
static void start_prompt(void){
 const char *text="TAP TO START";const unsigned char glyphs[][7]={
  {31,4,4,4,4,4,4}, {14,17,17,31,17,17,17}, {30,17,17,30,16,16,16},
  {14,17,17,17,17,17,14}, {15,16,16,14,1,1,30}, {30,17,17,30,20,18,17}};
 glEnable(GL_SCISSOR_TEST);glClearColor(.95f,.95f,.95f,1);
 for(int c=0;text[c];c++){
  int g=-1;switch(text[c]){case 'T':g=0;break;case 'A':g=1;break;case 'P':g=2;break;case 'O':g=3;break;case 'S':g=4;break;case 'R':g=5;break;}
  if(g<0)continue;
  for(int y=0;y<7;y++)for(int x=0;x<5;x++)if(glyphs[g][y]&(1U<<(4-x))){glScissor(112+c*48+x*8,1120+(6-y)*8,8,8);glClear(GL_COLOR_BUFFER_BIT);}
 }
 glDisable(GL_SCISSOR_TEST);
}

int main(void){
 (void)&ft_serial_output;
 (void)&ft_acm_setup;(void)&ft_discover_udc;
 setvbuf(stdout,NULL,_IONBF,0);setvbuf(stderr,NULL,_IONBF,0);
 const char *stage="display discovery";unsigned int error_code=1;int fd=-1,input=-1;uint32_t connector=0,crtc=0;drmModeModeInfo mode={0};drmModeCrtc *saved=NULL;
 for(int i=0;i<4&&fd<0;i++){
  char path[32];snprintf(path,sizeof(path),"/dev/dri/card%d",i);int candidate=open(path,O_RDWR|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC);if(candidate<0)continue;
  struct stat st;drmVersion *version=drmGetVersion(candidate);
  int accepted=version&&version->name_len==8&&!memcmp(version->name,"mediatek",8)&&!fstat(candidate,&st)&&S_ISCHR(st.st_mode)&&major(st.st_rdev)==226&&minor(st.st_rdev)==(unsigned int)i;
  if(version)drmFreeVersion(version);if(!accepted){close(candidate);continue;}
  drmModeRes *res=drmModeGetResources(candidate);if(!res){close(candidate);continue;}
  for(int k=0;k<res->count_connectors&&!connector;k++){
   drmModeConnector *con=drmModeGetConnector(candidate,res->connectors[k]);if(!con)continue;
   if(con->connection==DRM_MODE_CONNECTED)for(int m=0;m<con->count_modes;m++)if(con->modes[m].hdisplay==800&&con->modes[m].vdisplay==1280){
    for(int e=0;e<con->count_encoders&&!crtc;e++){
     drmModeEncoder *enc=drmModeGetEncoder(candidate,con->encoders[e]);if(!enc)continue;
     for(int c=0;c<res->count_crtcs&&c<32;c++)if(enc->possible_crtcs&(1U<<c)){crtc=res->crtcs[c];break;}
     drmModeFreeEncoder(enc);
    }
    if(crtc){connector=con->connector_id;mode=con->modes[m];}break;
   }
   drmModeFreeConnector(con);
  }
  drmModeFreeResources(res);if(connector)fd=candidate;else close(candidate);
 }
 if(fd<0||!connector||!crtc)goto failure;
 saved=drmModeGetCrtc(fd,crtc);stage="GBM display buffers";error_code=2;
 struct gbm_device *gbm=gbm_create_device(fd);if(!gbm)goto failure;
 struct gbm_surface *surface=gbm_surface_create(gbm,800,1280,GBM_FORMAT_XRGB8888,GBM_BO_USE_SCANOUT|GBM_BO_USE_RENDERING|GBM_BO_USE_LINEAR);if(!surface)goto failure;
 stage="EGL initialization";error_code=3;EGLDisplay display=eglGetPlatformDisplay(EGL_PLATFORM_GBM_KHR,gbm,NULL);EGLint major_version=0,minor_version=0;
 if(display==EGL_NO_DISPLAY||!eglInitialize(display,&major_version,&minor_version)||!eglBindAPI(EGL_OPENGL_ES_API))goto failure;
 const EGLint attrs[]={EGL_SURFACE_TYPE,EGL_WINDOW_BIT,EGL_RENDERABLE_TYPE,EGL_OPENGL_ES2_BIT,EGL_RED_SIZE,8,EGL_GREEN_SIZE,8,EGL_BLUE_SIZE,8,EGL_DEPTH_SIZE,16,EGL_NONE};
 EGLConfig configs[64],config=NULL;EGLint count=0;if(!eglChooseConfig(display,attrs,configs,64,&count))goto failure;
 for(int i=0;i<count;i++){EGLint format=0;if(eglGetConfigAttrib(display,configs[i],EGL_NATIVE_VISUAL_ID,&format)&&format==(EGLint)GBM_FORMAT_XRGB8888){config=configs[i];break;}}
 if(!config)goto failure;
 const EGLint context_attrs[]={EGL_CONTEXT_CLIENT_VERSION,2,EGL_NONE};EGLContext context=eglCreateContext(display,config,EGL_NO_CONTEXT,context_attrs);
 EGLSurface window=eglCreateWindowSurface(display,config,(EGLNativeWindowType)surface,NULL);
 if(context==EGL_NO_CONTEXT||window==EGL_NO_SURFACE||!eglMakeCurrent(display,window,window,context))goto failure;
 stage="hardware renderer identity";error_code=4;const char *renderer=(const char *)glGetString(GL_RENDERER);
 if(!renderer||!strstr(renderer,"T720")||strstr(renderer,"llvmpipe")||strstr(renderer,"softpipe"))goto failure;
 printf("VALETHON GRAPHICS renderer=%s EGL=%d.%d\n",renderer,major_version,minor_version);fflush(stdout);
 stage="GPU shader compilation";error_code=5;
 const char *vs="attribute vec3 position;attribute vec3 color;uniform mat4 matrix;varying vec3 shade;void main(){gl_Position=matrix*vec4(position,1.0);shade=color;}";
 const char *fs="precision mediump float;varying vec3 shade;void main(){gl_FragColor=vec4(shade,1.0);}";
 GLuint vertex=shader(GL_VERTEX_SHADER,vs),fragment=shader(GL_FRAGMENT_SHADER,fs);if(!vertex||!fragment)goto failure;
 GLuint program=glCreateProgram();glAttachShader(program,vertex);glAttachShader(program,fragment);glBindAttribLocation(program,0,"position");glBindAttribLocation(program,1,"color");glLinkProgram(program);
 GLint linked=0;glGetProgramiv(program,GL_LINK_STATUS,&linked);if(!linked)goto failure;glUseProgram(program);GLint transform=glGetUniformLocation(program,"matrix");if(transform<0)goto failure;
 static const float vertices[]={
 -.65f,-.65f,.65f, .65f,-.65f,.65f, .65f,.65f,.65f, -.65f,-.65f,.65f, .65f,.65f,.65f, -.65f,.65f,.65f,
 .65f,-.65f,-.65f, -.65f,-.65f,-.65f, -.65f,.65f,-.65f, .65f,-.65f,-.65f, -.65f,.65f,-.65f, .65f,.65f,-.65f,
 -.65f,-.65f,-.65f, -.65f,-.65f,.65f, -.65f,.65f,.65f, -.65f,-.65f,-.65f, -.65f,.65f,.65f, -.65f,.65f,-.65f,
 .65f,-.65f,.65f, .65f,-.65f,-.65f, .65f,.65f,-.65f, .65f,-.65f,.65f, .65f,.65f,-.65f, .65f,.65f,.65f,
 -.65f,.65f,.65f, .65f,.65f,.65f, .65f,.65f,-.65f, -.65f,.65f,.65f, .65f,.65f,-.65f, -.65f,.65f,-.65f,
 -.65f,-.65f,-.65f, .65f,-.65f,-.65f, .65f,-.65f,.65f, -.65f,-.65f,-.65f, .65f,-.65f,.65f, -.65f,-.65f,.65f};
 static const float colors[6][3]={{.9f,.15f,.15f},{.15f,.9f,.3f},{.15f,.3f,.95f},{.95f,.8f,.15f},{.8f,.15f,.9f},{.15f,.9f,.9f}};
 float mesh[36*6];for(int i=0;i<36;i++){memcpy(mesh+i*6,vertices+i*3,3*sizeof(float));memcpy(mesh+i*6+3,colors[i/6],3*sizeof(float));}
 GLuint buffer;glGenBuffers(1,&buffer);glBindBuffer(GL_ARRAY_BUFFER,buffer);glBufferData(GL_ARRAY_BUFFER,sizeof(mesh),mesh,GL_STATIC_DRAW);
 glEnableVertexAttribArray(0);glEnableVertexAttribArray(1);glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,6*sizeof(float),(void *)0);glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,6*sizeof(float),(void *)(3*sizeof(float)));glEnable(GL_DEPTH_TEST);glViewport(0,0,800,1280);
 stage="touch input";error_code=6;for(int retry=0;retry<500&&input<0;retry++){input=touch_open();if(input<0){struct timespec wait={0,10000000};nanosleep(&wait,NULL);}}if(input<0)goto failure;
 struct tp_state touch={0};float x=0,y=0;struct gbm_bo *previous=NULL;uint32_t previous_fb=0;unsigned long began=milliseconds(),started_at=0,frames=0;int started=0;if(!began)goto failure;
 stage="GPU rendering and scanout";error_code=7;
 while((!started&&milliseconds()-began<900000)||(started&&milliseconds()-started_at<300000)){
  struct tp_event events[32];for(int batch=0;batch<8;batch++){
   ssize_t n=read(input,events,sizeof(events));if(n<0){if(errno==EINTR)continue;if(errno==EAGAIN)break;goto failure;}if(n<=0||n%(ssize_t)sizeof(events[0]))goto failure;
   for(unsigned int i=0;i<(unsigned long)n/sizeof(events[0]);i++)tp_feed(&touch,&events[i]);if(touch.failed)goto failure;
   for(int i=0;i<TP_SLOTS;i++)if(touch.slots[i].active&&touch.slots[i].valid==3){x=touch.slots[i].x/400.f-1.f;y=1.f-touch.slots[i].y/640.f;if(!started){started=1;started_at=milliseconds();}break;}
  }
  if(!started&&frames){struct timespec pause={0,20000000};nanosleep(&pause,NULL);continue;}
  float m[16];matrix(m,(started?(milliseconds()-started_at)/1100.f:0)+x*2.f,x,y,800.f/1280.f);glUniformMatrix4fv(transform,1,GL_FALSE,m);glClearColor(.015f,.02f,.04f,1);glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);glDrawArrays(GL_TRIANGLES,0,36);
  if(!frames){unsigned char pixel[4];glFinish();glReadPixels(400,640,1,1,GL_RGBA,GL_UNSIGNED_BYTE,pixel);if((unsigned int)pixel[0]+pixel[1]+pixel[2]<64)goto failure;}
  if(!started)start_prompt();
  if(glGetError()!=GL_NO_ERROR||!eglSwapBuffers(display,window))goto failure;
  struct gbm_bo *bo=gbm_surface_lock_front_buffer(surface);uint32_t fb=0;if(!bo||framebuffer(fd,bo,&fb))goto failure;
  if(!frames){if(drmModeSetCrtc(fd,crtc,fb,0,0,&connector,1,&mode))goto failure;}
  else{
   int pending=1;if(drmModePageFlip(fd,crtc,fb,DRM_MODE_PAGE_FLIP_EVENT,&pending))goto failure;
   drmEventContext ev={0};ev.version=DRM_EVENT_CONTEXT_VERSION;ev.page_flip_handler=flip_done;
   unsigned long deadline=milliseconds()+2000;
   while(pending&&milliseconds()<deadline){struct pollfd pollfd={fd,POLLIN,0};int r=poll(&pollfd,1,100);if(r<0&&errno!=EINTR)goto failure;if(r>0&&drmHandleEvent(fd,&ev))goto failure;}
   if(pending)goto failure;
  }
  if(previous){drmModeRmFB(fd,previous_fb);gbm_surface_release_buffer(surface,previous);}previous=bo;previous_fb=fb;frames++;
  struct timespec pause={0,16000000};nanosleep(&pause,NULL);
 }
 printf("VALETHON GRAPHICS completed frames=%lu touch_regions=%u\n",frames,touch.visited);fflush(stdout);idle();
failure:
 if(saved&&saved->mode_valid)(void)drmModeSetCrtc(fd,saved->crtc_id,saved->buffer_id,saved->x,saved->y,&connector,1,&saved->mode);
 printf("\033[41m\033[2J\033[HVALETHON GRAPHICS STOPPED\nStage: %s\nNo graphics pass. Leave Power untouched.\033[0m\n",stage);error_number(error_code);fflush(stdout);idle();
}
