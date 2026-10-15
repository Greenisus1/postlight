import json,os,tempfile,unittest
from pathlib import Path
import postlight as a

class Tests(unittest.TestCase):
 def test_add(self):
  b=a.Board();n=b.add(2,3)
  self.assertEqual(n['id'],1);self.assertEqual(n['color'],0);self.assertEqual(len(b.notes),1)
 def test_color_wrap(self):
  b=a.Board();n=b.add(0,0,7);self.assertEqual(n['color'],7%len(a.COLORS))
 def test_title_cap(self):
  b=a.Board();n=b.add(0,0,0,'x'*100);self.assertEqual(len(n['title']),40)
 def test_remove(self):
  b=a.Board();n=b.add(0,0);b.remove(n['id']);self.assertEqual(b.notes,[])
 def test_get(self):
  b=a.Board();n=b.add(0,0);self.assertIs(b.get(n['id']),n);self.assertIsNone(b.get(99))
 def test_move(self):
  b=a.Board();n=b.add(5,5);b.move(n['id'],3,-2)
  self.assertEqual((n['x'],n['y']),(8,3))
 def test_move_bounds(self):
  b=a.Board();n=b.add(0,0);b.move(n['id'],-5,-5)
  self.assertEqual((n['x'],n['y']),(0,0))
  b.move(n['id'],600,600);self.assertEqual((n['x'],n['y']),(500,500))
 def test_save_suffix(self):
  with tempfile.TemporaryDirectory() as d:
   b=a.Board();b.add(1,2,1,'Hi','hello')
   p=b.save(Path(d)/'myboard')
   self.assertEqual(p.suffix,'.postlight');self.assertTrue(p.exists())
 def test_roundtrip(self):
  with tempfile.TemporaryDirectory() as d:
   b=a.Board();b.add(1,2,3,'Groceries','milk and eggs');b.add(9,4,0,'Ideas','build a robot')
   p=b.save(Path(d)/'b.postlight')
   c=a.Board();c.load(p)
   self.assertEqual(len(c.notes),2);self.assertEqual(c.notes[0]['title'],'Groceries');self.assertEqual(c.next_id,3)
 def test_load_rejects_non_postlight(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.postlight';p.write_text('{"format":"Other","notes":[]}')
   b=a.Board();self.assertRaises(ValueError,b.load,p)
 def test_load_cleans(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.postlight'
   p.write_text(json.dumps({'format':'Postlight','version':1,'notes':[{'id':5,'x':-3,'y':999999,'color':99,'title':'t'*100,'text':'ok'}]}))
   b=a.Board();b.load(p)
   n=b.notes[0];self.assertEqual(n['x'],0);self.assertEqual(n['color'],99%len(a.COLORS));self.assertEqual(len(n['title']),40);self.assertEqual(b.next_id,6)
 def test_load_bad_note(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.postlight';p.write_text(json.dumps({'format':'Postlight','version':1,'notes':['nope']}))
   self.assertRaises(ValueError,a.Board().load,p)
 def test_save_symlink_refused(self):
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/'real.postlight';target.write_text('{}')
   link=Path(d)/'link.postlight';os.symlink(target,link)
   self.assertRaises(OSError,a.Board().save,link)
 def test_data_format(self):
  b=a.Board();b.add(0,0)
  self.assertEqual(b.data()['format'],'Postlight');self.assertEqual(b.data()['version'],1)

class SpecTests(unittest.TestCase):
 def test_default_note_is_yellow(self):
  b=a.Board();n=b.add(4,4)
  self.assertEqual(a.COLORS[n['color']][0],'yellow')
 def test_atomic_save_no_tmp_left(self):
  import tempfile
  from pathlib import Path
  with tempfile.TemporaryDirectory() as d:
   b=a.Board();b.add(1,1,0,'A','body')
   p=b.save(Path(d)/'x')
   self.assertEqual([f.name for f in Path(d).iterdir()],['x.postlight'])
   self.assertEqual(json.loads(p.read_text())['notes'][0]['text'],'body')
 def test_default_name(self):
  self.assertEqual(a.DEFAULT_NAME,'board.postlight')

if __name__=='__main__':unittest.main()
