import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image

# Display the selected mask in image cropped from original based on segmentation
def better_cropped_mask(anns, i, image):
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    # image = cv2.imread(InputFilePath)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    m = sorted_anns[i]['segmentation']
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            if m[x][y] == False:
                image[x][y][:] = 0
    return image 
    # plt.figure(figsize=(20,20))
    # plt.imshow(image)
    # plt.axis('off')
    # figureName = f'./segment/test' + f'{i}.png'
    # plt.savefig(figureName)

def cropped_objects(anns, i, image, segment_map):
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    m = sorted_anns[i]['segmentation']

    # check if the segment is already in the segment map
    segment_tmask = np.zeros((image.shape[0], image.shape[1], 4))
    segment_area = 0
    covered_area = 0
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            # in the segment area 
            if m[x][y] == True:
                segment_area += 1
                if segment_map[x][y] == 1:
                    covered_area += 1
    if covered_area/segment_area > 0.3:
        return False
    else:
        for x in range(image.shape[0]):
            for y in range(image.shape[1]):
                if m[x][y] == False:
                    segment_tmask[x][y][:3] = image[x][y][:]
                    segment_tmask[x][y][3] = 256
                    image[x][y][:] = 0
                else:
                    segment_tmask[x][y][3] = 0
                    segment_map[x][y] = 1
        return image, segment_tmask



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
def show_cropped_mask(anns, i, InputFilePath):
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    img = Image.open(InputFilePath)
    bbox = sorted_anns[i]['bbox']
    cropped_image = img.crop([bbox[0], bbox[1], bbox[0]+bbox[2], bbox[1]+bbox[3]])
    figureName = ''f'./test{i}.jpg'''
    cropped_image.save(figureName)

def remain_except_mask(anns, i, InputFilePath, InputFileName):
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    image = cv2.imread(InputFilePath)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    m = sorted_anns[i]['segmentation']
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            if m[x][y] == True:
                image[x][y][:] = 0
    plt.figure(figsize=(20,20))
    plt.imshow(image)
    plt.axis('off')
    figureName = f'./segment/' + InputFileName + f'{i}.jpg'
    plt.savefig(figureName)


def detect_overlap(bboxMemo, i, j):
    if j == i:
        return False
    if bboxMemo[i][0] > bboxMemo[j][0] + bboxMemo[j][2] or bboxMemo[j][0] > bboxMemo[i][0] + bboxMemo[i][2]:
        return False
    if bboxMemo[i][1] + bboxMemo[i][3] < bboxMemo[j][1] or bboxMemo[j][1] + bboxMemo[j][3] < bboxMemo[i][1]:
        return False
    return True

# Erase the current layer and all layers that overlap with it in the boundary
def crop_overlay(anns, boundary, i, inputImage):
    bboxMemo = []
    overlay = [False] * boundary
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    for j in range(boundary):
        bboxMemo.append(sorted_anns[j]['bbox'])
    for j in range(boundary):
        overlay[j] = detect_overlap(bboxMemo, i, j)
    
    image = cv2.imread(inputImage)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    m = sorted_anns[i]['segmentation']
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            if m[x][y] == True:
                image[x][y][:] = 0
    for j in range(len(overlay)):
        if overlay[j]:
            for x in range(image.shape[0]):
                for y in range(image.shape[1]):
                    if sorted_anns[j]['segmentation'][x][y] == True:
                        image[x][y][:] = 0
    plt.figure(figsize=(20,20))
    plt.imshow(image)
    plt.axis('off')
    figureName = f'./segment/' + 'test' + f'{i}.jpg'
    plt.savefig(figureName)
    # return image 


