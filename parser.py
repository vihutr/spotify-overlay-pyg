from dotenv import load_dotenv
from io import BytesIO
import os

import pygame as pg
import requests

from config import SETTINGS
import spotipy
from spotipy.oauth2 import SpotifyOAuth



# rename and consider distinguishing/combining with ui_elements
class CurrentlyPlayingParser:
    def __init__(self):
        load_dotenv()

        s_id = os.environ['s_id']
        s_secret = os.environ['s_secret']
        redirect_uri = "http://localhost"
        scope = "user-read-currently-playing"

        auth_manager = SpotifyOAuth(client_id=s_id,
                                    client_secret=s_secret,
                                    redirect_uri=redirect_uri,
                                    scope=scope)
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        self.song = None
        self.album = None
        self.progress_ms = 0
        self.duration_ms = 1
        self.playing = False
        self.data = None
        self.load()
        self.parse()
        self.calculate_percent()
    
    def __str__(self):
        return f'{self.song.name}, {self.song.artists}, {self.album.name}'
        # return f'{self.song.name}, {self.song.artists}, {self.album.name}, {self.album.url}, {self.song.url}'

    def load(self):
        self.data = self.sp.currently_playing()

    def parse(self):
        # print('loading data')
        if self.data:
            # print('loading album and song info')
            self.song = ParsedSong(self.data['item'])
            self.album = ParsedAlbum(self.data['item']['album'])
            self.progress_ms = self.data['progress_ms']
            self.duration_ms = self.data['item']['duration_ms']
            self.playing = self.data['is_playing']

    def sync_time(self):
        if self.data:
            self.progress_ms = self.data['progress_ms']
            self.duration_ms = self.data['item']['duration_ms']
            self.playing = self.data['is_playing']
        self.calculate_percent()

    def calculate_percent(self):
        self.progress_percent = self.progress_ms / self.duration_ms

    def quick_name_compare(self) -> bool:
        if self.data['item']['name'] != self.song.name:
            return True
        return False

class ParsedAlbum:
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

class ParsedSong:
    def __init__(self, data: dict):
        self.name = data['name']
        self.artists = []
        self.artists_string = ''
        for a in data['artists']:
            self.artists.append(a['name'])
            if self.artists_string == '':
                self.artists_string = a['name']
            else:
                self.artists_string += f", {a['name']}"
        self.url = data['external_urls']['spotify']
