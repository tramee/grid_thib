#!/usr/bin/python3

import pygame
import pygame.gfxdraw
import math
import sys
from time import sleep, time
import colorsys

config = {
    'screen': None,
    'cells': (80, 80),     # number of cells
    'border': 0,           # pixel
    'size': (1200, 1000),  # size of the screen
    'min_size': (800, 600),  # minimum size of the screen
    'bg_color': (51, 51, 51),
    'line_color': (191, 191, 151),
    'text_color': (90, 154, 185),
    'fill_color': (51, 214, 244),
    'start_time': None,
    'fps': 60
}


def RGB2YUV(rgb):
    R, G, B = rgb
    Y = 0.299 * R + 0.587 * G + 0.114 * B
    U = - 0.168736 * R - 0.331264 * G + 0.5 * B
    V = 0.5 * R - 0.418688 * G - 0.081312 * B
    return (Y, U, V)
    # return (math.floor(Y), math.floor(U), math.floor(V))


def RGB2YIQ(rgb):
    R, G, B = rgb
    Y, I, Q = colorsys.rgb_to_yiq(R/255, G/255, B/255)
    return (Y, I, Q)
    # return (math.floor(Y), math.floor(U), math.floor(V))


def YIQ2RGB(yiq):
    Y, I, Q = yiq
    R, G, B = colorsys.yiq_to_rgb(Y, I, Q)
    R = math.floor(255*R)
    G = math.floor(255*G)
    B = math.floor(255*B)
    return (R, G, B)


def YUV2RGB(yuv):
    Y, U, V = yuv
    R = 1 * Y + 0 * U + 1.4022 * V
    G = 1 * Y - 0.3456 * U - 0.7145 * V
    B = 1 * Y + 1.7710 * U + 0 * V
    return (max(0, min(255, math.floor(R))), max(0, min(255, math.floor(G))), max(0, min(255, math.floor(B))))


class star():
    def __init__(self, conf, x, y):
        self.pos = (x, y)
        self.conf = conf
        self.size = 1
        self.max_size = 10
        self.cells = [cell(conf, x, y)]
        self.timeout = 0.05
        self.start = time()
        self.live = True
        self.color = (255, 255, 255)

    def setColor(self, i, j):
        i = (i / 255) % 2.0 - 1
        j = (j / 255) % 2.0 - 1
        color = (51, 214, 244)
        Y, I, Q = RGB2YIQ(color)
        self.color = YIQ2RGB((Y, i, j))

    def update(self):
        for c in self.cells:
            c.active = True
            c.color = self.color
        if not self.live:
            return
        if time() - self.start > self.timeout:
            w, h = self.pos
            maxw, maxh = self.conf['cells']
            self.start += self.timeout
            if self.size > self.max_size:
                self.live = False
                return
            # star pattern
            # new_cells = ((w + self.size, h), (w - self.size, h), (w, h+self.size), (w,h-self.size))
            new_cells = [(i, h+j) for j in range(-self.size, self.size)
                         for i in (w-abs(j), w+abs(j))]
            for a, b in new_cells:
                if a >= 0 and b >= 0 and a < maxw and b < maxh:
                    self.cells.append(cell(self.conf, a, b))
            self.size += 1
            return self.live

    def draw(self):
        if not self.live:
            return
        if self.cells is None:
            return
        for c in self.cells:
            c.draw()


