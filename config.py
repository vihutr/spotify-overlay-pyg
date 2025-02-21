import pygame as pg

pg.font.init()

# todo:
# consider scrolling text for player?
# auto resizing elements
# consolidate more values into settings and relying on them throughout the code
## move more colors into here
# add controls?
# limit requests to make script more efficient (consider adding this as a config setting var too)

class SETTINGS:
    fps = 60
    update_interval = 5
    win_size = (400, 64 + 20)
    art_size = 64
    time_color = '#ffffff'
    font_size = 12
    font = pg.font.SysFont('notosanscjksc', size=font_size)

