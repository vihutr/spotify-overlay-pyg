import pygame as pg

pg.font.init()

# todo:
# consider scrolling text for player?
# auto resizing elements (vertical)
# add controls?

class SETTINGS:
    # pg settings
    fps = 60
    # api call interval in seconds
    request_interval = 5
    win_size = (400, 64 + 20)
    art_size = 64

    # colors
    win_bg_color = '#000000'
    time_color = '#ffffff'
    song_color = '#ffffff'
    album_color = '#ffffff'
    artists_color = '#ffffff'
    bar_empty_color = '#4d4d4d'
    bar_filled_color = '#ffffff'
    bar_highlight_color = '#1db954'

    # font
    font_size = 12
    # font_name = 'notosanscjksc'
    # font = pg.font.SysFont(font_name, size=font_size)
    font = pg.font.Font('fonts/NotoSansCJK-Medium.ttc', size=font_size)
