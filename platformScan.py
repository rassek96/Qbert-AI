import numpy as np
import cv2
from matplotlib import pyplot as plt

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

    #cv2.imshow("res", img_bgr)
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
