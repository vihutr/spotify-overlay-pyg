import os

import pygame as pg

from mgl_context import ModernGLHandler
from visuals import RendererObject
from config import SETTINGS


# def surf_to_texture(surf: pg.Surface) -> mgl.Texture:
#     tex = ctx.texture(surf.get_size(), 4)
#     tex.filter = (mgl.NEAREST, mgl.NEAREST)
#     tex.swizzle = 'BGRA'
#     tex.write(surf.get_view('1'))
#     return tex

# current_playlist = url['external_urls']['spotify']

win_flags = pg.RESIZABLE
if SETTINGS.moderngl:
    win_flags = win_flags | pg.OPENGL | pg.DOUBLEBUF

pg.init()
pg.font.init()

info = pg.display.Info()
win_x = info.current_w - SETTINGS.win_size[0]
# 70 = account for potential taskbar + the extra window frame size
win_y = info.current_h - 70 - SETTINGS.win_size[1]
os.environ['SDL_VIDEO_WINDOW_POS'] = f'{win_x}, {win_y}'

window = pg.display.set_mode(SETTINGS.win_size, flags=win_flags)
pg.display.set_caption('pyg-spotify')
clock = pg.time.Clock()

main_surf = window
if SETTINGS.moderngl:
    gl_screen = pg.Surface(SETTINGS.win_size)
    mglh = ModernGLHandler()
    main_surf = gl_screen
    

running = True
pressed = False
start_mouse_pos = None
timer = 0
seconds = 0

robj = RendererObject()

while running:
    dt = clock.tick(SETTINGS.fps)
    timer += dt / 1000
    robj.update(dt, timer, seconds)
    for e in pg.event.get():
        if e.type == pg.QUIT:
            running = False
        if e.type == pg.KEYDOWN:
            if e.key == pg.K_ESCAPE:
                running = False
        if e.type == pg.MOUSEBUTTONDOWN:
            pressed = True
            start_mouse_pos = pg.mouse.get_pos()
        if e.type == pg.MOUSEBUTTONUP:
            pressed = False
        if e.type == pg.VIDEORESIZE:
            SETTINGS.win_size = main_surf.get_size()
            robj.resize_update()

    main_surf.fill(SETTINGS.win_bg_color)
    robj.bar.draw(main_surf)
    if robj.current.song:
        robj.draw(main_surf)
    if SETTINGS.moderngl:
        mglh.render(main_surf)
        
    pg.display.flip()

if SETTINGS.moderngl:
    mglh.release()
pg.quit()
