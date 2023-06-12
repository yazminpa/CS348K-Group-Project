import cv2
import numpy as np
from PIL import Image
from typing import Any, Dict, List
import io
import base64
import openai
import requests

def load_img_to_array(img_p):
    img = Image.open(img_p)
    if img.mode == "RGBA":
        img = img.convert("RGB")
    return np.array(img)

def load_base64_to_array(img_base64):
    img = Image.open(io.BytesIO(base64.b64decode(img_base64)))
    if img.mode == "RGBA":
        img = img.convert("RGB")
    return np.array(img)

def load_array_to_base64(img_np):
    img = Image.fromarray(img_np)
    rawBytes = io.BytesIO()
    img.save(rawBytes, "PNG")
    rawBytes.seek(0)
    img_base64 = base64.b64encode(rawBytes.read())
    return img_base64

def edit_dalle(img_path = "./uploads/Dog.png", mask_path = "./segmented_images/segment3_tmask.png", prompt = "a golden retriever on the sofa"):
    openai.api_key = ""
    response = openai.Image.create_edit(
    image= open(img_path, "rb"),
    mask= open(mask_path, "rb"),
    prompt= prompt,
    n=1,
    size="256x256"
    )
    image_url = response['data'][0]['url']
    
    print(image_url)

    response = requests.get(image_url)
    response.raise_for_status()

    with open("image.jpg", "wb") as file:
        file.write(response.content)

    print("Image downloaded successfully.")

    return "dalle edit is done"
