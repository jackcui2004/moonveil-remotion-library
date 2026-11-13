#!/usr/bin/env python3
"""AAC-LC MP4 delivery gate. Python stdlib + FFmpeg; never re-encode video."""
import argparse
from array import array
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile

POLICY = 'mp4-aac-lc-v1'

def run(args):
    return subprocess.run(args, capture_output=True, check=True)

def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]).stdout)

def stream(meta, kind):
    streams = [s for s in meta['streams'] if s.get('codec_type') == kind]
    if not streams:
        raise ValueError('Missing ' + kind + ' stream')
    return streams[0]

def seconds(meta, track):
    return float(track.get('duration') or meta['format']['duration'])

def packet_hash(path, selector):
    return run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', selector,
                '-c', 'copy', '-f', 'hash', '-hash', 'sha256', '-']).stdout.decode().strip()

def audio_policy(master):
    a = stream(probe(master), 'audio')
    compatible = (a.get('codec_name') == 'aac' and a.get('profile') == 'LC'
                  and int(a.get('sample_rate', 0)) in (44100, 48000)
                  and int(a.get('channels', 0)) in (1, 2))
    return {'policy': POLICY, 'mode': 'copy_aac_lc' if compatible else 'encode_aac_lc',
            'source_codec': a.get('codec_name'), 'source_profile': a.get('profile'),
            'source_channels': a.get('channels'), 'source_sample_rate': a.get('sample_rate')}

def make_mux_command(video, master, output, video_input_args=None):
    if Path(output).resolve() in (Path(video).resolve(), Path(master).resolve()):
        raise ValueError('Output must be distinct from source media')
    policy = audio_policy(master)
    cmd = ['ffmpeg', '-y', '-v', 'error', *(video_input_args or []), '-i', str(video), '-i', str(master),
           '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy']
    if policy['mode'] == 'copy_aac_lc':
        cmd += ['-c:a', 'copy']
    else:
        cmd += ['-c:a', 'aac', '-profile:a', 'aac_low', '-b:a', '192k', '-ar', '48000',
                '-ac', str(min(2, int(policy['source_channels'])))]
    return cmd + ['-disposition:a:0', 'default', '-movflags', '+faststart', str(output)]

def pcm(path, start, duration):
    # Accurate input seeking and a common mono analysis rate; delivery itself is not retimed.
    data = run(['ffmpeg', '-v', 'error', '-ss', str(start), '-i', str(path),
                '-map', '0:a:0', '-t', str(duration), '-vn', '-ac', '1', '-ar', '8000',
                '-f', 'f32le', '-']).stdout
    values = array('f'); values.frombytes(data)
    if sys.byteorder != 'little': values.byteswap()
    return values

def correlation(a, b):
    n = min(len(a), len(b))
    if n < 100: raise ValueError('Audio sample is unexpectedly short')
    a, b = a[:n:4], b[:n:4]
    def score(x, y):
        n = min(len(x), len(y)); x=x[:n]; y=y[:n]
        mx=sum(x)/n; my=sum(y)/n
        xx=sum((v-mx)**2 for v in x); yy=sum((v-my)**2 for v in y)
        if xx < 1e-12 or yy < 1e-12: return None
        return sum((u-mx)*(v-my) for u,v in zip(x,y))/math.sqrt(xx*yy)
    direct=score(a,b)
    if direct is None or direct >= .98: return direct, 0
    # Bounded resampler/codec seek tolerance, recorded rather than hidden.
    best=(direct,0)
    for lag in range(-80,81):
        x,y=(a[-lag:],b[:lag]) if lag<0 else (a[:-lag],b[lag:]) if lag else (a,b)
        value=score(x,y)
        if value is not None and value>best[0]: best=(value,lag/2000)
    return best

