import win32api as wapi

fileName = "training_data.npy"

if os.path.isfile(fileName):
    trainingData = list(np.load(fileName))
else:
    trainingData = []
def outputKeys(keyPress):
    #[Left,Right,Up,Down,None]
    output = [0,0,0,0,0]
    if keyPress == "Left":
        output[0] = 1
    elif keyPress == "Right":
        output[1] = 1
    elif keyPress == "Up":
        output[2] = 1
    elif keyPress == "Down":
        output[3] = 1
    else:
        output[4] = 1
        
    return output


        #Self learning AI
        #screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        #screen = cv2.resize(screen, (80,60))
        #output = outputKeys(keyPress)
        #trainingData.append([screen,output])
        #if len(trainingData) % 100 == 0:
        #    print("Saving to file")
        #    np.save(fileName, trainingData)
