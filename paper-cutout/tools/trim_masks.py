"""Keep the original RGB and apply reviewed native-instance alpha masks."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image

def derive(source,masks,output):
 source=Path(source).resolve();masks=Path(masks).resolve();output=Path(output).resolve()
 if output.exists():raise ValueError('Use a new output revision; do not overwrite previous layers')
 output.mkdir(parents=True)
 catalog={}
 for p in sorted(masks.glob('*.json')):
  meta=json.loads(p.read_text());aid=meta['parent_asset_id'];original=source/(aid+'.png')
  rgb=Image.open(original).convert('RGBA');items=[]
  for entry in meta['instances']:
   mask=Image.open(masks/entry['file']).convert('RGBA')
   if mask.size!=rgb.size:raise ValueError('Mask/source dimensions differ: '+aid)
   alpha=mask.getchannel('A');box=alpha.getbbox()
   if not box:continue
   box=(max(0,box[0]-3),max(0,box[1]-3),min(rgb.width,box[2]+3),min(rgb.height,box[3]+3))
   layer=rgb.copy();layer.putalpha(alpha);layer=layer.crop(box);name=f"{aid}-piece-{entry['instance']}.png";layer.save(output/name)
   items.append(dict(parent_asset_id=aid,parent_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),instance=entry['instance'],file=name,bbox=list(box),width=layer.width,height=layer.height,rgb_from_unchanged_parent=True,visually_checked=False))
  catalog[aid]=items
 (output/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2))
 return catalog

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--masks',required=True);p.add_argument('--output',required=True);a=p.parse_args();result=derive(a.source,a.masks,a.output);print(json.dumps({'parents':len(result),'layers':sum(map(len,result.values())),'visual_review_required':True}))