def verify_audio_delivery(output, master, video_source=None):
    policy=audio_policy(master); source=probe(master); final=probe(output)
    a=stream(final,'audio'); stream(final,'video'); sa=stream(source,'audio')
    if len([s for s in final['streams'] if s.get('codec_type')=='audio']) != 1:
        raise ValueError('Delivery must contain exactly one selected full audio track')
    if a.get('codec_name')!='aac' or a.get('profile')!='LC':
        raise ValueError('Delivery audio is not AAC-LC; MP3-in-MP4 is rejected')
    if not a.get('disposition',{}).get('default'):
        raise ValueError('Audio track is not selected as default')
    if int(a.get('sample_rate',0)) not in (44100,48000) or int(a.get('channels',0)) not in (1,2):
        raise ValueError('Unsupported delivery audio rate/channel count')
    duration=seconds(source,sa); final_duration=seconds(final,a)
    if abs(final_duration-duration)>.12:
        raise ValueError('Narration duration mismatch; do not trim or stretch to hide it')
    video_duration=seconds(final,stream(final,'video'))
    if abs(video_duration-duration)>1:
        raise ValueError('Video/narration length mismatch exceeds one second')
    # Fully decode the delivered audio and measure real samples, not just container metadata.
    result=run(['ffmpeg','-hide_banner','-nostats','-xerror','-threads','2','-i',str(output),
                '-map','0:a:0','-vn','-af','volumedetect','-f','null','-'])
    match=re.search(r'max_volume:\s*([-\d.]+|-inf) dB',result.stderr.decode(errors='replace'))
    if not match or float(match[1]) < -80:
        raise ValueError('Decoded narration is silent or effectively silent')
    windows=[]; length=min(5,duration/3)
    starts=sorted(set([0, max(0,duration/2-length/2), max(0,duration-length)]))
    for start in starts:
        src=pcm(master,start,length); dst=pcm(output,start,length)
        if abs(len(src)-len(dst))>800:
            raise ValueError('Audio sample length mismatch')
        rms=lambda x:math.sqrt(sum(v*v for v in x)/max(1,len(x)))
        sr,dr=rms(src),rms(dst); corr,lag=correlation(src,dst)
        if sr>1e-5 and (dr<sr*.8 or dr>sr*1.2 or corr is None or corr<.98):
            raise ValueError('Narration waveform/level mismatch near %.3fs'%start)
        if sr<=1e-5 and dr>1e-3:
            raise ValueError('Unexpected audio in a source-silent window')
        windows.append({'start_seconds':round(start,6),'seconds':length,'source_rms':sr,
                        'delivery_rms':dr,'correlation':corr,'seek_lag_seconds':lag,
                        'source_silent':sr<=1e-5})
    same=None
    if policy['mode']=='copy_aac_lc':
        same=packet_hash(output,'0:a:0')==packet_hash(master,'0:a:0')
        if not same: raise ValueError('Copied AAC packet hash mismatch')
    video_same=None
    if video_source:
        video_same=packet_hash(output,'0:v:0')==packet_hash(video_source,'0:v:0')
        if not video_same: raise ValueError('Video stream was changed during audio mux')
    return {**policy,'delivery_codec':'aac','delivery_profile':'LC','audio_default':True,
            'source_duration_seconds':duration,'delivery_duration_seconds':final_duration,
            'full_audio_decode_passed':True,'max_volume_dbfs':float(match[1]),
            'audio_hash_match':same,'audio_hash_note':'Only required for copied AAC; not applicable to lossy transcoding',
            'video_packet_hash_match':video_same,'sample_windows':windows,
            'target_player_listening_verified':False}

def mux(video, master, output, report=None):
    output=Path(output); output.parent.mkdir(parents=True,exist_ok=True)
    if output.resolve() in (Path(video).resolve(),Path(master).resolve()):
        raise ValueError('Refusing to overwrite source media')
    with tempfile.NamedTemporaryFile(dir=output.parent,prefix=output.stem+'.',suffix='.partial.mp4',delete=False) as f:
        partial=Path(f.name)
    try:
        run(make_mux_command(video,master,partial))
        result=verify_audio_delivery(partial,master,video)
        partial.replace(output)  # Publish only after the gate passes; leave prior delivery intact on failure.
        if report: Path(report).write_text(json.dumps(result,ensure_ascii=False,indent=2))
        return result
    finally:
        partial.unlink(missing_ok=True)

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('command',choices=['mux','verify'])
    p.add_argument('--video'); p.add_argument('--audio',required=True); p.add_argument('--output',required=True); p.add_argument('--report')
    args=p.parse_args()
    if args.command=='mux':
        if not args.video: p.error('--video is required for mux')
        result=mux(args.video,args.audio,args.output,args.report)
    else:
        result=verify_audio_delivery(args.output,args.audio,args.video)
        if args.report: Path(args.report).write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
