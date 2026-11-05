#!/usr/bin/env python3
"""Render 65 independent 1080p clips with 6 native-Chrome workers, then mux one continuous master."""
import concurrent.futures, json, os, pathlib, subprocess, threading, time, wave, array, hashlib
P=pathlib.Path(__file__).resolve().parents[1];OUT=P.parent
ROWS=json.loads((OUT/'catalog.json').read_text());WORK=P/'.render';WORK.mkdir(exist_ok=True)
for name in ['videos','posters']:(OUT/name).mkdir(exist_ok=True)
STATUS=OUT/'render-progress.json';lock=threading.Lock();started=time.time();active={};done=[];failed=[]
def write_status(stage='rendering'):
 with lock:
  STATUS.write_text(json.dumps({'stage':stage,'total':65,'completed':len(done),'completed_ids':sorted(done),'active':list(active),'failed':failed,'elapsed_seconds':round(time.time()-started,1),'updated_at':time.time()},ensure_ascii=False,indent=2))
def run(args,log):
 with open(log,'w') as f:subprocess.run(list(map(str,args)),cwd=P,stdout=f,stderr=subprocess.STDOUT,check=True)
def probe(path):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
def valid(path,frames):
 try:return any(s.get('codec_type')=='video' and int(s.get('nb_frames',0))==frames and s.get('width')==1920 for s in probe(path)['streams'])
 except Exception:return False
bundle=WORK/'bundle'
if not (bundle/'index.html').exists():
 run(['node','scripts/bundle.cjs'],WORK/'bundle.log')
master=WORK/'audio-master.wav';sr=48000
if not master.exists():
 samples=array.array('h',[0])*(405*sr*2)
 c=probe(P/'public/sfx/click_kenney_001.wav')
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'public/sfx/click_kenney_001.wav'),'-f','s16le','-ar',str(sr),'-ac','2','-'])
 sound=array.array('h');sound.frombytes(raw)
 for index in [0,2,5,10,13]:
  offset=round((index*7+.8)*sr)*2
  for i,v in enumerate(sound):samples[offset+i]=int(v*.06)
 with wave.open(str(master),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes(samples.tobytes())
ports=threading.local();counter=iter(range(6))
def initializer():ports.port=3200+next(counter)
def one(r):
 id=r['slug'];frames=r['时长秒']*30;dst=OUT/r['video'];raw=WORK/f'{id}.raw.mp4';duration=r['时长秒']
 if valid(dst,frames):
  with lock:done.append(id)
  write_status();return
 with lock:active[id]=True
 write_status();print('START',id,r['名称'],flush=True)
 try:
  if not valid(raw,frames):
   for attempt in range(3):
    try:
     run([P/'node_modules/.bin/remotion','render',bundle,r['composition'],raw,'--concurrency=1',f'--port={ports.port}','--gl=angle','--disable-shared-memory-capture','--browser-executable=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--muted','--codec=h264','--crf=18','--x264-preset=veryfast','--image-format=jpeg','--jpeg-quality=90','--log=info','--overwrite'],WORK/f'{id}.render.log')
     if valid(raw,frames):break
    except subprocess.CalledProcessError:
     if attempt==2:raise
   if not valid(raw,frames):raise RuntimeError('Invalid rendered frames')
  run(['ffmpeg','-y','-v','error','-i',raw,'-ss',r['合集开始秒'],'-t',duration,'-i',master,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','128k','-t',duration,'-movflags','+faststart',dst],WORK/f'{id}.mux.log')
  if not valid(dst,frames):raise RuntimeError('Invalid final frames')
  run(['ffmpeg','-y','-v','error','-ss',min(4.5,duration-.5),'-i',dst,'-frames:v','1','-vf','scale=640:-1','-q:v','3',OUT/r['poster']],WORK/f'{id}.poster.log')
  with lock:done.append(id)
  print('DONE',id,flush=True)
 except Exception as e:
  with lock:failed.append({'id':id,'error':str(e)})
  print('FAILED',id,str(e),flush=True)
 finally:
  with lock:active.pop(id,None)
  write_status()
write_status()
with concurrent.futures.ThreadPoolExecutor(max_workers=6,initializer=initializer) as ex:list(ex.map(one,ROWS))
if failed:write_status('failed');raise SystemExit('Some effects failed; rerun to resume')
write_status('assembling')
listing=WORK/'ordered.txt';listing.write_text(''.join("file '"+str(WORK/(r['slug']+'.raw.mp4')).replace("'","'\\''")+"'\n" for r in ROWS))
final=OUT/'videos/All-65.mp4'
run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',listing,'-i',master,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','128k','-t','405','-movflags','+faststart',final],WORK/'all.mux.log')
if not valid(final,12150):raise RuntimeError('Full catalog frame count mismatch')
reports=[]
for r in ROWS:
 path=OUT/r['video'];meta=probe(path);v=next(x for x in meta['streams'] if x['codec_type']=='video');a=next(x for x in meta['streams'] if x['codec_type']=='audio')
 reports.append({'id':r['id'],'file':r['video'],'frames':int(v['nb_frames']),'duration':float(v['duration']),'width':v['width'],'height':v['height'],'audio_codec':a['codec_name'],'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 r['status']='已渲染；视频帧数和音轨通过检查'
(OUT/'catalog.json').write_text(json.dumps(ROWS,ensure_ascii=False,indent=2))
(OUT/'render-verification.json').write_text(json.dumps({'count':65,'full_frames':12150,'duration_seconds':405,'clips':reports,'audio':'5 sparse click events; remaining clips intentionally silent','visual_review':'用户已看过预览；此次未做逐项人工目检'},ensure_ascii=False,indent=2))
write_status('complete');print('FINAL_READY',final,flush=True)
