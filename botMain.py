import numpy as np
from PIL import ImageGrab
from PIL import Image
import cv2
import time
import pyautogui
from matplotlib import pyplot as plt
import imutils
import random
from platformScan import scanPlatforms
from platformScan import Platform
from imgProcessing import startGameScan
from imgProcessing import clickNewGame


def main():
    for i in list(range(3))[::-1]:
        print(i+1)
        time.sleep(1)
    print("Go!")

    dimensions = startGameScan()
    clickNewGame(dimensions)
    img = ImageGrab.grab(bbox=(dimensions))
    #Initial play area scan
    platforms = scanPlatforms(img)
    while(True):
        img = ImageGrab.grab(bbox=(dimensions))
        screen = np.array(img)
        
        #Check if game over
        if checkGameOver(screen) == True:
            print("Go!")
            clickNewGame(dimensions)
            continue
        
        calcPlay(platforms, img)
        


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
        
    try:
        rndDirect = random.choice(goodPlatDirect)
        pyautogui.keyDown(rndDirect)
        pyautogui.keyUp(rndDirect)
        return rndDirect
    except:
        return



def checkNewLevel(platforms, screen):
    print()
    
def checkGameOver(screen):
    #36,36,80
    px = screen[415,195]
    if px[0] == 36 and px[1] == 36 and px[2] == 80:
        return True
    else:
        return False
    

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

