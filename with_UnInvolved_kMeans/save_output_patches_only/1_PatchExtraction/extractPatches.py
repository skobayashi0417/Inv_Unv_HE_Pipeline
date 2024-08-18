import os
import numpy
import PIL
import csv
import openslide
import shutil
from PIL import Image
from autofilter import *

def expandPts(tupledOrigCoords):
    expandedCoordsList = []

    x = tupledOrigCoords[0]
    y = tupledOrigCoords[1]
    for x_c in range(x-220,x+221,20):
        if x_c < 0:
            next
        else:
            for y_c in range(y-220,y+221,20):
                if y_c < 0:
                    next
                else:
                    coords = (x_c,y_c)
                    #print(coords)
                    expandedCoordsList.append(coords)

    final = [a for a in expandedCoordsList if a != tupledOrigCoords]
    
    return final

def extractPatches(im, possibleCoords, PATCH_SIZE, mouseDir, filtered_mouseDir, WSI, WSI_EXTENSION, MESHMAP, MusclemeshMap):
    sampleID = str(mouseDir).split('/')[-1]
    
    for possibleCoord in possibleCoords:
        newTile = im.read_region((possibleCoord[0],possibleCoord[1]), 0, (PATCH_SIZE,PATCH_SIZE)).convert("RGB")
        
        decision = filter_and_sort(newTile,PATCH_SIZE)
        
        if decision == 'NoKeep':
            # tmp save to check
            savePath = os.path.join(filtered_mouseDir,str(WSI)[:-(len(WSI_EXTENSION))] + '_%dX_%dY_w%d_h%d_BGFILTER.png' % (int(possibleCoord[0]), int(possibleCoord[1]),int(PATCH_SIZE),int(PATCH_SIZE)))
            newTile.save(savePath)
            next
            
        else:
            ### Calculate Mesh Slice amount of Non-Tissue (bg + muscle) but with a higher thresh ###
            meshSlice = MESHMAP[possibleCoord[1]:possibleCoord[1]+PATCH_SIZE,possibleCoord[0]:possibleCoord[0]+PATCH_SIZE]
            sliceSize = PATCH_SIZE * PATCH_SIZE
            
            ## Get Amount of Non Tisses in Array Slice -- should be 0s
            nonTissueValues = sliceSize - np.count_nonzero(meshSlice)
            
            ### Calculate Muscle Mesh Slice amount of Non-Tissue (Muscle) with a lower thresh ###
            MusclemeshSlice = MusclemeshMap[possibleCoord[1]:possibleCoord[1]+PATCH_SIZE,possibleCoord[0]:possibleCoord[0]+PATCH_SIZE]
            
            ## Get Amount of Muscle in Array Slice -- should be 0s
            MuscleValues = sliceSize - np.count_nonzero(MusclemeshSlice)

            if nonTissueValues/sliceSize >= 0.65:
                ### Too little tissue
                
                # tmp save to check
                savePath = os.path.join(filtered_mouseDir,str(WSI)[:-(len(WSI_EXTENSION))] + '_%dX_%dY_w%d_h%d_MESHFILTER_NONTISSUE_%s_MUSCLE_%s.png' % (int(possibleCoord[0]), int(possibleCoord[1]),int(PATCH_SIZE),int(PATCH_SIZE),str(float(nonTissueValues/sliceSize)),str(float(MuscleValues/sliceSize))))
                newTile.save(savePath)
                
                next
                
            elif MuscleValues/sliceSize >= 0.35:
                ### Too much Muscle
                
                # tmp save to check
                savePath = os.path.join(filtered_mouseDir,str(WSI)[:-(len(WSI_EXTENSION))] + '_%dX_%dY_w%d_h%d_MESHFILTER_NONTISSUE_%s_MUSCLE_%s.png' % (int(possibleCoord[0]), int(possibleCoord[1]),int(PATCH_SIZE),int(PATCH_SIZE),str(float(nonTissueValues/sliceSize)),str(float(MuscleValues/sliceSize))))
                newTile.save(savePath)
                
                next
            
            else:
                savePath = os.path.join(mouseDir,str(WSI)[:-(len(WSI_EXTENSION))] + '_NONTISSUE_%s_MUSCLE_%s_%dX_%dY_w%d_h%d.png' % (str(float(nonTissueValues/sliceSize)),str(float(MuscleValues/sliceSize)),int(possibleCoord[0]), int(possibleCoord[1]),int(PATCH_SIZE),int(PATCH_SIZE)))
        
                newTile.save(savePath)
        
        newTile.close()
            
