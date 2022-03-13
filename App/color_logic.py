import pygame
from pygame import gfxdraw
import colorsys
import numpy as np
import time
import random
from audio_analysis import AudioAnalysis


class ColorLogic():
    def __init__(self):
        self.length, self.width = (1024, 512)
        self.padding = 13
        self.band_size = 25
        self.size = self.band_size + 2  # 2 is the gap
        self.aud = AudioAnalysis()
        self.aud.start_stream()
        self.white = (255, 255, 255)
        self.green = (0, 255, 0)
        self.y_data = []
        self.av = []
        self.height = 0
        self.max_height = 0
        self.light_level = 0  # change from 0 -> 1
        self.mode = "m"
        self.h = random.choice(range(0, 360))/259
        self.v = 1
        self.s = 1
        self.c = [round(i*255)
                  for i in colorsys.hsv_to_rgb(self.h, self.s, self.v)]
        self.full_lim = 0
        self.lim_count = 0
        self.lim = 0
        self.et = 0
        self.st = 0
        self.allow = False
        self.drop = False
        self.block_time = 0.5
        self.lc = self.white
        self.reset_lim = 1
        self.reset_time = 10
        self.rst = 0
        self.ret = 0
        self.offset = 0
        self.offset_factor = 1/720

    def change_mode(self, mode):  # checks for current color mode
        if mode.lower() == "m":  # music
            self.mode = mode.lower()
            self.h = random.choice(range(0, 360))/259
        elif mode.lower() == "g":  # gamming
            self.mode = mode.lower()
            self.h = 0
        elif mode.lower() == "c":  # color
            self.mode = mode.lower()

        self.c = [round(i*255)
                  for i in colorsys.hsv_to_rgb(self.h, self.s, self.v)]

    def logic(self):  # process sound data to control the colors hue and saturation
        self.y_data = self.aud.analyze_fft()
        self.av = [round(np.average(self.y_data[i:i+len(self.y_data)//36]))
                   for i in range(0, len(self.y_data)-len(self.y_data)//36, len(self.y_data)//36)]  # divides frequency bands into 36

        max_av = self.av.index(max(self.av[2:]))  # gets the maximum band
        # gets the surrounding 2 bands from each side
        range_av = self.av[max_av:max_av+3] + self.av[max_av-2:max_av]
        # gets the average height between the range bands
        self.height = sum(range_av)//len(range_av)
        if self.height > self.max_height:
            self.max_height = self.height

        if self.height > self.reset_lim:
            self.v = self.light_level + \
                (self.height/self.max_height) * \
                (1-self.light_level)  # changes the brightness of the led depending on the height of the band
        self.full_lim += max(self.av[12:25])  # + min(self.av[12:])
        self.lim_count += 1
        self.lim = self.full_lim/self.lim_count
        self.et = time.time()

        # allows for color change
        if np.average(self.av[12:25]) < self.lim and self.et - self.st > self.block_time:
            self.allow = True
            self.lc = self.green

        # checks for color dropping (dropping the current color and getting a new one)
        if np.average(self.av[12:25]) > self.lim and np.average(self.av[12:25]) > self.reset_lim and self.allow:
            self.drop = True
            self.allow = False
            self.lc = self.white
            self.max_height = 0

        if max(self.av) < self.reset_lim:
            if not self.rst:
                self.rst = time.time()
            self.ret = time.time()
            if self.ret - self.rst > self.reset_time:
                self.full_lim = 0
                self.lim_count = 0
                self.ret = 0
                self.rst = 0
                self.lim = 0
                self.max_height = 0
        else:
            self.rst = 0

        # changes the color to a new one
        if self.drop:
            self.st = time.time()
            if self.mode.lower() == "m":
                self.h = self.av.index(
                    max(self.av[2:]))/len(self.av) + self.offset
            elif self.mode.lower() == "g":
                self.h += 11/360
                self.h %= 1
            else:
                pass
            self.drop = False
            self.max_height = 0

        self.c = [round(i*255)
                  for i in colorsys.hsv_to_rgb(self.h, self.s, self.v)]

    # draws the frequency bands
    def draw_spectrum(self, win):
        length = len(self.av)
        for i, j in enumerate(self.av):
            hue = [round(255*x) for x in colorsys.hsv_to_rgb((i /
                                                              (length-1)) + self.offset, 1, 1)]  # rainbow
            c_color = [round(i*255)
                       for i in colorsys.hsv_to_rgb(self.h, 1, 1)]  # same color
            pygame.draw.rect(win, hue, (i*self.size + self.padding,
                             self.width-j, self.band_size, j))  # change hue with c_color
            pygame.draw.rect(win, self.white, (i*self.size +
                             self.padding, self.width-j, self.band_size, j), 1)

        pygame.draw.line(win, self.lc, (0, self.width-self.lim),
                         (self.length, self.width-self.lim))
        pygame.draw.rect(win, self.c, (self.length, 0,
                         self.length+170, self.width))
        self.offset += self.offset_factor
        if int(self.offset) == 1:
            self.offset = 0

# color picker for controlling the lights manually


class ColorPicker:
    def __init__(self):
        self.length, self.width = (1024, 512)
        self.h = 0
        self.s = 1
        self.v = 1
        self.can_l = 255
        self.can_w = 255
        self.c1 = (255, 255, 255)
        self.c2 = [round(i*255) for i in colorsys.hsv_to_rgb(self.h, 1, 1)]
        self.c = [round(i*255)
                  for i in colorsys.hsv_to_rgb(self.h, self.s, self.v)]
        self.c = self.c2
        self.alpha = 255
        self.bfade = pygame.Surface((self.can_l, 1))
        self.bratio = 255/self.can_w
        self.gap = 20
        self.slider_width = 25
        self.sx = (self.length - self.can_l - self.gap - self.slider_width)//2
        self.sy = (self.width - self.can_w)//2
        self.ey = (self.width + self.can_w)//2
        self.h_ratio = (360/self.can_w)/360
        self.sh = 0
        self.radius = 5
        self.cx = self.sx+self.can_l
        self.cy = self.sy
        self.extra = 6
        self.rlength = self.slider_width + 1 + self.extra
        self.rwidth = 12
        self.rx = self.sx+self.can_l+self.gap
        self.ry = self.sy-self.rwidth//2
        self.click_check = False
        self.pick = "b"
        self.first_color = self.c
        self.second_color = self.c

    # checks for clicks and movment on the color picker
    def logic(self, mx, my, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.click_check = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.click_check = False

        if self.click_check and self.sx <= mx <= self.sx+self.can_l and self.sy <= my <= self.sy+self.can_w:
            self.cx = mx
            self.cy = my
            self.v = 1 - (self.cy-self.sy)/self.can_w
            self.s = 1 - (self.sx+self.can_l-self.cx)/self.can_l
            self.c = [round(i*255)
                      for i in colorsys.hsv_to_rgb(self.h, self.s, self.v)]

        if self.click_check and self.sx+self.can_l+self.gap <= mx <= self.sx+self.can_l+self.gap+self.slider_width and self.sy <= my <= self.sy+self.can_w:
            self.ry = my-self.rwidth//2
            self.h = (my-self.sy)/self.can_w
            self.c2 = [round(i*255) for i in colorsys.hsv_to_rgb(self.h, 1, 1)]
            self.c = [round(i*255)
                      for i in colorsys.hsv_to_rgb(self.h, self.s, self.v)]

    # draws the color picker
    def draw_canvas(self, win):
        for i in range(self.can_l):
            pygame.draw.line(win, (self.c1[0] + i*(self.c2[0]-self.c1[0])//self.can_l, self.c1[1] + i*(self.c2[1]-self.c1[1]) //
                             self.can_l, self.c1[2] + i*(self.c2[2]-self.c1[2])//self.can_l), (self.sx+i, self.sy), (self.sx+i, self.ey))

        for i in range(self.can_w):
            self.bfade.set_alpha(self.alpha)
            win.blit(self.bfade, (self.sx, self.ey - i))
            self.alpha -= self.bratio
        self.alpha = 255

        gfxdraw.aacircle(win, self.cx, self.cy, self.radius, (255, 255, 255))
        gfxdraw.aacircle(win, self.cx, self.cy, self.radius-1, (0, 0, 0))
        for i in range(self.can_w):
            pygame.draw.line(win, [round(i*255) for i in colorsys.hsv_to_rgb(self.sh, 1, 1)], (self.sx +
                             self.can_l+self.gap, self.sy+i), (self.sx+self.can_l+self.gap+self.slider_width, self.sy+i))
            self.sh += self.h_ratio
        self.sh = 0

        pygame.draw.rect(win, (255, 255, 255), (self.rx -
                         self.extra//2, self.ry, self.rlength, self.rwidth))

        pygame.draw.rect(win, self.c, (self.length, 0,
                         self.length+170, self.width))
