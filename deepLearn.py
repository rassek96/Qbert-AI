import win32api as wapi
import numpy as np
import cv2
import os
from random import shuffle
import tflearn
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression

fileName = "training_data.npy"
fileNameV2 = "training_data_v2.npy"

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

def balanceData():
    lefts = []
    rights = []
    ups = []
    downs = []
    
    shuffle(trainingData)
    for data in trainingData:
        img = data[0]
        choice = data[1]
        if choice == [1,0,0,0,0]:
            lefts.append([img, choice])
        elif choice == [0,1,0,0,0]:
            rights.append([img, choice])
        elif choice == [0,0,1,0,0]:
            ups.append([img, choice])
        elif choice == [0,0,0,1,0]:
            downs.append([img, choice])

    lefts = lefts[:len(rights)][:len(ups)][:len(downs)]
    rights = rights[:len(lefts)]
    ups = ups[:len(lefts)]
    downs = downs[:len(lefts)]

    finalData = lefts + rights + ups + downs
    shuffle(finalData)
    np.save(fileNameV2, finalData)

def saveToFile(screen, output):
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    screen = cv2.resize(screen, (80,60))
    global trainingData
    trainingData.append([screen,output])
    if len(trainingData) % 100 == 0:
        print("Saving to file!")
        print(len(trainingData))
        np.save(fileName, trainingData)


def getModel(width, height, lr):
    convnet = input_data(shape=[None, width, height, 1], name='input')
    convnet = conv_2d(convnet, 32, 5, activation='relu')
    convnet = max_pool_2d(convnet, 5)
    convnet = conv_2d(convnet, 64, 5, activation='relu')
    convnet = max_pool_2d(convnet, 5)
    convnet = conv_2d(convnet, 128, 5, activation='relu')
    convnet = max_pool_2d(convnet, 5)
    convnet = conv_2d(convnet, 64, 5, activation='relu')
    convnet = max_pool_2d(convnet, 5)
    convnet = conv_2d(convnet, 32, 5, activation='relu')
    convnet = max_pool_2d(convnet, 5)
    convnet = fully_connected(convnet, 1024, activation='relu')
    convnet = dropout(convnet, 0.8)
    convnet = fully_connected(convnet, 5, activation='softmax')
    convnet = regression(convnet, optimizer='adam', learning_rate=lr, loss='categorical_crossentropy', name='targets')
    model = tflearn.DNN(convnet, tensorboard_dir='log')
    return model



width = 80
height = 60
lr = 1e-3
gModel = None
def train():
    modelName = "qbert-bot-{}-{}-epochs.model".format(lr, "modelnet")
    #trainData = getTrainingData()
    trainData = np.load(fileName)
    model = getModel(width, height, lr)
    global gModel
    gModel = model
    
    train = trainData[:-500]
    test = trainData[-500:]

    x = np.array([i[0] for i in train]).reshape(-1,width,height,1)
    y = [i[1] for i in train]

    test_x = np.array([i[0] for i in test]).reshape(-1,width,height,1)
    test_y = [i[1] for i in test]
    
    model.fit(x, y, n_epoch=3, validation_set=(test_x, test_y), 
    snapshot_step=500, show_metric=True, run_id=modelName)
    model.save(modelName)

def test(screen):
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    screen = cv2.resize(screen, (width,height))
    data = screen.reshape(width, height, 1)
    model = gModel
    modelOut = model.predict([data])[0]
    modelList = modelOut.tolist()
    i = modelList.index(max(modelList))
    if i == 0:
        #print("deep", "left")
        return "left"
    elif i == 1:
        #print("deep", "right")
        return "right"
    elif i == 2:
        #print("deep", "up")
        return "up"
    elif i == 3:
        #print("deep", "down")
        return "down"
    else:
        return None
        
