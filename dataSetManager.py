import glob 
from cv2 import VideoCapture, imshow, waitKey, destroyAllWindows, imwrite
import pytesseract
import json
import os
from dataloader import DataManager


labelPath = r'labels.json'
imagePath = r'images'
 

def main():
    image = getImage() 
    showImage(image) 
    label = getUserInput()
    makeDataEntry(image, label)


    

def showImage(image):
    imshow("YEET2", image)
    waitKey()
    destroyAllWindows()
       
def getUserInput(): 
    return input("Please enter the label for this notecard: ")

def getImage(): 
    port = 0 
    #Set the camera
    camera = VideoCapture(port)
    
    #Capture a frame
    result, image = camera.read() 
    
    #Only return if we got an image 
    if result:
        return image

#Wrapper function
def makeDataEntry(image, trueValue): 
    photoId = savePhotoIdAndLabel(trueValue)
    saveImage(image, photoId)


def saveImage(image, imageID):
    #Check if the outter directory exists
    if not os.path.exists(imagePath):
        #it doesn't so lets make one 
        os.mkdir(imagePath)
    
    #Set the name 
    imageName = str(imageID)+".png"
    #Join its path to the directory we want
    path = os.path.join(imagePath, imageName)
    #Write it 
    check = imwrite(path, image)

    #Check if it worked
    if not check: 
        print("Image save failed")
    else: 
        print("Image succesfully saved at ", str(path))
     



#Manages all external file I/O for photo ids and the corresponding label
def savePhotoIdAndLabel(trueValue):
    #We need to maintain two files, one for the images, and one for the keys
        #Key stucture will be dict with {int image number (also used for name) : label}

    fileIndex = 0
    #Check if the file has been made
    if not os.path.exists(labelPath):

        #The file doesn't exist, so make one
        fp = open(labelPath, 'x')
        fp.close()

        #Now lets kick off our dictionary 
        labels = {fileIndex: trueValue}
        
        #Finally just dump that dictionary in 
        with open(labelPath, 'w') as f: 
            json.dump(labels, f)

    #Theres already a file so lets load it before we write to it 
    else: 

        data = {}
        with open(labelPath, "r") as f: 
            #Get our dictionary
            try:
                data = json.load(f)
            except Exception as e: 
                #Catch exceptions for is someone manually deleted every entry
                data = None; 

            #handle exception
            if data == None: 
                print("data is none")
                data = {} 
            #find what the next entry should be if not 0  
            else:
                fileIndex = getNextIndex(data)
            
            #Assign its true value and add it to the existing dict
            data[fileIndex] = trueValue

        with open(labelPath, "w") as f: 
            #open the file in write mode and dump the updated dict 
            json.dump(data, f)
    
    #Return the file index for future use
    return fileIndex

#Just goes through all keys and adds 1 to the max 
def getNextIndex(curDict): 
    localMax = 0 
    #print("heres the dict we loaded", curDict)
    for key in curDict.keys(): 
        if int(key) >= localMax:
            #print("Current index", int(key))
            localMax = int(key) 

    return localMax + 1
            

if __name__ == "__main__":
	main() 

