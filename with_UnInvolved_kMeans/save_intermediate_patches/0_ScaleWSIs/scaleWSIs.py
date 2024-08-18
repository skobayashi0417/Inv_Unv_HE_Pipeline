import os
import PIL
from PIL import Image
import csv
import math
import openslide
import io
import pyvips
import numpy as np

def save_img(img, saveName, saveDir):

    dtype_to_format = {
      'uint8': 'uchar',
      'int8': 'char',
      'uint16': 'ushort',
      'int16': 'short',
      'uint32': 'uint',
      'int32': 'int',
      'float32': 'float',
      'float64': 'double',
      'complex64': 'complex',
      'complex128': 'dpcomplex',
    }
    
    img_path = os.path.join(saveDir,saveName)
    npimg = np.asarray(img)
    height, width, bands = npimg.shape
    linear = npimg.reshape(width * height * bands)
    vimg = pyvips.Image.new_from_memory(linear.data, width, height, bands, dtype_to_format[str(npimg.dtype)])
    vimg.tiffsave(img_path,compression='lzw',tile=True,tile_width=448,tile_height=448,pyramid=True,bigtiff=True)

def return_scaled_PIL(cropped_WSI,SCALE_FACTOR,cropped_width,cropped_height):
    cWidth, cHeight = cropped_WSI.size

    assert cWidth == cropped_width
    assert cHeight == cropped_height
    
    assert cWidth % SCALE_FACTOR == 0
    assert cHeight % SCALE_FACTOR == 0
    
    scaled_w = int(math.floor(cWidth/SCALE_FACTOR))
    scaled_h = int(math.floor(cHeight/SCALE_FACTOR))

    scaled_WSI = cropped_WSI.resize((scaled_w, scaled_h), PIL.Image.BILINEAR)
    
    return scaled_WSI, scaled_w, scaled_h, cWidth, cHeight
    

def return_cropped_PIL(orig_WSI, INPUT_WSI_DIR, SCALE_FACTOR, PATCH_SIZE):
    oWSI = openslide.open_slide(os.path.join(INPUT_WSI_DIR,orig_WSI))
    
    orig_w, orig_h = oWSI.dimensions
    expectedScale = SCALE_FACTOR * PATCH_SIZE
    
    new_w = int((math.floor(orig_w / expectedScale)) * expectedScale)
    new_h = int((math.floor(orig_h / expectedScale)) * expectedScale)
    
    wDiff = int(orig_w - new_w)
    hDiff = int(orig_h - new_h)
    
    xStart = int(wDiff/2)
    yStart = int(hDiff/2)
    
    #cropped_whole_slide_image = oWSI.read_region(location=(xStart, yStart), level=0, size = (new_w,new_h))
    #level = oWSI.get_best_level_for_downsample(SCALE_FACTOR)
    
    # for some reason, these images scanned with a weird black border... crop an extra patch worth (8*224)
    
    cropped_whole_slide_image = oWSI.read_region((xStart, yStart), 0, size = (new_w,new_h))
    cropped_img = cropped_whole_slide_image.convert("RGB")
    
    return cropped_img, new_w, new_h, orig_w, orig_h,
    
def scale_WSI(INPUT_WSI_DIR,SCALED_WSI_DIR, BASE_DIR, PATCH_SIZE = 224, WSI_EXTENSION='.tif',SCALE_FACTOR=8, SAVE_CROPPED_WSI=True):
    global appendList
    
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)
    
    if SAVE_CROPPED_WSI == True:
        CROPPED_DEST_DIR = os.path.join(BASE_DIR,'croppedWSIs')
        if not os.path.exists(CROPPED_DEST_DIR):
            os.mkdir(CROPPED_DEST_DIR)
    
    appendList = []
    appendDict = {}
    
    cropTracker = []
    
    orig_WSIs = [w for w in os.listdir(INPUT_WSI_DIR) if str(w).endswith(WSI_EXTENSION)]
    
    orig_WSIs = [a for a in orig_WSIs if a =='14big.tif' or a=='322big.tif']
    print(orig_WSIs)
    
    tot_num = len(orig_WSIs)
    counter = 1
    
    for orig_WSI in orig_WSIs:
        
        print('Performing Cropping on %s.. ------ %d out of %d total samples.' % (orig_WSI,counter,tot_num))
        cropped_img, new_w, new_h, orig_w, orig_h = return_cropped_PIL(orig_WSI = orig_WSI, INPUT_WSI_DIR=INPUT_WSI_DIR, SCALE_FACTOR = SCALE_FACTOR, PATCH_SIZE = PATCH_SIZE)
        
        lostPixels = (orig_w*orig_h) - (new_w*new_h)
        cropTracker.append([orig_WSI,orig_w,orig_h,new_w,new_h,lostPixels])
        
        if SAVE_CROPPED_WSI == True:
            saveName = str(orig_WSI)[:-len(WSI_EXTENSION)] + '_cropped' + WSI_EXTENSION
            save_img(img = cropped_img, saveName = saveName, saveDir = CROPPED_DEST_DIR)
            
        
        print('Performing Scaling on %s.. ------ %d out of %d total samples.' % (orig_WSI,counter,tot_num))
        scaled_img, scaled_w, scaled_h, cropped_w, cropped_h = return_scaled_PIL(cropped_WSI = cropped_img, SCALE_FACTOR=SCALE_FACTOR, cropped_width=new_w, cropped_height=new_h)
        
        scaledSaveName = str(orig_WSI)[:-len(WSI_EXTENSION)] + '_cropped_scaledFactor' + str(SCALE_FACTOR) + WSI_EXTENSION
        
        scaled_img.save(os.path.join(SCALED_WSI_DIR,scaledSaveName))
        #save_img(img = scaled_img, saveName = scaledSaveName, saveDir = SCALED_WSI_DIR)
        
        counter += 1
        
    
    with open(os.path.join(CROPPED_DEST_DIR,'cropSummary.csv'),'w') as csvfile:
        fieldnames = ['WSI_ID','originalW',
                    'originalH','newW',
                    'newH','LostPixels']
        testwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        testwriter.writeheader()
        for i in range(len(cropTracker)):
            toAppend = cropTracker[i]
            appendDict['WSI_ID']=toAppend[0]
            appendDict['originalW']=toAppend[1]
            appendDict['originalH']=toAppend[2]
            appendDict['newW']=toAppend[3]
            appendDict['newH']=toAppend[4]
            appendDict['LostPixels']=toAppend[5]
            testwriter.writerow(appendDict)

