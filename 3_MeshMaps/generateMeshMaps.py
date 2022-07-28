import os
import PIL
from PIL import Image, ImageDraw, ImageOps
import shutil
import pandas as pd
import numpy as np

WSI_DIR = '/data06/shared/skobayashi/python-wsi-preprocessing_outputs/python-wsi-preprocessing_downsampledTIF/training_downsampled_VIPS_tif_scalefactor_2_Cropped_VIPS_scaledby4_to_sf8/training_downsampled_tif_scalefactor_8'

def rgb(value,classification,minimum=0, maximum=1):
    minimum, maximum = float(minimum), float(maximum)
    halfway = (minimum+maximum)/2
    if classification == 'bg':
        if value >= halfway:
            g = 1 + int(180 - (value-halfway)*(180/halfway))
            r = 1 + int(180 - (value-halfway)*(180/halfway))
            b = 1 + int(180 - (value-halfway)*(180/halfway))
        elif value < halfway:
            r = 0
            g = 0
            b = 0
        #r = 10
        #g = 10
        #b = 10
    elif classification == 'muscle':
        if value >= halfway:
            r = 255
            g = int(180 - (value-halfway)*(180/halfway))
            b = int(180 - (value-halfway)*(180/halfway))
        elif value < halfway:
            r = 0
            g = 0
            b = 0
    elif classification == 'tissue':
        if value >= halfway:
            b = 255
            g = int(180 - (value-halfway)*(180/halfway))
            r = int(180 - (value-halfway)*(180/halfway))
        elif value < halfway:
            r = 0
            g = 0
            b = 0
    elif classification == 'submucosa':
        if value >= halfway:
            g = 255
            b = int(180 - (value-halfway)*(180/halfway))
            r = int(180 - (value-halfway)*(180/halfway))
        elif value < halfway:
            r = 0
            g = 0
            b = 0
    return r, g, baa

def return_Xcoord(fn):
    Xcoord = str(fn).split('_')[-4][:-1]
    
    return Xcoord

def return_Ycoord(fn):
    Ycoord = str(fn).split('_')[-3][:-1]
    
    return Ycoord

def createMeshMaps(config):
    BASE_DIR = config['directories']['BASE_DIR']
    WSI_DIR = config['directories']['SCALED_WSI_DIR']
    MESH_PREDICTIONS_DIR = config['directories']['meshPREDICTIONS_DIR']
    PATCH_SIZE = config['PatchInfo']['meshPATCH_SIZE']
    
    DEST_DIR = os.path.join(BASE_DIR, 'meshMaps')
    if not os.path.exists(DEST_DIR):
        os.mkdir(DEST_DIR)
    
    config['directories']['MESH_MAPS_DIR'] = DEST_DIR
    
    samples = [a for a in os.listdir(MESH_PREDICTIONS_DIR)]
    
    for sample in samples:
        
        if not sample.startswith('.'):
            sample_dest_dir = os.path.join(DEST_DIR,sample)
        if not os.path.exists(sample_dest_dir):
            os.mkdir(sample_dest_dir)
                    
        pred_df = pd.read_csv(os.path.join(os.path.join(MESH_PREDICTIONS_DIR,sample),'adjustlabel_predicts.csv'), header=None)
                
        #print(pred_df)
                
        pred_df = pred_df.drop(pred_df.columns[0:4],axis=1)
                
        pred_df.columns=['conf','pred','fn']
                
        pred_df['XCoord'] = pred_df['fn'].map(return_Xcoord)
        pred_df['YCoord'] = pred_df['fn'].map(return_Ycoord)
                
        fileName = sample + '.tif'
                
        base = Image.open(os.path.join(WSI_DIR,fileName))
                
        im_width, im_height = base.size
        base.close()

        meshMap_check = np.zeros((im_height,im_width), dtype=int)
                
        for index, row in pred_df.iterrows():
            topLeftX = int(row['XCoord'])
            topLeftY = int(row['YCoord'])
                    
            conf = float(row['conf'])
            prediction = str(row['pred'])
                    
            if conf < 0.5:
                next
                    
            else:
                if prediction=='1':
                    for i in range(topLeftX,topLeftX+PATCH_SIZE):
                        for u in range(topLeftY,topLeftY+PATCH_SIZE):
                            meshMap_check[u,i] = 0
                elif prediction=='2':
                    for i in range(topLeftX,topLeftX+PATCH_SIZE):
                        for u in range(topLeftY,topLeftY+PATCH_SIZE):
                            meshMap_check[u,i] = 0
                elif prediction=='3':
                    for i in range(topLeftX,topLeftX+PATCH_SIZE):
                        for u in range(topLeftY,topLeftY+PATCH_SIZE):
                            meshMap_check[u,i] = 1
                elif prediction=='4':
                    for i in range(topLeftX,topLeftX+PATCH_SIZE):
                        for u in range(topLeftY,topLeftY+PATCH_SIZE):
                            meshMap_check[u,i] = 1
                    
        saveName = 'meshMap_' + str(sample) + '.tif'
        meshMap_check = np.multiply(meshMap_check,255)
        Image.fromarray(meshMap_check.astype(np.uint8)).save(os.path.join(sample_dest_dir,saveName))

        meshMap_Muscle = np.zeros((im_height,im_width), dtype=int)
                
        for index, row in pred_df.iterrows():
            topLeftX = int(row['XCoord'])
            topLeftY = int(row['YCoord'])
            
            conf = float(row['conf'])
            prediction = str(row['pred'])
                    
            if conf < 0.5:
                next
                    
            else:
                if prediction=='1':
                    for i in range(topLeftX,topLeftX+PATCH_SIZE):
                        for u in range(topLeftY,topLeftY+PATCH_SIZE):
                            meshMap_Muscle[u,i] = 1
                elif prediction=='2':
                    for i in range(topLeftX,topLeftX+PATCH_SIZE):
                        for u in range(topLeftY,topLeftY+PATCH_SIZE):
                            meshMap_Muscle[u,i] = 0
                elif prediction=='3':
                    for i in range(topLeftX,topLeftX+PATCH_SIZE):
                        for u in range(topLeftY,topLeftY+PATCH_SIZE):
                            meshMap_Muscle[u,i] = 1
                elif prediction=='4':
                    for i in range(topLeftX,topLeftX+PATCH_SIZE):
                        for u in range(topLeftY,topLeftY+PATCH_SIZE):
                            meshMap_Muscle[u,i] = 1
                    
        saveName = 'MusclemeshMap_' + str(sample) + '.tif'
        meshMap_Muscle = np.multiply(meshMap_Muscle,255)
        Image.fromarray(meshMap_Muscle.astype(np.uint8)).save(os.path.join(sample_dest_dir,saveName))
        
    return config
