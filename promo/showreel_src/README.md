# Modern Arsenal 60초 쇼릴

`../ModernArsenal_Showreel_60s.mp4`를 만든 코드예요. 1920×1080, 60fps, 60초이고, 음악은 "Low Altitude Assault"(120BPM)예요.

- `core.js`: 타이밍(비트 = 0.085 + 0.5k초), 이징, 텍스트와 HUD, 파티클, 후처리(흔들림, 색수차, 블룸, 그레인)
- `actors.js`: 아파치, 드론, 스파이크, 험비를 게임 코드랑 같은 오프셋으로 조립하고, 픽셀 배경을 그려요
- `scenes.js`: 장면 10개로 된 타임라인, 카메라 임팩트, 효과음 큐
- `render.mjs`: 헤드리스 Chromium으로 프레임을 JPEG로 뽑아요
- `mix.py`: 곡 0~48.06초와 168.06초~끝을 이어 붙이고, 합성 효과음이랑 모드 사운드(드론 통과음, 험비 엔진, M2)를 섞어요

## 다시 만들기
1. `assets/`에 스프라이트를 넣어요. `entrance_gif_v5_final/assets/*`, `humvee_sprites/tools/export.py`로 뽑은 `export/npc/*`, `v0512_tools/items_v0512.py`로 뽑은 아이템 아이콘이에요.
2. `fonts/`에 @fontsource 폰트를 넣어요. Anton, Black Ops One, Chakra Petch, JetBrains Mono, Noto Sans KR, Silkscreen이에요.
3. `node render.mjs --frames 0:3600:1 --out frames --workers 4 --cues cues.json`
4. `python3 mix.py`를 돌리면 `mix.wav`가 나와요.
5. `ffmpeg -framerate 60 -i frames/f%05d.jpg -i mix.wav -c:v libx264 -crf 21 -pix_fmt yuv420p -c:a aac -b:a 256k final.mp4`
