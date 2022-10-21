# By Henry Graves, Pierce Powell, Zachary Dawson
# Connect to StableDiffusion API: POST a text string (that we'll get from webcam computer vision), GET the resulting image (async await?)
# eventually connect to Dall-e-2 API

# TODO hide environment variables before deploying
import os
os.environ['REPLICATE_API_TOKEN'] = '' # enter API key here
os.environ.setdefault('USER_2', 'True')

# TODO clean imports once project done
import requests, urllib.request
import replicate
from PIL import ImageTk, Image
import tkinter as tk
from io import BytesIO
import shutil

while (True):
    parsedPrompt = input("input your prompt: ")
    print(parsedPrompt)
    # parsedPrompt = "Minecraft herobrine attacking you"
    print("calling StableDiffusion through Replicate...")
    # Call StableDiffusion API through Replicate, get generated image link
    model = replicate.models.get("stability-ai/stable-diffusion")
    imageLink = model.predict(prompt=parsedPrompt)[0] # returns a list, so get link through 1st element
    print(imageLink)

    # gets image, saves to output.png, opens
    # TODO this is a workaround from replicate.com blocking bot access to resources, check if this is a stable solution.
    r = requests.get(imageLink, stream=True, headers={'User-agent': 'Mozilla/5.0'})
    if r.status_code == 200:
        with open("output.png", 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
        img = Image.open("output.png")
        img.show()

    # line break before next call
    print()

    # Image opening idea graveyard, might use later if the workaround above gets blocked.
    # # open image, not working yet, TKINTER?
    # img = Image.open(requests.get(imageLink, stream=True).raw)
    # def show_imge(path):
    #     image_window = tk.Tk()
    #     img = ImageTk.PhotoImage(Image.open(path))
    #     panel = tk.Label(image_window, image=img)
    #     panel.pack(side="bottom", fill="both", expand="yes")
    #     image_window.mainloop()
    # show_imge(img)
    # # gives a 403 forbidden bc Replicate doesn't like?? It works with other image links
    # urllib.request.urlretrieve(imageLink, "ouput.png")
    # img = Image.open("output.png") # may need to await image write first
    # img.show()