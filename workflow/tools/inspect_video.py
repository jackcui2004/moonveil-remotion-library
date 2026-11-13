#!/usr/bin/env python3
"""Small continuous-frame inspection: motion evidence, flash candidates, contact sheet.
Candidates are not verdicts; legitimate transitions and lighting may trigger them.
"""
import argparse,json,math,pathlib,subprocess

def main():
    ap=argparse.ArgumentParser();ap.add_argument('video');ap.add_argument('--start',type=float,default=0);ap.add_argument('--duration',type=float,default=2);ap.add_argument('--roi');ap.add_argument('--out',required=True);a=ap.parse_args()
    if a.start<0 or not 0<a.duration<=10:raise ValueError('Use a nonnegative start and a 0–10 second inspection window')
    out=pathlib.Path(a.out).expanduser().resolve();out.mkdir(parents=True,exist_ok=True);video=pathlib.Path(a.video).expanduser().resolve()
    meta=json.loads(subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate','-of','json',str(video)],capture_output=True,text=True,check=True).stdout)['streams'][0]
    num,den=map(int,meta['avg_frame_rate'].split('/'));fps=num/den;crop=''
    if a.roi:
        x,y,w,h=map(int,a.roi.split(':'))
        if min(x,y)<0 or min(w,h)<1 or x+w>meta['width'] or y+h>meta['height']:raise ValueError('ROI is outside the video frame')
        crop=f'crop={w}:{h}:{x}:{y},'
    base=['ffmpeg','-v','error','-ss',str(a.start),'-i',str(video),'-t',str(a.duration),'-an']
    r=subprocess.run(base+['-vf',crop+'scale=64:36:flags=area','-f','rawvideo','-pix_fmt','gray','-'],capture_output=True,check=True)
    size=64*36;frames=[r.stdout[i:i+size] for i in range(0,len(r.stdout)-size+1,size)]
    def diff(x,y):return sum(abs(i-j) for i,j in zip(x,y))/size
    pairs=[];step=max(1,round(fps*.5))
    for i in range(step,len(frames),step):
        prev=frames[i-step];curr=frames[i];pairs.append({'time':round(a.start+i/fps,4),'mean_abs_difference':round(diff(prev,curr),4),'changed_pixel_ratio':round(sum(abs(x-y)>8 for x,y in zip(prev,curr))/size,4)})
    flashes=[]
    for i in range(1,len(frames)-1):
        before=diff(frames[i-1],frames[i]);after=diff(frames[i],frames[i+1]);bridge=diff(frames[i-1],frames[i+1])
        if min(before,after)>7 and bridge<.35*(before+after):flashes.append(i)
    cols=10;rows=max(1,math.ceil(len(frames)/cols));sheet=out/'continuous_frames.jpg'
    subprocess.run(base+['-vf',crop+f'scale=160:90,tile={cols}x{rows}','-frames:v','1','-y',str(sheet)],check=True)
    candidates=[]
    for i in flashes[:6]:
        p=out/f'candidate_{i:04d}.png';subprocess.run(base+['-vf',crop+f'select=eq(n\\,{i})','-frames:v','1','-fps_mode','vfr','-y',str(p)],check=True);candidates.append(str(p))
    report={'video':str(video),'start':a.start,'duration':a.duration,'fps':fps,'frame_count':len(frames),'roi':a.roi,'motion_pairs':pairs,'isolated_flash_candidates':[{'relative_frame':i,'time':round(a.start+i/fps,4)} for i in flashes],'contact_sheet':str(sheet),'candidate_images':candidates,'interpretation':'Statistical candidates only; inspect actual images and narrative intent. Without a static-camera panel ROI, motion may come from captions or camera rather than the video subject.'}
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
