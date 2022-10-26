# By Henry Graves
# AI Art generation demo using Imgur API, Replicate StableDiffusion API

import os
import pyqrcode # pip install pyqrcode
import requests # pip install requests
import replicate # pip install replicate
import shutil
import webbrowser
from datetime import datetime
from decouple import config # pip install python-decouple
from imgur_python import Imgur # pip install imgur-python 
from PIL import Image # pip install pillow
from tkinter import *

# Environment variables
os.environ['REPLICATE_API_TOKEN'] = config('REPLICATE_API_TOKEN')
imgurClient = Imgur({
    "client_id": config('CLIENT_ID'),
    "client_secret": config('CLIENT_SECRET'),
    "access_token": config('ACCESS_TOKEN'),
    "expires_in": config('EXPIRES_IN'),
    "token_type": config('TOKEN_TYPE'),
    "refresh_token": config('REFRESH_TOKEN'),
    "account_username": config('ACCOUNT_USERNAME'),
    "account_id": config('ACCOUNT_ID')
})

# Encapsulation
class DataContainer:
    def __init__(self):
         self.__numPhotos = 0
         self.__albumID = None
         self.__QR = None

    def get_numPhotos(self):
        return self.__numPhotos

    def set_numPhotos(self, x):
        self.__numPhotos = x

    def get_albumID(self):
        return self.__albumID

    def set_albumID(self, x):
        self.__albumID = x

    def set_QR(self, x):
        self.__QR = x

    def get_QR(self):
        return self.__QR

def handleSubmit(dataContainer, numPhotosLabel):
    # TODO replace with webcam openCV string input & a submit button
    parsedPrompt = input("input your prompt: ")
    print(parsedPrompt)

     # generate image and get its link
    print("calling StableDiffusion through Replicate...")
    model = replicate.models.get("stability-ai/stable-diffusion")
    imageLink = model.predict(prompt=parsedPrompt)[0]
    if (imageLink):
        print(imageLink)
    else:
        print("error during image generation")

    # get image & save to currPhoto.png
    # Use a user-agent to get around replicate.com blocking bot access
    r = requests.get(imageLink, stream=True, headers={'User-agent': 'Mozilla/5.0'})
    if r.status_code == 200:
        # save image locally
        with open("currPhoto.png", 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

        # upload image to Imgur
        timestamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        numPhotos = dataContainer.get_numPhotos() + 1
        description = 'Photo %d: "%s"\nGenerated '%(numPhotos, parsedPrompt)  + timestamp
        response = imgurClient.image_upload('currPhoto.png', parsedPrompt, description, None, 0)
        print(response)
        # TODO Fault tolerance, maybe try again? See best practice for this
        alreadyFailed = False
        if (response['status'] != 200):
            alreadyFailed = True
            numPhotos -= 1

        # update album with new image
        if (not alreadyFailed):
            photoID = response['response']['data']['id']
            photoLink = response['response']['data']['link']
            response = imgurClient.album_add(dataContainer.get_albumID(), [photoID])
            print(response)
            # TODO Fault tolerance, maybe try again? See best practice for this
            if (response['status'] != 200):
                numPhotos -= 1

        # open new image in browser (better UX, see the whole album using the QR code)
        webbrowser.open(photoLink)
    else:
        print("error getting generated image")

    dataContainer.set_numPhotos(numPhotos)
    numPhotosLabel.config(text="Number of photos: %d"%(dataContainer.get_numPhotos()))

    # line break before next call
    print()

def handleNewStory(dataContainer, window):
    # destroy old widgets
    if (dataContainer.get_numPhotos() != 0 and window):
        for widget in window.winfo_children():
            widget.destroy()
            print('destroying')
    dataContainer.set_numPhotos(0)
    dataContainer.set_albumID(None)

    # create a new album AT START OF NEW PROMPT STORY
    images = []
    title = 'AI Art'
    description = 'The start of a new prompt story...'
    privacy = 'secret'
    response = imgurClient.album_create(images, title, description, privacy)
    dataContainer.set_albumID(response['response']['data']['id'])
    print(response)
    print("albumID is " + response['response']['data']['id'] + "\n")

    # append albumID links to a txt file for our record keeping
    albumIDRecord = open("albumIDRecord.txt", "a")
    albumIDRecord.write("https://imgur.com/a/" + response['response']['data']['id'] + "\n")
    albumIDRecord.close()

    # create QR code for the album
    qrCode = pyqrcode.create('https://imgur.com/a/' + dataContainer.get_albumID())
    print(qrCode)
    qrCode.png('qrCode.png', scale=20)
    dataContainer.set_QR(PhotoImage(file='qrCode.png'))

    # Display header, numPhotos, and QR code
    Label(window, text="Track the evolution of this prompt story!", font=("Arial", 30)).pack()
    numPhotosLabel = Label(window, text="Number of photos: %d"%(dataContainer.get_numPhotos()), font=("Arial", 12))
    numPhotosLabel.pack()
    Label(window, image=dataContainer.get_QR(), compound='center', anchor="n").pack()

    # Display buttons
    newStoryButton = Button(window, text="New Story", font=("Arial", 24), width=15, padx=20, pady=5, bd=1, fg="white",
                            bg="#55acee", activeforeground="white", activebackground="green", command=lambda: handleNewStory(dataContainer, window))
    submitButton = Button(window, text="Submit Prompt", font=("Arial", 24), width=15, padx=20, pady=5, bd=1, fg="white",
                        bg="#55acee", activeforeground="white", activebackground="green", command=lambda: handleSubmit(dataContainer, numPhotosLabel))
    newStoryButton.pack(side="left", expand=1, anchor="e", padx=10)
    submitButton.pack(side="left", expand=1, anchor="w", padx=10)

# TODO further fault tolerance: while loop so that users can't break the exhibit by closing Tkinter window
# Keyboard interrupt program at CLI then close tkinter to fully exit
while (True):
    # Initialize Tkinter window & encapsulated data
    window = Tk()
    dataContainer = DataContainer()
    handleNewStory(dataContainer, window)

    # start UI event loop.
    # Runs until user closes Tkinter window (returns control to while loop, doesn't break program) OR admin kills program.
    window.mainloop()
