#!/usr/bin/env python3
"""Resumable Moonveil render queue. Standard library + installed Node/Remotion/ffmpeg."""
import argparse, concurrent.futures, fcntl, hashlib, json, math, os, pathlib, re
import shutil, signal, socket, subprocess, threading, time

import importlib.util
_audio_spec=importlib.util.spec_from_file_location('moonveil_audio_delivery',pathlib.Path(__file__).with_name('audio_delivery.py'))
_audio=importlib.util.module_from_spec(_audio_spec);_audio_spec.loader.exec_module(_audio)
POLICY=_audio.POLICY;make_mux_command=_audio.make_mux_command;verify_audio_delivery=_audio.verify_audio_delivery

Path = pathlib.Path
BROWSER = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

def read(p): return json.loads(Path(p).read_text())
def write(p, d):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + '.tmp'); tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2)); tmp.replace(p)
def probe(p):
    r = subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)
def duration(p): return float(probe(p)['format']['duration'])
def video_ok(p, frames):
    try:
        return any(s.get('codec_type') == 'video' and int(s.get('nb_frames', -1)) == frames for s in probe(p)['streams'])
    except (OSError, subprocess.CalledProcessError, ValueError, KeyError): return False

def inputs(project, audio=None, metadata=None):
    project = Path(project)
    files = []
    for directory in ['src', 'public']:
        root = project / directory
        if root.is_dir(): files.extend(p for p in root.rglob('*') if p.is_file())
    files += [project/n for n in ['package.json','package-lock.json','remotion.config.ts','remotion.config.js'] if (project/n).is_file()]
    if audio and Path(audio) not in files: files.append(Path(audio))
    if metadata and Path(metadata) not in files: files.append(Path(metadata))
    return sorted(set(files), key=str)
