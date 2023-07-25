import pygame
from color_logic import ColorLogic, ColorPicker
from utils import Checkbox, Client
import colorsys


def init():
    global win, font
    length, width = (1024 + 170, 512)
    pygame.init()
    win = pygame.display.set_mode((length, width))
    pygame.display.set_caption("CBEATS")
    icon = pygame.image.load(
        r"App\Data\Graphics\Circle-icons-rgb.jpg").convert()
    pygame.display.set_icon(icon)
    font = pygame.font.Font(r"App\Data\Fonts\LEMONMILK-Bold.otf", 28)


# Checks for mode changes
def handle_modes(objs, mx, my, main_obj, event, picker):
    for obj in objs:
        if obj.action_check(mx, my, event, False):
            for obj2 in objs:
                obj2.checked = False
            obj.checked = True
            if main_obj.mode != obj.mode:
                main_obj.change_mode(obj.mode)

        if obj.mode == "c":
            obj.draw_check(win, picker.c)
        else:
            obj.draw_check(win, main_obj.c)

# checks for color changes


def handle_colors(objs, mx, my, event, picker):
    for obj in objs:
        if obj.checked:
            selected_obj = obj
            break
    for obj in objs:
        if obj.action_check(mx, my, event, False):
            for obj2 in objs:
                obj2.checked = False
            selected_obj.data = [picker.h, picker.s, picker.v,
                                 picker.c, picker.cx, picker.cy, picker.ry]
            obj.checked = True

            picker.h = obj.data[0]
            picker.s = obj.data[1]
            picker.v = obj.data[2]
            picker.c = obj.data[3]
            picker.cx = obj.data[4]
            picker.cy = obj.data[5]
            picker.ry = obj.data[6]
            picker.c2 = [round(i*255)
                         for i in colorsys.hsv_to_rgb(picker.h, 1, 1)]
            break


def app():
    init()
    last_message = ""
    a = ColorLogic()
    picker = ColorPicker()
    gtext = font.size("Gaming")
    ctext = font.size("Color")
    rtext = font.size("React")
    ftext = font.size("First")
    stext = font.size("Second")
    btext = font.size("Both")
    check_radius = 10
    modes = [Checkbox(a.padding, a.padding, check_radius, (255, 255, 255), "m", font, "Music", 50, 100),
             Checkbox(1024//2 - (gtext[0]+check_radius*2+10+a.padding)//2, a.padding,
                      check_radius, (255, 255, 255), "g", font, "Gaming", 150, 100),
             Checkbox(1024 - (ctext[0]+check_radius*2+10+a.padding), a.padding,
                      check_radius, (255, 255, 255), "c", font, "Color", 150, 100)
             ]
    react_check = Checkbox(1024 - (ctext[0]+check_radius*2+10+a.padding), a.padding +
                           ctext[1], check_radius, (255, 255, 255), "c", font, "React", 150, 100)
    f_color = Checkbox(picker.sx, picker.ey+a.padding, check_radius,
                       (255, 255, 255), "c", font, "First", 150, 100)
    s_color = Checkbox(picker.sx, picker.ey+a.padding +
                       ftext[1], check_radius, (255, 255, 255), "c", font, "Second", 150, 100)
    b_color = Checkbox(picker.sx+picker.can_l+picker.gap+picker.slider_width -
                       btext[0]-a.padding//2-check_radius*2, picker.ey+a.padding, check_radius, (255, 255, 255), "c", font, "Both", 150, 100)
    b_color.checked = True
    a_color = Checkbox(picker.sx+picker.can_l+picker.gap+picker.slider_width -
                       btext[0]-a.padding//2-check_radius*2, picker.ey+a.padding+btext[1], check_radius, (255, 255, 255), "c", font, "Add", 150, 100)
    Checkbox.data = [picker.h, picker.s, picker.v,
                     picker.c, picker.cx, picker.cy, picker.ry]
    client = Client()
    for obj in modes:
        if obj.mode == a.mode:
            obj.checked = True
    run = True
    allow = True
    while run:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if a.mode == "c":
            react_check.action_check(mx, my, event, True)
            picker.logic(mx, my, event)
            if react_check.checked:
                f_color.checked = False
                s_color.checked = False
                b_color.checked = True
                a.h = picker.h
                a.logic()
                picker.c = a.c
                f_color.elipse_color = (0, 0, 0)
                s_color.elipse_color = (0, 0, 0)
                b_color.elipse_color = (255, 255, 255)
                picker.pick = "b"
            else:
                handle_colors([f_color, s_color, b_color],
                              mx, my, event, picker)
                a_color.action_check(mx, my, event, False)

                if f_color.checked:
                    picker.first_color = picker.c
                    picker.pick = "f"
                elif s_color.checked:
                    picker.second_color = picker.c
                    picker.pick = "s"
                elif b_color.checked:
                    b_color.elipse_color = picker.c
                    picker.pick = "b"

                f_color.elipse_color = picker.first_color
                s_color.elipse_color = picker.second_color
            if react_check.checked or last_message != picker.pick + str(picker.c):
                client.send(picker.pick, picker.c)
                last_message = picker.pick + str(picker.c)
            picker.draw_canvas(win)
            f_color.draw_check(win, picker.first_color)
            s_color.draw_check(win, picker.second_color)
            b_color.draw_check(win, picker.c)
            a_color.draw_check(win, (255, 255, 255))

            react_check.draw_check(win, picker.c)

        else:
            a.logic()
            client.send("b", a.c)
            a.draw_spectrum(win)
        handle_modes(modes, mx, my, a, event, picker)
        pygame.display.update()
        win.fill((0, 0, 0))
    # time.sleep(client.delay*2)
    # client.send("b", [0, 0, 0])
    pygame.quit()


if __name__ == "__main__":
    app()
