# By Henry Graves
# AI Art generation demo using Imgur API, Replicate StableDiffusion API

import os
import pyqrcode # pip install pyqrcode
# import png # pip install pypng
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

# create a new album AT START OF NEW PROMPT STORY
images = []
title = 'AI Art'
description = 'The start of a new prompt story...'
privacy = 'secret'
response = imgurClient.album_create(images, title, description, privacy)
albumID = response['response']['data']['id']
print(response)
print("albumID is " + response['response']['data']['id'] + "\n")

# create QR code for the album
qrCode = pyqrcode.create('https://imgur.com/a/' + albumID)
qrCode.png('qrCode.png', scale=20)

# display QR code in tkinter UI
window = Tk()
img = PhotoImage(file='qrCode.png')
Label(window, text="Track the evolution of this prompt story!", font=("Arial", 30)).pack()
Label(window, image=img, compound='center').pack()
# window.mainloop() # TODO use mainloop with buttons [submit prompt](add to album) and [new story](make new album) for control loop.

numPhotos = 0
while (True):
    # TODO replace with webcam openCV string input & a submit button
    parsedPrompt = input("input your prompt: ")
    print(parsedPrompt)

    print("calling StableDiffusion through Replicate...")
    model = replicate.models.get("stability-ai/stable-diffusion") # generate image
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
        numPhotos += 1
        description = 'Photo number %d: "%s"\nGenerated '%(numPhotos, parsedPrompt)  + timestamp
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
            response = imgurClient.album_add(albumID, [photoID])
            print(response)
            # TODO Fault tolerance, maybe try again? See best practice for this
            if (response['status'] != 200):
                numPhotos -= 1

        # open new image in browser (better UX, see the whole album using the QR code)
        webbrowser.open(photoLink)
    else:
        print("error getting generated image")

    # line break before next call
    print()