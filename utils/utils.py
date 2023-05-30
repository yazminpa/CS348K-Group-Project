import cv2
import numpy as np
from PIL import Image
from typing import Any, Dict, List
import io
import base64

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