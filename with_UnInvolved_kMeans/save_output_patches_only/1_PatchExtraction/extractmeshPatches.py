import os
import numpy
import PIL
import csv
import openslide
import shutil
from PIL import Image

def extractPatches(im, possibleCoords, PATCH_SIZE, mouseDir, WSI, WSI_EXTENSION):
    sampleID = str(mouseDir).split('/')[-1]
    
    for possibleCoord in possibleCoords:
        newTile = im.read_region((possibleCoord[0],possibleCoord[1]), 0, (PATCH_SIZE,PATCH_SIZE)).convert("RGB")

        savePath = os.path.join(mouseDir,str(WSI)[:-(len(WSI_EXTENSION))] + '_%dX_%dY_w%d_h%d.png' % (int(possibleCoord[0]), int(possibleCoord[1]),int(PATCH_SIZE),int(PATCH_SIZE)))
        
        newTile.save(savePath)
        
        newTile.close()
            
def meshpatchExtraction(config):
    Image.MAX_IMAGE_PIXELS = None
    
    BASE_DIR = config['directories']['BASE_DIR']
    PATCH_SIZE = config['PatchInfo']['meshPATCH_SIZE']
    WSI_EXTENSION = config['SlideInfo']['WSI_EXTENSION']
    SCALED_WSI_DIR = config['directories']['SCALED_WSI_DIR']
    
    WSIs = [a for a in os.listdir(SCALED_WSI_DIR) if str(a).endswith(WSI_EXTENSION)]
    tot_num = len(WSIs)
    
    PATCH_DEST_DIR = os.path.join(BASE_DIR,'extractedPatches')
    if not os.path.exists(PATCH_DEST_DIR):
        os.mkdir(PATCH_DEST_DIR)
    
    byMouseMeshDir = os.path.join(PATCH_DEST_DIR,'byMouse_Mesh')
    if not os.path.exists(byMouseMeshDir):
        os.mkdir(byMouseMeshDir)
    
    config['directories']['byMouseMeshPatches'] = byMouseMeshDir
    
    counter = 1
    for WSI in WSIs:
        print('Extracting patches from sample  %s.. ------ %d out of %d total samples.' % (WSI,counter,tot_num))
        
        mouseDir = os.path.join(byMouseMeshDir,str(WSI)[:-(len(WSI_EXTENSION))])
        if not os.path.exists(mouseDir):
            os.mkdir(mouseDir)
        
        im = openslide.open_slide(os.path.join(SCALED_WSI_DIR,WSI))
        orig_width, orig_height = im.dimensions
        
        possibleXs = list(range(0,orig_width,PATCH_SIZE))
        possibleYs = list(range(0,orig_height,PATCH_SIZE))
        
        possibleCoords = []
        for i in possibleXs:
            possibleCoords += list(tuple(zip([i]*len(possibleYs),possibleYs)))
        
        extractPatches(im=im, possibleCoords=possibleCoords, PATCH_SIZE = PATCH_SIZE, mouseDir=mouseDir, WSI = WSI, WSI_EXTENSION = WSI_EXTENSION)
        
        counter += 1
    
    counter = 1
    
    return config
    
if __name__=='__main__':
    main()
