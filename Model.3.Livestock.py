#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 13 07:36:50 2018

@author: JFM3
"""

#LIVESTOCK DATA
import pandas as pd

#HEAD OF LIVESTOCK IN SWBC 
cows = pd.read_csv('cansim0040221.2011.csv', header = 0)
sheep_lambs = pd.read_csv('cansim0040222.2011.csv', header = 0)
poultry = pd.read_csv('cansim0040225.2011.csv', header = 0)
pigs = pd.read_csv('cansim0040223.2011.csv', header = 0)
pigs.columns = ['Ref_Date', 'GEO', 'LIVE', 'UOM', 'Value']
frames = [cows, sheep_lambs, poultry, pigs]
head_livestock = pd.concat(frames, ignore_index = True)
head_livestock.ix[:, 4] = head_livestock.ix[:, 4].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
head_livestock = head_livestock.drop(['Ref_Date', 'UOM'], axis = 1).fillna(value=0) #delete reference date column
head_livestock = head_livestock.groupby('LIVE', as_index=False).sum() 
head_livestock.columns = ['livestock', 'head']

feedreqs = pd.read_csv('feedrequirements.csv', header = 0)


#2.1 - FIELD CROPS DATA CLEANING
fieldcrops = pd.read_csv('cansim0010017.dbloading.csv', header = 0)
#fieldcrops2 = pd.read_csv('cansim0010017.tascol.csv', header = 0)
#fieldcrops.index = fieldcrops['Ref_Date']
#fieldcrops = fieldcrops.drop(['Ref_Date'], axis = 1) #delete reference date column
fieldcrops.ix[:, 4] = fieldcrops.ix[:, 4].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
fieldcrops = fieldcrops.dropna(axis=0, how='any').reset_index(drop=True)  #if value is NA, delete that row
fieldcrops.columns = ['year', 'geo', 'unit', 'crop', 'value'] #name first column header 'commodity' and name second column header 'kg/person'

fieldcrops_pivot = fieldcrops.pivot_table(index = 'year', columns = 'unit', values = 'value')

#
#stacked = fieldcrops.stack()
#unstacked = stacked.unstack('unit')
#unstacked = fieldcrops.stack().unstack('unit')

g = fieldcrops.groupby(['geo', 'unit', 'crop'])
for geo, geo_fieldcrops in g:
    print(geo)
    print(geo_fieldcrops)
        
g2 = g.pivot_table(index = 'year', columns = 'crop', values = 'value')    
    
r = fieldcrops.groupby('unit')['value'].mean()
print(r)
#fieldcrops.stack().unstack('GEO')
#p = fieldcrops.pivot(columns='geo', values='value')
bc_yield = fieldcrops.loc[fieldcrops['geo']== 'British Columbia']
#bc_yield = bc_yield.groupby(['year', 'crop'])
canada_yield = fieldcrops.loc[fieldcrops['geo']== 'Canada']
bc_yield = bc_yield.pivot(columns='geo', values='value')
#mean_yield = fieldcrops.groupby([ 'year' ,'crop'], as_index=False)
#print(fieldcrops.TYP[1990])
#means = df.groubby(industries).mean()
#IF NO DATA FOR BC, USE DATA FOR CANADA
#fieldcrops = fieldcrops.drop(['Ref_Date'], axis = 1) #delete reference date column
#fieldcrops.columns = ['geo', 'unit', 'type', 'value'] #name first column header 'commodity' and name second column header 'kg/person'
##cropunits = np.unique(fieldcrops[['unit']].values)
#fieldcrops = pd.DataFrame(data=fieldcrops)
#hectares =fieldcrops.loc[fieldcrops['unit']== 'Seeded area (hectares)']
#tonnes =fieldcrops.loc[fieldcrops['unit']== 'Production (metric tonnes)']
#field_table = pd.merge(left=hectares, right = tonnes, left_on = 'type', right_on = 'type')
#field_table = field_table.drop(['geo_y', 'geo_x', 'unit_x', 'unit_y'], axis = 1).reset_index(drop=True) #delete first three columns
#field_table.ix[:, 1:2] = field_table.ix[:, 1:2].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
#field_table = field_table.dropna(axis=0, how='any').reset_index(drop=True)  #if value is NA, delete that row
#field_table.columns = ['crop', 'hectares', 'tonnes']
#field_table['crop'].loc[field_table['crop']== 'Tame hay'] = 'Tame hay only'
#field_table['crop'].loc[field_table['crop']== 'Wheat, all'] = 'Total wheat'
#
##SWBC LAND AREA
#field_land = pd.read_csv('cansim0040213.2011.2.csv', header = 0)
#field_land.ix[:, 4] = field_land.ix[:, 4].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
#field_land = field_land.drop(['Ref_Date', 'UOM'], axis = 1).fillna(value=0) #delete reference date column
#field_land = field_land.groupby('CROPS', as_index=False).sum() 
#field_land.columns = ['crop','value'] #name first column header 'commodity' and name second column header 'kg/person'
##field_land['crop'].loc[field_land['crop']== 'Total corn'] = 'Corn'
#