class cell():
    def __init__(self, conf, x, y):
        self.pos = (x, y)
        self.conf = conf
        self.border = conf['border']
        self.pads = conf['pads']
        self.width = conf['width']
        self.active = False
        self.color = conf['fill_color']
        self.display_text = False
        self.resize()

    def resize(self):
        self.pads = self.conf['pads']
        self.width = self.conf['width']
        x, y = self.pos
        w, b1 = self.width, math.floor(self.border*.5)
        b2 = self.border-b1
        px, py = self.pads
        x = x * (w + b1 + b2) + px
        y = y * (w + b1 + b2) + py
        # print(f'drawing x:{x} y:{y} w:{w} b1:{b1} b2:{b2} ')
        self.xywb1b2 = (x, y, w, b1, b2)

    def draw(self):
        x, y, w, b1, b2 = self.xywb1b2
        if b1 > 0 or b2 > 0:
            pygame.draw.rect(
                self.conf['screen'], self.conf['line_color'], (x, y, w+b1+b2, w+b1+b2))
        if self.active:
            pygame.gfxdraw.box(self.conf['screen'],
                               (x+b1, y+b1, w, w), self.color)
        else:
            pygame.draw.rect(
                self.conf['screen'], self.conf['bg_color'], (x+b1, y+b1, w, w))
        if self.display_text:
            txt = self.conf['cfont'].render(
                f'{self.pos}', True, self.conf['text_color'])
            a, b = txt.get_size()
            txt = pygame.transform.scale(txt, (w-2, b))
            self.conf['screen'].blit(txt, (x+b1+1, y+b1+1))

    def isClicked(self, mouse):
        x, y, w, b1, b2 = self.xywb1b2
        a, b = mouse
        print(f'a:{a}, b:{b}, x:{x}, y:{y}')
        if (x+b1 < a and a < x+b1+w) and (y+b1 < b and b < y+b1+w):
            self.active = not self.active

    def getActive(self, mouse):
        x, y, w, b1, b2 = self.xywb1b2
        a, b = mouse
        if (x+b1 < a and a < x+b1+w) and (y+b1 < b and b < y+b1+w):
            return(self.active)
        return None

    def setActive(self, mouse, status):
        x, y, w, b1, b2 = self.xywb1b2
        a, b = mouse
        if (x+b1 < a and a < x+b1+w) and (y+b1 < b and b < y+b1+w):
            self.active = status == True

    def getColor(self):
        return self.color

    def setColor(self, c):
        self.color = c


