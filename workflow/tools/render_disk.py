"""Use the validated skill queue, muxing directly from chunks to conserve disk space."""
import importlib.util,pathlib,sys,json,subprocess,time
S=pathlib.Path(__file__).resolve().with_name('render.py');spec=importlib.util.spec_from_file_location('moonveil_render_core',S);core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
class FullFilmQueue(core.Queue):
 def assemble(self):
  self.s['stage']='assembling';self.save()
  parts=[self.run/'chunks'/(j['key']+'.mp4') for j in self.jobs]
  for j,f in zip(self.jobs,parts):
   if not core.video_ok(f,j['frames']):raise RuntimeError('Invalid slice before final assembly: '+j['key'])
  listing=self.run/'ordered_chunks.txt';listing.write_text(''.join("file '"+str(f).replace("'","'\\''")+"'\n" for f in parts))
  final=pathlib.Path(self.p['final']);partial=final.with_name(final.stem+'.partial.mp4');self.s['stage']='muxing';self.save()
  cmd=core.make_mux_command(listing,self.p['audio'],partial,video_input_args=['-f','concat','-safe','0'])
  if not self.command(cmd,self.run/'logs/final_mux.log'):raise RuntimeError('Final sound-and-picture assembly failed')
  self.s['stage']='verifying';self.save();meta=core.probe(partial)
  if not core.video_ok(partial,self.s['total_frames']):raise RuntimeError('Final video frame count mismatch')
  audio_check=core.verify_audio_delivery(partial,self.p['audio'])
  if self.stop.is_set():raise InterruptedError('Stopped before final delivery')
  partial.replace(final);core.write(self.run/'verification.json',{'metadata':meta,'audio_delivery':audio_check,'audio_hash_match':audio_check['audio_hash_match'],'expected_frames':self.s['total_frames'],'assembly':'direct_from_ordered_chunks'})
  self.s.update(stage='complete',final=str(final),finished=time.time());self.save();print('FINAL_READY',final,flush=True)
if __name__=='__main__':FullFilmQueue(sys.argv[1]).run_all()
