import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

TOOLS=Path(__file__).resolve().parents[1]/'tools'
spec=importlib.util.spec_from_file_location('audio_delivery',TOOLS/'audio_delivery.py')
audio=importlib.util.module_from_spec(spec);spec.loader.exec_module(audio)
def ff(*args):subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True)

class AudioDeliveryIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.r=Path(cls.tmp.name)
        cls.video=cls.r/'video.mp4';cls.mp3=cls.r/'voice.mp3';cls.aac=cls.r/'voice.m4a'
        ff('-f','lavfi','-i','color=c=0x284146:s=320x180:r=30:d=6','-an','-c:v','libx264','-pix_fmt','yuv420p',cls.video)
        ff('-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=6','-c:a','libmp3lame',cls.mp3)
        ff('-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=6','-c:a','aac','-profile:a','aac_low',cls.aac)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_mp3_becomes_aac_lc_and_keeps_video(self):
        out=self.r/'converted.mp4';r=audio.mux(self.video,self.mp3,out)
        self.assertEqual(r['mode'],'encode_aac_lc');self.assertEqual(r['delivery_profile'],'LC')
        self.assertTrue(r['audio_default']);self.assertTrue(r['full_audio_decode_passed']);self.assertTrue(r['video_packet_hash_match'])
        self.assertIsNone(r['audio_hash_match']);self.assertEqual(len(r['sample_windows']),3)
    def test_compatible_aac_is_copied(self):
        r=audio.mux(self.video,self.aac,self.r/'copied.mp4')
        self.assertEqual(r['mode'],'copy_aac_lc');self.assertTrue(r['audio_hash_match']);self.assertTrue(r['video_packet_hash_match'])
    def test_old_mp3_in_mp4_is_rejected(self):
        out=self.r/'legacy.mp4';ff('-i',self.video,'-i',self.mp3,'-map','0:v:0','-map','1:a:0','-c','copy',out)
        with self.assertRaisesRegex(ValueError,'AAC-LC'):audio.verify_audio_delivery(out,self.mp3,self.video)
    def test_missing_audio_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'Missing audio'):audio.mux(self.video,self.video,self.r/'missing.mp4')
    def test_silent_track_does_not_replace_existing_delivery(self):
        silent=self.r/'silent.wav';ff('-f','lavfi','-i','anullsrc=r=48000:cl=mono','-t','6',silent)
        out=self.r/'preserved.mp4';out.write_bytes(b'prior-delivery')
        with self.assertRaisesRegex(ValueError,'silent'):audio.mux(self.video,silent,out)
        self.assertEqual(out.read_bytes(),b'prior-delivery');self.assertFalse(list(self.r.glob('*.partial.mp4')))
    def test_truncated_narration_is_rejected(self):
        out=self.r/'short.mp4';ff('-i',self.video,'-i',self.mp3,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-t','2',out)
        with self.assertRaisesRegex(ValueError,'duration mismatch'):audio.verify_audio_delivery(out,self.mp3,self.video)
    def test_wrong_narration_is_rejected(self):
        wrong=self.r/'wrong.m4a';ff('-f','lavfi','-i','sine=frequency=880:sample_rate=48000:duration=6','-c:a','aac',wrong)
        out=self.r/'wrong.mp4';ff('-i',self.video,'-i',wrong,'-map','0:v:0','-map','1:a:0','-c','copy',out)
        with self.assertRaisesRegex(ValueError,'waveform/level'):audio.verify_audio_delivery(out,self.mp3,self.video)
    def test_source_cannot_be_overwritten(self):
        with self.assertRaisesRegex(ValueError,'overwrite source'):audio.mux(self.video,self.mp3,self.video)


class QueueAssemblyIntegration(unittest.TestCase):
    setUpClass=classmethod(AudioDeliveryIntegration.setUpClass.__func__)
    tearDownClass=classmethod(AudioDeliveryIntegration.tearDownClass.__func__)
    # Exercise both real queue entrypoints; no browser, fake command strings, or Remotion render required.
    def queue(self, filename):
        spec=importlib.util.spec_from_file_location('queue_under_test',TOOLS/filename);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        cls=module.Queue if filename=='render.py' else module.FullFilmQueue
        import json
        run_dir=self.r/filename.replace('.py','');run_dir.mkdir(exist_ok=True);project=self.r
        plan={'run_dir':str(run_dir),'project':str(project),'root':str(project),'title':'AAC regression','final':str(run_dir/'final.mp4'),
              'audio':str(self.mp3),'audio_duration':float(audio.probe(self.mp3)['format']['duration']),'fps':30,
              'config':{'slice_frames':180},'units':[{'id':'test','composition':'test','frames':180}]}
        plan_path=run_dir/'plan.json';plan_path.write_text(json.dumps(plan));q=cls(plan_path)
        import shutil
        shutil.copy2(self.video,run_dir/'chunks/test_s000.mp4');q.assemble()
        self.assertEqual(q.s['stage'],'complete');report=json.loads((run_dir/'verification.json').read_text());self.assertEqual(report['audio_delivery']['mode'],'encode_aac_lc');self.assertIsNone(report['audio_hash_match'])
    def test_standard_queue_applies_audio_gate(self):self.queue('render.py')
    def test_direct_chunk_queue_applies_audio_gate(self):self.queue('render_disk.py')

if __name__=='__main__':unittest.main()
