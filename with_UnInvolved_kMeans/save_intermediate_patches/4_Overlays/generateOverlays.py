import os
import PIL
from PIL import Image, ImageDraw, ImageOps
import shutil
import pandas as pd

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
    return r, g, b

def return_Xcoord(fn):
    Xcoord = str(fn).split('_')[-4][:-1]
    
    return Xcoord

def return_Ycoord(fn):
    Ycoord = str(fn).split('_')[-3][:-1]
    
    return Ycoord

def createOverlays(config):
    DEST_DIR = config['directories']['DEST_DIR']
    WSI_DIR = config['directories']['SCALED_WSI_DIR']
    PREDICTIONS_DIR = config['directories']['PREDICTIONS_DIR']
    PATCH_SIZE = config['PatchInfo']['PATCH_SIZE']
    
    DEST_DIR = os.path.join(DEST_DIR, 'OverlayOutputs')
    if not os.path.exists(DEST_DIR):
        os.mkdir(DEST_DIR)
    
    spec_PREDICTIONS_DIRS = [a for a in os.listdir(PREDICTIONS_DIR)]
    
    for spec_PREDICTIONS_DIR in spec_PREDICTIONS_DIRS:
        samples = [s for s in os.listdir(os.path.join(PREDICTIONS_DIR,spec_PREDICTIONS_DIR))]
        
        specDestDir = os.path.join(DEST_DIR,str(spec_PREDICTIONS_DIR))
        if not os.path.exists(specDestDir):
            os.mkdir(specDestDir)
        
        for sample in samples:
            if not sample.startswith('.'):
                sample_dest_dir = os.path.join(specDestDir,sample)
                if not os.path.exists(sample_dest_dir):
                    os.mkdir(sample_dest_dir)
                    
                pred_df = pd.read_csv(os.path.join(os.path.join(os.path.join(PREDICTIONS_DIR,spec_PREDICTIONS_DIR),sample),'adjustlabel_predicts.csv'), header=None)
                
                pred_df = pred_df.drop(pred_df.columns[0:4],axis=1)
                
                pred_df.columns=['conf','pred','fn']
                
                pred_df['XCoord'] = pred_df['fn'].map(return_Xcoord)
                pred_df['YCoord'] = pred_df['fn'].map(return_Ycoord)
                
                fileName = sample + '.tif'
                
                base = Image.open(os.path.join(WSI_DIR,fileName))
                
                for index, row in pred_df.iterrows():
                    #print(str(row['fn']))
                    topLeftX = int(row['XCoord'])
                    topLeftY = int(row['YCoord'])
                    
                    conf = float(row['conf'])
                    prediction = str(row['pred'])
                    
                    if prediction=='1':
                        r, g, b = rgb(conf,classification='bg')
                        if r==g==b==0:
                            next
                        else:
                            image=Image.new('RGB',(PATCH_SIZE, PATCH_SIZE), color = (r, g, b))
                            image.putalpha(100)
                            base.paste(im=image,box=(topLeftX,topLeftY),mask=image)
                    elif prediction=='2':
                        r, g, b = rgb(conf,classification='muscle')
                        if r==g==b==0:
                            next
                        else:
                            image=Image.new('RGB',(PATCH_SIZE, PATCH_SIZE), color = (r, g, b))
                            image.putalpha(100)
                            base.paste(im=image,box=(topLeftX,topLeftY),mask=image)
                    elif prediction=='3':
                        r, g, b = rgb(conf,classification='tissue')
                        if r==g==b==0:
                            next
                        else:
                            image=Image.new('RGB',(PATCH_SIZE, PATCH_SIZE), color = (r, g, b))
                            image.putalpha(100)
                            base.paste(im=image,box=(topLeftX,topLeftY),mask=image)
                    elif prediction=='4':
                        r, g, b = rgb(conf,classification='submucosa')
                        if r==g==b==0:
                            next
                        else:
                            image=Image.new('RGB',(PATCH_SIZE, PATCH_SIZE), color = (r, g, b))
                            image.putalpha(100)
                            base.paste(im=image,box=(topLeftX,topLeftY),mask=image)
                    
                saveName = 'Overlayed_' + str(sample) + '.tif'
                base.save(os.path.join(sample_dest_dir,saveName))
