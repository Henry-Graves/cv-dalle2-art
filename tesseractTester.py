from dataloader import DataManager
from cv2 import imshow
import pytesseract 
from dataProcessor import ProcessData

tess_path = r'C:\Program Files\Tesseract-OCR\tesseract'

def main():
	#Load our data dataLoader 
	dataLoader = DataManager() 
	imageList = dataLoader.getListOfImages() 

	predictions = getPhotoPredictions(imageList)

	labelsDict = dataLoader.getLabelsDict()

	results = comparePredictionsToActualResults(predictions, labelsDict)

	print("We had ", results, "% accuracy")


def getPhotoPredictions(photosList): 
	predictions = {}
	pytesseract.pytesseract.tesseract_cmd = tess_path

	pd = ProcessData(True)

	for key in photosList.keys(): 	
		image = pd.preProcessImage(photosList[key])
		textFromImage = pytesseract.image_to_string(image)
		predictions[key] = textFromImage

	return predictions 



def comparePredictionsToActualResults(predictions, labelsDict):
	numCorrect = 0
	for key in labelsDict.keys(): 
		print("For photo", key, "we guessed ", predictions[key], "the actual label is ", labelsDict[key])

		if (predictions[key] == labelsDict[key]): 
			numCorrect += 1

	return numCorrect / len(predictions)
	
if __name__ == "__main__":
	main() 