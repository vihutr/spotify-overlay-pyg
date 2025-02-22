import pygame as pg

pg.font.init()

# todo:
# consider scrolling text for player?
# auto resizing elements (vertical)
# add controls?

class SETTINGS:
    # colors
    win_bg_color = '#000000'
    time_color = '#ffffff'
    song_color = '#ffffff'
    album_color = '#ffffff'
    artists_color = '#ffffff'
    bar_empty_color = '#4d4d4d'
    bar_filled_color = '#ffffff'
    bar_highlight_color = '#1db954'

    # api call interval in seconds
    request_interval = 5
    
    # pg settings
    fps = 60
    # font
    font_size = 12
    # font_name = 'notosanscjksc'
    # font = pg.font.SysFont(font_name, size=font_size)
    font = pg.font.Font('fonts/NotoSansCJK-Medium.ttc', size=font_size)

    win_size = (400, 64 + font_size * 2)

    # ui adjustments, offsets are from closest edge
    art_size = 64
    text_offset_x = 6
    text_margin_y = 2
    text_padding_y = 3
    time_offset_x = 4
    time_offset_y = 2
    
