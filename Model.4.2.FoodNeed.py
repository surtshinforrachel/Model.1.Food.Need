#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  3 13:51:20 2018

@author: JFM3
"""

# NEW FOOD NEED
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
head_livestock.loc[head_livestock['LIVE']== 'Broilers, roasters and Cornish', 'LIVE'] = 'Chicken'
head_livestock.loc[head_livestock['LIVE']== 'Dairy cows', 'LIVE'] = 'Dairy'
head_livestock.loc[head_livestock['LIVE']== 'Laying hens, 19 weeks and over, that produce table eggs', 'LIVE'] = 'Eggs'

breeding_stock_chicken_and_eggs = (int(head_livestock.loc[head_livestock['LIVE']== 'Other poultry', 'Value']))+(int(head_livestock.loc[head_livestock['LIVE']== 'Layer and broiler breeders (pullets and hens)', 'Value']))
(head_livestock.loc[head_livestock['LIVE']== 'Chicken', 'Value']) = (int(head_livestock.loc[head_livestock['LIVE']== 'Chicken', 'Value']))+ (breeding_stock_chicken_and_eggs*.1)
(head_livestock.loc[head_livestock['LIVE']== 'Eggs', 'Value']) = (int(head_livestock.loc[head_livestock['LIVE']== 'Eggs', 'Value'])+int(head_livestock.loc[head_livestock['LIVE']== 'Pullets under 19 weeks, intended for laying table eggs', 'Value']))+ (breeding_stock_chicken_and_eggs*.90)

breeding_stock_beef_and_dairy = (int(head_livestock.loc[head_livestock['LIVE']== 'Bulls, 1 year and over', 'Value']))+(int(head_livestock.loc[head_livestock['LIVE']== 'Calves, under 1 year', 'Value']) + (int(head_livestock.loc[head_livestock['LIVE']== 'Total heifers, 1 year and over', 'Value'])))
(head_livestock.loc[head_livestock['LIVE']== 'Beef', 'Value']) = int(head_livestock.loc[head_livestock['LIVE']== 'Beef', 'Value'])+ int(head_livestock.loc[head_livestock['LIVE']== 'Steers, 1 year and over', 'Value']) + int(head_livestock.loc[head_livestock['LIVE']== 'Beef cows', 'Value'])+ (breeding_stock_beef_and_dairy*(.65))
(head_livestock.loc[head_livestock['LIVE']== 'Dairy', 'Value']) = int(head_livestock.loc[head_livestock['LIVE']== 'Dairy', 'Value'])+ (breeding_stock_beef_and_dairy*(.35))

livestock = pd.merge(left=newmethod, right = head_livestock, left_on=['livestock'], right_on =['LIVE'], how = 'inner')
livestock['SWBC yield'] = livestock['commodity_per_head']*livestock['Value']
livestock = livestock.drop(['commodity_per_head', 'LIVE', 'Value'], axis = 1)
livestock.columns = ['crop', 'SWBC yield']


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


                    #With balanced and unbalanced recs
fn3 = pd.read_csv('foodneedresults.3.csv', header = 0)
                 
fn3.loc[fn3['commodity']== 'Apple juice (litres per person, per year)', 'commodity'] = 'Apples juice'
fn3.loc[fn3['commodity']== 'Apple pie filling', 'commodity'] = 'Apples pie filling'
fn3.loc[fn3['commodity']== 'Apple sauce', 'commodity'] = 'Apples sauce'
fn3.loc[fn3['commodity']== 'Pineapples canned', 'commodity'] = 'Pineapple canned'
fn3.loc[fn3['commodity']== 'Pineapples fresh', 'commodity'] = 'Pineapple fresh'
#fn3.loc[fn3['commodity']== 'Butter', 'commodity'] = 'Butter milk'
fn3.loc[fn3['commodity']== 'Buttermilk (litres per person, per year)', 'commodity'] = 'Butter milk'
fn3.loc[fn3['commodity']== 'Cottage cheese', 'commodity'] = 'Cottage cheese milk'
fn3.loc[fn3['commodity']== 'Grape juice (litres per person, per year)', 'commodity'] = 'Grapes juice'
fn3.loc[fn3['commodity']== 'Powder buttermilk', 'commodity'] = 'Powder butter milk '
fn3.loc[fn3['commodity']== 'Processed cheese', 'commodity'] = 'Processed cheese milk'
fn3.loc[fn3['commodity']== 'Cheddar cheese', 'commodity'] = 'Cheddar cheese milk'
fn3.loc[fn3['commodity']== 'Concentrated skim milk (litres per person, per year)', 'commodity'] = 'Concentrated skim milk'
fn3.loc[fn3['commodity']== 'Concentrated whole milk (litres per person, per year)', 'commodity'] = 'Concentrated whole milk'
fn3.loc[fn3['commodity']== 'Partly skimmed milk 1% (litres per person, per year)', 'commodity'] = '1% milk'
fn3.loc[fn3['commodity']== 'Partly skimmed milk 2% (litres per person, per year)', 'commodity'] = '2% milk'
fn3.loc[fn3['commodity']== 'Skim milk (litres per person, per year)', 'commodity'] = 'Skim milk'
fn3.loc[fn3['commodity']== 'Standard milk 3.25% (litres per person, per year)', 'commodity'] = 'Standard milk'
fn3.loc[fn3['commodity']== 'Tomato juice (litres per person, per year)', 'commodity'] = 'Tomatoes juice'
fn3.loc[fn3['commodity']== 'Variety cheese', 'commodity'] = 'Variety cheese milk'
fn3.loc[fn3['commodity']== 'Beef and veal total, boneless weight', 'commodity'] = 'Beef'
fn3.loc[fn3['commodity']== 'Eggs (15)', 'commodity'] = 'Eggs'
fn3.loc[fn3['commodity']== 'Mutton and lamb, boneless weight', 'commodity'] = 'Lamb'
fn3.loc[fn3['commodity']== 'Pork, boneless weight', 'commodity'] = 'Pork'
fn3.loc[fn3['commodity']== 'Turkey, boneless weight', 'commodity'] = 'Turkey'
fn3.loc[fn3['commodity']== 'Onions and shallots fresh', 'commodity'] = 'Dry onions'

fn3.loc[fn3['commodity']== 'Salad oils (17)', 'commodity'] = 'Salad oils Canola Oil'
fn3.loc[fn3['commodity']== 'Shortening and shortening oils', 'commodity'] = 'Shortening Canola Oil'
fn3.loc[fn3['commodity']== 'Margarine', 'commodity'] = 'Margarine Canola Oil'

ommited_crops = fn3.loc[fn3['diet and seasonality constraint (balanced)']==0].reset_index(drop =True)
ommited_crops = ommited_crops.drop(['Unnamed: 0'], axis =1)

fn4 = fn3.copy()
#FUZZY STRING MATCHING
fn3_copy = np.copy(fn3['commodity'])
cy_copy = np.copy(cy['crop'])
fuzzmatch = np.copy(fn3_copy)
for i in range(len(fn3_copy)):
    match = process.extractOne(fn3_copy[i], cy_copy, score_cutoff = 90)
    if match is None:
        fuzzmatch[i] = match
    else:
        fuzzmatch[i] = match[0]
#fuzzmatch = pd.DataFrame(fuzzmatch)
fn3['cropmatch'] = fuzzmatch
#fn3 = fn3.drop(['Unnamed: 0', 'kg/person', 'name', 'serving', 'servings/person', 'reference', 'waste', 'conversion', 'season', 'percent of group', 'balanced rec(kg)', 'balanced rec(t)', 'incwaste', 'Food Need (tonnes)/person'], axis =1)
fn3 = fn3.groupby(['cropmatch', 'group'], as_index=False).sum() 
fn3 = fn3.drop(['Unnamed: 0'], axis =1)







#ERROR CALC
                #SR for 10yr ave crop yield
cy2 = pd.read_csv('cropyieldresults.ave.csv', header = 0)
cy2 = cy2.drop(['Unnamed: 0'], axis = 1)
cy2.columns = ['crop','SWBC yield', 'ave upper', 'ave lower']
livestock['ave lower'] = livestock['SWBC yield']
livestock['ave upper'] = livestock['SWBC yield']
cy2 = cy2.append(livestock).fillna(0)
cy2.loc[cy2['crop']== 'Cherries, sweet', 'crop'] = 'Cherries'
cy2.loc[cy2['crop']== 'Cherries, sour', 'crop'] = 'Cherries'
cy2.loc[cy2['crop']== 'Corn, sweet', 'crop'] = 'Corn'
cy2.loc[cy2['crop']== 'Corn for grain', 'crop'] = 'Corn for flour and meal'
cy2.loc[cy2['crop']== 'Peaches (fresh and clingstone)', 'crop'] = 'Peaches'
cy2.loc[cy2['crop']== 'Peas, green', 'crop'] = 'Peas'
cy2.loc[cy2['crop']== 'Plums and prunes', 'crop'] = 'Plums'
cy2.loc[cy2['crop']== 'Total wheat', 'crop'] = 'Wheat'
cy2.loc[cy2['crop']== 'Rye, all', 'crop'] = 'Rye'
cy2.loc[cy2['crop']== 'Dairy', 'crop'] = 'milk'
cy2.loc[cy2['crop']== 'Fresh tomatoes, greenhouse', 'crop'] = 'Tomatoes'
cy2.loc[cy2['crop']== 'Fresh cucumbers, greenhouse', 'crop'] = 'Cucumbers'
cy2.loc[cy2['crop']== 'Cucumbers and gherkins (all varieties)', 'crop'] = 'Cucumbers'
cy2.loc[cy2['crop']== 'Fresh peppers, greenhouse', 'crop'] = 'Peppers'
cy2 = cy2.groupby('crop')['SWBC yield', 'ave upper', 'ave lower'].sum().reset_index()

#AVE
ave =pd.merge(left =cy, right= cy2, left_on = 'crop', right_on= 'crop')
ave = ave.drop(['SWBC yield_x','ave upper', 'ave lower'], axis =1)
ave.columns = ['crop', 'SWBC yield']
#UPPER
upper =pd.merge(left =cy, right= cy2, left_on = 'crop', right_on= 'crop')
upper = upper.drop(['SWBC yield_x', 'SWBC yield_y', 'ave lower'], axis =1)
upper.columns = ['crop', 'SWBC yield']
#LOWER
lower =pd.merge(left =cy, right= cy2, left_on = 'crop', right_on= 'crop')
lower = lower.drop(['SWBC yield_x', 'SWBC yield_y', 'ave upper'], axis =1)
lower.columns = ['crop', 'SWBC yield']

#cy = ave.copy()

cropsr3 = pd.merge(left=fn3, right = cy, left_on=['cropmatch'], right_on =['crop'], how = 'inner')
cropsr3 = cropsr3.drop(['crop'], axis = 1) #delete reference date column
cropsr3['self reliance (balanced)'] = cropsr3['SWBC Food Need Balanced (t)'].copy()
cropsr3['self reliance (unbalanced)'] = cropsr3['SWBC Food Need Unbalanced (t)'].copy()

for i in range(len(cropsr3['SWBC Food Need Balanced (t)'])):
    mymin = np.minimum(cropsr3['diet and seasonality constraint (balanced)'][i], cropsr3['SWBC yield'][i])
    cropsr3['self reliance (balanced)'][i] = (mymin /cropsr3['SWBC Food Need Balanced (t)'][i])*100

for i in range(len(cropsr3['SWBC Food Need Unbalanced (t)'])):
    mymin = np.minimum(cropsr3['diet and seasonality constraint (unbalanced)'][i], cropsr3['SWBC yield'][i])
    cropsr3['self reliance (unbalanced)'][i] = (mymin /cropsr3['SWBC Food Need Unbalanced (t)'][i])*100

plot3 = cropsr3.plot(x='cropmatch', y='self reliance (balanced)', title = 'Percent Self Reliance by Crop', kind = 'bar')
plot4 = cropsr3.plot(x='cropmatch', y='self reliance (unbalanced)', title = 'Percent Self Reliance by Crop', kind = 'bar')

#ommited_crops = ommited_crops.drop(['Unnamed: 0', 'kg/person','servings/person', 'name', 'reference', 'waste', 'conversion', 'season', 'percent of group', 'balanced rec(t)', 'balanced rec(kg)', 'incwaste', 'Food Need (tonnes)/person', 'cropmatch'], axis = 1)
#ommited_crops.columns = ['cropmatch', 'group', 'SWBC Food Need', 'diet and seasonality constraint']

myzeros = pd.DataFrame(np.zeros((len(ommited_crops['commodity']))))
ommited_crops['SWBC yield'] = myzeros
ommited_crops['self reliance (balanced)'] = myzeros
ommited_crops['self reliance (unbalanced)'] = myzeros
ommited_crops.columns = ['cropmatch', 'group', 'SWBC Food Need Balanced (t)','diet and seasonality constraint (balanced)', 'SWBC Food Need Unbalanced (t)', 'diet and seasonality constraint (unbalanced)', 'SWBC yield','self reliance (balanced)', 'self reliance (unbalanced)']
cropsr3 = cropsr3.append(ommited_crops).reset_index(drop=True)


mymet3 = (cropsr3['SWBC Food Need Balanced (t)']*(cropsr3['self reliance (balanced)']/100))
totalfoodneed = sum(cropsr3['SWBC Food Need Balanced (t)'])
totalsr3_balanced = (sum(mymet3)/totalfoodneed)
print(totalsr3_balanced)

mymet3 = (cropsr3['SWBC Food Need Unbalanced (t)']*(cropsr3['self reliance (unbalanced)']/100))
totalfoodneed = sum(cropsr3['SWBC Food Need Unbalanced (t)'])
totalsr3_unbalanced = (sum(mymet3)/totalfoodneed)
print(totalsr3_unbalanced)


          #group by food group
sr_by_group = cropsr3.groupby('group')['SWBC Food Need Balanced (t)', 'diet and seasonality constraint (balanced)','SWBC Food Need Unbalanced (t)', 'diet and seasonality constraint (unbalanced)', 'SWBC yield'].sum().reset_index()
sr_by_group['self reliance (balanced)'] = sr_by_group['SWBC yield'].copy()
for i in range(len(sr_by_group['self reliance (balanced)'])):
    mymin = np.minimum(sr_by_group['diet and seasonality constraint (balanced)'][i], sr_by_group['SWBC yield'][i])
    sr_by_group['self reliance (balanced)'][i] = (mymin /sr_by_group['SWBC Food Need Balanced (t)'][i])*100

          #group by food group
sr_by_group['self reliance (unbalanced)'] = sr_by_group['SWBC yield'].copy()
for i in range(len(sr_by_group['self reliance (unbalanced)'])):
    mymin = np.minimum(sr_by_group['diet and seasonality constraint (unbalanced)'][i], sr_by_group['SWBC yield'][i])
    sr_by_group['self reliance (unbalanced)'][i] = (mymin /sr_by_group['SWBC Food Need Unbalanced (t)'][i])*100

plot2= sr_by_group.plot(x='group', y = 'self reliance (balanced)', kind = 'bar', title = 'Percent Self Reliance')
plot2 = sr_by_group.plot.bar( x= 'group',stacked = True, title = 'Food Need (T) vs Food Production (T)')
plot3 = cropsr3.plot(x='cropmatch', y='self reliance (balanced)', title = 'Percent Self Reliance by Crop', kind = 'bar')
















