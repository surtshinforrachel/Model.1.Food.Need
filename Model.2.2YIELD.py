#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 17:50:19 2018

@author: JFM3
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 12:00:22 2017

@author: JFM3
"""
#YIELD DATA

import pandas as pd
import numpy as np
from fuzzywuzzy import process

#CONVERSTION FACTORS
tons_to_tonnes = 1.10231
acres_to_hectares = 2.47105
thousand_sq_ft_to_hectare = (107639/1000)
hundred_weight_to_tonne = 19.6841
kg_to_tonne = 1000
sq_m_to_hectare = 10000

                                #BC YIELD DATA
fieldcrops = pd.read_csv('cansim0010017.csv', header = 0)
canadafieldcrops = pd.read_csv('cansim0010017.canada.csv', header = 0)#For corn for grain, soybeans, and beans, all dry
fieldcrops = fieldcrops.append(canadafieldcrops)
fieldcrops.columns = ['date', 'geo', 'unit', 'crop', 'value']

fruitcrops = pd.read_csv('cansim0010009.csv', header = 0)
fruitcrops = fruitcrops.drop(['EST'], axis = 1)
fruitcrops.columns = ['date', 'geo', 'crop', 'unit', 'value']

vegcrops = pd.read_csv('cansim0010013.csv', header = 0)
vegcrops.columns = ['date', 'geo', 'unit', 'crop', 'value']

greencrops = pd.read_csv('cansim0010006.csv', header = 0)
greencrops = greencrops.drop(['PRO'], axis = 1)
greencrops.columns = ['date', 'geo', 'crop', 'unit', 'value']
greencrops.ix[:, 4] = greencrops.ix[:, 4].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
for i in range(len(greencrops['value'])):
    if greencrops['unit'][i] == 'Square metres':
        greencrops.ix[i, 4] = (greencrops.ix[i, 4].astype(float))*sq_m_to_hectare
        greencrops.ix[i, 3] = 'Hectares'
    if greencrops['unit'][i] == 'Kilograms':
        greencrops.ix[i, 4] = (greencrops.ix[i, 4].astype(float))*kg_to_tonne
        greencrops.ix[i, 3] = 'Tonnes'
        
potcrops = pd.read_csv('cansim0010014.csv', header = 0)
potcrops.columns = ['date', 'geo', 'unit', 'value']
potcrops.ix[:, 3] = potcrops.ix[:, 3].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
for i in range(len(potcrops['value'])):
    if potcrops['unit'][i] == 'Seeded area, potatoes (acres)':
        potcrops.ix[i, 3] = (potcrops.ix[i, 3].astype(float))*acres_to_hectares
        potcrops.ix[i, 2] = 'Hectares'
    if potcrops['unit'][i] == 'Production, potatoes (hundredweight x 1,000)':
        potcrops.ix[i, 3] = (potcrops.ix[i, 3].astype(float))*hundred_weight_to_tonne
        potcrops.ix[i, 2] = 'Tonnes'
potcrops['crop'] = 'Potatoes'
#Have to get data from 1996
mushcrops = pd.read_csv('cansim0010012.csv', header = 0)
mushcrops.columns = ['date', 'geo', 'unit', 'value']
mushcrops.ix[:, 3] = mushcrops.ix[:, 3].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
for i in range(len(mushcrops['value'])):
    if mushcrops['unit'][i] == 'Area beds, total (square feet x 1,000)':
        mushcrops.ix[i, 3] = (mushcrops.ix[i, 3].astype(float))*thousand_sq_ft_to_hectare
        mushcrops.ix[i, 2] = 'Hectares'
    if mushcrops['unit'][i] == 'Production (fresh and processed), total (tons)':
        mushcrops.ix[i, 3] = (mushcrops.ix[i, 3].astype(float))*tons_to_tonnes
        mushcrops.ix[i, 2] = 'Tonnes'
mushcrops['crop'] = 'Mushrooms'


frames = [fieldcrops, fruitcrops, vegcrops, greencrops, potcrops, mushcrops] 
allcrops = pd.concat(frames, ignore_index =True) 
for i in range(len(allcrops['value'])):
    if (allcrops['unit'][i] == 'Area planted (hectares)') | (allcrops['unit'][i] == 'Seeded area (hectares)'):
        allcrops.ix[i, 3] = 'Hectares'
    if (allcrops['unit'][i] == 'Marketed production (metric tonnes)') | (allcrops['unit'][i] == 'Production (metric tonnes)') | (allcrops['unit'][i] == 'Metric tonnes'):
        allcrops.ix[i, 3] = 'Tonnes'
    
allcrops.ix[:, 4] = allcrops.ix[:, 4].apply(pd.to_numeric, errors = 'coerce')
allcrops = allcrops.dropna(axis=0, how='any').reset_index(drop=True)  #if value is NA, delete that row
#allcropsg = allcrops.groupby(['crop', 'date'])['value'].sum().reset_index()
hectares = allcrops.loc[allcrops['unit']== 'Hectares']
tonnes = allcrops.loc[allcrops['unit']== 'Tonnes'] 
allcrops = pd.merge(hectares, tonnes, left_on=['date','crop'], right_on=['date','crop']).drop(['geo_x', 'unit_x', 'geo_y', 'unit_y'], axis = 1, )
allcrops.columns = ['crop', 'date', 'hectares', 'tonnes']
allcrops['tonnes_per_hec'] = allcrops['tonnes']/allcrops['hectares']

ten_yr_ave = allcrops.groupby('crop')['hectares', 'tonnes', 'tonnes_per_hec'].mean().reset_index()

baseline_yr = 2011
baseline = allcrops.loc[allcrops['date']== baseline_yr]

mushroom_exception = pd.DataFrame(ten_yr_ave.loc[ten_yr_ave['crop']== 'Mushrooms'])
baseline = baseline.append(mushroom_exception).reset_index(drop = True)


                                #SWBC LAND USE DATA
field_land = pd.read_csv('cansim0040213.2011.2.csv', header = 0)
field_land.columns = ['date', 'geo', 'crop', 'unit', 'SWBC hectares planted']
fruit_land = pd.read_csv('cansim0040214.2011.csv', header = 0)
fruit_land.columns = ['date', 'geo', 'crop', 'unit', 'SWBC hectares planted']
veg_land = pd.read_csv('cansim0040215.2011.csv', header = 0)
veg_land.columns = ['date', 'geo', 'crop', 'unit', 'SWBC hectares planted']
greenmush_land = pd.read_csv('cansim0040217.2011.csv', header = 0)
greenmush_land.columns = ['date', 'geo', 'crop', 'unit', 'SWBC hectares planted']
pot_land = pd.read_csv('cansim0040213.2011.2.csv', header = 0)
pot_land.columns = ['date', 'geo', 'crop', 'unit', 'SWBC hectares planted']

frames = [field_land, fruit_land, veg_land, greenmush_land, pot_land]
allcropland = pd.concat(frames, ignore_index =True) 
allcropland.ix[:, 4] = allcropland.ix[:, 4].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
allcropland = allcropland.groupby('crop')['SWBC hectares planted'].sum().reset_index()


                                #FUZZY STRING MATCHING
                                
allland2 = allcropland['crop'].copy()
allcrops2 = allcrops['crop'].copy()
fuzzmatch = allland2.copy()
for i in range(len(allcrops2)):
    match = process.extractOne(allcrops2[i], allland2, score_cutoff = 90)
    if match is None:
        fuzzmatch[i] = match
    else:
        fuzzmatch[i] = match[0]
fuzzmatch = pd.DataFrame(fuzzmatch)

allcrops['crop'] = fuzzmatch
allcrops = pd.merge(left=allcrops, right = allcropland, left_on = 'crop', right_on = 'crop')

#allcrops.ix[:, 1:3] = allcrops.ix[:, 1:3].astype(float) #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
#field_table['SWBC yield'] = ((field_table['tonnes']/field_table['hectares']) * field_table['value'])




