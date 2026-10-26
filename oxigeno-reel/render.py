from PIL import Image,ImageDraw,ImageFont
import math,random,subprocess,wave,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent
W,H,FPS,DURATION=540,960,24,20
FONT='/usr/share/fonts/google-noto-vf/NotoSansMono[wght].ttf'
font=ImageFont.truetype(FONT,12);small=ImageFont.truetype(FONT,13);label=ImageFont.truetype(FONT,16);bold=ImageFont.truetype(FONT,34);huge=ImageFont.truetype(FONT,100);medium=ImageFont.truetype(FONT,24)
random.seed(23)
buildings=[(i*19-10,random.randint(65,200),random.randint(15,29),i) for i in range(32)]
stars=[(random.randrange(270),random.randrange(180),random.random())for _ in range(70)]
clamp=lambda x:max(0,min(1,x))
def smooth(x):
 x=clamp(x);return x*x*(3-2*x)
def text(draw,xy,txt,f=label,color='#e9f8ff',center=False):
 if center:xy=(xy[0]-draw.textlength(txt,font=f)/2,xy[1])
 draw.text(xy,txt,font=f,fill=color,stroke_width=0)
def city(t):
 im=Image.new('RGB',(270,390),(5,10,29));d=ImageDraw.Draw(im)
 for y in range(390):
  q=math.exp(-((y-175)/95)**2);d.line((0,y,270,y),fill=(int(5+10*q),int(10+16*q),int(29+30*q)))
 for x,y,k in stars:d.point((x,y),fill=(40+int(k*60),70+int(k*80),110+int(k*90)))
 # Parallax, moving scan and neon windows.
 cam=math.sin(t*.22)*12
 for layer in range(2):
  for x,h,w,i in buildings:
   xx=x-(cam if layer else cam*.3);hh=h*(.7 if layer==0 else 1);ground=275+layer*35
   d.rectangle((xx,ground-hh,xx+w,ground),fill=(9+layer*4,17+layer*4,35+layer*4),outline=(24,40,62))
   for wy in range(int(ground-hh)+6,ground-2,10):
    for wx in range(int(xx)+3,int(xx+w)-2,6):
     if (wx*7+wy*13+i*3)%11<5:
      color=[(53,194,220),(239,157,93),(114,91,212)][i%3]
      if (i+int(t*2))%19==0:color=(20,40,60)
      d.rectangle((wx,wy,wx+2,wy+3),fill=color)
 # Road in perspective and moving light trails.
 d.polygon([(115,292),(156,292),(270,390),(0,390)],fill=(14,22,37))
 for i in range(7):
  z=((i/7+t*.14)%1)**2;y=295+z*95
  d.line((134-z*4,y,134-z*5,y+2+z*8),fill=(115,152,169),width=1)
 for i in range(12):
  z=((i*.13+t*.12)%1)**1.7;y=300+z*92;x=140+z*(62 if i%2 else -66)
  d.line((x,y,x-z*9,y-3-z*3),fill=(255,92,111) if i%2 else (99,238,255),width=2)
 for i in range(60):
  x=(i*67)%270;y=320+(i*29)%70;d.line((x,y,x+3,y),fill=(20,48+(i%4)*7,68))
 # Oxygen dots disappear, only N2-like cool specks remain.
 for i in range(32):
  x=(i*71+t*(5+i%3))%270;y=70+(i*47)%155+math.sin(t+i)*3
  if i%4==0 and t>2.5:continue
  col=(253,111,103) if i%4==0 else (64,116,172)
  d.ellipse((x,y,x+2,y+2),fill=col)
 return im

