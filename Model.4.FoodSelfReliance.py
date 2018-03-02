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
fn = fn.drop(['serving'], axis =1)
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

#livestock.loc[livestock['LIVE']== 'Pork', 'SWBC yield'] = 14196.9387
#livestock.loc[livestock['LIVE']== 'Turkey', 'SWBC yield'] = 14557.319
#livestock.loc[livestock['LIVE']== 'Chicken', 'SWBC yield'] = 119486.655
#

livestock = livestock.drop(['commodity_per_head', 'LIVE', 'Value'], axis = 1)
livestock.columns = ['crop', 'SWBC yield']
#livestock = pd.read_csv('livestock.caitlin.csv', header = 0)
cy = cy.drop(['Unnamed: 0', 'date', 'hectares', 'tonnes', 'tonnes_per_hec', 'SWBC hectares planted'], axis = 1)
cy.columns = ['crop','SWBC yield']
cy = cy.append(livestock)

cy.loc[cy['crop']== 'Cherries, sweet', 'crop'] = 'Cherries'
cy.loc[cy['crop']== 'Cherries, sour', 'crop'] = 'Cherries'
cy.loc[cy['crop']== 'Corn, sweet', 'crop'] = 'Corn'
cy.loc[cy['crop']== 'Corn for grain', 'crop'] = 'Corn for flour and meal'
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
fn.loc[fn['commodity']== 'Beef and veal total, boneless weight', 'commodity'] = 'Beef'
fn.loc[fn['commodity']== 'Eggs (15)', 'commodity'] = 'Eggs'
fn.loc[fn['commodity']== 'Mutton and lamb, boneless weight', 'commodity'] = 'Lamb'
fn.loc[fn['commodity']== 'Pork, boneless weight', 'commodity'] = 'Pork'
fn.loc[fn['commodity']== 'Turkey, boneless weight', 'commodity'] = 'Turkey'
fn.loc[fn['commodity']== 'Salad oils (17)', 'commodity'] = 'Salad oils Canola'
fn.loc[fn['commodity']== 'Onions and shallots fresh', 'commodity'] = 'Dry onions'

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
fuzzmatch = pd.DataFrame(fuzzmatch)
fn['cropmatch'] = fuzzmatch
ommited_crops = fn[fn.isnull().any(axis =1)].reset_index(drop =True)

fn = fn.groupby('cropmatch', as_index=False)['SWBC Food Need', 'diet and seasonality constraint'] .sum() 


cropsr = pd.merge(left=fn, right = cy, left_on=['cropmatch'], right_on =['crop'], how = 'outer')
cropsr = cropsr.drop(['crop'], axis = 1) #delete reference date column
#cropsr.columns = ['commodity', 'season', 'percent of group', 'balanced rec(kg)', 'balanced rec (t)', 'incwaste', 'Food Need (t/per)', 'Food Need (t)', 'diet and seasonality constraint', 'SWBC yield (t)']
cropsr['self reliance'] = cropsr['SWBC Food Need']
for i in range(len(cropsr['SWBC Food Need'])):
    mymin = min(cropsr['diet and seasonality constraint'][i], cropsr['SWBC yield'][i])
    cropsr['self reliance'][i] = (mymin /cropsr['SWBC Food Need'][i])*100
    #print(mymin)

mymet = (cropsr['SWBC Food Need']*(cropsr['self reliance']/100))
totalsr = (sum(mymet)/sum(cropsr['SWBC Food Need']))*100
print(totalsr)



                    #TRY to measure SR WITHOUT BALANCING FOOD NEED TO DIETARY RECOMMENDATION
