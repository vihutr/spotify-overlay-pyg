from io import BytesIO
import pygame as pg
import requests

from config import SETTINGS

class ParsedCurrentlyPlaying:
    def __init__(self, data: dict):
        self.progress_ms = 0
        self.duration_ms = 1
        self.load(data)
        self.update_time(data)

    def load(self, data):
        if data:
            self.album = ParsedAlbum(data['item']['album'])
            self.song = ParsedSong(data['item'])
        else:
            self.song = None

    def update_time(self, data=None):
        # we can assume the song is playing normally for the most part
        # we make a request to the api every x% of the song length to verify
        # use duration_ms to calculate update timing to not overuse api calls
        if data:
            self.progress_ms = data['progress_ms']
            self.duration_ms = data['item']['duration_ms']
            self.is_playing = data['is_playing']
        self.progress_percent = self.progress_ms / self.duration_ms
        self.duration_text = SETTINGS.font.render(
            convert_ms(self.duration_ms),
            True,
            SETTINGS.time_color)
        self.duration_text_rect = self.duration_text.get_rect()
        self.duration_text_rect.bottomright = (SETTINGS.win_size[0] - 1,
                                               SETTINGS.win_size[1] - 1)

    def render_text(self):
        if self.song:
            self.album.render_text()
            self.song.render_text()
            # color = '#ffffff'
            self.progress_text = SETTINGS.font.render(
                convert_ms(self.progress_ms),
                True,
                SETTINGS.time_color)
            self.progress_text_rect = self.progress_text.get_rect()
            self.progress_text_rect.bottomleft = (1, SETTINGS.win_size[1] - 1)


class ParsedAlbum:
    color = '#ffffff'

    def __init__(self, data: dict):
        self.name = data['name']
        images = data['images']
        if len(images) > 0:
            # get the smallest image
            self.image_url = images[-1]['url']
            self.image_size = (images[-1]['width'], images[-1]['height'])
            self.image = requests.get(self.image_url).content
            self.pg_img = pg.image.load(BytesIO(self.image))
            if self.image_size[0] != SETTINGS.art_size:
                self.pg_img = pg.transform.scale(
                    self.pg_img, (SETTINGS.art_size, SETTINGS.art_size))
        # not displayed
        self.url = data['external_urls']['spotify']
    
    def render_text(self):
        self.name_text = render_cutoff_text(self.name,
                                            ParsedAlbum.color)

class ParsedSong:
    color = '#ffffff'
    subcolor = '#aaaaaa'

    def __init__(self, data: dict):
        self.name = data['name']
        self.artists = []
        self.artists_string = ''
        for a in data['artists']:
            self.artists.append(a['name'])
            if self.artists_string == '':
                self.artists_string = a['name']
            else:
                self.artists_string += f', {a['name']}'
        self.url = data['external_urls']['spotify']

    def render_text(self):
        self.name_text = render_cutoff_text(self.name,
                                            ParsedSong.color)
        self.artist_text = render_cutoff_text(self.artists_string,
                                              ParsedSong.subcolor)

def render_cutoff_text(string: str, color) -> pg.Surface:
    result = SETTINGS.font.render(string, True, color)
    trim = 0
    while result.get_size()[0] + 70 > SETTINGS.win_size[0]:
        result = SETTINGS.font.render(
            string[0:len(string) - trim] + '...',
            True,
            color)
        trim += 1
    return result

def convert_ms(ms: int) -> str:
    ms = int(ms)
    secs = int((ms / 1000) % 60)
    mins = int((ms / (1000 * 60)) % 60)
    hrs = int((ms / (1000 * 60 * 60)) % 24)
    if hrs > 0:
        return f'{hrs}:{mins}:{str(secs).zfill(2)}'
    return f'{mins}:{str(secs).zfill(2)}'
