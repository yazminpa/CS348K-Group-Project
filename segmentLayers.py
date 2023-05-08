import numpy as np
# import torch
import matplotlib.pyplot as plt
import cv2
from PIL import Image

InputFileName = 'TestShape.jpg'
InputFilePath = '/home/alisaazxh/' + InputFileName
ModelCheckpointPath = "/home/alisaazxh/segment/sam_vit_h_4b8939.pth"
# Display all masks in the image
def show_anns(anns):
    if len(anns) == 0:
        return
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    ax = plt.gca()
    ax.set_autoscale_on(False)

    img = np.ones((sorted_anns[0]['segmentation'].shape[0], sorted_anns[0]['segmentation'].shape[1], 4))
    img[:,:,3] = 0
    for ann in sorted_anns:
        m = ann['segmentation']
        color_mask = np.concatenate([np.random.random(3), [0.35]])
        img[m] = color_mask
    ax.imshow(img)

# Display the selected mask in the image
def show_selected_anns(anns, i):
    if len(anns) == 0:
        return
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    ax = plt.gca()
    ax.set_autoscale_on(False)

    img = np.ones((sorted_anns[0]['segmentation'].shape[0], sorted_anns[0]['segmentation'].shape[1], 4))
    img[:,:,3] = 0   
    m = sorted_anns[i]['segmentation']
    color_mask = np.concatenate([np.random.random(3), [0.35]])
    img[m] = color_mask
    ax.imshow(img)

# Display the selected mask without image
def show_selected_mask(anns, i):
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    img = np.ones((sorted_anns[0]['segmentation'].shape[0], sorted_anns[0]['segmentation'].shape[1], 4))
    img[:,:,3] = 0
    m = sorted_anns[i]['segmentation']
    color_mask = np.concatenate([np.random.random(3), [0.35]])
    img[m] = color_mask
    print(sorted_anns[i]['bbox'])
    print(sorted_anns[i]['crop_box'])
    plt.figure(figsize=(20,20))
    plt.imshow(img)
    plt.axis('off')
    plt.savefig('/home/alisaazxh/segment/testMask.jpg')

# Display the selected mask in image cropped from original
def show_cropped_mask(anns, i):
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    img = Image.open(InputFilePath)
    bbox = sorted_anns[i]['bbox']
    cropped_image = img.crop([bbox[0], bbox[1], bbox[0]+bbox[2], bbox[1]+bbox[3]])
    figureName = ''f'/home/alisaazxh/segment/test{i}.jpg'''
    cropped_image.save(figureName)

# Display the selected mask in image cropped from original based on segmentation
def better_cropped_mask(anns, i):
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    image = cv2.imread(InputFilePath)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    m = sorted_anns[i]['segmentation']
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            if m[x][y] == False:
                image[x][y][:] = 0
    plt.figure(figsize=(20,20))
    plt.imshow(image)
    plt.axis('off')
    figureName = f'/home/alisaazxh/segment/' + InputFileName + f'{i}.jpg'
    plt.savefig(figureName)
    

image = cv2.imread(InputFilePath)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

plt.figure(figsize=(20,20))
plt.imshow(image)
plt.axis('off')
plt.savefig('/home/alisaazxh/segment/test.jpg')

import sys
sys.path.append("..")
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor

sam_checkpoint = ModelCheckpointPath
model_type = "vit_h"
device = "cuda"

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)

mask_generator = SamAutomaticMaskGenerator(sam)
masks = mask_generator.generate(image)
print(len(masks))
print(masks[0].keys())

# Display all masks in the image
# show_anns(masks)
# figureName = f'/home/alisaazxh/segment/testAllMasks.jpg'
# plt.savefig(figureName)

# for i in range(len(masks)):
#     plt.figure(figsize=(20,20))
#     plt.imshow(image)
#     plt.axis('off')
#     show_cropped_mask(masks,i)
#     figureName = f'/home/alisaazxh/segment/test{i}.jpg'
#     plt.savefig(figureName)

boundary = len(masks) if len(masks) < 15 else 15
for i in range(boundary):
    better_cropped_mask(masks, i)

