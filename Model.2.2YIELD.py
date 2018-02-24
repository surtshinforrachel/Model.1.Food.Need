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
tons_to_tonnes = 0.907185
acres_to_hectares = 0.404686
thousand_sq_ft_to_hectare = 0.0092903
hundred_weight_x1k_to_tonne = 50.8
kg_to_tonne = .001
sq_m_to_hectare = .0001

                                #BC YIELD DATA
fieldcrops = pd.read_csv('cansim0010017.csv', header = 0)
canadafieldcrops = pd.read_csv('cansim0010017.canada.csv', header = 0)#For beans, all dry, chickpeas, corn for grain, flaxseed, lentils, rye all, soybeans
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
        potcrops.ix[i, 3] = ((potcrops.ix[i, 3].astype(float))*hundred_weight_x1k_to_tonne)
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
baseline_yield = allcrops.loc[allcrops['date']== baseline_yr]

mushroom_exception = pd.DataFrame(ten_yr_ave.loc[ten_yr_ave['crop']== 'Mushrooms'])
drypeas_exception = pd.DataFrame(ten_yr_ave.loc[ten_yr_ave['crop']== 'Peas, dry'])
mixedgrains_exception = pd.DataFrame(ten_yr_ave.loc[ten_yr_ave['crop']== 'Mixed grains'])
sourcherry_exception = pd.DataFrame(ten_yr_ave.loc[ten_yr_ave['crop']== 'Cherries, sour'])
frames = [mushroom_exception, drypeas_exception, mixedgrains_exception, sourcherry_exception]
baseline_yield = baseline_yield.append(frames).reset_index(drop = True)

#CANOLA MEAL, SOYBEAN MEAL, PASTURE
oilandmeal = pd.read_csv('cansim0010010.csv', header = 0)
oilandmeal.index = pd.to_datetime(oilandmeal['Ref_Date'])
oilandmeal = oilandmeal.drop(['Ref_Date', 'GEO'], axis = 1)
oilandmealg = oilandmeal.groupby([(oilandmeal.index.year), 'PRO', 'COM']).sum()
oilandmeal = pd.DataFrame(oilandmealg)
oilandmeal.columns = ['Value']
c_seed = oilandmeal.Value.ix[2011, 'Seed crushed', 'Canola (rapeseed)', 'Value']
c_meal = oilandmeal.Value.ix[2011, 'Meal produced', 'Canola (rapeseed)', 'Value']
canolamealyield = ((c_meal/c_seed)*(baseline_yield.loc[(baseline_yield['crop']== 'Canola', 'tonnes_per_hec')])) #CHECK THIS SHIT!!!
canolamealyield = canolamealyield.ix[1,1]
canolamealyield = 0.97
canolaoilyield = 0.75
soybeanmealyield = 2.005 #2002-2011 average meal/hectare seeded [(from 'Yields - Historic, Crops_2015.07.20.xlsx' 'Soybeans' workbook
pastureyield = 4.2 #Average SC, SL, PR - 4 tonnes DM/Ha (Wallapak says just use this one)
yieldadditions = pd.DataFrame({'date': [0, 0, 0, 0], 'tonnes': [0, 0, 0, 0], 'hectares': [0, 0, 0, 0], 'tonnes_per_hec': [canolamealyield, canolaoilyield, soybeanmealyield, pastureyield]}, index=['Canola Meal', 'Canola Oil', 'Soybean Meal', 'Pasture']).reset_index()
yieldadditions.columns = ['crop', 'date', 'tonnes', 'hectares', 'tonnes_per_hec']
baseline_yield = baseline_yield.append(yieldadditions).reset_index(drop = True)


                                #SWBC LAND USE DATA
field_land = pd.read_csv('cansim0040213.2011.3.csv', header = 0)
field_land.columns = ['date', 'geo', 'crop', 'unit', 'SWBC hectares planted']
fruit_land = pd.read_csv('cansim0040214.2011.csv', header = 0)
fruit_land.columns = ['date', 'geo', 'crop', 'unit', 'SWBC hectares planted']
veg_land = pd.read_csv('cansim0040215.2011.csv', header = 0)
veg_land.columns = ['date', 'geo', 'crop', 'unit', 'SWBC hectares planted']
greenmush_land = pd.read_csv('cansim0040217.2011.csv', header = 0)
greenmush_land.ix[:, 4] = greenmush_land.ix[:, 4].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
greenmush_land.loc['Value'] = (greenmush_land['Value']*sq_m_to_hectare)
greenmush_land.columns = ['date', 'geo', 'crop', 'unit', 'SWBC hectares planted']


