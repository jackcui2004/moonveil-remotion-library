"""Copy manifest-selected assets into a real public directory and verify hashes."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,shutil

def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def materialize(project,entries):
 root=Path(project).resolve();public=root/'public'
 if public.is_symlink():raise ValueError('public must be a real directory')
 public.mkdir(parents=True,exist_ok=True);result=[]
 for item in entries:
  rel=PurePosixPath(item['public'])
  if rel.is_absolute()or '..'in rel.parts:raise ValueError('Destination must stay inside public')
  src=Path(item['source']);src=(root/src).resolve()if not src.is_absolute()else src.resolve()
  dst=public.joinpath(*rel.parts)
  if not src.is_file():raise ValueError('Missing source: '+str(src))
  parent=public
  for part in rel.parts[:-1]:
   parent=parent/part
   if parent.is_symlink():raise ValueError('Symlinked parent: '+str(parent))
  dst.parent.mkdir(parents=True,exist_ok=True);expected=sha(src)
  if dst.is_symlink():dst.unlink()
  if dst.exists():
   if sha(dst)!=expected:raise ValueError('Existing file differs; use a new revision: '+str(dst))
  else:
   tmp=dst.with_name(dst.name+'.materializing');shutil.copy2(src,tmp)
   if sha(tmp)!=expected:raise ValueError('Copy hash mismatch')
   tmp.replace(dst)
  result.append(dict(asset_id=item['id'],public=item['public'],sha256=expected,bytes=dst.stat().st_size,real_file=True))
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--project',default='.');p.add_argument('--report',default='materialized-assets.json');a=p.parse_args();data=json.loads(Path(a.manifest).read_text());result=materialize(a.project,data['assets']);Path(a.report).write_text(json.dumps(result,ensure_ascii=False,indent=2));print('Verified real media files:',len(result))
