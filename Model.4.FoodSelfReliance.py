#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 16:13:27 2018

@author: JFM3
"""


import pandas as pd
import numpy as np
from fuzzywuzzy import process

#FOOD SELF RELIANCE CALCULATION
fn = pd.read_csv('foodneedresults.csv', header = 0)
cy = pd.read_csv('cropyieldresults.csv', header = 0)

cy['crop'].loc[cy['crop']== 'Cherries, sweet'] = 'Cherries'
cy['crop'].loc[cy['crop']== 'Sweet corn'] = 'Corn'
cy['crop'].loc[cy['crop']== 'Shallots and green onions'] = 'Shallots and onions'
cy['crop'].loc[cy['crop']== 'Peaches (fresh and clingstone)'] = 'Peaches'
cy['crop'].loc[cy['crop']== 'Green peas'] = 'Peas'
cy['crop'].loc[cy['crop']== 'Plums and prunes'] = 'Plums'
cy['crop'].loc[cy['crop']== 'Total wheat'] = 'Wheat'


#FUZZY STRING MATCHING
fn_copy = np.copy(fn['commodity'])
cy_copy = np.copy(cy['crop'])
fuzzmatch = np.copy(fn_copy)
for i in range(len(fn_copy)):
    match = process.extractOne(fn_copy[i], cy_copy, score_cutoff = 90)
    if match is None:
        fuzzmatch[i] = match
    else:
        fuzzmatch[i] = match[0]
print(fuzzmatch)
#fn_copy = pd.DataFrame.copy(fuzzmatch)




#field_table['crop'] = fuzzmatch
#field_table = pd.merge(left=field_table, right = field_land, left_on = 'crop', right_on = 'crop')
#field_table.ix[:, 1:3] = field_table.ix[:, 1:3].astype(float) #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
#field_table['SWBC yield'] = ((field_table['tonnes']/field_table['hectares']) * field_table['value'])
