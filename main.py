from dotenv import load_dotenv
import os
import pygame as pg
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from parser import ParsedCurrentlyPlaying
from ui_elements import ProgressBar, render_info
from config import SETTINGS


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
pg.init()
pg.font.init()
win_flags = pg.RESIZABLE
info = pg.display.Info()
screen_w = info.current_w
screen_h = info.current_h
win_x = 10
win_y = screen_h - 40
os.environ['SDL_VIDEO_WINDOW_POS'] = f'{win_x}, {win_y}'

window = pg.display.set_mode(SETTINGS.win_size, flags=win_flags)
pg.display.set_caption('pyg-spotify')
clock = pg.time.Clock()

running = True
pressed = False
start_mouse_pos = None
timer = 0
seconds = 0
current = ParsedCurrentlyPlaying(result)
p_bar = ProgressBar()
p_bar.highlight = True
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

    pg.display.flip()
pg.quit()
