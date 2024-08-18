import os
import pandas as pd
import numpy as np
import csv

def extract_sampleID_UNInvolved(fn):
    sampleID = str(fn)[1:].split('_')[0]
    return sampleID

def extract_sampleID(fn):
    sampleID = str(fn).split('_')[0]
    return sampleID

def mergeCounts(config):
    BASE_DIR = config['directories']['BASE_DIR']
    
    KMEANS_DIR = config['directories']['KMEANS_OUTPUT_DIR']
    
    # load involved df
    involved_df = pd.read_csv(os.path.join(KMEANS_DIR,[a for a in os.listdir(KMEANS_DIR) if a.endswith('_involvedwOverlaps_test.csv')][0]), header=None)
    involved_df.columns = ['fn','Cluster']
    involved_df['sample'] = involved_df['fn'].map(extract_sampleID)
    
    # load uninvovled df
    UNinvolved_df = pd.read_csv(os.path.join(config['directories']['GEN_PATCHES_DIR'],'merged_Uninvolved.csv'),header=None)
    UNinvolved_df.columns = ['healthyProb','pathProb','maxProb','Pred','fn']
    UNinvolved_df['sample'] = UNinvolved_df['fn'].map(extract_sampleID_UNInvolved)
    
    # get involved clusters
    invClusters = list(set(involved_df['Cluster']))
    
    samples = list(set(list(involved_df['sample'])))

    tracker = []
    
    for sample in samples:
        # start mouseTracker
        sampleTracker = [str(sample)]
    
        # log number of uninvolved patches
        sampleTracker.append(len(UNinvolved_df[UNinvolved_df['sample']==str(sample)]))
        
        # subset involved_df for this mouse
        subset = involved_df[involved_df['sample']==str(sample)]
        
        # iterate and log involved kMeans cluster counts
        for invCluster in invClusters:
            sampleTracker.append(len(subset[subset['Cluster']==invCluster]))
        
        # append to overall tracker
        tracker.append(sampleTracker)
    
    ## save info to df ##
    # convert involvedClusters into ColNames
    invClasses = ['Cluster_' + str(z) for z in invClusters]
    
    appendDict = {}

    with open(os.path.join(config['directories']['GEN_PATCHES_DIR'],'invUninvolvedPatchCounts_test.csv'),'w') as csvfile:
        fieldnames = ['mouse','UNinvCount'] + invClasses
                    
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvwriter.writeheader()
        for i in range(len(tracker)):
            toAppend = tracker[i]
            appendDict['mouse']=toAppend[0]
            appendDict['UNinvCount']=toAppend[1]
            appendDict[fieldnames[2]]=toAppend[2]
            appendDict[fieldnames[3]]=toAppend[3]
            appendDict[fieldnames[4]]=toAppend[4]
            appendDict[fieldnames[5]]=toAppend[5]
            csvwriter.writerow(appendDict)
    
    return config
        
if __name__=='__main__':
    main()