def patchExtraction(config):
    Image.MAX_IMAGE_PIXELS = None
    
    BASE_DIR = config['directories']['BASE_DIR']
    PATCH_SIZE = config['PatchInfo']['PATCH_SIZE']
    WSI_EXTENSION = config['SlideInfo']['WSI_EXTENSION']
    SCALED_WSI_DIR = config['directories']['SCALED_WSI_DIR']
    MESHMAPS_DIR = config['directories']['MESH_MAPS_DIR']
    extractOverlaps= config['PatchInfo']['extractOverlaps']
    
    WSIs = [a for a in os.listdir(SCALED_WSI_DIR) if str(a).endswith(WSI_EXTENSION)]
    tot_num = len(WSIs)
    
    PATCH_DEST_DIR = os.path.join(BASE_DIR,'extractedPatches')
    if not os.path.exists(PATCH_DEST_DIR):
        os.mkdir(PATCH_DEST_DIR)
    
    byMouseDir = os.path.join(PATCH_DEST_DIR,'byMouse')
    if not os.path.exists(byMouseDir):
        os.mkdir(byMouseDir)
    
    filtered_byMouseDir = os.path.join(PATCH_DEST_DIR,'filteredOut_byMouse')
    if not os.path.exists(filtered_byMouseDir):
        os.mkdir(filtered_byMouseDir)
    
    config['directories']['byMousePatches'] = byMouseDir
    
    counter = 1
    for WSI in WSIs:
        print('Extracting patches from sample  %s.. ------ %d out of %d total samples.' % (WSI,counter,tot_num))
        
        sample = str(WSI)[:-(len(WSI_EXTENSION))]
        
        mouseDir = os.path.join(byMouseDir,sample)
        if not os.path.exists(mouseDir):
            os.mkdir(mouseDir)
        
        filtered_mouseDir = os.path.join(filtered_byMouseDir,sample)
        if not os.path.exists(filtered_mouseDir):
            os.mkdir(filtered_mouseDir)
        
        im = openslide.open_slide(os.path.join(SCALED_WSI_DIR,WSI))
        orig_width, orig_height = im.dimensions
        
        possibleXs = list(range(0,orig_width,PATCH_SIZE))
        possibleYs = list(range(0,orig_height,PATCH_SIZE))
        
        possibleCoords = []
        for i in possibleXs:
            possibleCoords += list(tuple(zip([i]*len(possibleYs),possibleYs)))
            
        ### GET MESH MAPS ###
        meshMap = Image.open(os.path.join(os.path.join(MESHMAPS_DIR, sample),'meshMap_' + str(sample) + '.tif'))
        meshMap = np.array(meshMap)

        MusclemeshMap = Image.open(os.path.join(os.path.join(MESHMAPS_DIR, sample),'MusclemeshMap_' + str(sample) + '.tif'))
        MusclemeshMap = np.array(MusclemeshMap)
        
        extractPatches(im=im, possibleCoords=possibleCoords, PATCH_SIZE = PATCH_SIZE, mouseDir=mouseDir, filtered_mouseDir = filtered_mouseDir, WSI = WSI, WSI_EXTENSION = WSI_EXTENSION, MESHMAP = meshMap, MusclemeshMap = MusclemeshMap)
        
        counter += 1
    
    if extractOverlaps == True:
        byMouse_overlapsDir = os.path.join(PATCH_DEST_DIR,'withOverlaps_byMouse')
        if not os.path.exists(byMouse_overlapsDir):
            os.mkdir(byMouse_overlapsDir)
        
        filtered_byMouse_overlapsDir = os.path.join(PATCH_DEST_DIR,'filteredOut_overlaps_byMouse')
        if not os.path.exists(filtered_byMouse_overlapsDir):
            os.mkdir(filtered_byMouse_overlapsDir)
        
        config['directories']['byMousePatches_withOverlaps'] = byMouse_overlapsDir
        
        counter = 1
        for WSI in WSIs:
            print('Extracting Overlap patches from sample  %s.. ------ %d out of %d total samples.' % (WSI,counter,tot_num))
            
            sample = str(WSI)[:-(len(WSI_EXTENSION))]
            
            Overlap_mouseDir = os.path.join(byMouse_overlapsDir,sample)
            if not os.path.exists(Overlap_mouseDir):
                os.mkdir(Overlap_mouseDir)
            
            im = openslide.open_slide(os.path.join(SCALED_WSI_DIR,WSI))
            orig_width, orig_height = im.dimensions
            
            ### Find the already extracted patches for this sample
            initialPatches = [p for p in os.listdir(os.path.join(byMouseDir,sample)) if p.endswith('.png')]
            
            num_orig = len(initialPatches)
            initialPatchCounter = 1
            
            ## trackers to give percent updates on iteration... only want to say once per quarter percent finished ##
            firstQTrigger = True
            secondQTrigger = True
            thirdQTrigger = True
            fourthQTrigger = True
            
            ## figure out quarter mark of patch #s
            quarterIndicator = num_orig * 0.25
    
            
            for initialPatch in initialPatches:
                if initialPatchCounter >= quarterIndicator and firstQTrigger == True:
                    print('Samples %s (%d out of %d samples) - 25 percent complete.' %(WSI,counter,tot_num))
                    firstQTrigger = False
                    
                elif initialPatchCounter >= (quarterIndicator*2) and secondQTrigger == True:
                    print('Samples %s (%d out of %d samples) - 50 percent complete.' %(WSI,counter,tot_num))
                    secondQTrigger = False

                elif initialPatchCounter >= (quarterIndicator*3) and thirdQTrigger == True:
                    print('Samples %s (%d out of %d samples) - 75 percent complete.' %(WSI,counter,tot_num))
                    thirdQTrigger = False

                elif initialPatchCounter == num_orig and fourthQTrigger == True:
                    print('Samples %s (%d out of %d samples) - 100 percent complete.' %(WSI,counter,tot_num))
                    fourthQTrigger = False
                
                # copy original patch to new overlaps destination
                src = os.path.join(os.path.join(byMouseDir, sample),initialPatch)
                dest = os.path.join(Overlap_mouseDir,initialPatch)
                shutil.copy(src,dest)
                
                # get this patch's coordinates
                origX = str(initialPatch).split('_')[-4][:-1]
                origY = str(initialPatch).split('_')[-3][:-1]
                
                # get possible overlap Coords
                shiftedCoords = expandPts((int(origX),int(origY)))
                
                ### GET MESH MAPS ###
                meshMap = Image.open(os.path.join(os.path.join(MESHMAPS_DIR, sample),'meshMap_' + str(sample) + '.tif'))
                meshMap = np.array(meshMap)
                
                # extract and filter these overlap patches
                extractPatches(im=im, possibleCoords=shiftedCoords, PATCH_SIZE = PATCH_SIZE, mouseDir=Overlap_mouseDir, filtered_mouseDir = filtered_byMouse_overlapsDir, WSI = WSI, WSI_EXTENSION = WSI_EXTENSION, MESHMAP = meshMap, MusclemeshMap = MusclemeshMap)
                
                
                initialPatchCounter += 1
            
            counter += 1
            
    return config
    
if __name__=='__main__':
    main()
