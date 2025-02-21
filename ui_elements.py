import pygame as pg
import os

from config import SETTINGS


class ProgressBar:
    empty_color = '#4d4d4d'
    filled_color = '#ffffff'
    highlight_color = '#1db954'

    def __init__(self):
        self.percent_filled = 0
        self.highlight = False
        self.resize()
        self.update()
    
    def update(self):
        self.surface = pg.Surface((self.w, self.h))
        pg.draw.rect(self.surface, ProgressBar.empty_color, self.empty_bar)
        if not self.highlight:
            pg.draw.rect(self.surface, ProgressBar.filled_color,
                         self.filled_bar)
        else:
            pg.draw.rect(self.surface, ProgressBar.highlight_color,
                         self.filled_bar)

    def draw(self, surf: pg.Surface):
        surf.blit(self.surface, self.rect)

    def fill_bar(self, percent):
        self.percent_filled = percent
        self.filled_bar = pg.Rect(0, 0, self.w * self.percent_filled, self.h)
    
    def resize(self):
        self.w, h = SETTINGS.win_size
        self.h = h // 25
        self.pos = (0, SETTINGS.art_size)
        self.rect = pg.Rect(self.pos, (self.w, self.h))
        self.empty_bar = pg.Rect(0, 0, self.w, self.h)
        self.fill_bar(self.percent_filled)

if __name__ == '__main__':
    pg.init()
    window_flags = pg.RESIZABLE
    info = pg.display.Info()
    screen_w = info.current_w
    screen_h = info.current_h
    win_x = 10
    win_y = screen_h - 40
    os.environ['SDL_VIDEO_WINDOW_POS'] = f'{win_x}, {win_y}'
    window = pg.display.set_mode((400, 100), flags=window_flags)
    clock = pg.time.Clock()

    p_bar = ProgressBar(window)
    print(p_bar.w, p_bar.h)

    running = True
    pressed = False
    start_mouse_pos = None
    timer = 0
    seconds = 0
    update_interval = 5
    fps = 30
    while running:
        dt = clock.tick(30)
        timer += dt / 1000
        if seconds != int(timer):
            seconds = int(timer)
            p_bar.fill_bar(seconds/60)
        p_bar.update()
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
        window.fill("black")
        p_bar.draw(window)
        pg.display.flip()

    pg.quit()

