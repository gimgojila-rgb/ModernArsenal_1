"""mirrors NavLightRig.Draw: facing left = port red near / starboard green far, facing right = the reverse"""
import numpy as np, json, math
from PIL import Image, ImageDraw
body=Image.open('out/GrayEagle.png').convert('RGBA')
slime=np.asarray(Image.open('out/GrayEagle_Slime.png').convert('RGBA'))[...,3].astype(np.float32)/255
prop=Image.open('out/GrayEagle_Prop.png').convert('RGBA'); blur=Image.open('out/GrayEagle_PropBlur.png').convert('RGBA')
L=json.load(open('out/GrayEagle_lights.json'))
PORT,STBD,LIME,WHITE,BEAC,TAILW=(255,46,34),(60,255,110),(196,255,140),(255,255,250),(255,34,22),(255,250,236)
FH=27; SC=3; pad=46
W,H=body.size
def frame(tick, face_left):
    im=Image.new('RGBA',(W+2*pad,H+2*pad),(40,43,52,255)); d=ImageDraw.Draw(im)
    for x in range(0,im.width,16): d.line([(x,0),(x,im.height)],fill=(47,52,61))
    for y in range(0,im.height,16): d.line([(0,y),(im.width,y)],fill=(47,52,61))
    c=(pad+W/2,pad+H/2)
    def P(off): return (c[0]+(off[0] if face_left else -off[0]), c[1]+off[1])
    b=(body if face_left else body.transpose(Image.FLIP_LEFT_RIGHT)).copy()
    b.alpha_composite(Image.open('out/GrayEagle_MarksL.png' if face_left else 'out/GrayEagle_MarksR.png').convert('RGBA'))
    ax=P(L['prop_axis'])
    im.alpha_composite(blur,(int(ax[0]-blur.width/2), int(ax[1]-blur.height/2)))
    im.alpha_composite(b,(pad,pad))
    f=(tick//1)%6
    fr=prop.crop((0,f*(FH+2)*2,prop.width,f*(FH+2)*2+FH*2))
    im.alpha_composite(fr,(int(ax[0]-fr.width/2), int(ax[1]-fr.height/2)))
    a=np.asarray(im).astype(np.float32)
    sm=slime if face_left else slime[:,::-1]
    a[pad:pad+H,pad:pad+W,:3]+=sm[...,None]*np.array(LIME)*0.75
    yy,xx=np.mgrid[0:im.height,0:im.width]
    def blob(p,size,col,k):
        r=np.hypot(xx-p[0],yy-p[1]); s=size/2
        a[...,:3]+=(np.exp(-(r/(s*0.5))**2)*0.85+np.exp(-(r/(s*0.15))**2)*0.7)[...,None]*np.array(col)*k
    near=PORT if face_left else STBD; far=STBD if face_left else PORT
    blob(P(L['near_wingtip']),28,near,1); blob(P(L['far_wingtip']),18,far,0.55); blob(P(L['tail_white']),18,TAILW,0.6)
    for i,off in enumerate([L['beacon_top'],L['beacon_bottom']]):
        t=((tick+i*36)%72)/72; pulse=max(0,math.sin(t*2*math.pi))**2
        blob(P(off),34,BEAC,0.15+0.85*pulse)
    ph=tick%60
    if ph<3:
        k=[1,0.75,0.4][ph]
        for off in L['strobe']:
            blob(P(off),70,WHITE,0.9*k)
    im=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
    return im.resize((im.width*SC,im.height*SC),Image.NEAREST)
frame(10,True).save('/mnt/user-data/outputs/gray_eagle_preview.png')
frame(0,True).save('/home/claude/uav/strobe_left.png')
frames=[frame(t,True).convert('RGB') for t in range(0,120,2)]+[frame(t,False).convert('RGB') for t in range(0,120,2)]
pal=frames[5].quantize(colors=255,method=Image.MEDIANCUT)
q=[f.quantize(palette=pal,dither=Image.NONE) for f in frames]
q[0].save('/mnt/user-data/outputs/gray_eagle_idle.gif',save_all=True,append_images=q[1:],duration=33,loop=0,disposal=1)
frame(10,False).save('/home/claude/uav/right.png')
