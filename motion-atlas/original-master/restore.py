#!/usr/bin/env python3
"""Verify and restore the original CRF18 full master from its binary parts."""
import hashlib,json,pathlib,sys,urllib.request
root=pathlib.Path(__file__).resolve().parent;m=json.loads((root/'manifest.json').read_text());dest=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else root/m['output']
if dest.exists():raise SystemExit('Output already exists; choose a fresh output path.')
base='https://jackcui2004.github.io/moonveil-remotion-library/motion-atlas/original-master/'
for r in m['parts']:
 p=root/r['file']
 if not p.exists():
  print('Downloading',r['file'],flush=True);urllib.request.urlretrieve(base+r['file'],p)
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 if p.stat().st_size!=r['bytes'] or h!=r['sha256']:raise SystemExit('Part verification failed: '+r['file'])
partial=dest.with_suffix(dest.suffix+'.partial');h=hashlib.sha256();n=0
with partial.open('wb') as out:
 for r in m['parts']:
  with (root/r['file']).open('rb') as f:
   for b in iter(lambda:f.read(1024*1024),b''):out.write(b);h.update(b);n+=len(b)
if h.hexdigest()!=m['sha256'] or n!=m['bytes']:raise SystemExit('Master verification failed; partial file retained.')
partial.replace(dest);print('Restored',dest)
