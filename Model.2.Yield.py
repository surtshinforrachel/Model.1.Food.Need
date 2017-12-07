#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 12:00:22 2017

@author: JFM3
"""
#YIELD DATA

import pandas as pd
import numpy as np
import difflib
import fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

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
#field_table['yield'] = (field_table['tonnes']/field_table['acres']) #NOT WORKING

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
#fruit_table = fruit_table['tons'].mul(tons_to_tonnes,axis=0) #CONVERT TONS TO TONNES
#fruit_table['yield'] = fruit_table['tons']/field_table['hectares'] #NOT WORKING 
#NOT IN METRIC TONNES

#VEG CROPS DATA CLEANING
vegcrops = pd.read_csv('cansim0010013.2014.csv', header = 0)
vegcrops = vegcrops.drop(['Ref_Date', 'GEO'], axis = 1) #delete reference date column
vegcrops.columns = ['unit', 'type', 'value'] #name first column header 'commodity' and name second column header 'kg/person'
acres = vegcrops.loc[vegcrops['unit']== 'Area planted (hectares)']
tonnes = vegcrops.loc[vegcrops['unit']== 'Marketed production (metric tonnes)']
veg_table = pd.merge(left=acres, right = tonnes, left_on = 'type', right_on = 'type')
veg_table = veg_table.drop(['unit_x', 'unit_y'], axis = 1).reset_index(drop=True) #delete first three columns
veg_table.ix[:, 1:3] = veg_table.ix[:, 1:3].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
veg_table = veg_table.dropna(axis=0, how='any').reset_index(drop=True)  #if value is NA, delete that row
veg_table.columns = ['crop', 'hectares', 'tons']
#veg_table['yield'] = fruit_table['tons']/field_table['hectares'] #NOT WORKING 
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
#green_table.columns = ['crop', 'square meters', 'kilograms']
#green_table['yield'] = green_table['kilograms']/green_table['square meters']
#NOT IN METRIC TONNES!!!! IN HUNDRED WEIGHT X 1000 AND ACRES

veg_land = pd.read_csv('cansim0040215.2011.csv', header = 0)
veg_land = veg_land.drop(['Ref_Date', 'GEO', 'UOM'], axis = 1) #delete reference date column
veg_table_2 = pd.merge(left=veg_table, right = veg_land, left_on = 'crop', right_on = 'VEG', how = 'outer')

veg_land2 = veg_land['VEG']
veg_crop2 = veg_table['crop']
#veg_crop2 = veg_crop2.index.map(lambda x: difflib.get_close_matches(x, veg_land2)[0])
#veg_table['crop'] = veg_table['crop'].apply(lambda x: difflib.get_close_matches(x, veg_land['VEG'])[0])


match = veg_crop2
for i in range(len(veg_crop2)):
   match[i] =  difflib.get_close_matches(veg_crop2[i], veg_land2, n=1, cutoff = 0.3)

fuzzmatch = veg_crop2
for i in range(len(veg_crop2)):
    fuzzmatch[1] = fuzz.token_set_ratio(veg_crop2[i], veg_land2)

#fuzzmatch2 = vegcrops['type']
#for i in range(len(veg_crop2)):
fuzzmatch2 =  fuzz.ratio(veg_crop2[1], veg_land2)
   #if fuzz.token_set_ratio(veg_crop2[i], fuzzmatch2[i]) < 70:
    #   fuzzmatch2[i] == 'NA'
           
#process.extract("new york jets", choices, limit=2)


# 1 -- Convert units
# 2 -- Calculate yield
# 3 -- Multiply by SWBC area for commodity


