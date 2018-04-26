#import numpy as np
#from PIL import ImageGrab
from PIL import Image
import pyautogui
import cv2
import mss
from win32api import GetSystemMetrics


def startGameScan():
    img = takeScreenshot(None)
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
    img = takeScreenshot(None)
    width, height = img.size
    x = (int(width) / 2)
    y = dimensions[3]
    windowImg = takeScreenshot(dimensions)
    r,g,b = windowImg.getpixel((5,5))
    while(r == 36 and g == 36 and b == 80):
        y = y - 5
        pyautogui.click(x, y)
        windowImg = takeScreenshot(dimensions)
        r,g,b = windowImg.getpixel((5,5))
        

def takeScreenshot(dimensions):
    if(dimensions == None):
        with mss.mss() as sct:
            monitor = 0,0,GetSystemMetrics(0),GetSystemMetrics(1)
            for num, monitor in enumerate(sct.monitors[1:], 1):
                sctImg = sct.grab(monitor)
                img = Image.frombytes("RGB", sctImg.size, sctImg.bgra, "raw", "BGRX")
                return img
    else:
        with mss.mss() as sct:
            for num, monitor in enumerate(sct.monitors[1:], 1):
                
                sctImg = sct.grab(dimensions)
                img = Image.frombytes("RGB", sctImg.size, sctImg.bgra, "raw", "BGRX")
                return img