fn2 = pd.read_csv('foodneedresults.2.csv', header = 0)
fn2.loc[fn2['commodity']== 'Apple juice (litres per person, per year)', 'commodity'] = 'Apples juice'
fn2.loc[fn2['commodity']== 'Apple pie filling', 'commodity'] = 'Apples pie filling'
fn2.loc[fn2['commodity']== 'Apple sauce', 'commodity'] = 'Apples sauce'
fn2.loc[fn2['commodity']== 'Pineapples canned', 'commodity'] = 'Pineapple canned'
fn2.loc[fn2['commodity']== 'Pineapples fresh', 'commodity'] = 'Pineapple fresh'
fn2.loc[fn2['commodity']== 'Butter', 'commodity'] = 'Butter milk'
fn2.loc[fn2['commodity']== 'Buttermilk (litres per person, per year)', 'commodity'] = 'Butter milk'
fn2.loc[fn2['commodity']== 'Cottage cheese', 'commodity'] = 'Cottage cheese milk'
fn2.loc[fn2['commodity']== 'Grape juice (litres per person, per year)', 'commodity'] = 'Grapes juice'
fn2.loc[fn2['commodity']== 'Powder buttermilk', 'commodity'] = 'Powder butter milk '
fn2.loc[fn2['commodity']== 'Processed cheese', 'commodity'] = 'Processed cheese milk'
fn2.loc[fn2['commodity']== 'Cheddar cheese', 'commodity'] = 'Cheddar cheese milk'
fn2.loc[fn2['commodity']== 'Concentrated skim milk (litres per person, per year)', 'commodity'] = 'Concentrated skim milk'
fn2.loc[fn2['commodity']== 'Concentrated whole milk (litres per person, per year)', 'commodity'] = 'Concentrated whole milk'
fn2.loc[fn2['commodity']== 'Partly skimmed milk 1% (litres per person, per year)', 'commodity'] = '1% milk'
fn2.loc[fn2['commodity']== 'Partly skimmed milk 2% (litres per person, per year)', 'commodity'] = '2% milk'
fn2.loc[fn2['commodity']== 'Skim milk (litres per person, per year)', 'commodity'] = 'Skim milk'
fn2.loc[fn2['commodity']== 'Standard milk 3.25% (litres per person, per year)', 'commodity'] = 'Standard milk'
fn2.loc[fn2['commodity']== 'Tomato juice (litres per person, per year)', 'commodity'] = 'Tomatoes juice'
fn2.loc[fn2['commodity']== 'Variety cheese', 'commodity'] = 'Variety cheese milk'
fn2.loc[fn2['commodity']== 'Beef and veal total, boneless weight', 'commodity'] = 'Beef'
fn2.loc[fn2['commodity']== 'Eggs (15)', 'commodity'] = 'Eggs'
fn2.loc[fn2['commodity']== 'Mutton and lamb, boneless weight', 'commodity'] = 'Lamb'
fn2.loc[fn2['commodity']== 'Pork, boneless weight', 'commodity'] = 'Pork'
fn2.loc[fn2['commodity']== 'Turkey, boneless weight', 'commodity'] = 'Turkey'
fn2.loc[fn2['commodity']== 'Salad oils (17)', 'commodity'] = 'Salad oils Canola'
fn2.loc[fn2['commodity']== 'Onions and shallots fresh', 'commodity'] = 'Dry onions'

#FUZZY STRING MATCHING
fn2_copy = np.copy(fn2['commodity'])
cy_copy = np.copy(cy['crop'])
fuzzmatch = np.copy(fn2_copy)
for i in range(len(fn2_copy)):
    match = process.extractOne(fn2_copy[i], cy_copy, score_cutoff = 90)
    if match is None:
        fuzzmatch[i] = match
    else:
        fuzzmatch[i] = match[0]
#fuzzmatch = pd.DataFrame(fuzzmatch)
fn2['cropmatch'] = fuzzmatch
#fn2 = fn2.drop(['Unnamed: 0', 'kg/person', 'name', 'serving', 'servings/person', 'reference', 'waste', 'conversion', 'season', 'percent of group', 'balanced rec(kg)', 'balanced rec(t)', 'incwaste', 'Food Need (tonnes)/person'], axis =1)
fn2 = fn2.groupby(['cropmatch', 'group'], as_index=False).sum() 
fn2 = fn2.drop(['Unnamed: 0', 'kg/person', 'servings/person', 'reference', 'waste', 'conversion', 'season', 't/person'], axis =1)
#fn2 = pd.merge(left= fn2g, right=fn2, left_on=['crop match'], right_on=['crop match'], how = 'inner')


cropsr2 = pd.merge(left=fn2, right = cy, left_on=['cropmatch'], right_on =['crop'], how = 'inner')
cropsr2 = cropsr2.drop(['crop'], axis = 1) #delete reference date column
#cropsr2 = cropsr2.append(ommited_crops)
#cropsr2 = cropsr2.fillna(value =0)


