import os

from dotenv import load_dotenv
import pygame as pg
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from mgl_context import ModernGLHandler
from parser import ParsedCurrentlyPlaying
from ui_elements import ProgressBar, render_info
from config import SETTINGS


# def surf_to_texture(surf: pg.Surface) -> mgl.Texture:
#     tex = ctx.texture(surf.get_size(), 4)
#     tex.filter = (mgl.NEAREST, mgl.NEAREST)
#     tex.swizzle = 'BGRA'
#     tex.write(surf.get_view('1'))
#     return tex

load_dotenv()

s_id = os.environ['s_id']
s_secret = os.environ['s_secret']
redirect_uri = "http://localhost"
scope = "user-read-currently-playing"

auth_manager = SpotifyOAuth(client_id=s_id,
                            client_secret=s_secret,
                            redirect_uri=redirect_uri,
                            scope=scope)

sp = spotipy.Spotify(auth_manager=auth_manager)

result = sp.currently_playing()
# current_playlist = url['external_urls']['spotify']

win_flags = pg.RESIZABLE
if SETTINGS.moderngl:
    win_flags = win_flags | pg.OPENGL | pg.DOUBLEBUF
print(win_flags)

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
current = ParsedCurrentlyPlaying(result)
p_bar = ProgressBar()
p_bar.fill_bar(current.progress_percent)
p_bar.update()

current.render_text()
current.render_time()

while running:
    dt = clock.tick(SETTINGS.fps)
    timer += dt / 1000
    if current.is_playing:
        current.progress_ms += dt
    if seconds != int(timer):
        seconds = int(timer)
        p_bar.fill_bar(current.progress_percent)
        p_bar.update()
        routine_call = seconds % SETTINGS.request_interval == 0
        check_new_song = current.progress_ms > current.duration_ms
        if check_new_song or routine_call:
            # print('api call')
            result = sp.currently_playing()
            if check_new_song or current.quick_compare(result):
                # print('reload assets')
                current = ParsedCurrentlyPlaying(result)
                current.render_text()
            else:
                # print('routine time sync')
                current.update_time(result)
        else:
            # print('non-api request update')
            current.update_time()
        current.render_time()

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
            p_bar.resize()
            p_bar.update()
            current.render_text()
            current.update_time()
            current.render_time()

    main_surf.fill(SETTINGS.win_bg_color)
    p_bar.draw(main_surf)
    if current.song:
        main_surf.blit(current.album.pg_img, (0, 0))
        render_info(main_surf, (current.song.name_text, current.album.name_text, current.song.artist_text))
        main_surf.blit(current.progress_text, current.progress_text_rect)
        main_surf.blit(current.duration_text, current.duration_text_rect)
    if SETTINGS.moderngl:
        mglh.render(main_surf)
        
    pg.display.flip()

if SETTINGS.moderngl:
    mglh.release()
pg.quit()