def signature(project, audio, metadata=None):
    rows = [(str(p),p.stat().st_size,p.stat().st_mtime_ns) for p in inputs(project,audio,metadata)]
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()
def fingerprint(project, audio, metadata=None):
    h=hashlib.sha256()
    for p in inputs(project,audio,metadata):
        h.update(str(p).encode())
        with p.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def prepare(args):
    root=Path(args.project).expanduser().resolve()
    project=next((p for p in [root,root/'proj'] if (p/'package.json').is_file()),None)
    if not project: raise ValueError('No package.json at the supplied directory or its proj/ subdirectory')
    candidates=[project/'src/vox_timeline.json',root/'manifest.json',project/'manifest.json',project/'src/timeline.json']
    meta_path=Path(args.timeline).resolve() if args.timeline else next((p for p in candidates if p.is_file()),None)
    if not meta_path: raise ValueError('No known timeline. Supply --timeline or create an explicit plan for this package.')
    data=read(meta_path); fps=data.get('fps',30) if isinstance(data,dict) else 30
    raw=data.get('units',[]) if isinstance(data,dict) else data
    if not isinstance(raw,list) or not raw: raise ValueError('Timeline has no units')
    units=[]
    for u in raw:
        uid=str(u['id'])
        if uid.lower().startswith(('preview','sample','test-')): continue
        n=u.get('frames')
        if n is None:
            seconds=(u['end']-u['start']) if 'start' in u and 'end' in u else u.get('dur',u.get('duration'))
            if seconds is None: raise ValueError('No duration for '+uid)
            n=math.floor(seconds*fps+.5)
        units.append({'id':uid,'composition':uid,'frames':int(n)})
    if not units or any(u['frames']<1 for u in units): raise ValueError('No full-episode units with positive frame counts')
    if len({u['id'] for u in units}) != len(units): raise ValueError('Duplicate unit IDs')
    # Ep1 manifests used underscores while the registered compositions used hyphens.
    source=(project/'src/Root.tsx').read_text() if (project/'src/Root.tsx').exists() else ''
    literals=set(re.findall(r'<Composition\s+id=["\']([^"\']+)',source))
    for u in units:
        if u['id'] not in literals and u['id'].replace('_','-') in literals: u['composition']=u['id'].replace('_','-')
    audio=Path(args.audio).expanduser().resolve() if args.audio else None
    if audio is None:
        masters=[p for p in root.glob('full_audio*.m4a') if p.is_file()]
        if masters: audio=max(masters,key=lambda p:p.stat().st_mtime).resolve()
    if audio is None and isinstance(data,dict) and data.get('audio'):
        for p in [project/'public'/data['audio'],root/data['audio']]:
            if p.is_file(): audio=p.resolve(); break
    if audio is None:
        choices=[p for base in [root,project,project/'public'] for p in base.glob('full_audio*.m4a') if p.is_file()]
        if choices: audio=max(choices,key=lambda p:p.stat().st_mtime).resolve()
    if audio is None: raise ValueError('Full mixed audio is missing; do not render a silent final episode')
    secs=sum(u['frames'] for u in units)/fps; audio_secs=duration(audio)
    if abs(audio_secs-secs) > 1: raise ValueError(f'Audio {audio_secs:.2f}s does not match video {secs:.2f}s. Locate the complete matching track; do not trim or stretch it.')
    # Check timeline assets without treating prose or external URLs as local filenames.
    missing=set()
    def audit(x):
        if isinstance(x,dict):
            for v in x.values(): audit(v)
        elif isinstance(x,list):
            for v in x: audit(v)
        elif isinstance(x,str) and not x.startswith(('http:','https:')) and re.search(r'\.(webp|png|jpg|jpeg|mp4|m4a|wav)$',x,re.I):
            if not (project/'public'/x).is_file() and not (root/x).is_file(): missing.add(x)
    if isinstance(data,dict): audit(data)
    if missing: raise ValueError('Missing assets: '+', '.join(sorted(missing)))
    browser=Path(args.browser).expanduser()
    if not browser.is_file(): raise ValueError('Native Chrome was not found. Supply --browser; do not silently claim GPU acceleration with the software-only headless shell.')
    entry=next((str(p.relative_to(project)) for p in [project/'src/index.ts',project/'src/index.tsx',project/'src/index.js'] if p.is_file()),None)
    if not entry: raise ValueError('No Remotion entrypoint; adapt this package explicitly')
    config={'audio_delivery_policy':POLICY,'browser':str(browser),'gl':'angle','image_format':'jpeg','jpeg_quality':90,'crf':18,'preset':'veryfast','slice_frames':int(fps*60),'concurrency':1,'disable_shared_memory_capture':True}
    stamp=fingerprint(project,audio,meta_path); cfg=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()[:6]
    run=root/'.moonveil-render'/f'{stamp[:12]}-{cfg}'; run.mkdir(parents=True,exist_ok=True)
    title=args.title or root.name
    plan={'version':1,'root':str(root),'project':str(project),'entry':entry,'metadata':str(meta_path),'audio':str(audio),'audio_duration':audio_secs,'video_duration':secs,'fps':fps,'units':units,'title':title,'source_hash':stamp,'input_signature':signature(project,audio,meta_path),'config':config,'run_dir':str(run),'final':str(root/f'{title}_完整有声版_{stamp[:8]}.mp4')}
    write(run/'plan.json',plan)
    if not (run/'settings.json').exists(): write(run/'settings.json',{'jobs':args.jobs})
    print(json.dumps({'plan':str(run/'plan.json'),'units':len(units),'frames':sum(u['frames'] for u in units),'audio_seconds':audio_secs,'video_seconds':secs,'audio_delta':round(audio_secs-secs,3)},ensure_ascii=False))

def make_jobs(plan):
    jobs=[]; run=Path(plan['run_dir']); step=plan['config']['slice_frames']
    for u in plan['units']:
        for i,a in enumerate(range(0,u['frames'],step)):
            jobs.append({'key':f"{u['id']}_s{i:03d}",'unit':u['id'],'composition':u['composition'],'a':a,'b':min(a+step,u['frames'])-1})
    for j in jobs: j['frames']=j['b']-j['a']+1
    return jobs

