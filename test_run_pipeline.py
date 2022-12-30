import os
import json
import torch
import sys
sys.path.insert(0,'./0_ScaleWSIs')
sys.path.insert(0,'./1_PatchExtraction')
sys.path.insert(0,'./2_Inference')
sys.path.insert(0,'./3_MeshMaps')
sys.path.insert(0,'./4_Overlays')
sys.path.insert(0,'./5_ProbMaps')
sys.path.insert(0,'./6_mouseModelInference')
sys.path.insert(0,'./7_clinicalScoreInference')
from generateJSON import *
from extractPatches import *
from extractmeshPatches import *
from meshPredictions import *
from largerPatchPredictions import *
from generateMeshMaps import *
from generateOverlays import *
from meshOverlayChecker import *
from scaleWSIs import *
from generateProbMaps import *
from mergeMice_Involved_Uninvolved import *
from RN_FeatureExtractor import *
from conductPCA import *
from kMeans_onPCA import *
from merge_Uninvolved_InvolvedkMeansCounts import *
from getProps import *
from LDA_inference import *
from sortkMeansClusters import *
from LDA_inference_CS import *

def prepare_directories(config):
    BASE_DIR = config['directories']['BASE_DIR']
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)

    SCALED_WSI_DIR = os.path.join(BASE_DIR,'scaled_WSIs')
    if not os.path.exists(SCALED_WSI_DIR):
        os.mkdir(SCALED_WSI_DIR)

    config['directories']['SCALED_WSI_DIR'] = SCALED_WSI_DIR
    
    return config

def runPipeline(config):
    ### Crop and scale input WSIs
    print('Cropping and Scaling WSIs...')
    #scale_WSI(INPUT_WSI_DIR = config['directories']['INPUT_WSI_DIR'],
    #          SCALED_WSI_DIR = config['directories']['SCALED_WSI_DIR'],
    #          BASE_DIR = config['directories']['BASE_DIR'],
    #          PATCH_SIZE = config['PatchInfo']['PATCH_SIZE'],
    #          WSI_EXTENSION = config['SlideInfo']['WSI_EXTENSION'],
    #          SCALE_FACTOR = config['SlideInfo']['SCALE_FACTOR'],
    #          SAVE_CROPPED_WSI = config['SlideInfo']['SAVE_CROPPED_WSI'])
    
    
    ### Extract patches
    print('Performing Mesh Patch Extraction...')
    #config = meshpatchExtraction(config = config)
    
    ### Run Mesh Predictions
    print('Running Mesh Predictions...')
    #config = perform_Meshpredictions(config = config)
    
    ### Generating Mesh Maps
    print('Generating Mesh Maps...')
    #config = createMeshMaps(config)
    
    ### Extract Larger Patches
    print('Performing Patch Extraction...')
    #config = patchExtraction(config)
    
    ### Generating Overlays
    print('Generating Overlays...')
    #meshOverlayCheck(config)
    
    ### Run Larger Patch Predictions
    print('Running Larger Patch Predictions...')
    #config = perform_predictions(config)

    if config['PatchInfo']['generateProbMaps'] == True:
    ### Generate Prob maps
        print('Generating Prob Maps...')
   #     config = generateProbMaps(config)
    
    if config['mouseModelInference']['performInference'] == True:
        assert config['PatchInfo']['PREDICT_OVERLAPS'] == True, "Overlap Predictions Must Be Performed."

        ### Gather Involved and Uninvolved Patches...
        print('Gathering Involved and Uninvolved Patches...')
    #    config = mergeMice(config)
        
        ### Perform RN Feature Extraction
        print('Performing RN Feature Extraction on Involved Patches...')
     #   config = RN_FeatureExtraction(config)
        
        ### Perform PCA
        print('Conducting PCA on Involved Patches...')
     #   config = performPCA(config)

        ### Perform kMeans
        print('performing kMeans on Involved Patches...')
     #   config = kMeansPCA(config)

        ### Merge InvolvedUninvolved Counts
        print('Merging Involved and Uninvolved Counts...')
     #   config = mergeCounts(config)

        ### Generate Proportions
        print('Generating Uninvolved and Involved k-mean Class Proportions...')
     #   config = generateProps(config)
        
        config['directories']['GEN_PATCHES_DIR'] = '/data03/shared/skobayashi/YANGPROSPECTIVE_fullPipeline_allMice_InvUnvPipeline_reLabeled/Involved_UninvolvedPatches'
        ### Perform Mouse Model Inference
        print('Performing LDA mouse model inference...')
        config = LDA_infer(config)
        
        ### Perform Clinical Score Bin Inference
        print('Performing LDA CS inference...')
        config = CS_LDA_infer(config)
        
        ### Sort kMeans Clusters to Visualize
        print('Sorting kMeans Clusters...')
        sortClusters(config)
    
if __name__ == '__main__':
    generate_JSON()
    
    config = json.load(open('config.json'))

    config = prepare_directories(config)
    
    runPipeline(config)
