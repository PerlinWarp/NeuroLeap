## Myo Commons
import struct

def pack(fmt, *args):
    return struct.pack('<' + fmt, *args)

def unpack(fmt, *args):
    return struct.unpack('<' + fmt, *args)

def text(scr, font, txt, pos, clr=(255,255,255)):
    scr.blit(font.render(txt, True, clr), pos)

## Pygame Commons
# Window size
SCALE = 1
WIN_X = 800
WIN_Y = 600