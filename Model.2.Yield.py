#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 12:00:22 2017

@author: JFM3
"""
#YIELD DATA

import pandas as pd
import numpy as np

#CONVERSTION FACTORS
tons_to_tonnes = 1.10231
acres_to_hectares = 2.47105
thousand_sq_ft_to_hectare = 107639
hundred_weight_to_tonne = 19.6841/1000

#FIELD CROPS DATA CLEANING
fieldcrops = pd.read_csv('cansim0010010.2014.csv', header = 0)
fieldcrops = fieldcrops.drop(['Ref_Date'], axis = 1) #delete reference date column
fieldcrops.columns = ['geo', 'unit', 'type', 'value'] #name first column header 'commodity' and name second column header 'kg/person'
#cropunits = np.unique(fieldcrops[['unit']].values)
fieldcrops = pd.DataFrame(data=fieldcrops)
acres =fieldcrops.loc[fieldcrops['unit']== 'Harvested area (hectares)']
tonnes =fieldcrops.loc[fieldcrops['unit']== 'Production (metric tonnes)']
field_table = pd.merge(left=acres, right = tonnes, left_on = 'type', right_on = 'type')
field_table = field_table.drop(['geo_y', 'geo_x', 'unit_x', 'unit_y'], axis = 1).reset_index(drop=True) #delete first three columns
field_table.ix[:, 1:2] = field_table.ix[:, 1:2].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
field_table = field_table.dropna(axis=0, how='any').reset_index(drop=True)  #if value is NA, delete that row
field_table.columns = ['crop', 'acres', 'tonnes']
field_table['yield'] = (field_table['tonnes']/field_table['acres']) #NOT WORKING

#FRUIT CROPS DATA CLEANING
fruitcrops = pd.read_csv('cansim0010009.2014.csv', header = 0)
fruitcrops = fruitcrops.drop(['Ref_Date', 'GEO', 'EST'], axis = 1) #delete reference date column
fruitcrops.columns = ['type', 'unit', 'value'] #name first column header 'commodity' and name second column header 'kg/person'
acres = fruitcrops.loc[fruitcrops['unit']== 'Hectares']
tonnes = fruitcrops.loc[fruitcrops['unit']== 'Tons']
#newtonnes = tonnes.mul(tons_to_tonnes,axis=0) #CONVERT TONS TO TONNES
fruit_table = pd.merge(left=acres, right = tonnes, left_on = 'type', right_on = 'type')
fruit_table = fruit_table.drop(['unit_x', 'unit_y'], axis = 1).reset_index(drop=True) #delete first three columns
fruit_table.ix[:, 1:2] = fruit_table.ix[:, 1:2].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
fruit_table = fruit_table.dropna(axis=0, how='any').reset_index(drop=True)  #if value is NA, delete that row
fruit_table.columns = ['crop', 'hectares', 'tons']
fruit_table = fruit_table['tons'].mul(tons_to_tonnes,axis=0) #CONVERT TONS TO TONNES
fruit_table['yield'] = (fruit_table['tons']/field_table['hectares']) #NOT WORKING 
#NOT IN METRIC TONNES

#VEG CROPS DATA CLEANING
vegcrops = pd.read_csv('cansim0010013.2014.csv', header = 0)
vegcrops = vegcrops.drop(['Ref_Date', 'GEO'], axis = 1) #delete reference date column
vegcrops.columns = ['unit', 'type', 'value'] #name first column header 'commodity' and name second column header 'kg/person'
acres = vegcrops.loc[vegcrops['unit']== 'Area beds, total (square feet x 1,000)']
tonnes = vegcrops.loc[vegcrops['unit']== 'Production (fresh and processed), total (tons)']
veg_table = pd.merge(left=acres, right = tonnes, left_on = 'type', right_on = 'type')
veg_table = veg_table.drop(['unit_x', 'unit_y'], axis = 1).reset_index(drop=True) #delete first three columns
veg_table.ix[:, 1:3] = veg_table.ix[:, 1:3].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
veg_table = veg_table.dropna(axis=0, how='any').reset_index(drop=True)  #if value is NA, delete that row
veg_table.columns = ['crop', 'hectares', 'tons']
veg_table['yield'] = (fruit_table['tons']/field_table['hectares']) #NOT WORKING 
#NOT IN METRIC TONNES

#MUSHROOM DATA CLEANING
mushcrops = pd.read_csv('cansim0010012.2014.csv', header = 0)
mushcrops = mushcrops.drop(['Ref_Date', 'GEO'], axis = 1) #delete reference date column
mushcrops.columns = ['unit', 'value'] #name first column header 'commodity' and name second column header 'kg/person'
mushcrops.ix[:, 1] = mushcrops.ix[:, 1].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
mushcrops = mushcrops.dropna(axis=0, how='any').reset_index(drop=True)  #if value is NA, delete that row
mushcrops['yield'] = mushcrops['value'][1]/mushcrops['value'][0]
#NOT IN METRIC TONNES!!!! IN TONS AND 1000 SQ FT


#POTATO DATA CLEANING
potcrops = pd.read_csv('cansim0010014.2014.csv', header = 0)
potcrops = potcrops.drop(['Ref_Date', 'GEO'], axis = 1) #delete reference date column
potcrops.columns = ['unit', 'value'] #name first column header 'commodity' and name second column header 'kg/person'
potcrops.ix[:, 1] = potcrops.ix[:, 1].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
potcrops = potcrops.dropna(axis=0, how='any').reset_index(drop=True)  #if value is NA, delete that row
potcrops['yield'] = potcrops['value'][1]/potcrops['value'][0]
#NOT IN METRIC TONNES!!!! IN HUNDRED WEIGHT X 1000 AND ACRES


#GREENHOUSE DATA CLEANING
greencrops = pd.read_csv('cansim0010006.2014.csv', header = 0)
greencrops = greencrops.drop(['Ref_Date', 'GEO', 'PRO'], axis = 1) #delete reference date column
greencrops.columns = ['type', 'unit', 'value'] #name first column header 'commodity' and name second column header 'kg/person'
acres = greencrops.loc[greencrops['unit']== 'Square metres']
tonnes = greencrops.loc[greencrops['unit']== 'Kilograms']
green_table = pd.merge(left=acres, right = tonnes, left_on = 'type', right_on = 'type')
green_table.ix[:, 1:3] = green_table.ix[:, 1:3].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
green_table = green_table.dropna(axis=0, how='any').reset_index(drop=True)  #if value is NA, delete that row
green_table.columns = ['crop', 'square meters', 'kilograms']
#NOT IN METRIC TONNES!!!! IN HUNDRED WEIGHT X 1000 AND ACRES



# 1 -- Convert units
# 2 -- Calculate yield
# 3 -- Multiply by SWBC area for commodity


