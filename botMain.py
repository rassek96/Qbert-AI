import numpy as np
from PIL import Image
import time
import pyautogui
import random
import mss
from platformScan import scanPlatforms
from platformScan import Platform
from imgProcessing import startGameScan
from imgProcessing import clickNewGame
from imgProcessing import takeScreenshot
import deepLearn


levelColor = (0,0,0)
dimensions = (0,0,0,0)

def main():
    for i in list(range(2))[::-1]:
        print(i+1)
        time.sleep(1)
    print("Go!")
    deepLearn.train()
    global dimensions
    dimensions = startGameScan()
    clickNewGame(dimensions)
    img = takeScreenshot(dimensions)
    #Initial play area scan
    platforms = scanPlatforms(img)
    updateLevel(platforms, img)
    gameOverCount = 0
    oldImg = img
    oldDirect = "down"
    oldQBertPlat = 0
    while(True):
        img = takeScreenshot(dimensions)
        screen = np.array(img)

        if checkEnemyCollision(platforms, img, oldQBertPlat) == False:
            #print("save", oldQBertPlat, oldDirect)
            output = deepLearn.outputKeys(oldDirect)
            oldScreen = np.array(oldImg)
            deepLearn.saveToFile(oldScreen, output)
            
        #Check if game over
        if checkGameOver(screen) == True:
            gameOverCount += 1
            filename = "gameovers/" + str(gameOverCount) + ".png"
            oldImg.save(filename, "PNG")
            print("Go!")
            clickNewGame(dimensions)
            img = takeScreenshot(dimensions)
            updateLevel(platforms, img)
            continue
        
        #Self-learning
        nnDirect = deepLearn.test(screen)
        direct, qBertPlat = calcPlay(platforms, img, nnDirect)
        oldQBertPlat = qBertPlat
        #print("Calc", direct)
        #print()
        
        oldImg = img
        oldDirect = direct
        

def calcPlay(platforms, imgScreen, nnDirect):
    playable, badPlat, ballPlat, qBertPlat = findQBert(platforms, imgScreen)
    #Logic
    isCorner = False
    goodPlatNumber = []
    goodPlatDirect = []
    # loops through all playable/possible moves and finds good platforms
    for i in range(0,len(playable[0])):
        if playable[0][i] in badPlat or playable[0][i] in ballPlat:
            continue
        else:
            playable2 = getPlayable(playable[0][i])
            platIsGood = True
            for i2 in range(0,len(playable2[0])):
                if(playable2[0][i2] in badPlat):
                    platIsGood = False
                    break
                elif playable2[0][i2] in ballPlat:
                    if playable2[0][i2] < playable[0][i]:
                        platIsGood = False
            if platIsGood == True:
                goodPlatNumber.append(playable[0][i])
                goodPlatDirect.append(playable[1][i])
            if len(playable[0]) == 1: 
                isCorner = True
    if len(goodPlatDirect) == 0:
        for i in range(0,len(playable[0])):
            if len(playable[0]) == 1:
                goodPlatNumber.append(playable[0][i])
                goodPlatDirect.append(playable[1][i])
            elif playable[0][i] in badPlat:
                continue
     
    goodPlatColorDirect = []
    i = 0
    for gNum in goodPlatNumber:
        if platforms[gNum].checkLevelColor(levelColor, imgScreen) == True:
            goodPlatColorDirect.append(goodPlatDirect[i])
        i += 1
        
    #if a direction matches neural network match use it
    for gDir in goodPlatColorDirect:
        if gDir == nnDirect:
            pyautogui.keyDown(gDir)
            pyautogui.keyUp(gDir)
            return gDir, qBertPlat
    for gDir in goodPlatDirect:
        if gDir == nnDirect:
            pyautogui.keyDown(gDir)
            pyautogui.keyUp(gDir)
            return gDir, qBertPlat
    ## otherwise pick a random good direction
    try:
        rndDirect = None
        if len(goodPlatColorDirect) > 0:
            rndDirect = random.choice(goodPlatColorDirect)
        else:
            rndDirect = random.choice(goodPlatDirect)
        pyautogui.keyDown(rndDirect)
        pyautogui.keyUp(rndDirect)
        if isCorner == True:
            time.sleep(0.2)
            pyautogui.keyDown(rndDirect)
            pyautogui.keyUp(rndDirect)
        return rndDirect, qBertPlat
    except:
        return None, qBertPlat

def findQBert(platforms, img):
    imgScreen = img
    qBertPlat = -1
    badPlat = []
    ballPlat = []
    isNewLevel = False
    while(qBertPlat == -1):
        for plat in platforms:
            platStand = plat.scanPlatform(imgScreen)
            if platStand == "QBERT":
                qBertPlat = plat.platNumber
            elif platStand == "BALL":
                ballPlat.append(plat.platNumber)
            elif platStand == "SNAKE":
                badPlat.append(plat.platNumber)
        #If qbert wasn't found check if it's a new level, if it is update
        if qBertPlat == -1:
            imgScreen = takeScreenshot(dimensions)
            if checkNewLevel(platforms, imgScreen) == True:
                isNewLevel = True

    if isNewLevel == True:
        updateLevel(platforms, imgScreen)

    return getPlayable(qBertPlat), badPlat, ballPlat, qBertPlat
    

def checkNewLevel(platforms, img):
    dimens = platforms[27].getBottomDimens()
    width, height = img.size
    imgCrop = img.crop((0, dimens[1], width, height))
    colors = imgCrop.getcolors(256)
    for c in colors:
        if c[1][0] == 255 and c[1][1] == 0 and c[1][2] == 255:
            return True
    return False

def updateLevel(platforms, img):
    bottomDimens = platforms[12].getBottomDimens()
    topDimens = platforms[12].getTopDimens()
    y = bottomDimens[1]
    x = (topDimens[0] + bottomDimens[0]) / 2
    imgPx = img.load()
    pxC = imgPx[int(x),int(y)]
    global levelColor
    levelColor = pxC

def checkGameOver(screen):
    px = screen[5,5]
    if px[0] == 36 and px[1] == 36 and px[2] == 80:
        return True
    else:
        return False
    
def checkEnemyCollision(platforms, img, qBertPlat):
    if qBertPlat == -1:
        return True
    return platforms[qBertPlat].scanPlatformForCollision(img)


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


