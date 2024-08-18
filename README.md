# Repository for Deep learning-based approach for the characterization and quantification of histopathology in mouse models of colitis, PLoS One 2022

## [Soma Kobayashi, Jason Shieh, Ainara Ruiz de Sabando, Julie Kim, Yang Liu, Sui Y. Zee, Prateek Prasanna, Agnieszka B. Bialkowska, Joel H. Saltz, Vincent W. Yang](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0268954)

	### Environment Setup: Please refer to ENVIRONMENT.md
	### WSIs and PCA training CSVs available at:
            - involved_wOverlap_RN_extractedFeatures_archivedMouseCohort.csv and involved_wOverlap_RN_extractedFeatures_archivedMouseCohort.csv: https://drive.google.com/drive/u/0/folders/1O6Bk57bmPSBSxkwlMpTY9pLQ9btt0laJ
            - WSIs at: https://plus.figshare.com/articles/dataset/Inference_Dataset_for_Paper_Deep_learning-based_approach_to_the_characterization_and_quantification_of_histopathology_in_mouse_models_of_colitis_PLoS_One/20425416/1
	
    ### Please move the involved_wOverlap_RN_extractedFeatures_archivedMouseCohort.csv file to './6_mouseModelInference/archivedMouseCohort_InvolvedPatches_RN_extracted_features'
    
    ### If interested in UNinvolved k_means outputs, Please also move the UNinvolved_wOverlap_RN_extractedFeatures_archivedMouseCohort.csv file to './6_mouseModelInference/archivedMouseCohort_UNinvolvedPatches_RN_extracted_features'
	
	### Running code:
		### - Edit input and base dir paths in generateJSON.py
		### - python run_pipeline.py 
