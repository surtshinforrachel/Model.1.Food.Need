#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 12:00:22 2017

@author: JFM3
"""
#YIELD DATA

import pandas as pd
import numpy as np


fieldcrops = pd.DataFrame.from_csv('cansim0010010.2014.csv', header = 0)
#fieldcrops = fieldcrops.drop(['Ref_Date'], axis = 1) #delete reference date column
fieldcrops.columns = ['geo', 'unit', 'type', 'value'] #name first column header 'commodity' and name second column header 'kg/person'
#cropunits = np.unique(fieldcrops[['unit']].values)

fieldcrops.groupby('unit')
#print(acres)