class Queue:
    def __init__(self,plan_path):
        self.plan_path=Path(plan_path).resolve(); self.p=read(self.plan_path); self.run=Path(self.p['run_dir']); self.project=Path(self.p['project'])
        self.lock=threading.RLock();self.stop=threading.Event();self.processes={};self.jobs=make_jobs(self.p)
        for d in ['chunks','logs','units']: (self.run/d).mkdir(exist_ok=True)
        self.s={'run_id':self.run.name,'title':self.p['title'],'pid':os.getpid(),'plan':str(self.plan_path),'started':time.time(),'stage':'rendering','total_frames':sum(j['frames'] for j in self.jobs),'total_slices':len(self.jobs),'completed_frames':0,'completed_keys':[],'active':{},'failed':[],'slices':self.jobs,'final':None}
        self.ports=self.find_ports()
    def find_ports(self):
        for base in range(6200,9000,20):
            sockets=[]
            try:
                for i in range(8):
                    s=socket.socket();s.bind(('127.0.0.1',base+i));sockets.append(s)
                return base
            except OSError: pass
            finally:
                for s in sockets:s.close()
        raise RuntimeError('No free range of rendering ports')
    def save(self): write(self.run/'state.json',self.s)
    def desired(self): return max(1,min(8,int(read(self.run/'settings.json').get('jobs',6))))
    def cancel(self,*_):
        self.stop.set()
        with self.lock:
            for proc in list(self.processes.values()):
                try:os.killpg(proc.pid,signal.SIGTERM)
                except ProcessLookupError:pass
    def command(self,cmd,log,job=None):
        with Path(log).open('w') as f:
            proc=subprocess.Popen(cmd,cwd=self.project,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
            with self.lock:self.processes[proc.pid]=proc
            previous=-1;last_change=time.time()
            while proc.poll() is None:
                if self.stop.wait(1):
                    try:os.killpg(proc.pid,signal.SIGTERM)
                    except ProcessLookupError:pass
                    try:proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                    break
                if job:
                    with Path(log).open('rb') as r:r.seek(0,2);size=r.tell();r.seek(max(0,size-8192));tail=r.read().decode(errors='replace')
                    hits=re.findall(r'Rendered (\d+)/(\d+)',tail);n=int(hits[-1][0]) if hits else 0
                    if n!=previous:previous=n;last_change=time.time()
                    with self.lock:
                        self.s['active'][job['key']]['current']=min(n,job['frames']);self.save()
                    if time.time()-last_change>180:
                        print('STALLED',job['key'],flush=True)
                        try:os.killpg(proc.pid,signal.SIGTERM);proc.wait(timeout=10)
                        except ProcessLookupError:pass
                        except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                        break
            with self.lock:self.processes.pop(proc.pid,None)
            return proc.returncode==0 and not self.stop.is_set()
    def render(self,j):
        key=j['key'];dst=self.run/'chunks'/(key+'.mp4')
        if video_ok(dst,j['frames']):
            with self.lock:self.s['completed_keys'].append(key);self.s['completed_frames']+=j['frames'];self.save()
            return True
        while not self.stop.is_set():
            with self.lock:
                if len(self.s['active'])<self.desired():
                    self.s['active'][key]={**j,'current':0,'start':time.time(),'attempt':1};self.save();break
            self.stop.wait(1)
        if self.stop.is_set():return False
        cfg=self.p['config'];idx=int(threading.current_thread().name.rsplit('_',1)[-1]);partial=dst.with_name(key+'.partial.mp4')
        try:
            for attempt in range(1,4):
                if self.stop.is_set():return False
                if signature(self.project,self.p['audio'],self.p['metadata'])!=self.p['input_signature']:
                    with self.lock:
                        current_signature=signature(self.project,self.p['audio'],self.p['metadata'])
                        if current_signature!=self.p['input_signature']:
                            if fingerprint(self.project,self.p['audio'],self.p['metadata'])!=self.p['source_hash']:
                                raise RuntimeError('Project inputs changed during rendering. Stop and prepare a new source revision.')
                            self.p['input_signature']=current_signature
                            write(self.run/'plan.json',self.p)
                with self.lock:self.s['active'][key].update(current=0,start=time.time(),attempt=attempt);self.save()
                cmd=[str(self.project/'node_modules/.bin/remotion'),'render',self.p['entry'],j['composition'],str(partial),f"--frames={j['a']}-{j['b']}",f"--concurrency={cfg['concurrency']}",f'--port={self.ports+idx}',f"--gl={cfg['gl']}",'--disable-shared-memory-capture',f"--browser-executable={cfg['browser']}",'--muted','--codec=h264',f"--crf={cfg['crf']}",f"--x264-preset={cfg['preset']}",f"--image-format={cfg['image_format']}",f"--jpeg-quality={cfg['jpeg_quality']}",'--log=info','--overwrite']
                print('START',key,'attempt',attempt,flush=True)
                if self.command(cmd,self.run/'logs'/f'{key}_attempt{attempt}.log',j) and video_ok(partial,j['frames']):
                    partial.replace(dst)
                    with self.lock:self.s['completed_keys'].append(key);self.s['completed_frames']+=j['frames']
                    print('DONE',key,flush=True);return True
                if self.stop.wait(2):return False
            raise RuntimeError('Three render attempts failed')
        except Exception as e:
            with self.lock:self.s['failed'].append({'key':key,'error':str(e)})
            print('FAILED',key,str(e),flush=True);return False
        finally:
            with self.lock:self.s['active'].pop(key,None);self.save()
    def concat(self,paths,dest,name):
        listing=self.run/(name+'.txt');listing.write_text(''.join("file '"+str(p).replace("'","'\\''")+"'\n" for p in paths))
        cmd=['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-map','0:v:0','-c','copy',str(dest)]
        if not self.command(cmd,self.run/'logs'/(name+'.log')):raise RuntimeError('Concat failed: '+name)
    def assemble(self):
        self.s['stage']='assembling';self.save();unit_files=[]
        for u in self.p['units']:
            dst=self.run/'units'/(u['id']+'.mp4');parts=[self.run/'chunks'/(j['key']+'.mp4') for j in self.jobs if j['unit']==u['id']]
            self.concat(parts,dst,'concat_'+u['id'])
            if not video_ok(dst,u['frames']):raise RuntimeError('Unit frame count mismatch: '+u['id'])
            unit_files.append(dst)
        video=self.run/'video_only.mp4';self.concat(unit_files,video,'concat_full')
        final=Path(self.p['final']);partial=final.with_name(final.stem+'.partial.mp4')
        self.s['stage']='muxing';self.save()
        cmd=make_mux_command(video,self.p['audio'],partial)
        if not self.command(cmd,self.run/'logs/mux.log'):raise RuntimeError('Final audio mux failed')
        self.s['stage']='verifying';self.save();meta=probe(partial)
        if not video_ok(partial,self.s['total_frames']):raise RuntimeError('Final frame count mismatch')
        audio_check=verify_audio_delivery(partial,self.p['audio'],video)
        if self.stop.is_set():raise InterruptedError('Stopped before final delivery')
        partial.replace(final);write(self.run/'verification.json',{'metadata':meta,'audio_delivery':audio_check,'audio_hash_match':audio_check['audio_hash_match'],'expected_frames':self.s['total_frames']})
        self.s.update(stage='complete',final=str(final),finished=time.time());self.save();print('FINAL',final,flush=True)
    def run_all(self):
        if signature(self.project,self.p['audio'],self.p['metadata'])!=self.p['input_signature']:raise RuntimeError('Source changed since prepare. Prepare a fresh revision first.')
        signal.signal(signal.SIGTERM,self.cancel);signal.signal(signal.SIGINT,self.cancel)
        with (self.run/'queue.lock').open('w') as f:
            try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise RuntimeError('This render revision already has a running queue')
            self.save()
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(self.render,self.jobs))
                if self.stop.is_set():self.s['stage']='stopped';self.save();return
                if not all(results):raise RuntimeError('Some slices failed; rerun this plan to resume')
                self.assemble()
            except Exception as e:
                self.s.update(stage='stopped' if self.stop.is_set() else 'failed',error=str(e));self.save();raise

