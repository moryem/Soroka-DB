# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 16:32:29 2019

@author: Mor
"""

import pandas as pd
import os

soroka_db = pd.read_excel(os.path.join('.', 'Mammo_Out.xlsx'))

#%%
# num of total patients
patients = set(soroka_db['Name'])
amount_patients = len(patients)

# num of only one breast:
patient_dict = {}

for patient in patients:
    patient_views = soroka_db['Laterality'][soroka_db['Name']==patient]
    is_left = any(patient_views.str.contains('L'))
    is_right = any(patient_views.str.contains('R'))
    if (is_right and is_left):
        patient_dict[patient] = 2
    else:
        patient_dict[patient] = 1
        
idx__mastectomy = [i for i, x in enumerate(list(patient_dict.values())) if x == 1]
amount_mastectomy = len(idx__mastectomy)
amount_normal = amount_patients - amount_mastectomy

num_images = 4*amount_normal + 2*amount_mastectomy

#%% num of images from each birads level

def num_birads(df, birad):
    bi = df['Bi-Rads']==birad
    return sum(bi)

bi_rads = [1,2,3,4,'4a','4b','4c',5,6]
birads = {}

for bi in bi_rads:
    amount = num_birads(soroka_db, bi)
    if (bi == '4a' or bi == '4b' or bi == '4c'):
        birads['Bi-Rads 4'] += num_birads(soroka_db, bi)
    else:
        birads['Bi-Rads ' + str(bi)] = num_birads(soroka_db, bi)

total_amount = sum(birads.values())

import matplotlib.pyplot as plt
from matplotlib import rcParams

fig = plt.figure(figsize=[8, 8])
ax = fig.add_subplot(111)

wedges, plt_labels, junk = ax.pie(birads.values(), autopct='%.f%%', pctdistance=1.1);
rcParams['font.size'] = 13
plt.legend(wedges, birads.keys(), bbox_to_anchor=(1.3, 0.6))

for pie_wedge in wedges:
    pie_wedge.set_edgecolor('white')

plt.tight_layout()

plt.savefig('Bi-Rads dist')

#%% num of images from each birads level with mass!

def num_birads(df, birad):
    bi = df['Bi-Rads']==birad
    mass  = ~df['Mass'].isna()
    return sum(np.logical_and(bi, mass))
    
bi_4 = num_birads(soroka_db, 4)
print('num of 4: ' + str(bi_4))
bi_4a = num_birads(soroka_db, '4a')
print('num of 4a: ' + str(bi_4a))
bi_4b = num_birads(soroka_db, '4b')
print('num of 4b: ' + str(bi_4b))
bi_4c = num_birads(soroka_db, '4c')
print('num of 4c: ' + str(bi_4c))
bi_5 = num_birads(soroka_db, 5)
print('num of 5: ' + str(bi_5))
bi_6 = num_birads(soroka_db, 6)
print('num of 6: ' + str(bi_6))

total_amount = bi_4a + bi_4b + bi_4c + bi_5 + bi_6
print('total with mass: ' + str(total_amount))
