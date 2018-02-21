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
from fuzzywuzzy import process

#CONVERSTION FACTORS
tons_to_tonnes = 1.10231
acres_to_hectares = 2.47105
thousand_sq_ft_to_hectare = (107639/1000)
hundred_weight_to_tonne = 19.6841
kg_to_tonne = 1000
sq_m_to_hectare = 10000


fieldcrops = pd.read_csv('cansim0010017.csv', header = 0)
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
        
frames = [fieldcrops, fruitcrops, vegcrops, greencrops]        
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
allcrops2 = pd.merge(hectares, tonnes, left_on=['date','crop'], right_on=['date','crop']).drop(['geo_x', 'unit_x', 'geo_y', 'unit_y'], axis = 1, )
allcrops2.columns = ['crop', 'date', 'hectares', 'tonnes']
allcrops2['tonnes/hec'] = allcrops2['tonnes']/allcrops2['hectares']

baseline_yr = 2011
baseline = allcrops2.loc[allcrops2['date']== baseline_yr]
ten_yr_ave = allcrops2.groupby('crop')['hectares', 'tonnes', 'tonnes/hec'].mean().reset_index()




mushcrops = pd.read_csv('cansim0010012.2014.csv', header = 0)
potcrops = pd.read_csv('cansim0010014.2014.csv', header = 0)


