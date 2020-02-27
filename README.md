# Soroka-DB

utils.py - Class for reading data from the dicom directories, constructs a DataFrame object with all cases and their info from the dicom files.

create_excel.py - Class for creating a new excel file for the mammograms interpretation, according to the DataFrame created in utils and the original excel file. 

DB_statistics.py - A script for calculating and plotting the statistics of the Soroka dataset

pre_process.py - Class for pre-process the images – resize to a pre-defined size and crop the background of the mammograms.

read_unilateral.py - Class for reading the Soroka dataset for a unilateral model. It produces mammograms.npy, labels.npy and birads.npy, which are the mammograms, their binary labels and their Bi-Rads level respectively.

read_bilateral.py - Class for reading the Soroka dataset for a bilateral model. It produces the right and left inputs of the train set and the test set, with their binary labels. 

read_similarity_test.py - Class for creating pairs of bilateral mammograms and their labels for the test set of the mammograms asymmetry model.

data augmentation.py - Script for creating augmentation on a specified train set
