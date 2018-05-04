import win32api as wapi
import numpy as np
import cv2
import os
from random import shuffle
import tflearn
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.normalization import local_response_normalization
from tflearn.layers.estimator import regression
import tensorflow as tf

tf.logging.set_verbosity(tf.logging.ERROR)
tf.reset_default_graph()

fileName = "training_data.npy"
fileNameV2 = "training_data_v2.npy"

trainingData = []
if os.path.isfile(fileName):
    trainingData = list(np.load(fileName))
    
def outputKeys(keyPress):
    #[Left,Right,Up,Down,None]
    output = [0,0,0,0]
    if keyPress == "left":
        output[0] = 1
    elif keyPress == "right":
        output[1] = 1
    elif keyPress == "up":
        output[2] = 1
    elif keyPress == "down":
        output[3] = 1
    return output

def keyCheck():
    if wapi.GetAsyncKeyState(39) != 0:
        print("right")
        return "right"
    elif wapi.GetAsyncKeyState(37) != 0:
        print("left")
        return "left"
    elif wapi.GetAsyncKeyState(38) != 0:
        print("up")
        return "up"
    elif wapi.GetAsyncKeyState(40) != 0:
        print("down")
        return "down"
    else:
        return None

def getTrainingData():
    return trainingData

def balanceData():
    trainData = np.load(fileName)
    
    lefts = []
    rights = []
    ups = []
    downs = []
    for data in trainData:
        img = data[0]
        choice = data[1]
        if choice == [1,0,0,0]:
            lefts.append([img, choice])
        elif choice == [0,1,0,0]:
            rights.append([img, choice])
        elif choice == [0,0,1,0]:
            ups.append([img, choice])
        elif choice == [0,0,0,1]:
            downs.append([img, choice])
    l = [len(downs), len(rights),len(lefts),len(ups)]
    shortestL = min(float(i) for i in l)
    finalData= []
    for i in range(int(shortestL)):
        finalData.append(downs[i])
        finalData.append(ups[i])
        finalData.append(rights[i])
        finalData.append(lefts[i])
    shuffle(finalData)
    print(len(finalData))
    np.save(fileNameV2, finalData)


def getModel(width, height, lr):
    convnet = input_data(shape=[None, width, height, 1], name='input')
    convnet = conv_2d(convnet, 32, 8, activation='relu')
    convnet = max_pool_2d(convnet, 8)
    convnet = conv_2d(convnet, 64, 8, activation='relu')
    convnet = max_pool_2d(convnet, 8)
    convnet = conv_2d(convnet, 128, 8, activation='relu')
    convnet = max_pool_2d(convnet, 8)
    convnet = conv_2d(convnet, 64, 8, activation='relu')
    convnet = max_pool_2d(convnet, 8)
    convnet = conv_2d(convnet, 32, 8, activation='relu')
    convnet = max_pool_2d(convnet, 8)
    convnet = fully_connected(convnet, 1024, activation='relu')
    convnet = dropout(convnet, 0.8)
    convnet = fully_connected(convnet, 4, activation='softmax')
    convnet = regression(convnet, optimizer='adam', learning_rate=lr, loss='categorical_crossentropy', name='targets')
    model = tflearn.DNN(convnet, tensorboard_dir='log')
    return model


width = 160
height = 120
lr = 1e-3
epochs = 6
hmData = 6
modelName = "qbert-bot-{}-{}-epochs.model".format(lr, "modelnet")

def saveToFile(img, output):
    if output == [0,0,0,0]:
        return False
    
    screen = convImage(img)
    global trainingData
    trainingData.append([screen,output])
    if len(trainingData) % 200 == 0:
        print("Saving to file!")
        print(len(trainingData))
        np.save(fileName, trainingData)
        return True
    else:
        return False

autoTrainingData = []
lastSize = 0
if os.path.isfile("autoTrainingData.npy"):
    autoTrainingData = list(np.load("autoTrainingData.npy"))
    lastSize = len(autoTrainingData)
def autoCollect(img, output):
    if output == [0,0,0,0]:
        return False
    screen = convImage(img)
    global autoTrainingData
    autoTrainingData.append([screen,output])

def autoSaveToFile(shouldSave):
    global autoTrainingData
    global lastSize
    
    if shouldSave == True and (len(autoTrainingData) - lastSize) < 120:
        print("Saving to file!")
        print(len(autoTrainingData))
        np.save("autoTrainingData.npy", autoTrainingData)
    else:
        autoTrainingData = []
        if os.path.isfile("autoTrainingData.npy"):
            autoTrainingData = list(np.load("autoTrainingData.npy"))

autoTrainingBadData = []
if os.path.isfile("autoTrainingBadData.npy"):
    autoTrainingBadData = list(np.load("autoTrainingBadData.npy"))
def autoBadCollect(img, output):
    if output == [0,0,0,0]:
        return False
    screen = convImage(img)
    global autoTrainingBadData
    autoTrainingBadData.append([screen,output])
def autoSaveToBadFile(shouldSave):
    global autoTrainingBadData
    # and (len(autoTrainingData) - lastSize) < 120
    if shouldSave == True:
        print("Saving to bad file!")
        print(len(autoTrainingBadData))
        np.save("autoTrainingBadData.npy", autoTrainingBadData)
    else:
        autoTrainingBadData = []
        if os.path.isfile("autoTrainingBadData.npy"):
            autoTrainingBadData = list(np.load("autoTrainingBadData.npy"))
def convImage(img):
    screen = img
    screen[np.where((screen == [239, 86, 0]).all(axis = 2))] = [69, 244, 66]
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    screen = cv2.resize(screen, (width,height))
    return screen

def train():
    #balanceData()
    model = getModel(width, height, lr)
    for e in range(epochs):
        for i in range(1, hmData+1):
            tf.reset_default_graph()
            trainData = np.load("autoTrainingBadData.npy")
            train = trainData[:-20]
            test = trainData[-20:]
            x = np.array([i[0] for i in train]).reshape(-1,width,height,1)
            y = [i[1] for i in train]
            test_x = np.array([i[0] for i in test]).reshape(-1,width,height,1)
            test_y = [i[1] for i in test]
            model.fit(x, y, n_epoch=1, validation_set=(test_x, test_y), snapshot_step=500, show_metric=True, run_id=modelName)
            model.save(modelName)

model = None
def loadModel():
    global model
    model = getModel(width, height, lr)
    model.load(modelName)

def test(img):
    if not os.path.isfile("autoTrainingBadData.npy"):
        return
    screen = convImage(img)
    tf.reset_default_graph()
    modelOut = model.predict([screen.reshape(width, height, 1)])[0]
    #print(modelOut)
    modelList = modelOut.tolist()
    i = modelList.index(min(modelList))
    if i == 0:
        return "left"
    elif i == 1:
        return "right"
    elif i == 2:
        return "up"
    elif i == 3:
        return "down"
    else:
        return None
        