frames = [field_land, fruit_land, veg_land, greenmush_land]
allcropland = pd.concat(frames, ignore_index =True) 
allcropland.ix[:, 4] = allcropland.ix[:, 4].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
allcropland = allcropland.groupby('crop')['SWBC hectares planted'].sum().reset_index()


                                #MANUAL MATCHING
baseline_yield.loc[baseline_yield['crop']== 'Tame hay','crop'] = 'Tame hay'
baseline_yield.loc[baseline_yield['crop']== 'Wheat, all', 'crop'] = 'Total wheat'
#baseline_yield.loc[baseline_yield['crop']== 'Cherries (sour) total area', 'crop'] = 'Repeat'
baseline_yield.loc[baseline_yield['crop']== 'Beans, green or wax', 'crop'] = 'Beans, green and wax'
baseline_yield.loc[(baseline_yield['crop']== 'Cabbage, Chinese (bok-choy, napa, etcetera)', 'crop')] = 'Repeated crop'
baseline_yield.loc[(allcrops['crop']== 'Cabbage, regular', 'crop')] = 'Repeated crop'

allcropland.loc[(allcropland['crop']== 'Asparagus, producing', 'crop')] = 'Asparagus'
allcropland.loc[(allcropland['crop']== 'Asparagus, non-producing', 'crop')] = 'Asparagus'
allcropland.loc[(allcropland['crop']== 'Chinese cabbage', 'crop')] = 'Cabbage'
allcropland.loc[(allcropland['crop']== 'All other tame hay and fodder crops', 'crop')] = 'Tame hay and fodder'
allcropland.loc[(allcropland['crop']== 'Canola (rapeseed)', 'crop')] = 'Canola'
allcropland.loc[(allcropland['crop']== 'Total growing area for mushrooms', 'crop')] = 'Mushrooms'
allcropland.loc[(allcropland['crop']== 'Dry white beans', 'crop')] = 'Beans, all dry'
allcropland.loc[(allcropland['crop']== 'Other dry beans', 'crop')] = 'Beans, all dry'
allcropland.loc[(allcropland['crop']== 'Peaches total area', 'crop')] = 'Peaches'
allcropland.loc[(allcropland['crop']== 'Dry field peas', 'crop')] = 'Peas, dry'
allcropland.loc[(allcropland['crop']== 'Total rye', 'crop')] = 'Rye, all'

frame1 = pd.DataFrame(allcropland.loc[allcropland['crop']== 'Greenhouse vegetables'])
frame2 = pd.DataFrame(allcropland.loc[allcropland['crop']== 'Greenhouse vegetables'])
frame3 = pd.DataFrame(allcropland.loc[allcropland['crop']== 'Greenhouse vegetables'])
frame1['SWBC hectares planted'] = (allcropland.loc[allcropland['crop']== 'Greenhouse vegetables', 'SWBC hectares planted']/3)
frame1['crop'] = 'Fresh tomatoes, greenhouse'
frame2['SWBC hectares planted'] = (allcropland.loc[allcropland['crop']== 'Greenhouse vegetables', 'SWBC hectares planted']/3)
frame2['crop'] = 'Fresh cucumbers, greenhouse'
frame3['SWBC hectares planted'] = (allcropland.loc[allcropland['crop']== 'Greenhouse vegetables', 'SWBC hectares planted']/3)
frame3['crop'] = 'Fresh peppers, greenhouse'
frames = [frame1, frame2, frame3]
allcropland = allcropland.append(frames)
allcropland = allcropland.groupby('crop')['SWBC hectares planted'].sum().reset_index()
                           
#FUZZY STRING MATCHING                         
allland2 = allcropland['crop'].copy()
allyields2 = baseline_yield['crop'].copy()
fuzzmatch = allland2.copy()
for i in range(len(allland2)):
    match = process.extractOne(allland2[i], allyields2, score_cutoff = 90)
    if match is None:
        fuzzmatch[i] = match
    else:
        fuzzmatch[i] = match[0]
fuzzmatch = pd.DataFrame(fuzzmatch)
allcropland['crop'] = fuzzmatch
allcrops = pd.merge(left=baseline_yield, right = allcropland, left_on = 'crop', right_on = 'crop', how = 'inner')
allcrops['SWBC tonnes'] = allcrops['tonnes_per_hec']*allcrops['SWBC hectares planted']

allcrops.to_csv('cropyieldresults.csv')
 
