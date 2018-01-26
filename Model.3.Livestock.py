#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 07:36:50 2018

@author: JFM3
"""

#LIVESTOCK DATA
import pandas as pd
import numpy as np
import math

feedreqs = pd.read_csv('feedrequirements.csv', header = 0)
feedreqs = feedreqs.index = feedreqs['Livestock Type']
feedreqs = feedreqs.drop(['Livestock Type'])
#feedreqs = feedreqs.transpose()
#feedreqs.columns = feedreqs.iloc[0]
#feedreqs = feedreqs.reindex(feedreqs.index.drop('Livestock Type'))

#2.1 - FIELD CROPS DATA CLEANING
fieldcrops = pd.read_csv('cansim0010017.dbloading.csv', header = 0)
fieldcrops.ix[:, 4] = fieldcrops.ix[:, 4].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
fieldcrops.columns = ['year', 'geo', 'unit', 'crop', 'value'] #name first column header 'commodity' and name second column header 'kg/person'

bc_yield = fieldcrops.loc[fieldcrops['geo']== 'British Columbia']
bc_hectares = bc_yield.loc[bc_yield['unit']== 'Seeded area (hectares)']
bc_prod = bc_yield.loc[bc_yield['unit']== 'Production (metric tonnes)']
bc_table = pd.merge(left=bc_prod, right = bc_hectares, on=['crop', 'year'] , how = 'inner')
bc_table = bc_table.drop([ 'geo_x', 'unit_x', 'unit_y', 'geo_y'], axis = 1) #delete reference date column
bc_table.columns = ['year', 'crop', 'BC: Production (metric tonnes)', 'BC: Seeded area (hectares)'] #name first column header 'commodity' and name second column header 'kg/person'

canada_yield = fieldcrops.loc[fieldcrops['geo']== 'Canada']
canada_hec = canada_yield.loc[canada_yield['unit'] == 'Seeded area (hectares)']
canada_prod = canada_yield.loc[canada_yield['unit']== 'Production (metric tonnes)']
canada_table = pd.merge(left=canada_prod, right=canada_hec, on=['crop', 'year'], how='inner')
canada_table = canada_table.drop([ 'geo_x', 'unit_x', 'unit_y', 'geo_y'], axis = 1) #delete reference date column
canada_table.columns = ['year', 'crop', 'Canada: Production (metric tonnes)', 'Canada: Seeded area (hectares)'] #name first column header 'commodity' and name second column header 'kg/person'

total_yield = pd.merge(left=bc_table, right=canada_table, on=['year', 'crop'], how='outer')
total_yield['BC yield'] = (total_yield['BC: Production (metric tonnes)']/total_yield['BC: Seeded area (hectares)'])
total_yield['Canada yield'] = (total_yield['Canada: Production (metric tonnes)']/total_yield['Canada: Seeded area (hectares)'])
#total_yield = total_yield.set_index('year')

ten_year_data = pd.DataFrame([])
years = np.array([2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017])
for i in range(10):
    frame = total_yield.loc[total_yield['year'] == years[i]]
    ten_year_data = ten_year_data.append(frame, ignore_index = True)
mymeans = ten_year_data.groupby('crop')['BC yield', 'Canada yield'].mean()
final_yields = pd.DataFrame(mymeans)
final_yields['yields used'] = np.zeros(len(final_yields))
for i in range(len(final_yields)):
    if (math.isnan(final_yields['BC yield'][i]) == False):
        final_yields['yields used'][i] = final_yields['BC yield'][i]
    if (math.isnan(final_yields['BC yield'][i]) == True):
        final_yields['yields used'][i] = final_yields['Canada yield'][i]


oilandmeal = pd.read_csv('cansim0010010.csv', header = 0)
oilandmeal.index = pd.to_datetime(oilandmeal['Ref_Date'])
oilandmeal = oilandmeal.drop(['Ref_Date', 'GEO'], axis = 1)
oilandmealg = oilandmeal.groupby([(oilandmeal.index.year), 'PRO', 'COM']).sum()
oilandmeal = pd.DataFrame(oilandmealg)
oilandmeal.columns = ['Value']

c_seed = oilandmeal.Value.ix[2011, 'Seed crushed', 'Canola (rapeseed)', 'Value']
#c_oil = oilandmeal.Value.ix[2011, 'Oil produced', 'Canola (rapeseed)', 'Value']
c_meal = oilandmeal.Value.ix[2011, 'Meal produced', 'Canola (rapeseed)', 'Value']
canolamealyield = ((c_meal/c_seed)*final_yields['yields used'].ix['Canola'])    #CHECK THIS SHIT!!!
    
soybeanmealyield = 2.005 #2002-2011 average meal/hectare seeded [(from 'Yields - Historic, Crops_2015.07.20.xlsx' 'Soybeans' workbook
pastureyield = 4 #Average SC, SL, PR - 4 tonnes DM/Ha (Wallapak says just use this one)
yieldadditions = pd.DataFrame({'BC yield': ['0', '0', '0'], 'Canada yield': ['0', '0', '0'], 'yields used': [canolamealyield, soybeanmealyield, pastureyield]}, index=['Canola meal', 'Soybean meal', 'Pasture'])
final_yields = final_yields.append(yieldadditions)
#SILAGE = 'Corn, fodder'

as_list = final_yields.index.tolist()
idx1 = as_list.index('Wheat, all')
idx2 = as_list.index('Corn for grain')
idx3 = as_list.index('Peas, dry')
idx4 = as_list.index('Corn, fodder')
as_list[idx1] = 'Wheat'
as_list[idx2] = 'Grain Corn'
as_list[idx3] = 'Dry Peas'
as_list[idx4] = 'Silage'
final_yields.index = as_list


landreqperanimal = pd.DataFrame(feedreqs)
commodity = (landreqperanimal.columns.values)
for i in range(len(commodity)):
    crop = 

#2 - Feed Reqs * Feed Crop Yield = Land Req Per Animal

#3 - Create Commodity/Animal table

#4 - Land Req/Aninal * Commodity/Animal = Land Req/Commodity





















#=================== Junk, Treasures, Dead Ends ==================================================================================
#oilandmeal.g = oilandmeal.groupby(oilandmeal.index.map(lambda x: x.year))
#oilandmeal1 = oilandmeal.groupby(pd.TimeGrouper(freq='M'))

#crops1 = canada_yield.crop.unique()
#crops2 = bc_yield.crop.unique()
#crops3 = total_yield.crop.unique()
#print(crops1)
#print(crops3)

#ten_year_yields = pd.DataFrame.empty(data = None, index = 19, columns = 10)
#ten_year_yields['y1'] = total_yield['BC yield'].loc[2001]


#bc_prod = bc_yield.loc[bc_yield['unit']== 'Production (metric tonnes)']
#ten_year_yields = np.zeros(10)
#crop_names = np.zeros(len(crops))
#crop_means = np.zeros(len(crops))
#for c in range(len(crops)):
#    for y in range(2007, 2017, 1):
#        BCyear_yield = total_yield['BC yield'].loc[y]
#        CAyear_yield = total_yield['Canada yield'].loc[y]
#        
#    crop_names[c] = crops[c]
#    crop_means[c] = ten_year_yields.mean()
#
##veg_table['crop'].loc[(veg_table['crop']== 'Cabbage, Chinese (bok-choy, napa, etcetera)') | (veg_table['crop']== 'Cabbage, regular')] = 'Repeated crop'


#fieldcrops_pivot = fieldcrops.pivot_table(index = 'year', columns = 'unit', values = 'value')
#stacked = fieldcrops.stack()
#unstacked = stacked.unstack()
#unstacked2 = stacked.unstack('unit')
#
#g = fieldcrops.groupby(['geo', 'unit', 'crop'])
#for geo, geo_fieldcrops in g:
#    geo_fieldcrops = geo_fieldcrops.pivot_table(index = ['year', 'crop'], columns= 'unit', values='value')
#    #print(geo)
#    #print(geo_fieldcrops)
#
##g2 = g.pivot_table(index = 'year', columns = 'crop', values = 'value')        
##r = fieldcrops.groupby('unit')['value'].mean()
##print(r)
#p = fieldcrops.stack().unstack('unit')
#p = fieldcrops.pivot(columns='geo', values='value')

#bc_yield2 = bc_yield.pivot(columns='unit', values='value')
#print(fieldcrops.TYP[1990])
#means = df.groubby(industries).mean()
#IF NO DATA FOR BC, USE DATA FOR CANADA

#HEAD OF LIVESTOCK IN SWBC 
#cows = pd.read_csv('cansim0040221.2011.csv', header = 0)
#sheep_lambs = pd.read_csv('cansim0040222.2011.csv', header = 0)
#poultry = pd.read_csv('cansim0040225.2011.csv', header = 0)
#pigs = pd.read_csv('cansim0040223.2011.csv', header = 0)
#pigs.columns = ['Ref_Date', 'GEO', 'LIVE', 'UOM', 'Value']
#frames = [cows, sheep_lambs, poultry, pigs]
#head_livestock = pd.concat(frames, ignore_index = True)
#head_livestock.ix[:, 4] = head_livestock.ix[:, 4].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
#head_livestock = head_livestock.drop(['Ref_Date', 'UOM'], axis = 1).fillna(value=0) #delete reference date column
#head_livestock = head_livestock.groupby('LIVE', as_index=False).sum() 
#head_livestock.columns = ['livestock', 'head']