def flames(t):
 im=city(t);d=ImageDraw.Draw(im);d.rectangle((18,191,252,344),fill=(10,16,28),outline=(45,76,100))
 # Stove closeup, extinction is a transition, electricity stays on.
 d.rounded_rectangle((51,274,220,320),radius=9,fill=(43,58,71),outline=(100,145,157),width=2)
 d.ellipse((87,266,184,287),fill=(17,29,42),outline=(109,179,196),width=2)
 strength=1-smooth((t-5.3)/1.8)
 for i in range(9):
  x=99+i*9;ht=(28+math.sin(t*9+i)*8)*strength
  if ht>1:
   d.polygon([(x-5,274),(x-5,265-ht*.4),(x+math.sin(t*8+i)*4,265-ht),(x+6,266),(x+5,274)],fill=(int(80+strength*50),int(180+strength*55),250))
 for i in range(8):
  x=117+i*6+math.sin(t+i)*4;y=240-((t*14+i*8)%64)
  if t>6.2:d.arc((x,y,x+12,y+16),0,230,fill=(64,80,94))
 d.ellipse((211,300,216,305),fill=(94,232,167))
 return im

def lungs(t):
 im=Image.new('RGB',(270,390),(8,13,29));d=ImageDraw.Draw(im)
 for x in range(0,270,15):d.line((x,0,x,390),fill=(13,24,43))
 for y in range(0,390,15):d.line((0,y,270,y),fill=(13,24,43))
 pulse=math.sin(t*4)*2
 # stylized anatomical diagram rather than a collapse countdown.
 for side in [-1,1]:
  x=135+side*41
  d.ellipse((x-35-pulse,134,x+35+pulse,265),fill=(52,25,51),outline=(228,104,136),width=2)
  for i in range(8):
   yy=161+i*11;d.line((135,140,x+side*(i%3)*7,yy),fill=(104,92,150),width=2)
 d.line((135,88,135,172),fill=(125,213,231),width=6)
 d.line((135,165,99,187),fill=(125,213,231),width=3);d.line((135,165,171,187),fill=(125,213,231),width=3)
 for i in range(22):
  z=(i/22+t*.2)%1;x=135+math.sin(i*2.4)*70;y=100+z*185
  d.ellipse((x,y,x+3,y+3),fill=(185,69,103))
 # stylized signal, explicitly not a vital-sign reading.
 points=[]
 for x in range(270):
  phase=(x+t*32)%70;value=0
  if 28<phase<31:value=-20
  elif 31<=phase<35:value=35
  elif 35<=phase<40:value=-12
  points.append((x,333-value))
 d.line(points,fill=(253,113,111),width=2)
 return im

