import numpy as np
import pandas as pd
from kneed import KneeLocator
import os
import copy
import pickle
import shutil
import csv

def aggregate_to_directory(OVERLAP_PATCHES_DIR,DEST_PATCHES_DIR,df):
    for index,row in df.iterrows():
        sample = str(('_').join(str(row[4][1:]).split('_')[0:3]))
        fn = str(row[4][1:])

        src = os.path.join(os.path.join(OVERLAP_PATCHES_DIR,sample),fn)
            
        dest = os.path.join(DEST_PATCHES_DIR,fn)
        shutil.copy(src,dest)
        

def merge_csvs(DEST_DIR,PRED_DIR, target):
    trigger = 0
    
    samples = [s for s in os.listdir(PRED_DIR) if not s.startswith('.')]
    
    for sample in samples:
        csvPath = os.path.join(os.path.join(PRED_DIR,sample),'adjustlabel_predicts.csv')
        
        if target == 'Involved':
            ID = 2
        
        elif target == 'Uninvolved':
            ID = 1
        
        if trigger == 0:
            mergedDF = pd.read_csv(csvPath,header=None)
            mergedDF = mergedDF[mergedDF[3]==ID]
            #print(mergedDF.head)
            trigger += 1
        else:
            df = pd.read_csv(csvPath,header=None)
            df = df[df[3]==ID]
            #print(df.head)
            mergedDF = pd.concat([mergedDF,df])
    
    output_file = os.path.join(DEST_DIR,'merged_' + str(target) + '.csv')
    
    mergedDF.to_csv(output_file,header=None,index=False)
    
    return mergedDF

def mergeMice(config):
    BASE_DIR = config['directories']['BASE_DIR']
    
    PRED_DIR = os.path.join(BASE_DIR,'predictions_wOverlaps')
    
    OVERLAP_PATCHES_DIR = os.path.join(os.path.join(BASE_DIR,'extractedPatches'),'withOverlaps_byMouse')
    
    DEST_DIR = os.path.join(BASE_DIR,'Involved_UninvolvedPatches')
    if not os.path.exists(DEST_DIR):
        os.mkdir(DEST_DIR)
    
    INVOLVED_PATCHES_DIR = os.path.join(DEST_DIR,'involvedPatches_wOverlaps')
    UNINVOLVED_PATCHES_DIR = os.path.join(DEST_DIR,'UNinvolvedPatches_wOverlaps')
    
    if not os.path.exists(INVOLVED_PATCHES_DIR):
        os.mkdir(INVOLVED_PATCHES_DIR)

    if not os.path.exists(UNINVOLVED_PATCHES_DIR):
        os.mkdir(UNINVOLVED_PATCHES_DIR)

    involved_df = merge_csvs(DEST_DIR,PRED_DIR,'Involved')
    uninvolved_df = merge_csvs(DEST_DIR,PRED_DIR,'Uninvolved')
    
    aggregate_to_directory(OVERLAP_PATCHES_DIR,INVOLVED_PATCHES_DIR,involved_df)
    aggregate_to_directory(OVERLAP_PATCHES_DIR,UNINVOLVED_PATCHES_DIR,uninvolved_df)

    config['directories']['INVOLVED_PATCHES_DIR'] = INVOLVED_PATCHES_DIR
    config['directories']['UNINVOLVED_PATCHES_DIR'] = UNINVOLVED_PATCHES_DIR
    config['directories']['GEN_PATCHES_DIR'] = DEST_DIR
    
    return config
