import cv2
import numpy as np
from skimage.transform import rotate 
from deskew import determine_skew

class ProcessData: 

	def __init__(self, showChanges = False): 
		#shouldn't need to do anything 
		self.showChanges = showChanges

	def preProcessImage(self, image): 
		print("Image type",  image)
		#image = self.removeNoise(image)
		#image = cv2.medianBlur(image, 5)
		#image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 33, 3)
		
		#image = self.threshHoldImage(image)
		self.showImage(image)
		image = self.removeEverythingThatsNotText(image)
		#image = self.threshHoldImage(image)
		image = self.deskewImage(image)
		#image = self.resizeImage(image)
		#image = self.threshHoldImage(image)
		#image = self.removeNoise(image)
		self.showImage(image)
		#image = self.ensureGrayScale(image)
		
		#image = cv2.medianBlur(image, 5)
		#image = cv2.medianBlur(image, 5)
		#image = self.smooth(image)
		#image = cv2.medianBlur(image, 5)
		#image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 33, 3)
		#image = self.fillContoursWithPoly(image, self.findContours(image))
		if (self.showChanges): 
			self.showImage(image)
		return image
	
	#This one is much shittier as of now, but we will see after more standardized photos 
	def deskewImage2(self, image): 
		angle = self.getSkewAngle(image)
		return self.rotateImage(image, -1.0*angle)

	def getSkewAngle(self, image) -> float: 
		copy = image.copy()
		blur = cv2.GaussianBlur(copy, (9, 9), 0)
		thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
		dilate = cv2.dilate(thresh, kernel, iterations = 5)

		contours, heir = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
		contours = sorted(contours, key = cv2.contourArea, reverse = True)

		largestContour = contours[0]
		minAreaRect = cv2.minAreaRect(largestContour)

		#Now that we have a rectangle around our largest character, lets figure out what to turn that by 
		angle = minAreaRect[-1]
		if angle < -45: 
			angle = 90 + angle
		return -1.0 * angle

	def rotateImage(self, cvImage, angle: float):
		newImage = cvImage.copy()
		(h, w) = newImage.shape[:2]
		center = (w // 2, h // 2)
		M = cv2.getRotationMatrix2D(center, angle, 1.0)
		newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
		return newImage

	#Uses skimage and deskew
	def deskewImage(self, image): 
		angle = determine_skew(image)
		image = rotate(image, angle, resize=True) * 255
		return image.astype(np.uint8)

	def removeEverythingThatsNotText(self, image): 
		mask = np.ones(image.shape, dtype = np.uint8)
		thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
		#thresh = self.removeNoise(image)
		kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
		dilate = cv2.dilate(thresh, kernel, iterations = 3)

		contours = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		contours = contours[0] if len(contours) == 2 else contours[1]
		for curCon in contours:
			area = cv2.contourArea(curCon)
			if area < 7000: 
				x,y,w,h = cv2.boundingRect(curCon)
				mask[y:y+h, x:x+w] = thresh[y:y+h, x:x+w]
		#self.showImage(thresh)
		#self.showImage(mask)
		return mask

	def findContours(self, image): 
		image = cv2.blur(image, (3, 3)) # blur the image
		#ret, thresh = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY)
		#image = cv2.Canny(image, 30, 200)
		image, contours = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		return np.array(contours).reshape((-1,1,2)).astype(np.int32)

	def fillContoursWithPoly(self, image, contours): 
		#print(contours)
		image = cv2.drawContours(image, [contours], -1, (255, 0, 0), thickness=cv2.FILLED)
		return image

	def smooth(self, image, threshold = 180): 
		ret1, th1 = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
		ret2, th2 = cv2.threshold(th1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
		blur = cv2.GaussianBlur(th2, (1, 1), 0)
		ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
		return th3	

	def removeNoise(self, image): 
		filtered = cv2.adaptiveThreshold(image.astype(np.uint8), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 41, 3)
		kernel = np.ones((1, 1), np.uint8)
		opening = cv2.morphologyEx(filtered, cv2.MORPH_OPEN, kernel)
		closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
		image = self.smooth(image)
		image = cv2.bitwise_or(image, closing)
		image = cv2.medianBlur(image, 5)
		return image

	def threshHoldImage(self, image): 
		image = cv2.medianBlur(image, 5)	
		image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 13, 3)
		image = cv2.medianBlur(image, 3)
		image = cv2.bitwise_not(image)
		return image

	def ensureGrayScale(self, image): 
		return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 

	def resizeImage(self, image):
		h, w = image.shape
		h *= 3
		w *= 3 
		resized = cv2.resize(image, (w, h), interpolation = cv2.INTER_AREA)
		return resized

	def showImage(self, image):
		cv2.imshow("YEET2", image)
		cv2.waitKey()
		cv2.destroyAllWindows()


