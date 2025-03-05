import pygame as pg
import os

from config import SETTINGS
from parser import CurrentlyPlayingParser

class RendererObject:
    def __init__(self):
        self.current = CurrentlyPlayingParser()
        self.bar = ProgressBar()
        self.bar.percent_filled = self.current.progress_percent
        self.render_text()
        self.render_duration()
        self.render_progress()
    
    def render_text(self):
        if self.current.song:
            self.album_text = render_cutoff_text(self.current.album.name,
                                                 SETTINGS.album_color)
            self.song_text = render_cutoff_text(self.current.song.name,
                                                SETTINGS.song_color)
            self.artists_text = render_cutoff_text(self.current.song.artists_string,
                                                   SETTINGS.artists_color)
            self.song_info = [self.song_text, self.artists_text, self.album_text]

    def render_duration(self):
        self.duration_text, self.duration_text_rect = generate_time_surf(self.current.duration_ms)
        self.duration_text_rect.bottomright = (SETTINGS.win_size[0] - SETTINGS.time_offset_x,
                                               SETTINGS.win_size[1] - SETTINGS.time_offset_y)

    def render_progress(self):
        self.progress_text, self.progress_text_rect = generate_time_surf(self.current.progress_ms)
        self.progress_text_rect.bottomleft = (SETTINGS.time_offset_x,
                                              SETTINGS.win_size[1] - SETTINGS.time_offset_y)
    
    def render_info(self, surf: pg.Surface):
        for i, s in enumerate(self.song_info):
            calc_x = SETTINGS.art_size + SETTINGS.text_offset_x
            calc_y = (SETTINGS.text_margin_y * (i + 1)) + (SETTINGS.font_size + SETTINGS.text_padding_y * 2) * i
            surf.blit(s, (calc_x, calc_y))

    def draw(self, surf: pg.Surface):
        surf.blit(self.current.album.pg_img, (0, 0))
        self.render_info(surf)
        surf.blit(self.progress_text, self.progress_text_rect)
        surf.blit(self.duration_text, self.duration_text_rect)


    def resize_update(self):
        self.bar.resize()
        self.bar.update()
        self.render_text()
        self.render_duration()
        self.render_progress()
        self.current.sync_time()
    
    def update(self, dt: float, timer: float, seconds: int):
        if self.current.playing:
            self.current.progress_ms += dt
        if seconds != int(timer):
            seconds = int(timer)
            self.bar.percent_filled = self.current.progress_percent
            self.bar.update()
            routine_call = seconds % SETTINGS.request_interval == 0
            check_new_song = self.current.progress_ms > self.current.duration_ms
            if check_new_song or routine_call:
                # print('api call')
                self.current.load()
                if self.current.quick_name_compare():
                    # print('reparse info')
                    self.current.parse()
                    self.render_text()
                else:
                    # print('routine time sync')
                    self.current.sync_time()
            else:
                # print('non-api request update')
                self.current.calculate_percent()
            self.render_progress()

class ProgressBar:
    def __init__(self):
        self.percent_filled = 0
        self.highlight = False
        self.resize()
        self.filled_bar = pg.FRect(0, 0, self.w * self.percent_filled, self.h)
        self.update()
    
    def update(self):
        self.filled_bar.update(0, 0, self.w * self.percent_filled, self.h)
        self.surface = pg.Surface((self.w, self.h))
        pg.draw.rect(self.surface, SETTINGS.bar_empty_color, self.empty_bar)
        if not self.highlight:
            pg.draw.rect(self.surface, SETTINGS.bar_filled_color,
                         self.filled_bar)
        else:
            pg.draw.rect(self.surface, SETTINGS.bar_highlight_color,
                         self.filled_bar)

    def draw(self, surf: pg.Surface):
        surf.blit(self.surface, self.rect)
    
    def resize(self):
        self.w, h = SETTINGS.win_size
        self.h = 3
        self.pos = (0, SETTINGS.art_size + 1)
        self.rect = pg.Rect(self.pos, (self.w, self.h))
        self.empty_bar = pg.Rect(0, 0, self.w, self.h)

# helper functions
def render_cutoff_text(string: str, color) -> pg.Surface:
    trim = 0
    result = SETTINGS.font.render(string, True, color)
    # consider calculating size based on font width?
    while result.get_size()[0] + 70 > SETTINGS.win_size[0] and trim < SETTINGS.win_size[0]:
        result = SETTINGS.font.render(
            string[0:len(string) - trim] + '...',
            True,
            color)
        trim += 1
        # print(trim)
    return result

def ms_to_formatted_time(ms: int) -> str:
    ms = int(ms)
    secs = int((ms / 1000) % 60)
    mins = int((ms / (1000 * 60)) % 60)
    hrs = int((ms / (1000 * 60 * 60)) % 24)
    if hrs > 0:
        return f'{hrs}:{mins}:{str(secs).zfill(2)}'
    return f'{mins}:{str(secs).zfill(2)}'

def generate_time_surf(ms: int) -> (pg.Surface, pg.Rect):
    text = SETTINGS.font.render(
        ms_to_formatted_time(ms),
        True,
        SETTINGS.time_color)
    text_rect = text.get_rect()
    return text, text_rect
