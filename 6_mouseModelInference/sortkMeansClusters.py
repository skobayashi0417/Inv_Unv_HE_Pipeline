#import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
import pandas as pd
import os
import copy
import shutil

def prepare_dirs(clusters,num_k,DEST_DIR):
    spec_dest = os.path.join(DEST_DIR,str(num_k)+'_clusters')
    if not os.path.exists(spec_dest):
        os.mkdir(spec_dest)
    for c in clusters:
        path = os.path.join(spec_dest,'Cluster_'+str(c))
        if not os.path.exists(path):
            os.mkdir(path)
    return spec_dest

def extract_sampleID(fn):
    sampleID = str(fn).split('-')[0]
    return sampleID

def sortClusters(config):
    kMeansDir = config['directories']['KMEANS_OUTPUT_DIR']
    src_dir = config['directories']['INVOLVED_PATCHES_DIR']

    kMeans_CSVs = [c for c in os.listdir(kMeansDir) if c.endswith('test.csv')]
    
    for kMeansCSV in kMeans_CSVs:
        df = pd.read_csv(os.path.join(kMeansDir,kMeansCSV),header=None)
        df.columns = ['fn','Cluster']

        df['sample'] = df['fn'].map(extract_sampleID)
        
        clusters = list(set(list(df['Cluster'])))
        num_k = 4
        
        spec_dest = prepare_dirs(clusters,num_k,kMeansDir)
        
        for index, row in df.iterrows():
            sample = row['sample']
            fn = row['fn']
            cluster = row['Cluster']
            
            src = os.path.join(src_dir,fn)
                
            dest = os.path.join(os.path.join(spec_dest,'Cluster_'+str(cluster)),fn)
            shutil.copy(src,dest)

if __name__=='__main__':
    main()