#cropsr2.columns = ['commodity', 'season', 'percent of group', 'balanced rec(kg)', 'balanced rec (t)', 'incwaste', 'Food Need (t/per)', 'Food Need (t)', 'diet and seasonality constraint', 'SWBC yield (t)']
cropsr2['self reliance'] = cropsr2['SWBC Food Need']


#mymin = np.minimum(cropsr2['diet and seasonality constraint'][65], cropsr2['SWBC yield'][65])
#cropsr2['self reliance'][65] = (mymin /cropsr2['SWBC Food Need'][65])*100


#mymin = min(cropsr2['diet and seasonality constraint'][3], cropsr2['SWBC yield'][3])
for i in range(len(cropsr2['SWBC Food Need'])):
    mymin = np.minimum(cropsr2['diet and seasonality constraint'][i], cropsr2['SWBC yield'][i])
    cropsr2['self reliance'][i] = (mymin /cropsr2['SWBC Food Need'][i])*100
    #print(mymin)
#cropsr2.loc[is.numeric(cropsr2['SWBC yield']) == False, 'self reliance']
#Problems here!!!!    

plot3 = cropsr2.plot(x='cropmatch', y='self reliance', title = 'Percent Self Reliance by Crop', kind = 'bar')


#WONT WORK BECAUSE DIVIDING BY 0!!!!!!!
#ommited_crops = ommited_crops.drop(['Unnamed: 0', 'kg/person','servings/person', 'name', 'reference', 'waste', 'conversion', 'season', 'percent of group', 'balanced rec(t)', 'balanced rec(kg)', 'incwaste', 't/person', 'cropmatch'], axis = 1)
ommited_crops.columns = ['cropmatch', 'group', 'SWBC Food Need', 'diet and seasonality constraint']

myzeros = pd.DataFrame(np.zeros((len(ommited_crops['cropmatch']))))
ommited_crops['SWBC yield'] = myzeros
ommited_crops['self reliance'] = myzeros
cropsr2 = cropsr2.append(ommited_crops)

mymet2 = (cropsr2['SWBC Food Need']*(cropsr2['self reliance']/100))
totalfoodneed = sum(cropsr2['SWBC Food Need'])
totalsr2 = (sum(mymet2)/totalfoodneed)
print(totalsr2)


grains = cropsr2.loc[cropsr2['group']== 'Grains']
print(grains)
            #group by food group
sr_by_group = cropsr2.groupby('group')['SWBC Food Need', 'diet and seasonality constraint', 'SWBC yield'].sum().reset_index()
sr_by_group['self reliance'] = sr_by_group['SWBC yield']
for i in range(len(sr_by_group['self reliance'])):
    mymin = np.minimum(sr_by_group['diet and seasonality constraint'][i], sr_by_group['SWBC yield'][i])
    sr_by_group['self reliance'][i] = (mymin /sr_by_group['SWBC Food Need'][i])*100

sr_by_group.to_csv('selfreliancebygroup.csv')





sr_by_group = pd.read_csv('selfreliancebygroup.csv', header = 0)
sr_by_group = sr_by_group.drop(['Unnamed: 0', 'diet and seasonality constraint'], axis =1)
plot2= sr_by_group.plot(x='group', y = 'self reliance', kind = 'bar', title = 'Percent Self Reliance')

sr_by_group = sr_by_group.drop(['self reliance'], axis =1)
plot2 = sr_by_group.plot.bar( x= 'group',stacked = True, title = 'Food Need (T) vs Food Production (T)')

plot3 = cropsr2.plot(x='cropmatch', y='self reliance', title = 'Percent Self Reliance by Crop', kind = 'bar')




        #add in dropped crops
#print(sum(mymet))
#print(sum(cropsr['Food Need (t)']))
#differences =pd.DataFrame(mymet).copy()
#differences = differences.append(cropsr['Food Need (t)'])
#differences['dif'] = differences
#cropsr['differences'] = (cropsr['Food Need (t)'] - (cropsr['Food Need (t)']*(cropsr['self reliance']/100)))

                            





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