def stop_queue(plan_path):
    p=read(plan_path);s=read(Path(p['run_dir'])/'state.json');pid=s.get('pid')
    args=subprocess.run(['ps','-p',str(pid),'-o','args='],capture_output=True,text=True).stdout
    if str(Path(plan_path).resolve()) not in args:raise RuntimeError('Recorded process is absent or belongs to another command; no signal was sent')
    os.kill(pid,signal.SIGTERM);print('Stop requested; completed slices are retained')

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('project');p.add_argument('--audio');p.add_argument('--timeline');p.add_argument('--title');p.add_argument('--browser',default=BROWSER);p.add_argument('--jobs',type=int,default=6)
    for name in ['run','stop','status']:
        p=sub.add_parser(name);p.add_argument('plan')
    p=sub.add_parser('jobs');p.add_argument('plan');p.add_argument('count',type=int,choices=range(1,9))
    a=ap.parse_args()
    if a.command=='prepare':prepare(a)
    elif a.command=='run':Queue(a.plan).run_all()
    elif a.command=='stop':stop_queue(a.plan)
    elif a.command=='status':print(json.dumps(read(Path(read(a.plan)['run_dir'])/'state.json'),ensure_ascii=False,indent=2))
    elif a.command=='jobs':write(Path(read(a.plan)['run_dir'])/'settings.json',{'jobs':a.count});print('Requested parallel slices:',a.count,'; active slices finish without interruption when reducing')
if __name__=='__main__':main()
