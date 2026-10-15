"""Real PTY create/type/save/pan/move/autosave test; no third-party dependencies.
Event-driven: waits for screen output and polls for files, so slow machines pass."""
import json,os,pty,subprocess,fcntl,termios,struct,time,select,tempfile
from pathlib import Path

def main():
 m,s=pty.openpty();fcntl.ioctl(s,termios.TIOCSWINSZ,struct.pack('HHHH',30,80,0,0));before=termios.tcgetattr(s)
 with tempfile.TemporaryDirectory() as d:
  p=subprocess.Popen(['python3',str(Path(__file__).with_name('postlight.py')),'myboard'],stdin=s,stdout=s,stderr=s,cwd=d,env=dict(os.environ,TERM='xterm-256color',LANG='C.UTF-8'));out=b''
  def collect(sec):
   nonlocal out
   end=time.monotonic()+sec
   while time.monotonic()<end:
    if select.select([m],[],[],.02)[0]:out+=os.read(m,65536)
  def wait_out(token,sec=10):
   nonlocal out
   end=time.monotonic()+sec
   while time.monotonic()<end:
    if token in out:return True
    collect(.1)
   raise AssertionError('missing output: '+str(token))
  def wait_file(path,sec=15):
   end=time.monotonic()+sec
   while time.monotonic()<end:
    if Path(path).exists():return True
    time.sleep(.1)
   raise AssertionError('missing file: '+str(path))
  wait_out(b'POSTLIGHT')                       # app is up before any key
  os.write(m,b'\n')                            # Enter creates a yellow note, drops into typing
  wait_out(b'Type, Enter saves')
  os.write(m,b'buy milk');collect(1.0)
  os.write(m,b'\n')                            # Enter saves the note + autosaves the board
  saved=Path(d)/'myboard.postlight'
  wait_file(saved)                             # autosave really writes immediately after commit
  data=json.loads(saved.read_text())
  assert data['notes'][0]['text']=='buy milk' and data['notes'][0]['color']==0,(data)
  os.write(m,b'\x1bOC\x1bOC\x1bOB');collect(.2)  # application-mode arrows pan the view
  os.write(m,b'ddd')                           # WASD moves the selected note
  wait_out(b'Saved')
  os.write(m,b'c')                             # color cycle extra
  wait_out(b'Color changed')
  fcntl.ioctl(s,termios.TIOCSWINSZ,struct.pack('HHHH',12,40,0,0));os.kill(p.pid,28)
  wait_out(b'Resize to 50x16')
  fcntl.ioctl(s,termios.TIOCSWINSZ,struct.pack('HHHH',30,80,0,0));os.kill(p.pid,28);collect(.2)
  with open('/tmp/postlight-terminal.ansi','wb') as f:f.write(out)
  os.write(m,b'Q')
  p.wait(timeout=10)
  assert p.returncode==0 and termios.tcgetattr(s)==before
  final=json.loads(saved.read_text())
  n=final['notes'][0]
  assert n['x']==35 and n['color']==1,(n)   # center 29 + 3 WASD moves, one color cycle
 os.close(m);os.close(s);print('PTY enter-create/type/enter-save/pan/WASD-move/autosave/resize/quit PASS')
if __name__=='__main__':main()
