import unittest,tempfile,json,importlib.util,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'tools'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

class ToolsTest(unittest.TestCase):
 def test_alpha_uses_original_rgb_and_keeps_parent(self):
  with tempfile.TemporaryDirectory()as tmp:
   r=Path(tmp);src=r/'src';masks=r/'masks';src.mkdir();masks.mkdir();image=Image.new('RGBA',(20,20),(19,71,126,255));image.save(src/'A.png');before=(src/'A.png').read_bytes()
   fake=Image.new('RGBA',(20,20),(255,0,0,0))
   for y in range(5,15):
    for x in range(5,15):fake.putpixel((x,y),(255,0,0,255))
   fake.save(masks/'A-instance-1.png');(masks/'A.json').write_text(json.dumps({'parent_asset_id':'A','instances':[{'instance':1,'file':'A-instance-1.png'}]}))
   result=load('trim_masks').derive(src,masks,r/'out');layer=Image.open(r/'out'/result['A'][0]['file']);self.assertEqual(layer.getpixel((5,5))[:3],(19,71,126));self.assertEqual(layer.getpixel((0,0))[3],0);self.assertEqual((src/'A.png').read_bytes(),before);self.assertEqual(result['A'][0]['parent_sha256'],hashlib.sha256(before).hexdigest())
 def test_materializes_file_link_without_changing_original(self):
  with tempfile.TemporaryDirectory()as tmp:
   r=Path(tmp);(r/'public').mkdir();src=r/'original.mp3';src.write_bytes(b'original-media');dst=r/'public/full.mp3';dst.symlink_to(src);m=load('materialize_public');result=m.materialize(r,[{'id':'voice','source':'original.mp3','public':'full.mp3'}]);self.assertFalse(dst.is_symlink());self.assertEqual(dst.read_bytes(),src.read_bytes());self.assertEqual(result[0]['sha256'],hashlib.sha256(src.read_bytes()).hexdigest())
 def test_refuses_existing_different_file_and_destination_escape(self):
  with tempfile.TemporaryDirectory()as tmp:
   r=Path(tmp);(r/'public').mkdir();(r/'in.mp3').write_bytes(b'new');dst=r/'public/full.mp3';dst.write_bytes(b'keep');m=load('materialize_public')
   with self.assertRaises(ValueError):m.materialize(r,[{'id':'voice','source':'in.mp3','public':'full.mp3'}])
   self.assertEqual(dst.read_bytes(),b'keep')
   with self.assertRaises(ValueError):m.materialize(r,[{'id':'voice','source':'in.mp3','public':'../outside.mp3'}])
if __name__=='__main__':unittest.main()
