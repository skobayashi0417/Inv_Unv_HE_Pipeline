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
    CTRL = ['45','602','603','562','563','44','505','506']
    TAM = ['600','601','42','43','296']
    DSS = ['621','622','24','560','561','7','504','294']
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
    CTRL = ['45','602','603','562','563','44','505','506']
    TAM = ['600','601','42','43','296']
    DSS = ['621','622','24','560','561','7','504','294']
    COMBO = ['595','610','611']
    
    if sampleNum in CTRL:
        return 3
    elif sampleNum in TAM:
        return 0
    elif sampleNum in DSS:
        return 1
    elif sampleNum in COMBO:
        return 2

def decode_cs_to_bin(CS):
    if int(CS)==0:
        return 'LOW'
    elif int(CS)==1:
        return 'MID'
    elif int(CS)==2:
        return 'HIGH'

def CS_LDA_infer(config):
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
    
    # Get rid of training mice for which we have no clinical scores
    train_df = train_df.dropna(subset=['CS_bin_0Low_1mid_2high'])
    
    # Extract Archived Mouse Cohort Proportions and GT Labels
    train_y = np.array(train_df['CS_bin_0Low_1mid_2high'])
    train_x = np.array(train_df[train_cols])
    
    # Extract Prospective or Inferene Cohort Proportions
    test_x = np.array(test_df[test_cols])
    test_mice = np.array(test_df['mouse'])

    # Fit LDA Classifier on Archived Mouse Cohort and Predict
    clf = LinearDiscriminantAnalysis()

    clf.fit(train_x, train_y)

    y_pred = clf.predict(test_x)
    
    
    if config['csInference']['onProspectiveCohort'] == True:
        # This is on the prospective cohort with our known GTs... load up their CS from csv
        cs_gt_df = pd.read_csv('./7_clinicalScoreInference/prospectiveCohort_CS_groundTruth/prospectiveMouseCohort_CS.csv')
        merged_df = pd.merge(test_df,cs_gt_df,on='mouse')

        test_y = np.array(merged_df['CS_bin_0Low_1mid_2high'])
        
        save_fn = "prospectiveCohort_LDA_clinicalScore_summary.txt"
        summaryFilePath = os.path.join(save_dir,save_fn)
        writeSummary = open(summaryFilePath, 'w')
        writeSummary.write('test_accuracy is: ' + str(accuracy_score(test_y, y_pred)) + '\n')
        writeSummary.write('f1 is: ' + str(f1_score(test_y, y_pred,average='macro')) + '\n')
        writeSummary.write('conf_matrix is: ' + '\n' + str(confusion_matrix(test_y, y_pred)) + '\n')
        for i in range(len(y_pred)):
            writeSummary.write('Mouse # ' + str(test_mice[i]) + ': Clinical Score of ' + str(y_pred[i]) + ' (' + decode_cs_to_bin(y_pred[i]) + ' bin) ' + '\n')
        writeSummary.close()
    
    else:
        save_fn = "nonProspective_InferenceCohort_LDA_clinicalScore_summary.txt"
        summaryFilePath = os.path.join(os.getcwd(),save_fn)
        writeSummary = open(summaryFilePath, 'w')
        for i in range(len(y_pred)):
            writeSummary.write('Mouse # ' + str(test_mice[i]) + ' Clincial Score Bin: ' + decode_cs_to_bin(y_pred[i]) + '\n')
        writeSummary.close()
    
    return config