def getXY(conf, pos):
    if pos is None:
        return None, None
    if len(pos) < 2:
        return None, None
    x, y = pos
    maxx, maxy = conf['cells']
    px, py = conf['pads']
    w = conf['width'] + conf['border']
    # print(f'x:{x} y:{y} w:{w} px:{px} py:{py} ')
    a, b = ((x-px)//w, (y-py)//w)
    a = a if a < maxx else maxx-1
    b = b if b < maxy else maxy-1
    return (a, b)


def resize(conf, size=None):
    # Calculate the base dimensions of the grid.
    if size is None:
        w, h = conf['size']
    else:
        conf['size'] = size
        w, h = size
    cx, cy = conf['cells']
    w -= conf['border'] * (cx+1)
    h -= conf['border'] * (cy+1)
    conf['width'] = width = min(w//cx, h//cy)
    conf['pads'] = (math.floor(0.5*(w-cx*width)), math.floor(0.5*(h-cy*width)))
    # print(f"width:{conf['width']} pads:{conf['pads']}")
    return conf


def init(conf):
    conf = resize(conf)
    # Initialize the graphics
    pygame.init()
    conf['font'] = pygame.font.SysFont('dejavu', 20)
    conf['cfont'] = pygame.font.SysFont('dejavu', 20)
    # Create the window
    conf['screen'] = pygame.display.set_mode(
        conf['size'], pygame.DOUBLEBUF | pygame.RESIZABLE)
    conf['screen'].fill(conf['bg_color'])
    pygame.display.set_caption('Grid 0.0.0')
    conf['start_time'] = time()
    pygame.display.flip()
    cx, cy = conf['cells']
    cells = [cell(conf, x, y) for x in range(cx) for y in range(cy)]
    return conf, cells


def update(conf, star_list):
    for s in star_list:
        status = s.update()


def draw(conf, table, star_list):
    conf['screen'].fill(conf['bg_color'])
    if len(table) == 0:
        pygame.display.flip()
        return
    c = table[0]
    x, y, w, b1, b2 = c.xywb1b2
    if x < w or y < w:
        sw, sh = conf['cells']
        ex, ey = sw*(w+b1+b2), sh*(w+b1+b2)
        for i in range(b1+b2):
            pygame.draw.rect(conf['screen'], conf['line_color'],
                             (x-b2+i, y-b2+i, ex+b1+b2-2*i, ey+b1+b2-2*i), width=1)
    for c in table:
        c.draw()
    for c in star_list:
        c.draw()
        # x, y = c.pos
        # if x+1 > conf['cells'][0]:
        #     x = 0
        #     y = (y + 1) % conf['cells'][1]
        # else:
        #     x += 1
        # c.pos = (x, y)
    now = time() - conf['start_time']
    w, h = conf['size']
    conf['screen'].blit(conf['font'].render(
        f'Time:', True, conf['text_color']), (w-100, 5))
    img = conf['font'].render(f'{now:000.1f}', True, conf['text_color'])
    # print(dir(img))
    conf['screen'].blit(img, (w-5-img.get_size()[0], 5))
    pygame.display.flip()


def main(conf):
    conf, cells = init(conf)
    stars = []
    status = None
    # Calculate time allowed by frame
    tpf = 1 / conf['fps']
    abs_pos = None
    cell_color = None
    movement = False
    buttons = None
    while True:
        t1 = time()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    print('Bye!')
                    pygame.quit()
                    exit(0)
                else:
                    print(f' [-] Key pressed: {pygame.key.name(event.key)} ')
            elif event.type == pygame.QUIT:
                pygame.quit()
                print('Bye!')
                exit(0)
            elif event.type == pygame.VIDEORESIZE:
                w, h = event.dict['size']
                minw, minh = conf['min_size']
                a, b = (max(w, minw), max(h, minh))
                conf = resize(conf, (a, b))
                for c in cells:
                    c.resize()
            elif (event.type == pygame.MOUSEBUTTONUP):
                if abs_pos is None or buttons is None:
                    pass
                elif (not movement) and buttons[0]:
                    x, y = getXY(conf, abs_pos)
                    # print(f'mouse at {x, y}')
                    status = cells[y+x*conf['cells'][1]].getActive(abs_pos)
                    if not status is None:
                        status = not status
                        stars.append(star(conf, x, y))
                        # cells[y+x*conf['cells'][1]].setActive(abs_pos, status)
                abs_pos = None
                status = None
                cell_color = None
                movement = False
            elif (event.type == pygame.MOUSEMOTION) and pygame.mouse.get_pressed()[0]:
                movement = True
                # if status is None:
                #     x, y = getXY(conf, abs_pos)
                #     if x is None:
                #         break
                # status = cells[y+x*conf['cells'][1]].getActive(abs_pos)
                # cell_color = cells[y+x*conf['cells'][1]].getColor()
                x, y = getXY(conf, abs_pos)
                pos = pygame.mouse.get_pos()
                i, j = getXY(conf, pos)
                # cells[y+x*conf['cells'][1]].setActive(pos, status)
                # cells[y+x*conf['cells'][1]].setColor(cell_color)
                if not(x == i and y == j):
                    s = star(conf, i, j)
                    s.setColor(i*6, j*6)
                    stars.append(s)
                    abs_pos = pos
            elif (event.type == pygame.MOUSEMOTION) and pygame.mouse.get_pressed()[2]:
                movement = True
                # If the right button is pressed, change the hue of the color
                if not abs_pos is None:
                    pos = pygame.mouse.get_pos()
                    x, y = pos
                    a, b = abs_pos
                    c, d = getXY(conf, abs_pos)
                    cell = cells[d+c*conf['cells'][1]]
                    Y, I, Q = RGB2YIQ(cell.getColor())
                    I = (I + 1.0 + (x - a)/100) % 2.0 - 1.0
                    Q = (Q + 1.0 + (y - b)/100) % 2.0 - 1.0
                    new_color = YIQ2RGB((Y, I, Q))
                    # print(f'  | New YUV:{(Y,I,Q)} |  New RGB:{new_color}')
                    cell.setColor(new_color)
                    pygame.mouse.set_pos(abs_pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                abs_pos = pygame.mouse.get_pos()
                buttons = pygame.mouse.get_pressed()

        update(conf, stars)
        draw(conf, cells, stars)
        # Clean up
        for s in stars:
            if not s.live:
                stars.remove(s)
        sys.stdout.write(
            f'\r load index: {((time()-t1)/tpf)*100:0.2f}% \t\t star list length: {len(stars)}')
        sleep(max(tpf - time()-t1, 0))


if __name__ == '__main__':
    main(config)
