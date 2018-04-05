import numpy as np
from PIL import ImageGrab
from PIL import Image
import cv2
import time
import pyautogui
from matplotlib import pyplot as plt
import imutils
import random
import os

def main():
    for i in list(range(3))[::-1]:
        print(i+1)
        time.sleep(1)
    print("Go!")
    pyautogui.click(970, 890)
    time.sleep(0.1)
    #Initial play area scan
    img = ImageGrab.grab(bbox=(412,191,1510,1020))
    platforms = scanPlatforms(img)
    while(True):
        imgScreen = ImageGrab.grab(bbox=(412,191,1510,1020))
        screen = np.array(imgScreen)
        
        calcPlay(platforms, imgScreen)    

def calcPlay(platforms, imgScreen):
    #Calc play
    qBertPlat = 0
    badPlat = []
    for plat in platforms:
        platStand = plat.scanPlatform(imgScreen)
        if platStand == "QBERT":
            qBertPlat = plat.platNumber
        elif platStand == "BALL" or platStand == "SNAKE":
            badPlat.append(plat.platNumber)

    playable = getPlayable(qBertPlat)
    #Logic
    goodPlatNumber = []
    goodPlatDirect = []
    for i in range(0,len(playable[0])):
        if playable[0][i] in badPlat:
            continue
        else:
            playable2 = getPlayable(playable[0][i])
            platIsGood = True
            for i2 in range(0,len(playable2[0])):
                if(playable2[0][i2] in badPlat):
                    platIsGood = False
                    break
            if platIsGood == True:
                goodPlatNumber.append(playable[0][i])
                goodPlatDirect.append(playable[1][i])
    if len(goodPlatDirect) == 0:
        for i in range(0,len(playable[0])):
            if len(playable[0]) == 1:
                goodPlatNumber.append(playable[0][i])
                goodPlatDirect.append(playable[1][i])
            elif playable[0][i] in badPlat:
                continue
            else:
                goodPlatNumber.append(playable[0][i])
                goodPlatDirect.append(playable[1][i])
            
    rndDirect = random.choice(goodPlatDirect)
    pyautogui.keyDown(rndDirect)
    pyautogui.keyUp(rndDirect)
    return

def scanPlatforms(img):
    img_bgr = np.array(img)
    img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_RGB2BGR)
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    template = cv2.imread("BlueTile2.png",0)
    w,h = template.shape[::-1]
    
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where(res >= threshold)
    oldPts = []
    #DETECTS PLATFORMS
    platforms = []
    for pt in zip(*loc[::-1]):
        #avoid duplicates
        duplicate = False
        for ptOld in oldPts:
            if  pt[0] - ptOld[0] != 0 and pt[0] - ptOld[0] in range(-6,6) or pt[1] - ptOld[1] != 0 and pt[1] - ptOld[1] in range(-6,6):
                duplicate = True
                break
        #REMOVE LATER
        if duplicate == True and pt != (770,650):
            continue
        oldPts.append(pt)
        #Move rectangle up slightly to cover platform area
        tempList = list(pt)
        tempList[1] = tempList[1] - 35
        pt = tuple(tempList)
        cv2.rectangle(img_bgr, pt, (pt[0]+w,pt[1]+h), (0,255,255), 2)

        pt1 = (pt[0], pt[1])
        pt2 = (pt[0]+w, pt[1]+h)
        p = Platform(pt1, pt2)
        platforms.append(p)

    cv2.imshow("res", img_bgr)
    #REMOVE LATER
    platforms[26], platforms[27] = platforms[27], platforms[26]
    platforms[26].platNumber, platforms[27].platNumber = 26, 27
    return platforms


class Platform:
    "Game level platform"
    platCount = 0

    def __init__(self, coords1, coords2):
        self.pt1 = coords1
        self.pt2 = coords2
        self.platNumber = Platform.platCount
        Platform.platCount += 1
        self.playable = []

    def scanPlatform(self, img):
        imgCrop = img.crop((self.pt1[0], self.pt1[1], self.pt2[0], self.pt2[1]))
        colors = imgCrop.getcolors(256)
        orange = False
        red = False
        purple = False
        for c in colors:
            if c[1][0] == 239 and c[1][1] == 86 and c[1][2] == 0:
                orange = True
            elif c[1][0] == 179 and c[1][1] == 0 and c[1][2] == 179:
                purple = True
            elif c[1][0] == 230 and c[1][1] == 0 and c[1][2] == 230:
                purple = True
            elif c[1][0] == 239 and c[1][1] == 16 and c[1][2] == 33:
                red = True
        if orange == True and red == True:
            return "QBERT"
        elif purple == True:
            return "SNAKE"
        elif red == True and orange == False:
            return "BALL"

def screenGrab():
    while(True):
        screen = np.array(ImageGrab.grab(bbox=(412,191,1510,1020)))
        cv2.imshow("window", cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break

def getPlayable(platNumber):
    if platNumber == 0:
        return [[1,2], ["down","right"]]
    elif platNumber == 1:
        return [[3,4,0], ["down","right","up"]]
    elif platNumber == 2:
        return [[4,5,0], ["down","right","left"]]
    elif platNumber == 3:
        return [[6,7,1], ["down","right","up"]]
    elif platNumber == 4:
        return [[7,8,1,2], ["down","right","left","up"]]
    elif platNumber == 5:
        return [[8,9,2], ["down","right","left"]]
    elif platNumber == 6:
        return [[10,11,3], ["down","right","up"]]
    elif platNumber == 7:
        return [[11,12,3,4], ["down","right","left","up"]]
    elif platNumber == 8:
        return [[12,13,4,5], ["down","right","left","up"]]
    elif platNumber == 9:
        return [[13,14,5], ["down","right","left"]]
    elif platNumber == 10:
        return [[15,16,6], ["down","right","up"]]
    elif platNumber == 11:
        return [[16,17,6,7], ["down","right","left","up"]]
    elif platNumber == 12:
        return [[17,18,7,8], ["down","right","left","up"]]
    elif platNumber == 13:
        return [[18,19,8,9], ["down","right","left","up"]]
    elif platNumber == 14:
        return [[19,20,9], ["down","right","left"]]
    elif platNumber == 15:
        return [[21,22,10], ["down","right","up"]]
    elif platNumber == 16:
        return [[22,23,10,11], ["down","right","left","up"]]
    elif platNumber == 17:
        return [[23,24,11,12], ["down","right","left","up"]]
    elif platNumber == 18:
        return [[24,25,12,13], ["down","right","left","up"]]
    elif platNumber == 19:
        return [[25,26,13,14], ["down","right","left","up"]]
    elif platNumber == 20:
        return [[26,27,14], ["down","right","left"]]
    elif platNumber == 21:
        return [[15], ["up"]]
    elif platNumber == 22:
        return [[15,16], ["left","up"]]
    elif platNumber == 23:
        return [[16,17], ["left","up"]]
    elif platNumber == 24:
        return [[17,18], ["left","up"]]
    elif platNumber == 25:
        return [[18,19], ["left","up"]]
    elif platNumber == 26:
        return [[19,20], ["left","up"]]
    elif platNumber == 27:
        return [[20], ["left"]]

main()


