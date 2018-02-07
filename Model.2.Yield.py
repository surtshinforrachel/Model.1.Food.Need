#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 12:00:22 2017

@author: JFM3
"""
#YIELD DATA

import pandas as pd
from fuzzywuzzy import process

#CONVERSTION FACTORS
tons_to_tonnes = 1.10231
acres_to_hectares = 2.47105
thousand_sq_ft_to_hectare = (107639/1000)
hundred_weight_to_tonne = (19.6841/1000)
kg_to_tonne = 1000
sq_m_to_hectare = 10000


#2.1 - FIELD CROPS DATA CLEANING
fieldcrops = pd.read_csv('cansim0010017.2014.csv', header = 0)
fieldcrops = fieldcrops.drop(['Ref_Date'], axis = 1) #delete reference date column
fieldcrops.columns = ['geo', 'unit', 'type', 'value'] #name first column header 'commodity' and name second column header 'kg/person'
#cropunits = np.unique(fieldcrops[['unit']].values)
fieldcrops = pd.DataFrame(data=fieldcrops)
hectares =fieldcrops.loc[fieldcrops['unit']== 'Seeded area (hectares)']
tonnes =fieldcrops.loc[fieldcrops['unit']== 'Production (metric tonnes)']
field_table = pd.merge(left=hectares, right = tonnes, left_on = 'type', right_on = 'type')
field_table = field_table.drop(['geo_y', 'geo_x', 'unit_x', 'unit_y'], axis = 1).reset_index(drop=True) #delete first three columns
field_table.ix[:, 1:2] = field_table.ix[:, 1:2].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
field_table = field_table.dropna(axis=0, how='any').reset_index(drop=True)  #if value is NA, delete that row
field_table.columns = ['crop', 'hectares', 'tonnes']
field_table['crop'].loc[field_table['crop']== 'Tame hay'] = 'Tame hay only'
field_table['crop'].loc[field_table['crop']== 'Wheat, all'] = 'Total wheat'

#SWBC LAND AREA
field_land = pd.read_csv('cansim0040213.2011.2.csv', header = 0)
field_land.ix[:, 4] = field_land.ix[:, 4].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
field_land = field_land.drop(['Ref_Date', 'UOM'], axis = 1).fillna(value=0) #delete reference date column
field_land = field_land.groupby('CROPS', as_index=False).sum() 
field_land.columns = ['crop','value'] #name first column header 'commodity' and name second column header 'kg/person'
#field_land['crop'].loc[field_land['crop']== 'Total corn'] = 'Corn'

#FUZZY STRING MATCHING
field_land2 = field_land['crop']
field_crops2 = field_table['crop']
fuzzmatch = field_crops2
for i in range(len(field_crops2)):
    match = process.extractOne(field_crops2[i], field_land2, score_cutoff = 90)
    if match is None:
        fuzzmatch[i] = match
    else:
        fuzzmatch[i] = match[0]
field_table['crop'] = fuzzmatch
field_table = pd.merge(left=field_table, right = field_land, left_on = 'crop', right_on = 'crop')
field_table.ix[:, 1:3] = field_table.ix[:, 1:3].astype(float) #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
field_table['SWBC yield'] = ((field_table['tonnes']/field_table['hectares']) * field_table['value'])


#2.2 - FRUIT CROPS DATA CLEANING
fruitcrops = pd.read_csv('cansim0010009.2014.csv', header = 0)
fruitcrops = fruitcrops.drop(['Ref_Date', 'GEO', 'EST'], axis = 1) #delete reference date column
fruitcrops.columns = ['type', 'unit', 'value'] #name first column header 'commodity' and name second column header 'kg/person'
acres = fruitcrops.loc[fruitcrops['unit']== 'Hectares']
tons = fruitcrops.loc[fruitcrops['unit']== 'Tons']
fruit_table = pd.merge(left=acres, right = tons, left_on = 'type', right_on = 'type')
fruit_table = fruit_table.drop(['unit_x', 'unit_y'], axis = 1).reset_index(drop=True) #delete first three columns
fruit_table.ix[:, 1:2] = fruit_table.ix[:, 1:2].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
fruit_table = fruit_table.dropna(axis=0, how='any').reset_index(drop=True)  #if value is NA, delete that row
fruit_table.columns = ['crop', 'hectares', 'tons']
fruit_table['tonnes'] = fruit_table['tons'].astype(float)*tons_to_tonnes #CONVERT tons to TONNES
fruit_table = fruit_table.drop(['tons'], axis = 1) #delete reference date column

fruit_land = pd.read_csv('cansim0040214.2011.csv', header = 0)
fruit_land.ix[:, 4] = fruit_land.ix[:, 4].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
fruit_land = fruit_land.drop(['Ref_Date', 'UOM'], axis = 1).fillna(value=0).groupby('NUTS', as_index=False).sum()  #delete reference date column
fruit_land.columns = ['crop','value'] 
fruit_land.loc[fruit_land['crop']== 'Cherries (sour) total area'] = 'Repeat'
#FUZZY STRING MATCHING
fruit_land2 = fruit_land['crop']
fruit_crops2 = fruit_table['crop']
fuzzmatch = fruit_land2
for i in range(len(fruit_land2)):
    match = process.extractOne(fruit_land2[i], fruit_crops2, score_cutoff = 86)
    if match is None:
        fuzzmatch[i] = match
    else:
        fuzzmatch[i] = match[0]
fuzzy_fruit_land = fruit_land
fuzzy_fruit_land['crop'] = fuzzmatch
fruit_table = pd.merge(left=fruit_table, right = fuzzy_fruit_land, left_on = 'crop', right_on = 'crop')
fruit_table.ix[:, 1:3] = fruit_table.ix[:, 1:3].astype(float) #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
fruit_table['SWBC yield'] = (((fruit_table['tonnes']/fruit_table['hectares'])*.25) * fruit_table['value']) #includes 25% reduction for the SWBC specific yield


#2.3 - VEG CROPS DATA CLEANING
vegcrops = pd.read_csv('cansim0010013.2014.csv', header = 0)
vegcrops = vegcrops.drop(['Ref_Date', 'GEO'], axis = 1) #delete reference date column
vegcrops.columns = ['unit', 'type', 'value'] #name first column header 'commodity' and name second column header 'kg/person'
hectares = vegcrops.loc[vegcrops['unit']== 'Area planted (hectares)']
tonnes = vegcrops.loc[vegcrops['unit']== 'Marketed production (metric tonnes)']
veg_table = pd.merge(left=hectares, right = tonnes, left_on = 'type', right_on = 'type')
veg_table = veg_table.drop(['unit_x', 'unit_y'], axis = 1).reset_index(drop=True) #delete first three columns
veg_table.columns = ['crop', 'hectares', 'tonnes']
veg_table.ix[:, 1:3] = veg_table.ix[:, 1:3].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
veg_table = veg_table.dropna(axis=0, how='any').reset_index(drop=True)  #if value is NA, delete that row
veg_table['crop'].loc[veg_table['crop']== 'Beans, green or wax'] = 'Beans, green and wax'
veg_table['crop'].loc[(veg_table['crop']== 'Cabbage, Chinese (bok-choy, napa, etcetera)') | (veg_table['crop']== 'Cabbage, regular')] = 'Repeated crop'
#FUZZY STRING MATCHING
veg_land = pd.read_csv('cansim0040215.2011.csv', header = 0)
veg_land = veg_land.drop(['Ref_Date', 'GEO', 'UOM'], axis = 1) #delete reference date column
veg_land['VEG'].loc[(veg_land['VEG']== 'Asparagus, producing') | (veg_land['VEG']== 'Asparagus, non-producing')] = 'Asparagus'
veg_land = veg_land.groupby(veg_land['VEG'], as_index=False).sum() #COMBINE ASPARAGAS
veg_land.columns = ['VEG', 'value']
veg_table_2 = pd.merge(left=veg_table, right = veg_land, left_on = 'crop', right_on = 'VEG', how = 'outer')
veg_land2 = veg_land['VEG']
veg_crop2 = veg_table['crop']
fuzzmatch = veg_crop2
for i in range(len(veg_crop2)):
    match = process.extractOne(veg_crop2[i], veg_land2, score_cutoff = 87)
    if match is None:
        fuzzmatch[i] = match
    else:
        fuzzmatch[i] = match[0]
veg_table['crop'] = fuzzmatch
veg_table_2fuzz = pd.merge(left=veg_table, right = veg_land, left_on = 'crop', right_on = 'VEG', how = 'inner')
veg_table_2fuzz = veg_table_2fuzz.drop(['VEG'], axis = 1) #delete reference date column
veg_table_2fuzz.ix[:, 1:3] = veg_table_2fuzz.ix[:, 1:3].astype(float) #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
veg_table_2fuzz['SWBC yield'] = ((veg_table_2fuzz['tonnes']/veg_table_2fuzz['hectares']) * veg_table_2fuzz['value'])


#2.4 - MUSHROOM DATA CLEANING
mushcrops = pd.read_csv('cansim0010012.2014.csv', header = 0)
mushcrops = mushcrops.drop(['Ref_Date'], axis = 1) #delete reference date column
mushcrops.columns = ['GEO', 'unit', 'value'] #name first column header 'commodity' and name second column header 'kg/person'
area = mushcrops.loc[mushcrops['unit']== 'Area beds, total (square feet x 1,000)']
tons = mushcrops.loc[mushcrops['unit']== 'Production (fresh and processed), total (tons)']
mush_table = pd.merge(left=area, right = tons, left_on = 'GEO', right_on = 'GEO').drop(['unit_x', 'unit_y'], axis = 1)
mush_table['GEO'] = 'Mushrooms'
mush_table.ix[:, 1] = mush_table.ix[:, 1].astype(float)*tons_to_tonnes #tons_to_tonnes = 1.10231
mush_table.ix[:, 2] = mush_table.ix[:, 2].astype(float)*thousand_sq_ft_to_hectare #thousand_sq_ft_to_hectare = (107639/1000) = 107.639
mush_table.columns = ['crop', 'hectares', 'tonnes'] #name first column header 'commodity' and name second column header 'kg/person'

#SWBC AREA DATA
greenmush_land = pd.read_csv('cansim0040217.2011.csv', header = 0)
greenmush_land.ix[:,4] = greenmush_land.ix[:,4].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
greenmush_land = greenmush_land.drop(['Ref_Date', 'UOM'], axis = 1).fillna(value=0).groupby('GREEN', as_index=False).sum()  #delete reference date column
greenmush_land.columns = ['crop','hectares'] 
greenmush_land['hectares'] = greenmush_land['hectares']*sq_m_to_hectare
mush_table['value'] = int(greenmush_land['hectares'].loc[greenmush_land['crop']== 'Total growing area for mushrooms'])
mush_table['SWBC yield'] = (mush_table['tonnes']/mush_table['hectares'])*mush_table['value']


#2.5 - POTATO DATA CLEANING
potcrops = pd.read_csv('cansim0010014.2014.csv', header = 0)
potcrops = potcrops.drop(['Ref_Date'], axis = 1) #delete reference date column
potcrops.columns = ['GEO', 'unit', 'value'] #name first column header 'commodity' and name second column header 'kg/person'
area = potcrops.loc[potcrops['unit']== 'Seeded area, potatoes (acres)']
hundredweight = potcrops.loc[potcrops['unit']== 'Production, potatoes (hundredweight x 1,000)']
pot_table = pd.merge(left=area, right = hundredweight, left_on = 'GEO', right_on = 'GEO').drop(['GEO', 'unit_x', 'unit_y'], axis = 1)
#pot_table.columns = ['acres', 'hundredweight'] #name first column header 'commodity' and name second column header 'kg/person'
pot_table.ix[:, 0] = pot_table.ix[:, 0].astype(float)*acres_to_hectares #acres_to_hectares = 2.47105
pot_table.ix[:, 1] = pot_table.ix[:, 1].astype(float)*hundred_weight_to_tonne #hundred_weight_to_tonne = (19.6841/1000) = 0.0196841
pot_table.columns = ['hectares', 'tonnes'] #name first column header 'commodity' and name second column header 'kg/person'
pot_table['crop'] = 'Potatoes'
cols = ['crop' , 'hectares', 'tonnes']
pot_table = pot_table[cols]

#SWBC AREA DATA
pot_land = pd.read_csv('cansim0040213.2011.2.csv', header = 0)
pot_land.ix[:, 4] = pot_land.ix[:, 4].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
pot_land = pot_land.drop(['Ref_Date', 'UOM'], axis = 1).fillna(value=0) #delete reference date column
pot_land = pot_land.groupby('CROPS', as_index=False).sum() 
pot_land.columns = ['crop','value'] 
pot_table['value'] = int(pot_land['value'].loc[pot_land['crop']== 'Potatoes'])
pot_table['SWBC yield'] = (pot_table['tonnes']/pot_table['hectares'])*pot_table['value']


#2.6 - GREENHOUSE DATA CLEANING
greencrops = pd.read_csv('cansim0010006.2014.csv', header = 0)
greencrops = greencrops.drop(['Ref_Date', 'GEO', 'PRO'], axis = 1) #delete reference date column
greencrops.columns = ['type', 'unit', 'value'] #name first column header 'commodity' and name second column header 'kg/person'
acres = greencrops.loc[greencrops['unit']== 'Square metres']
tonnes = greencrops.loc[greencrops['unit']== 'Kilograms']
green_table = pd.merge(left=acres, right = tonnes, left_on = 'type', right_on = 'type').drop(['unit_x', 'unit_y'], axis = 1)
green_table.columns =['type', 'square meters', 'kg']
green_table.ix[:, 1:3] = green_table.ix[:, 1:3].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
green_table = green_table.dropna(axis=0, how='any').reset_index(drop=True)  #if value is NA, delete that row
green_table.ix[:, 1] = green_table.ix[:, 1].astype(float)*kg_to_tonne #*1000
green_table.ix[:, 2] = green_table.ix[:, 2].astype(float)*sq_m_to_hectare #*1000
green_table.columns = ['crop', 'hectares', 'tonnes'] #name first column header 'commodity' and name second column header 'kg/person'
green_table['value'] = green_table['tonnes']
#SWBC AREA DATA
for i in range(len(green_table['value'])):
    green_table['value'][i] = int(greenmush_land['hectares'].loc[greenmush_land['crop']== 'Greenhouse vegetables'] / 3)
green_table['SWBC yield'] = (green_table['tonnes']/green_table['hectares'])*green_table['value'] 
     
# 1 -- Convert units
# 2 -- Calculate yield
# 3 -- Merge tables using fuzzy string matching
#mostfuzzy = fuzzmatch6[0]
# 4 -- Multiply by SWBC area for commodity
# 5 -- Combine all tables


frames = [field_table, fruit_table, veg_table_2fuzz, mush_table, pot_table, green_table]
yield_table = pd.concat(frames, ignore_index = True)
yield_table.to_csv('cropyieldresults.csv')
