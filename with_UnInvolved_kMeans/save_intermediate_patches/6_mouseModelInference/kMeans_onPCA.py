import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
import pandas as pd
import os
import copy
import shutil
import pickle
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def kMeansPCA(config):
    BASE_DIR = config['directories']['BASE_DIR']
    PCA_DIR = config['directories']['PCA_OUTPUTS_DIR']
    home_dir = ('/').join(str(os.getcwd()).split('/')[0:-2])
    
    saveDir = os.path.join(BASE_DIR,'kMeans_Outputs')
    
    if not os.path.exists(saveDir):
        os.mkdir(saveDir)
        
    #First Involved Patches
    print('kMeans on Involved...')
    
    K_MEANS_MODEL = home_dir + '/6_mouseModelInference/kmeans_model/kmeans_model_k4.pkl'
    k = 4
        
    config['directories']['KMEANS_OUTPUT_DIR'] = saveDir

    df = pd.read_csv(os.path.join(PCA_DIR,[a for a in os.listdir(PCA_DIR) if a.endswith('testData.csv')][0]))
        
    values = df.drop(['fns'],axis=1)
    arrayvalues = np.array(values)

    labels = df[['fns']]
    
    kmeans = pickle.load(open(K_MEANS_MODEL,'rb'))
    pred_y = kmeans.predict(arrayvalues)
    
    output_df = copy.deepcopy(labels)

    output_df.columns = ['fn']
    output_df['Predictions'] = pred_y
    
    output_df.to_csv(os.path.join(saveDir,'kmeansClusters_onPCA_k' + str(k) + '_involvedwOverlaps_'  + 'test.csv'),header=None,index=False)
    
    #UNinvolved Patches Next
    print('kMeans on UNInvolved...')
    
    K_MEANS_MODEL = home_dir + '/6_mouseModelInference/kmeans_model/kMeanssave_onPCA_k3_UninvolvedwOverlaps_255Comps_Uninvolved.pkl'
    k = 4

    df = pd.read_csv(os.path.join(PCA_DIR,[a for a in os.listdir(PCA_DIR) if a.endswith('testData_UNinv.csv')][0]))
        
    values = df.drop(['fns'],axis=1)
    arrayvalues = np.array(values)

    labels = df[['fns']]
    
    kmeans = pickle.load(open(K_MEANS_MODEL,'rb'))
    pred_y = kmeans.predict(arrayvalues)
    
    output_df = copy.deepcopy(labels)

    output_df.columns = ['fn']
    output_df['Predictions'] = pred_y
    
    output_df.to_csv(os.path.join(saveDir,'kmeansClusters_onPCA_k' + str(k) + '_UNinvolvedwOverlaps_'  + 'test.csv'),header=None,index=False)
    
    

    return config
