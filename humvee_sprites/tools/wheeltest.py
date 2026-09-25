from ext import *
from PIL import Image
fr = make_wheel_frames()
imgs = [Image.fromarray(f.render()) for f in fr]
W2 = Image.new('RGBA', (21*4+12, 21), (118,128,140,255))
for i, im in enumerate(imgs):
    W2.alpha_composite(im, (i*24, 0))
W2.resize((W2.width*12, W2.height*12), Image.NEAREST).save('out/wheel_test.png')
