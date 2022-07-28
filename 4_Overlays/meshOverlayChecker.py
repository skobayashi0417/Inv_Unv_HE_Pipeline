import os
import PIL
from PIL import Image, ImageDraw, ImageOps
import shutil
import pandas as pd


def return_Xcoord(fn):
    Xcoord = str(fn).split('_')[-4][:-1]
    
    return Xcoord

def return_Ycoord(fn):
    Ycoord = str(fn).split('_')[-3][:-1]
    
    return Ycoord

def meshOverlayCheck(config):
    BASE_DIR = config['directories']['BASE_DIR']
    SCALED_WSI_DIR = config['directories']['SCALED_WSI_DIR']
    #PREDICTIONS_DIR = config['directories']['PREDICTIONS_DIR']
    PATCH_SIZE = config['PatchInfo']['PATCH_SIZE']
    BYMOUSE_DIR = config['directories']['byMousePatches']
    WSI_EXTENSION = config['SlideInfo']['WSI_EXTENSION']
    
    DEST_DIR = os.path.join(BASE_DIR, 'PatchExtraction_MeshFilter_Overlays')
    if not os.path.exists(DEST_DIR):
        os.mkdir(DEST_DIR)
        
    counter = 1
    
    WSIs = [a for a in os.listdir(SCALED_WSI_DIR) if str(a).endswith(WSI_EXTENSION)]
    tot_num = len(WSIs)
    
    for WSI in WSIs:
        print('Generating Patch Extraction Check Overlays for Sample %s.. ------ %d out of %d total samples.' % (WSI,counter,tot_num))
        
        sample = str(WSI)[:-(len(WSI_EXTENSION))]
        
        fileName = sample + '.tif'
                
        base = Image.open(os.path.join(SCALED_WSI_DIR,fileName))
        
        patches = [a for a in os.listdir(os.path.join(BYMOUSE_DIR,sample)) if str(a).endswith('png')]
        
        for patch in patches:
            XCoord = int(str(patch).split('_')[-4][:-1])
            YCoord = int(str(patch).split('_')[-3][:-1])
            
            image=Image.new('RGB',(PATCH_SIZE, PATCH_SIZE), color = (0, 255, 0))
            image.putalpha(100)
            base.paste(im=image,box=(XCoord,YCoord),mask=image)
        
        saveName = 'Overlayed_' + str(sample) + '.tif'
        base.save(os.path.join(DEST_DIR,saveName))
