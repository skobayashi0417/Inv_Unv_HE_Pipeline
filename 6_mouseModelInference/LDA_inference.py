import os
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score

def prospective_conditions(sampleNum):
    # ground truths
    CTRL = ['ND09','ND16','ND17','ND20','ND21','ND24','ND27','ND28']
    TAM = ['ND14','ND15','ND22','ND23','ND30']
    DSS = ['621','622','ND10','ND18','ND19','ND25','ND26','ND29']
    COMBO = ['595','610','611']
    
    if sampleNum in CTRL:
        return 'Ctrl'
    elif sampleNum in TAM:
        return 'TAM_colitis'
    elif sampleNum in DSS:
        return 'DSS_colitis'
    elif sampleNum in COMBO:
        return 'Combined_Induction'

def prospective_conditions_numEncoded(sampleNum):
    # ground truths
    CTRL = ['ND09','ND16','ND17','ND20','ND21','ND24','ND27','ND28']
    TAM = ['ND14','ND15','ND22','ND23','ND30']
    DSS = ['621','622','ND10','ND18','ND19','ND25','ND26','ND29']
    COMBO = ['595','610','611']
    
    if sampleNum in CTRL:
        return 3
    elif sampleNum in TAM:
        return 0
    elif sampleNum in DSS:
        return 1
    elif sampleNum in COMBO:
        return 2

def decode_conditions(cond):
    if cond == 0:
        return 'TAM_colitis'
    elif cond == 1:
        return 'DSS_colitis'
    elif cond == 2:
        return 'Combined_Induction'
    elif cond ==3:
        return 'Ctrl'

def LDA_infer(config):
    BASE_DIR = config['directories']['BASE_DIR']
    save_dir = os.path.join(BASE_DIR,'LDA_Predictions')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    # Load up DFs
    train_df = pd.read_csv('./6_mouseModelInference/archivedMouseCohort_Proportions/archivedMouseCohort.csv')
    
    test_df = pd.read_csv(os.path.join(config['directories']['GEN_PATCHES_DIR'],'invUninvolvedPatchCounts_test_wProps.csv'))

    # Extract column Names with patch proportions
    test_cols = [a for a in test_df.columns if str(a).endswith('percent')]
    train_cols = [a for a in train_df.columns if str(a).endswith('percent')]
    
    # Extract Archived Mouse Cohort Proportions and GT Labels
    train_y = np.array(train_df['condition'])
    train_x = np.array(train_df[train_cols])
    
    # Extract Prospective or Inferene Cohort Proportions
    test_x = np.array(test_df[test_cols])
    test_mice = np.array(test_df['mouse'])

    # Fit LDA Classifier on Archived Mouse Cohort and Predict
    clf = LinearDiscriminantAnalysis()
    clf.fit(train_x, train_y)

    y_pred = clf.predict(test_x)
    
    
    if config['mouseModelInference']['onProspectiveCohort'] == True:
        # This is on the prospective cohort with our known GTs... load up their labels
        print(test_df.head)
        test_df['condition_string'] = test_df['mouse'].map(prospective_conditions)
        test_df['condition'] = test_df['mouse'].map(prospective_conditions_numEncoded)
        print(test_df.head)
        test_y = np.array(test_df['condition'])
        
        save_fn = "prospectiveCohort_LDA_summary.txt"
        summaryFilePath = os.path.join(save_dir,save_fn)
        writeSummary = open(summaryFilePath, 'w')
        print('CHECK')
        print(y_pred[0:15])
        print(test_y[0:15])
        print('ENDCHECK')
        
        writeSummary.write('test_accuracy is: ' + str(accuracy_score(test_y, y_pred)) + '\n')
        writeSummary.write('f1 is: ' + str(f1_score(test_y, y_pred,average='macro')) + '\n')
        writeSummary.write('conf_matrix is: ' + '\n' + str(confusion_matrix(test_y, y_pred)) + '\n')
        for i in range(len(y_pred)):
            writeSummary.write('Mouse # ' + str(test_mice[i]) + ': ' + decode_conditions(y_pred[i]) + '\n')
        writeSummary.close()
    
    else:
        save_fn = "nonProspective_InferenceCohort_LDA_summary.txt"
        summaryFilePath = os.path.join(os.getcwd(),save_fn)
        writeSummary = open(summaryFilePath, 'w')
        for i in range(len(y_pred)):
            writeSummary.write('Mouse # ' + str(test_mice[i]) + ': ' + decode_conditions(y_pred[i]) + '\n')
        writeSummary.close()
    
    return config