def frame(t):
 if t<4.8:raw=city(t)
 elif t<9:raw=flames(t)
 elif t<14.5:raw=lungs(t)
 else:raw=city(t)
 # 67x97 cells; all scenery is rasterized as colored glyphs.
 pix=raw.resize((67,50),Image.Resampling.BOX);im=Image.new('RGB',(W,H),(4,9,20));d=ImageDraw.Draw(im);ramp=' .,:;it+fxX%#@'
 for y in range(50):
  for x in range(67):
   r,g,b=pix.getpixel((x,y));lum=.2126*r+.7152*g+.0722*b
   k=min(len(ramp)-1,int((min(255,lum*1.4)/255)**.65*len(ramp)))
   if k<1:continue
   col=tuple(min(255,int(v*1.85+28))for v in (r,g,b))
   d.text((x*8,110+y*10),ramp[k],font=font,fill=col)
 # Header, countdown and animated oxygen gauge.
 text(d,(28,24),'¿Y SI DESAPARECE EL OXÍGENO?',small)
 text(d,(28,47),'EXPERIMENTO MENTAL / ASCII LAB',small,'#69899c')
 elapsed=min(20,t*20/18);remaining=max(0,20-elapsed)
 text(d,(510,76),f'{remaining:04.1f}',medium,'#ff9c84',center=False) if False else None
 text(d,(W/2,77),f'{remaining:04.1f} s',medium,'#ffb19c',True)
 oxygen=21 if t<2.3 else (0 if t<17.6 else 21*smooth((t-17.6)/1.2))
 d.rounded_rectangle((28,810,512,842),radius=8,fill=(13,28,43))
 d.rounded_rectangle((32,814,32+max(1,476*oxygen/21),838),radius=5,fill=(49,181,197) if oxygen>2 else (129,48,69))
 text(d,(37,817),f'O2 DEL AIRE: {oxygen:02.0f}%',small,'#fff')
 if t<3.8:
  title=['20 SEGUNDOS','SIN OXÍGENO'];sub=['Solo O2 del aire.','El agua y los materiales no cambian.'];color='#a9edff'
 elif t<8.7:
  title=['LAS LLAMAS','SE APAGAN'];sub=['Sin oxígeno no sostienen la combustión.','Las luces eléctricas no se apagan por eso.'];color='#ffb493'
 elif t<14.5:
  title=['RESPIRAR YA','NO BASTA'];sub=['La falta de O2 puede causar','pérdida de conciencia en segundos.'];color='#ff9eb4'
 elif t<17.5:
  title=['LA CIUDAD','SIGUE EN PIE'];sub=['Ni el agua ni el hormigón desaparecen.','El peligro es la falta de aire respirable.'];color='#a9edff'
 else:
  title=['EL O2 VUELVE.','EL RIESGO NO SE BORRA.'];sub=['Veinte segundos pueden ser graves.','No hay un reloj universal de desmayo.'];color='#9aecd4'
 # Caption plate protects legibility while city keeps moving behind it.
 d.rectangle((0,620,540,801),fill=(5,12,24))
 for i,line in enumerate(title):text(d,(270,630+i*43),line,medium if len(line)>20 else bold,color,True)
 for i,line in enumerate(sub):text(d,(270,731+i*23),line,small,'#d3e1e9',True)
 text(d,(270,860),'SUPUESTO: SOLO O2 ATMOSFÉRICO',small,'#7e9aaa',True)
 text(d,(270,881),'Escenas ilustrativas, no simulación fisiológica.',small,'#7e9aaa',True)
 # Editorial scene tabs, progress and gentle cut accents.
 for i,name in enumerate(['CIUDAD','FUEGO','CUERPO','REGRESO']):
  active=0 if t<4.8 else 1 if t<9 else 2 if t<14.5 else 3
  text(d,(29+i*129,923),name,small,'#f2e2d1' if i==active else '#4b677e')
 d.rectangle((0,954,int(W*t/20),959),fill=(82,218,224))
 for cut in [2.4,4.8,9,14.5,17.6]:
  if 0<=t-cut<.15:
   q=int((1-(t-cut)/.15)*60);overlay=Image.new('RGB',im.size,(120,205,230));im=Image.blend(im,overlay,q/255)
 return im

def soundtrack():
 rate=22050;out=ROOT/'sound.wav'
 with wave.open(str(out),'w')as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);buf=bytearray()
  for i in range(rate*20):
   t=i/rate;fade=min(1,t/1.5,(20-t)/1.4);beat=t%.5;freq=55 if t<9 else 49 if t<14.5 else 65.4
   v=.11*math.sin(2*math.pi*freq*t)+.055*math.sin(2*math.pi*freq*1.5*t)+.04*math.sin(2*math.pi*freq*4*t)*(.5+.5*math.sin(t*.8))
   v+=.18*math.exp(-beat*24)*math.sin(2*math.pi*(80*beat-45*beat*beat))
   for cut in [2.4,4.8,9,14.5,17.6]:
    a=t-cut
    if 0<a<.35:v+=.12*math.exp(-a*13)*math.sin(2*math.pi*(430*a+1300*a*a))
   buf+=struct.pack('<h',int(max(-1,min(1,v*fade))*24000))
  w.writeframes(buf)
 return out
if __name__=='__main__':
 sound=soundtrack();cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(sound),'-vf','scale=1080:1920:flags=lanczos','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-t','20','-movflags','+faststart',str(ROOT/'oxigeno-20s.mp4')]
 process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for i in range(FPS*DURATION):
   image=frame(i/FPS);process.stdin.write(image.tobytes())
   if i in [0,144,264,432]:image.save(ROOT/f'preview-{i}.png')
   if i%96==0:print(f'Render {i}/{FPS*DURATION}',flush=True)
 finally:process.stdin.close()
 if process.wait()!=0:raise RuntimeError('FFmpeg export failed')
 print('Export complete',flush=True)
