"""SpikeNLOS_Deploy.png: 5 frames 40x34 (2 px gap), nose right, drawn in 1x cells (20x17) and scaled 2x.
Frame 0 folded in the tube; the mid-body wings and the tail fins swing out over frames 1-4."""
from PIL import Image
K = {'A': (22, 21, 17), 'B': (48, 45, 36), 'C': (72, 68, 54), 'D': (98, 93, 74), 'F': (152, 146, 118), 'G': (182, 176, 148),
     'Q': (242, 218, 114), 'k': (10, 11, 13), 'L': (79, 107, 120), 'w': (212, 230, 235)}
BODY = ['ACGGGGGGGGGGGGGGGkw', 'ABDDDDDDQDDDDDDDDkL']   # 19 cells long, rows 8-9, tail at x=1
WING = [0, 1, 3, 4, 5]     # wing half-span in cells per frame
FIN = [0, 1, 1, 2, 2]
out = Image.new('RGBA', (40, 36 * 5 - 2), (0, 0, 0, 0))
for f in range(5):
    im = Image.new('RGBA', (20, 17), (0, 0, 0, 0))
    def px(x, y, c):
        if 0 <= x < 20 and 0 <= y < 17: im.putpixel((x, y), K[c] + (255,))
    for y, r in enumerate(BODY):
        for x, ch in enumerate(r): px(x + 1, 7 + y, ch)
    # tail fins, swept, at the very back
    for s in range(1, FIN[f] + 1):
        px(2 - (s > 1), 7 - s, 'D'); px(3 - (s > 1), 7 - s, 'A')
        px(2 - (s > 1), 8 + s, 'D'); px(3 - (s > 1), 8 + s, 'A')
    # mid-body pop-out wings, swept back as they open
    for s in range(1, WING[f] + 1):
        x = 9 - s // 2
        px(x, 7 - s, 'F' if s < WING[f] else 'C'); px(x + 1, 7 - s, 'A')
        px(x, 8 + s, 'D' if s < WING[f] else 'C'); px(x + 1, 8 + s, 'A')
    if f == 0:
        px(3, 6, 'D'); px(3, 9, 'D')   # stubs of the folded fins
    out.alpha_composite(im.resize((40, 34), Image.NEAREST), (0, f * 36))
out.save('assets/SpikeNLOS_Deploy.png')
big = out.resize((out.width * 6, out.height * 6), Image.NEAREST); bg = Image.new('RGBA', big.size, (40, 44, 52, 255)); bg.alpha_composite(big); bg.save('/tmp/claude-0/deploy.png')
