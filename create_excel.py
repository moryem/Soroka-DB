# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 12:18:03 2020

@author: Mor
"""
import os
import pandas as pd
from utils import read_dcm

class create_exl():

    def __init__(self, exl_name = 'Soroka_Mammo.xlsx', out_exl_name = 'Mammo_Out.xlsx', path = '.'):
# =============================================================================
#         initialize parameters
# =============================================================================
        
        self.exl_name = exl_name                # excel file's name
        self.out_exl_name = out_exl_name        # output excel file's name
        self.path = path                        # root directory
        self.rd = read_dcm(mode='unilateral')   # read dicom object


    def merge_excel_dicom(self):
# =============================================================================
#         read the excel file and merge with the dicom details
# =============================================================================

        # read dicom details
        self.rd.read_dicom()
        dicom_df = (self.rd.dicom_df).drop(columns=['Orientation'])
        
        # read the xls file as dataframe
        self.exl_df = pd.read_excel(os.path.join(self.path, self.exl_name))
        
        # merge dataframs        
        for i in range(len(dicom_df)):
            # get the dcm data
            data_dcm = dicom_df.iloc[[i]]
            # find rows in excel file of same patient with same laterality
            indx = self.exl_df.index[self.exl_df['File Name'] == dicom_df['Name'][i]].tolist()
            for j in indx:
                data_indx = self.exl_df.iloc[indx]
                ind = data_indx.index[data_indx['Laterality'] == dicom_df['Laterality'][i]].tolist()
            # get the corresponding excel data     
            data_exl = self.exl_df.iloc[ind].iloc[:,2:]
            # merge into one dataframe
            new_row = pd.concat([data_dcm.reset_index(drop=True), data_exl.reset_index(drop=True)],axis=1)
            if not i:
                self.df = new_row.copy()
            else:
                self.df = pd.concat([self.df, new_row], axis=0)
        
        # reindex
        self.df.index = range(len(self.df))
        
    def export_to_excel(self):
# =============================================================================
#         export data into one excel file
# =============================================================================

        if os.path.isfile(os.path.join(self.path, self.out_exl_name)):
            print('File already exists!')
        else:
            self.merge_excel_dicom()
            # export to excel
            file_name = os.path.join(self.path, self.out_exl_name)
            self.df.to_excel(file_name)


    