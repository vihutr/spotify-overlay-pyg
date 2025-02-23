import os
from array import array

from dotenv import load_dotenv
import moderngl as mgl
import pygame as pg
import spotipy
from spotipy.oauth2 import SpotifyOAuth

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

win_flags = pg.RESIZABLE | pg.OPENGL | pg.DOUBLEBUF

pg.init()
pg.font.init()
info = pg.display.Info()
screen_w = info.current_w
screen_h = info.current_h
win_x = screen_w - SETTINGS.win_size[0]
# 70 = account for potential taskbar + the extra window frame size
win_y = screen_h - 70 - SETTINGS.win_size[1]
os.environ['SDL_VIDEO_WINDOW_POS'] = f'{win_x}, {win_y}'

screen = pg.display.set_mode(SETTINGS.win_size, flags=win_flags)
window = pg.Surface(screen.get_size())
pg.display.set_caption('pyg-spotify')
clock = pg.time.Clock()

ctx = mgl.create_context()
quad_buffer = ctx.buffer(data=array('f', [
    # position (x, y), uv coords (x, y)
    -1.0, 1.0, 0.0, 0.0,    # topleft
    1.0, 1.0, 1.0, 0.0,     # topright
    -1.0, -1.0, 0.0, 1.0,   # bottomleft
    1.0, -1.0, 1.0, 1.0,    # bottomright
]))

vert_shader = '''
#version 330 core

in vec2 vert;
in vec2 texcoord;
out vec2 uvs;

void main() {
    uvs = texcoord;
    gl_Position = vec4(vert, 0.0, 1.0);
}
'''

frag_shader = '''
#version 330 core

uniform sampler2D tex;
uniform float time;

in vec2 uvs;
out vec4 f_color;

void main() {
    // vec2 sample_pos = vec2(uvs.x + sin(uvs.y * 10 + time) * 0.01, uvs.y);
    f_color = vec4(texture(tex, uvs).rgb, 1.0);
}
'''

program = ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
render_obj = ctx.vertex_array(program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

window_tex = ctx.texture(window.get_size(), 4)
window_tex.filter = (mgl.NEAREST, mgl.NEAREST)
window_tex.swizzle = 'BGRA'

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
            SETTINGS.win_size = window.get_size()
            p_bar.resize()
            p_bar.update()
            current.render_text()
            current.update_time()
            current.render_time()

    window.fill(SETTINGS.win_bg_color)
    p_bar.draw(window)
    if current.song:
        window.blit(current.album.pg_img, (0, 0))
        render_info(window, (current.song.name_text, current.album.name_text, current.song.artist_text))
        window.blit(current.progress_text, current.progress_text_rect)
        window.blit(current.duration_text, current.duration_text_rect)
    
    window_tex.write(window.get_view('1'))
    window_tex.use(0)
    program['tex'] = 0
    # program['time'] = timer
    render_obj.render(mode=mgl.TRIANGLE_STRIP)

    pg.display.flip()

window_tex.release()
pg.quit()
