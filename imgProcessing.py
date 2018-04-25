import numpy as np
from PIL import ImageGrab
from PIL import Image
import pyautogui
import cv2


def startGameScan():
    img = ImageGrab.grab()
    screen = np.array(img)
    width, height = img.size
    fPxMatch = (0,0)
    lPxMatch = (0,0)
    for x in range(width):
        for y in range(height):
            r,g,b = img.getpixel((x,y))
            if r == 36 and g == 36 and b == 80:
                if fPxMatch == (0,0):
                    fPxMatch = (x,y)
                lPxMatch = (x,y)

    return (fPxMatch[0], fPxMatch[1], lPxMatch[0], lPxMatch[1])
    
    
    
def clickNewGame(dimensions):
    img = ImageGrab.grab()
    width, height = img.size
    #x = (dimensions[0] + dimensions[1]) / 2
    x = (int(width) / 2)
    y = dimensions[3]
    windowImg = ImageGrab.grab(bbox=(dimensions))
    r,g,b = windowImg.getpixel((5,5))
    while(r == 36 and g == 36 and b == 80):
        y = y - 5
        pyautogui.click(x, y)
        windowImg = ImageGrab.grab(bbox=(dimensions))
        r,g,b = windowImg.getpixel((5,5))
        
