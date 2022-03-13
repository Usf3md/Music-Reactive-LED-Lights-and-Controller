import pygame
from pygame import gfxdraw
import socket
import time


class Checkbox:  # Creates pygame circle checkbox
    data = []

    def __init__(self, x, y, radius, elipse_color, mode, font, text, textx, texty):
        self.mode = mode
        self.x = x
        self.y = y
        self.radius = radius
        self.elipse_color = elipse_color
        self.neg = -1
        self.checked = False
        self.text = font.render(text, True, (255, 255, 255))
        self.textx = textx
        self.texty = texty
        self.text_width, self.text_height = font.size(text)
        self.gap = 10
        self.offset = 1

    def action_check(self, mx, my, event, radio):  # checks for mouse clicks
        if self.x < mx < self.x+self.radius*2 and self.y < my < self.y+self.radius*2:
            if event.type == pygame.MOUSEBUTTONUP:
                self.checked = False if self.checked and radio else True
                self.offset *= -1
                pygame.mouse.set_pos((mx+self.offset, my))
                return self.checked

    def draw_check(self, win, fill_color):  # draws the check
        if self.checked:
            gfxdraw.filled_circle(win, self.x+self.radius,
                                  self.y+self.radius, self.radius, fill_color)
        gfxdraw.aacircle(win, self.x+self.radius, self.y +
                         self.radius, self.radius, self.elipse_color)
        gfxdraw.aacircle(win, self.x+self.radius, self.y +
                         self.radius, self.radius, self.elipse_color)
        win.blit(self.text, (self.x+2*self.radius+self.gap,
                 self.y+self.radius-self.text_height//2))


class Client:  # creates a udp client
    def __init__(self):
        self.HEADER = 2
        self.PORT = 5050  # change the port to your esp8266 port
        self.SERVER = "192.168.1.69"  # change the ip to your esp8266 ip
        self.ADDR = (self.SERVER, self.PORT)
        self.FORMAT = "utf-8"
        self.DISCONNECT_MESSAGE = "!DISCONNECT"

        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.start_time = time.time()
        self.delay = 0.01  # delay is added to avoid overloading the esp8266

    def send(self, pick, msg):  # sends rgb color data to the esp8266
        if time.time() - self.start_time >= self.delay:
            message = pick.encode(
                self.FORMAT) + "".join(["0"*(3-len(str(i)))+str(i) for i in msg]).encode(self.FORMAT)
            self.client.sendto(message, self.ADDR)
            self.start_time = time.time()
