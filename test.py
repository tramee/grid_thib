#!/usr/bin/python3

import matplotlib
matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt
import numpy as np
import math
import glob
from scipy.signal import sepfir2d
from time import sleep
from IPython.display import clear_output
import pygame

# Set Global Variables
W_WIDTH = 300
W_HEIGHT = 300

def init():
    loc = glob.glob("/home/tramee/code/im_viz/*.jpeg")[0]
    print(f' [+] Loading image: {loc}')
    img = plt.imread(loc)
    if len(img.shape) == 3:
        print(f' [-] RGB image size {img.shape}, calculating luminance')
        img = RGB2YUV(img)
        # exit(0)
    print(f' [+] Initialization at this size: {img.shape}.')
    pygame.init()
    SCREEN = pygame.display.set_mode(img.shape)
    return SCREEN, img 

def RGB2YUV( rgb ):
    w, h, pix = rgb.shape
    m = np.array([[ 0.29900, -0.16874,  0.50000],
                 [0.58700, -0.33126, -0.41869],
                 [ 0.11400, 0.50000, -0.08131]])
    yuv = np.dot(rgb,m)
    yuv[:,:,1:]+=128.0
    return np.array(yuv[:,:,1], dtype=np.uint8).reshape((w,h))

def draw(screen, data):
    w, h = data.shape
    frame = np.array(data.data, copy=False, dtype=np.uint8).reshape((w, h, 1))
    screenarray = np.repeat(frame, 3, axis = 2)
    # print(f" [-] Screen array dims: {screenarray.shape}")
    # print(f" [-] Screen dims: {screen.get_size()}")
    pygame.surfarray.blit_array(screen, screenarray)
    pygame.display.flip()
    pass


def grayScale(data):
    for x in data[:2]:
        print(x[:10])
    return data
    
    
def main():
    screen, data = init()
    p = [0.03032, 0.249726, 0.439911, 0.249726, 0.03032]
    d = [-0.104550, -0.292315, 0.0, 0.292315, 0.104550] 
    img_x = sepfir2d(data, d, p)
    img_y = sepfir2d(data, p, d)
    print(f' [+] Rendering...')
    # for x in imx[:10]:
    #     print(np.rint(x)[:20].astype(np.uint8))
    draw(screen, data)
    sleep (1)
    for th in range(0, 361, 3):
        draw(screen, np.cos(np.radians(th))*img_x + np.sin(np.radians(th))*img_y)
        sleep(1/30)
    #     clear_output()
    # input (' [?] Press Enter key...')
    pygame.quit()


    print(f' [+] Closing.')

if __name__ == '__main__':
    main()
