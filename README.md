**Project Overview:**

The project is an installation for modern art / tech museums to showcase AI-generated art, introduce people to AI concepts, present AI/AI-generated art in a positive manner and prompt viewing it as a creative tool.

**The setup:**

A webcam is mounted above a pen & stack of sticky notes, looking straight down onto it. A computer screen is visible to users.

**Project MVP:**

User writes the prompt they want to see on the sticky note → user presses a button or does some action → webcam takes a photo of the paper → processed by Python script into a text string → string input to Dall-e-2 (compute done on OpenAI server) → dall-e-2 generated image shown on computer screen → the next user can add to the prompt the last user wrote, or can pull the sticky note off and start a new prompt.

**Tech Required:**

OpenCV computer vision using Python, handwritten text dataset (IAM Handwriting)), Dall-e-2 API access (already acquired), webcam, computer for local hosting & processing & displaying the generated image. 

**We have plans for implementing extra complexity if needed:**

- 3d printing or otherwise creating a structure to hold the webcam and sticky note stack, as would be included if the project were actually presented in a museum.
- using gesture recognition to allow users to submit through a thumbs up instead of pressing a button.
- using computer vision to keep track of the words on the sticky note then automatically submit that prompt once the sticky note is pulled off the stack.
- having a QR code attached to the installation for users to scan and see the evolution of the prompt they were a part of.

We think that this process of adding onto each other's prompts, what we're calling "collaborative storytelling", can make some really compelling art and would be a fun way to teach people more about generative AI. Here's an example of images generated using this process:

![image](https://user-images.githubusercontent.com/73561858/197267835-eac878bc-b301-46d0-a68a-af900d599851.png)
