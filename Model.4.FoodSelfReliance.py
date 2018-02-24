#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 16:13:27 2018

@author: JFM3
"""


import pandas as pd
import numpy as np
from fuzzywuzzy import process

#MATCH CROPS TO COMMODITIES
fn = pd.read_csv('foodneedresults.csv', header = 0)
cy = pd.read_csv('cropyieldresults.csv', header = 0)

                            #Livestock Redo
newmethod = pd.read_csv('livestock.newmethod.csv', header = 0)
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
head_livestock.loc[head_livestock['LIVE']== 'Total cattle and calves', 'LIVE'] = 'Beef'
head_livestock.loc[head_livestock['LIVE']== 'Total sheep and lambs', 'LIVE'] = 'Lamb'
head_livestock.loc[head_livestock['LIVE']== 'Total pigs', 'LIVE'] = 'Pork'
head_livestock.loc[head_livestock['LIVE']== 'Turkeys', 'LIVE'] = 'Turkey'
head_livestock.loc[head_livestock['LIVE']== 'Total hens and chickens', 'LIVE'] = 'Chicken'
head_livestock.loc[head_livestock['LIVE']== 'Total cows', 'LIVE'] = 'Dairy'
head_livestock.loc[head_livestock['LIVE']== 'Laying hens, 19 weeks and over, that produce table eggs', 'LIVE'] = 'Eggs'


livestock = pd.merge(left=newmethod, right = head_livestock, left_on=['livestock'], right_on =['LIVE'], how = 'inner')
livestock['SWBC yield'] = livestock['commodity_per_head']*livestock['Value']
livestock = livestock.drop(['commodity_per_head', 'LIVE', 'Value'], axis = 1)
livestock.columns = ['crop', 'SWBC yield']
cy = cy.drop(['Unnamed: 0', 'date', 'hectares', 'tonnes', 'tonnes_per_hec', 'SWBC hectares planted'], axis = 1)
cy.columns = ['crop','SWBC yield']
cy = cy.append(livestock)

cy.loc[cy['crop']== 'Cherries, sweet', 'crop'] = 'Cherries'
cy.loc[cy['crop']== 'Corn, sweet', 'crop'] = 'Corn'
cy.loc[cy['crop']== 'Shallots and green onions', 'crop'] = 'Shallots and onions'
cy.loc[cy['crop']== 'Peaches (fresh and clingstone)', 'crop'] = 'Peaches'
cy.loc[cy['crop']== 'Peas, green', 'crop'] = 'Peas'
cy.loc[cy['crop']== 'Plums and prunes', 'crop'] = 'Plums'
cy.loc[cy['crop']== 'Total wheat', 'crop'] = 'Wheat'
cy.loc[cy['crop']== 'Rye, all', 'crop'] = 'Rye'
cy.loc[cy['crop']== 'Dairy', 'crop'] = 'milk'
cy.loc[cy['crop']== 'Fresh tomatoes, greenhouse', 'crop'] = 'Tomatoes'
cy.loc[cy['crop']== 'Fresh cucumbers, greenhouse', 'crop'] = 'Cucumbers'
cy.loc[cy['crop']== 'Cucumbers and gherkins (all varieties)', 'crop'] = 'Cucumbers'
cy.loc[cy['crop']== 'Fresh peppers, greenhouse', 'crop'] = 'Peppers'

cy = cy.groupby('crop')['SWBC yield'].sum().reset_index()

fn.loc[fn['commodity']== 'Apple juice (litres per person, per year)', 'commodity'] = 'Apples juice'
fn.loc[fn['commodity']== 'Apple pie filling', 'commodity'] = 'Apples pie filling'
fn.loc[fn['commodity']== 'Apple sauce', 'commodity'] = 'Apples sauce'
fn.loc[fn['commodity']== 'Pineapples canned', 'commodity'] = 'Pineapple canned'
fn.loc[fn['commodity']== 'Pineapples fresh', 'commodity'] = 'Pineapple fresh'
fn.loc[fn['commodity']== 'Butter', 'commodity'] = 'Butter milk'
fn.loc[fn['commodity']== 'Buttermilk (litres per person, per year)', 'commodity'] = 'Butter milk'
fn.loc[fn['commodity']== 'Cottage cheese', 'commodity'] = 'Cottage cheese milk'
fn.loc[fn['commodity']== 'Grape juice (litres per person, per year)', 'commodity'] = 'Grapes juice'
fn.loc[fn['commodity']== 'Powder buttermilk', 'commodity'] = 'Powder butter milk '
fn.loc[fn['commodity']== 'Processed cheese', 'commodity'] = 'Processed cheese milk'
fn.loc[fn['commodity']== 'Cheddar cheese', 'commodity'] = 'Cheddar cheese milk'
fn.loc[fn['commodity']== 'Concentrated skim milk (litres per person, per year)', 'commodity'] = 'Concentrated skim milk'
fn.loc[fn['commodity']== 'Concentrated whole milk (litres per person, per year)', 'commodity'] = 'Concentrated whole milk'
fn.loc[fn['commodity']== 'Partly skimmed milk 1% (litres per person, per year)', 'commodity'] = '1% milk'
fn.loc[fn['commodity']== 'Partly skimmed milk 2% (litres per person, per year)', 'commodity'] = '2% milk'
fn.loc[fn['commodity']== 'Skim milk (litres per person, per year)', 'commodity'] = 'Skim milk'
fn.loc[fn['commodity']== 'Standard milk 3.25% (litres per person, per year)', 'commodity'] = 'Standard milk'
fn.loc[fn['commodity']== 'Tomato juice (litres per person, per year)', 'commodity'] = 'Tomatoes juice'
fn.loc[fn['commodity']== 'Variety cheese', 'commodity'] = 'Variety cheese milk'
fn.loc[fn['commodity']== 'Beef and veal, boneless weight', 'commodity'] = 'Beef'
fn.loc[fn['commodity']== 'Eggs (15)', 'commodity'] = 'Eggs'
fn.loc[fn['commodity']== 'Mutton and lamb, boneless weight', 'commodity'] = 'Lamb'
fn.loc[fn['commodity']== 'Pork, boneless weight', 'commodity'] = 'Pork'
fn.loc[fn['commodity']== 'Turkey, boneless weight', 'commodity'] = 'Turkey'
fn.loc[fn['commodity']== 'Turkey, boneless weight', 'commodity'] = 'Turkey'

#DO GREENHOUSE CROPS
#                            #Livestock Redo
#newmethod = pd.read_csv('livestock.newmethod.csv', header = 0)
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
#head_livestock.loc[head_livestock['LIVE']== 'Total cattle and calves', 'LIVE'] = 'Beef'
#head_livestock.loc[head_livestock['LIVE']== 'Total sheep and lambs', 'LIVE'] = 'Lamb'
#head_livestock.loc[head_livestock['LIVE']== 'Total pigs', 'LIVE'] = 'Pork'
#head_livestock.loc[head_livestock['LIVE']== 'Turkeys', 'LIVE'] = 'Turkey'
#head_livestock.loc[head_livestock['LIVE']== 'Total hens and chickens', 'LIVE'] = 'Chicken'
#head_livestock.loc[head_livestock['LIVE']== 'Total cows', 'LIVE'] = 'Dairy'
#head_livestock.loc[head_livestock['LIVE']== 'Laying hens, 19 weeks and over, that produce table eggs', 'LIVE'] = 'Eggs'

#livestock = pd.merge(left=newmethod, right = head_livestock, left_on=['livestock'], right_on =['LIVE'], how = 'inner')
#livestock['SWBC yield'] = livestock['commodity_per_head']*livestock['Value']
#livestock = livestock.drop(['commodity_per_head', 'LIVE', 'Value'], axis = 1)
#livestock.columns = ['Commodity', 'SWBC yield']
#cy = cy.drop(['Unnamed: 0', 'date', 'hectares', 'tonnes', 'tonnes_per_hec', 'SWBC hectares planted'], axis = 1)
#cy.columns = ['Commodity','SWBC yield']
#cy = cy.append(livestock)

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
#fuzzmatch = pd.DataFrame(fuzzmatch)
fn['crop match'] = fuzzmatch
#fn = fn.drop(['Unnamed: 0', 'kg/person', 'name', 'serving', 'servings/person', 'reference', 'waste', 'conversion', 'season', 'percent of group', 'balanced rec(kg)', 'balanced rec(t)', 'incwaste', 'Food Need (tonnes)/person'], axis =1)
fn = fn.groupby('crop match', as_index=False)['SWBC Food Need (tonnes)', 'diet and seasonality constraint'] .sum() 


cropsr = pd.merge(left=fn, right = cy, left_on=['crop match'], right_on =['crop'], how = 'inner')
cropsr = cropsr.drop(['crop'], axis = 1) #delete reference date column
#cropsr.columns = ['commodity', 'season', 'percent of group', 'balanced rec(kg)', 'balanced rec (t)', 'incwaste', 'Food Need (t/per)', 'Food Need (t)', 'diet and seasonality constraint', 'SWBC yield (t)']
cropsr['self reliance'] = cropsr['SWBC Food Need (tonnes)']
for i in range(len(cropsr['SWBC Food Need (tonnes)'])):
    mymin = min(cropsr['diet and seasonality constraint'][i], cropsr['SWBC yield'][i])
    cropsr['self reliance'][i] = (mymin /cropsr['SWBC Food Need (tonnes)'][i])*100
    #print(mymin)

mymet = (cropsr['SWBC Food Need (tonnes)']*(cropsr['self reliance']/100))
totalsr = (sum(mymet)/sum(cropsr['SWBC Food Need (tonnes)']))*100
print(totalsr)

print(sum(mymet))
print(sum(cropsr['Food Need (t)']))

differences =pd.DataFrame(mymet).copy()
differences = differences.append(cropsr['Food Need (t)'])
differences['dif'] = differences


cropsr['differences'] = (cropsr['Food Need (t)'] - (cropsr['Food Need (t)']*(cropsr['self reliance']/100)))







#LIVESTOCK YIELD TO SWBC YIELD
##HEAD OF LIVESTOCK IN SWBC 
#hec_per_tonne = pd.read_csv('livestockhecpertonne.csv', header = 0)
#hec_per_tonne = hec_per_tonne.drop([ 'Pasture', 'Hay', 'GSM', 'Barn', 'Total', 'Hay, Barn, Pasture', 'Class 1-4 Land Portion - With Imports', 'Class 1-4 Land Portion - No Imports', 'headperheci', 'headperhecni', 'Yield(T/ha) - With Imports', 'Yield(T/ha) - Without Imports'], axis = 1) #delete reference date column
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
#head_livestock.loc[head_livestock['LIVE']== 'Beef cows', 'LIVE'] = 'Beef'
#head_livestock.loc[head_livestock['LIVE']== 'Lambs', 'LIVE'] = 'Lamb'
#head_livestock.loc[head_livestock['LIVE']== 'Grower and finishing pigs', 'LIVE'] = 'Pork'
#head_livestock.loc[head_livestock['LIVE']== 'Turkeys', 'LIVE'] = 'Turkey'
#head_livestock.loc[head_livestock['LIVE']== 'Broilers, roasters and Cornish', 'LIVE'] = 'Chicken'
#head_livestock.loc[head_livestock['LIVE']== 'Dairy cows', 'LIVE'] = 'Milk'
#head_livestock.loc[head_livestock['LIVE']== 'Laying hens, 19 weeks and over, that produce table eggs', 'LIVE'] = 'Eggs'
#
#livestock = pd.merge(left=hec_per_tonne, right = head_livestock, left_on=['Commodity'], right_on =['LIVE'], how = 'inner')
#livestock = livestock.drop(['LIVE'], axis =1)
#livestock['SWBC yield'] = livestock['headpercommodity - imports']*livestock['Value']
#livestock = livestock.drop(['headpercommodity - imports', 'headpercommodity - no imports', 'Value'], axis = 1)


