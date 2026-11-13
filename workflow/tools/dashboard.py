#!/usr/bin/env python3
"""Read-only local render dashboard. Never opens cloud accounts or sends messages."""
import argparse, collections, json, pathlib, time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

def main():
    ap=argparse.ArgumentParser();ap.add_argument('plan');ap.add_argument('--port',type=int,default=3033);args=ap.parse_args()
    plan=json.loads(pathlib.Path(args.plan).read_text());run=pathlib.Path(plan['run_dir'])
    html=pathlib.Path(__file__).resolve().parents[1]/'assets/progress.html';history=collections.deque(maxlen=120)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_):pass
        def send(self,code,data,mime):
            self.send_response(code);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
        def do_GET(self):
            if self.path.split('?')[0]=='/':return self.send(200,html.read_bytes(),'text/html; charset=utf-8')
            if self.path.split('?')[0]!='/api/progress':return self.send(404,b'Not found','text/plain')
            try:
                d=json.loads((run/'state.json').read_text());now=time.time()
                if getattr(self.server,'started',None)!=d['started']:history.clear();self.server.started=d['started']
                active=[dict(v,total=v['frames'],elapsed=now-v['start']) for v in d['active'].values()]
                done=d['completed_frames']+sum(v['current'] for v in active)
                history.append((now,done));base=next((h for h in history if now-h[0]<=60),history[0]);dt=now-base[0]
                speed=max(0,(done-base[1])/dt) if dt>=15 else None
                eta=(d['total_frames']-done)/speed if d['stage']=='rendering' and speed and speed>.05 else None
                result={**d,'complete':len(d['completed_keys']),'total':d['total_slices'],'active_jobs':active,'percentage':100*done/max(1,d['total_frames']),'done_frames':done,'elapsed':now-d['started'],'speed':speed,'eta':eta,'updated':now}
                self.send(200,json.dumps(result,ensure_ascii=False).encode(),'application/json; charset=utf-8')
            except (OSError,ValueError) as e:self.send(503,json.dumps({'error':str(e)}).encode(),'application/json')
    server=None
    for port in range(args.port,args.port+30):
        try:server=ThreadingHTTPServer(('127.0.0.1',port),Handler);break
        except OSError:continue
    if server is None:raise RuntimeError('No free dashboard port')
    print(json.dumps({'url':f'http://localhost:{server.server_port}/','plan':str(pathlib.Path(args.plan).resolve())}),flush=True)
    server.serve_forever()
if __name__=='__main__':main()
