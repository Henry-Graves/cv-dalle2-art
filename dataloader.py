import os, json
from cv2 import imread, imshow, waitKey, destroyAllWindows


labelPath = r'labels.json'
imagePath = r'images'

class DataManager: 



	def __init__(self): 
		#Lets pre-emptively load our data 
		self.labelsDict = self.loadLabels()
		self.imageList = self.loadImages() 

	"""
	This function takes our two seperate data types and returns our favored types

	parameters: 
		labelsDict: A dictionary of where key = photoId, value = labelPath
		imageList: A list of all our images named according to photoID
		

	returns: 
		A dicto
	"""

	def getLabelsDict():
		return self.labelsDict

	def getListOfImages(self):
		return self.imageList

	def mergeDataTypes(labelsDict, imageList):
		...
		
	def loadLabels(self): 
		with open(labelPath, "r") as f: 
			try: 
				labels = json.load(f)
				return labels
			except Exception as e: 
				print("Error loading data, make sure it exists and is not empty: ", e)
	
	def loadImages(self): 
		listOfImages = []
		for fileName in os.listdir(imagePath): 
			
			if not fileName.startswith("."):
				#f = str(fileName)
				print("looking at ", fileName)
				path = os.path.join(imagePath, fileName)
				img = imread(path)
				self.showImage(img)
				listOfImages.append(img)

		return listOfImages


	def showImage(self, image):
		imshow("YEET2", image)
		waitKey()
		destroyAllWindows()