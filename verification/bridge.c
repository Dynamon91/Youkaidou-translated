#include <mgba/flags.h>
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/gba/core.h>
#include <mgba/core/log.h>
#include <stdlib.h>
#include <stdint.h>
static void quiet(struct mLogger* l,int c,enum mLogLevel v,const char* f,va_list a){}
static struct mLogger logger={.log=quiet,.filter=NULL};
struct Session {struct mCore* core; color_t* pixels;};
struct Session* open_game(const char* path) {
 mLogSetDefaultLogger(&logger);
 struct Session* s=calloc(1,sizeof(*s));
 s->core=GBACoreCreate();
 if(!s->core || !s->core->init(s->core)){free(s);return NULL;}
 mCoreInitConfig(s->core,"localization");
 mCoreConfigSetDefaultIntValue(&s->core->config,"skipBios",1);
 mCoreConfigSetDefaultIntValue(&s->core->config,"useBios",0);
 s->core->loadConfig(s->core,&s->core->config);
 s->pixels=calloc(240*160,sizeof(color_t));
 s->core->setVideoBuffer(s->core,s->pixels,240);
 if(!mCoreLoadFile(s->core,path)){s->core->deinit(s->core);free(s->pixels);free(s);return NULL;}
 s->core->reset(s->core);return s;
}
void close_game(struct Session* s){s->core->deinit(s->core);free(s->pixels);free(s);}
void frames(struct Session* s,int count,uint32_t keys){s->core->setKeys(s->core,keys);for(int i=0;i<count;i++)s->core->runFrame(s->core);}
void step_one(struct Session* s){s->core->step(s->core);}
void* pixels(struct Session* s){return s->pixels;}
int pixel_size(void){return sizeof(color_t);}
uint32_t read8(struct Session* s,uint32_t addr){return s->core->busRead8(s->core,addr);}
uint32_t read16(struct Session* s,uint32_t addr){return s->core->busRead16(s->core,addr);}
uint32_t read32(struct Session* s,uint32_t addr){return s->core->busRead32(s->core,addr);}
void write8(struct Session* s,uint32_t addr,uint32_t value){s->core->busWrite8(s->core,addr,value);}
void raw8(struct Session* s,uint32_t addr,uint32_t value){s->core->rawWrite8(s->core,addr,-1,value);}
void dump(struct Session* s,uint32_t addr,void* out,int n){for(int i=0;i<n;i++)((uint8_t*)out)[i]=s->core->busRead8(s->core,addr+i);}
uint32_t reg(struct Session* s,const char* name){uint32_t v=0;s->core->readRegister(s->core,name,&v);return v;}
size_t state_size(struct Session* s){return s->core->stateSize(s->core);}
int save_state(struct Session* s,void* out){return s->core->saveState(s->core,out);}
int load_state(struct Session* s,void* in){return s->core->loadState(s->core,in);}
#include <mgba/internal/arm/arm.h>
#include <stdio.h>
void trace_steps(struct Session* s,int count,uint32_t keys,const char* name){
 FILE* f=fopen(name,"w");struct ARMCore* cpu=s->core->cpu;
 s->core->setKeys(s->core,keys);
 for(int i=0;i<count;i++){
  uint32_t pc=cpu->gprs[15];
  if(pc==0x8003f1c || pc==0x8077418 || pc==0x80049ac || pc==0x8004e78 || pc==0x8004e80 || pc==0x80050a0 || pc==0x80040f8 || pc==0x806e988 || pc==0x806ee38){
   fprintf(f,"%08x %08x %08x %08x %08x lr=%08x\n",pc,cpu->gprs[0],cpu->gprs[1],cpu->gprs[2],cpu->gprs[3],cpu->gprs[14]);
  }
  s->core->step(s->core);
 }
 fclose(f);
}
int until_pc(struct Session* s,uint32_t target,int limit){struct ARMCore* cpu=s->core->cpu;for(int i=0;i<limit;i++){if((uint32_t)cpu->gprs[15]==target)return i;s->core->step(s->core);}return -1;}
size_t dump_save(struct Session* s,const char* path){void* data=NULL;size_t n=s->core->savedataClone(s->core,&data);if(data&&n&&n<=0x100000){FILE* f=fopen(path,"wb");fwrite(data,1,n,f);fclose(f);free(data);}return n;}
int load_save(struct Session* s,const char* path){return mCoreLoadSaveFile(s->core,path,false);}
void reset_game(struct Session* s){s->core->reset(s->core);}
void trace_targets(struct Session* s,int count,uint32_t keys,const uint32_t* targets,int nt,const char* path){
 FILE* f=fopen(path,"w");struct ARMCore* cpu=s->core->cpu;s->core->setKeys(s->core,keys);
 for(int i=0;i<count;i++){
  uint32_t pc=cpu->gprs[15];int found=0;
  for(int j=0;j<nt;j++)if(pc==targets[j]){found=1;break;}
  if(found){fprintf(f,"%08x",pc);for(int j=0;j<16;j++)fprintf(f," %08x",cpu->gprs[j]);fputc('\n',f);}
  s->core->step(s->core);
 }
 fclose(f);
}
