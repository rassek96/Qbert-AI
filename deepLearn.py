import win32api as wapi
import numpy as np
import cv2
from modelnet import modelnet
import os

fileName = "training_data.npy"

trainingData = []
if os.path.isfile(fileName):
    trainingData = list(np.load(fileName))
    
def outputKeys(keyPress):
    #[Left,Right,Up,Down,None]
    output = [0,0,0,0,0]
    if keyPress == "left":
        output[0] = 1
    elif keyPress == "right":
        output[1] = 1
    elif keyPress == "up":
        output[2] = 1
    elif keyPress == "down":
        output[3] = 1
    else:
        output[4] = 1
        
    return output

def getTrainingData():
    return trainingData

def saveToFile(screen, output):
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    screen = cv2.resize(screen, (80,60))
    global trainingData
    trainingData.append([screen,output])
    if len(trainingData) % 500 == 0:
        print("Saving to file!")
        print(len(trainingData))
        np.save(fileName, trainingData)


def train():
    width = 80
    height = 60
    lr = 1e-3
    epochs = 8
    modelName = "qbert-bot-{}-{}-{}-epochs.model".format(lr, "modelnet",epochs)
    model = modelnet(width, height, lr)

    trainData = np.load(fileName)
    train = trainData[:-500]
    test = trainData[-500:]

    x = np.array([i[0] for i in train]).reshape(-1,width,height,1)
    y = [i[1] for i in train]
    test_x = np.array([i[0] for i in test]).reshape(-1, width, height, 1)
    test_y = [i[1] for i in test]

    model.fit({"input": x}, {"targets": y}, n_epoch=epochs, validation_set=({"input": test_x}, {"targets": test_y}), snapshot_step=500, show_metric=True, run_id=modelName)

    model.save("./" + modelName)



gModel = None

def start():
    width = 80
    height = 60
    lr = 1e-3
    epochs = 8
    modelName = "qbert-bot-{}-{}-{}-epochs.model".format(lr, "modelnet",epochs)
    model = modelnet(width, height, lr)
    model.load("./" + modelName)
    global gModel
    gModel = model

def test(screen):
    try:
        

        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        screen = cv2.resize(screen, (80,60))
        
        moves = list(np.around(gModel.predict([screen.reshape(80,60,1)])[0]))

        if moves == [1,0,0,0,0]:
            print("deep", "left")
            return "left"
        elif moves == [0,1,0,0,0]:
            print("deep", "right")
            return "right"
        elif moves == [0,0,1,0,0]:
            print("deep", "up")
            return "up"
        elif moves == [0,0,0,1,0]:
            print("deep", "down")
            return "down"
        else:
            return None
    except:
        print("fail")
        return
