import json

def generate_JSON():

    data = {}

    data['directories'] = {}
    data['SlideInfo'] = {}
    data['PatchInfo'] = {}
    data['mouseModelInference'] = {}
    data['csInference'] = {}

    data['directories']['INPUT_WSI_DIR'] = '/data02/shared/skobayashi/downloadVSI/Yang_Prospect2/Scan_composite_wChronic_reLabeled'
    data['directories']['BASE_DIR'] = '/data01/shared/skobayashi/HE_Inv_UnInv_sortUnInvKmeans'

    data['SlideInfo']['WSI_EXTENSION'] = '.tif'
    data['SlideInfo']['SCALE_FACTOR'] = 8
    data['SlideInfo']['SAVE_CROPPED_WSI'] = True
    
    data['PatchInfo']['meshPATCH_SIZE'] = 32
    data['PatchInfo']['PATCH_SIZE'] = 224
    data['PatchInfo']['extractOverlaps'] = True
    data['PatchInfo']['PREDICT_OVERLAPS'] = True
    data['PatchInfo']['generateProbMaps'] = True
    data['mouseModelInference']['performInference'] = True
    data['mouseModelInference']['onProspectiveCohort'] = False
    data['csInference']['onProspectiveCohort'] = False

    data['DEVICE'] = 0

    with open('config.json','w') as outfile:
        json.dump(data,outfile)

if __name__=='__main__':
    generate_JSON()
