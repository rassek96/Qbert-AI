import win32api as wapi
import numpy as np
from alexnet import alexnet

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
    if len(tData) % 500 == 0:
        print("Saving to file!")
        print(len(trainingData))
        np.save(fileName, tData)


def train():
    width = 80
    height = 60
    lr = 1e-3
    epochs = 8
    modelName = "qbert-bot-{}-{}-{}-epochs.model".format(lr, "alexnetv2",epochs)
    model = alexnet(width, height, lr)

    trainData = np.load(fileName)
    train = trainData[:-500]
    test = trainData[-500:]

    x = np.array([i[0] for i in train]).reshape(-1,width,height,1)
    y = [i[1] for i in train]
    test_x = np.array([i[0] for i in test]).reshape(-1, width, height, 1)
    test_y = [i[1] for i in test]

    model.fit({"input": x}, {"targets": y}, n_epoch=epochs, validation_set=({"input": test_x}, {"targets": test_y}), snapshot_step=500, show_metric=True, run_id=modelName)

    model.save(modelName)
