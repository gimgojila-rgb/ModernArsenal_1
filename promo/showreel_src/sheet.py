import sys, glob, os
from PIL import Image, ImageDraw
d=sys.argv[1]; out=sys.argv[2]; cols=int(sys.argv[3]) if len(sys.argv)>3 else 4; tw=int(sys.argv[4]) if len(sys.argv)>4 else 480
fs=sorted(glob.glob(d+'/*.jpg'))
th=tw*9//16; rows=(len(fs)+cols-1)//cols
sheet=Image.new('RGB',(cols*tw,rows*th),(0,0,0)); dr=ImageDraw.Draw(sheet)
for i,f in enumerate(fs):
    im=Image.open(f).resize((tw,th)); x,y=(i%cols)*tw,(i//cols)*th; sheet.paste(im,(x,y))
    fr=int(os.path.basename(f)[1:6]); dr.rectangle([x,y,x+70,y+16],fill=(0,0,0)); dr.text((x+3,y+2),f"{fr/60:.2f}s",fill=(255,255,0))
sheet.save(out,quality=88)
