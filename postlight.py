#!/usr/bin/env python3
"""Original offline sticky-note board for the terminal. Saves FILENAME.postlight boards."""
import curses,json,os,sys,textwrap
from pathlib import Path
from ui import put,run
VERSION='1.0.0'
DEFAULT_NAME='board.postlight'
COLORS=[('yellow',220,3),('pink',213,5),('green',118,2),('blue',75,4),('orange',208,1)]
class Board:
 def __init__(self):
  self.notes=[];self.next_id=1
 def add(self,x,y,color=0,title='Note',text=''):
  n={'id':self.next_id,'x':x,'y':y,'color':color%len(COLORS),'title':title[:40],'text':text}
  self.next_id+=1;self.notes.append(n);return n
 def remove(self,nid):self.notes=[n for n in self.notes if n['id']!=nid]
 def get(self,nid):
  for n in self.notes:
   if n['id']==nid:return n
 def move(self,nid,dx,dy):
  n=self.get(nid)
  if not n:return False
  n['x']=max(0,min(500,n['x']+dx));n['y']=max(0,min(500,n['y']+dy));return True
 def data(self):return {'format':'Postlight','version':1,'notes':self.notes}
 def load(self,path):
  raw=json.loads(Path(path).read_text(encoding='utf-8'))
  if not isinstance(raw,dict) or raw.get('format')!='Postlight':raise ValueError('Not a Postlight board file.')
  notes=raw.get('notes')
  if not isinstance(notes,list):raise ValueError('Board has no notes list.')
  clean=[]
  for n in notes:
   if not isinstance(n,dict):raise ValueError('Bad note entry.')
   clean.append({'id':int(n['id']),'x':max(0,int(n['x'])),'y':max(0,int(n['y'])),
    'color':int(n['color'])%len(COLORS),'title':str(n['title'])[:40],'text':str(n['text'])[:4000]})
  self.notes=clean;self.next_id=max([n['id'] for n in clean],default=0)+1
 def save(self,path):
  p=Path(path)
  if p.suffix.lower()!='.postlight':p=p.with_suffix('.postlight')
  if p.is_symlink():raise OSError('Refusing to write through a symlink.')
  tmp=p.with_name('.'+p.name+'.tmp')
  fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'w',encoding='utf-8') as f:
   json.dump(self.data(),f,indent=2);f.flush();os.fsync(f.fileno())
  os.replace(tmp,p);return p
def palette():
 if not curses.has_colors():return False
 curses.start_color()
 for i,(name,c256,c8) in enumerate(COLORS,1):curses.init_pair(i,0,c256 if curses.COLORS>=256 else c8)
 return True
def draw_note(s,n,sx,sy,colors,selected,editing):
 def col(i):return curses.color_pair(i)|curses.A_BOLD if colors else 0
 a=col(n['color']+1)
 wdt=18;rows=textwrap.wrap(n['text'],wdt-2)[:4]
 for dy in range(6):put(s,sy+dy,sx,' '*wdt,a)
 put(s,sy,sx,' '+n['title'][:wdt-2],a|(curses.A_UNDERLINE if selected else 0))
 for i,row in enumerate(rows):put(s,sy+2+i,sx,' '+row,a)
 if editing:put(s,sy+5,sx+wdt-2,'>',a|curses.A_BOLD)
 elif selected:put(s,sy+5,sx+wdt-2,'*',a|curses.A_BOLD)
def play(s,board,path):
 h,w=s.getmaxyx();sel=board.notes[0]['id'] if board.notes else None
 colors=palette();ox=0;oy=0;mode='view';status='Enter new yellow note | Arrows pan | Tab select | WASD move | Q save+quit'
 def autosave():
  nonlocal status
  try:board.save(path);status='Saved '+str(path)
  except OSError as e:status='Save failed: '+str(e)
 while True:
  s.timeout(60);key=s.getch();h,w=s.getmaxyx();s.erase()
  if h<16 or w<50:put(s,1,1,'Resize to 50x16. Q quits.');s.refresh()
  else:
   put(s,0,2,'POSTLIGHT '+VERSION+' | '+str(path)+' | '+str(len(board.notes))+' notes | '+mode,curses.A_BOLD)
   for n in board.notes:
    sx,sy=n['x']-ox+2,n['y']-oy+2
    if -18<sx<w and -6<sy<h-2:draw_note(s,n,sx,sy,colors,n['id']==sel,mode=='edit' and n['id']==sel)
   put(s,h-1,2,status);s.refresh()
  if key==-1:continue
  note=board.get(sel) if sel is not None else None
  if mode=='edit' and note:
   if key in (10,13,curses.KEY_ENTER):mode='view';autosave();status='Note saved.'
   elif key==27:mode='view';status='Edit cancelled.'
   elif key in (curses.KEY_BACKSPACE,127,8):note['text']=note['text'][:-1]
   elif 32<=key<127 and len(note['text'])<4000:note['text']+=chr(key)
   continue
  if key in (ord('q'),ord('Q')):autosave();return
  if key in (10,13,curses.KEY_ENTER):
   k=len(board.notes);n=board.add(ox+w//2-11,oy+h//2-5,0,'Note '+str(board.next_id));sel=n['id'];mode='edit';status='Type, Enter saves, Esc cancels.'
  elif key==curses.KEY_RIGHT:ox+=4
  elif key==curses.KEY_LEFT:ox=max(0,ox-4)
  elif key==curses.KEY_DOWN:oy+=2
  elif key==curses.KEY_UP:oy=max(0,oy-2)
  elif key==9 and board.notes:
   ids=[n['id'] for n in board.notes];sel=ids[(ids.index(sel)+1)%len(ids)] if sel in ids else ids[0]
  elif key in (ord('w'),ord('W')) and note:board.move(sel,0,-2);autosave()
  elif key in (ord('s'),ord('S')) and note:board.move(sel,0,2);autosave()
  elif key in (ord('a'),ord('A')) and note:board.move(sel,-2,0);autosave()
  elif key in (ord('d'),ord('D')) and note:board.move(sel,2,0);autosave()
  elif key in (ord('c'),ord('C')) and note:note['color']=(note['color']+1)%len(COLORS);autosave();status='Color changed.'
  elif key in (ord('x'),ord('X')) and note:
   board.remove(sel);sel=board.notes[0]['id'] if board.notes else None;autosave();status='Note removed.'
  elif key in (ord('e'),ord('E')) and note:mode='edit';status='Type, Enter saves, Esc cancels.'
if __name__=='__main__':
 args=[a for a in sys.argv[1:] if not a.startswith('--')]
 if '--version' in sys.argv:print(VERSION);raise SystemExit(0)
 board=Board();path=args[0] if args else DEFAULT_NAME
 if Path(path).suffix.lower()!='.postlight':path=path+'.postlight'
 if Path(path).exists():
  try:board.load(path)
  except (OSError,ValueError) as e:print('Postlight:',e);raise SystemExit(1)
 raise SystemExit(run(lambda s:play(s,board,path)))
