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

cy['crop'].loc[cy['crop']== 'Cherries, sweet'] = 'Cherries'
cy['crop'].loc[cy['crop']== 'Sweet corn'] = 'Corn'
cy['crop'].loc[cy['crop']== 'Shallots and green onions'] = 'Shallots and onions'
cy['crop'].loc[cy['crop']== 'Peaches (fresh and clingstone)'] = 'Peaches'
cy['crop'].loc[cy['crop']== 'Green peas'] = 'Peas'
cy['crop'].loc[cy['crop']== 'Plums and prunes'] = 'Plums'
cy['crop'].loc[cy['crop']== 'Total wheat'] = 'Wheat'
fn['commodity'].loc[fn['commodity']== 'Pineapples canned'] = 'Pineapple canned'
fn['commodity'].loc[fn['commodity']== 'Pineapples fresh'] = 'Pineapple fresh'
fn['commodity'].loc[fn['commodity']== 'Corn flour and meal'] = 'C0rnflour and meal'
fn['commodity'].loc[fn['commodity']== 'Beef and veal, boneless weight'] = 'Beef'
fn['commodity'].loc[fn['commodity']== 'Eggs (15)'] = 'Eggs'
fn['commodity'].loc[fn['commodity']== 'Mutton and lamb, boneless weight'] = 'Lamb'
fn['commodity'].loc[fn['commodity']== 'Pork, boneless weight'] = 'Pork'
fn['commodity'].loc[fn['commodity']== 'Turkey, boneless weight'] = 'Turkey'


#LIVESTOCK YIELD TO SWBC YIELD
#HEAD OF LIVESTOCK IN SWBC 
hec_per_tonne = pd.read_csv('livestockhecpertonne.csv', header = 0)
hec_per_tonne = hec_per_tonne.drop([ 'Pasture', 'Hay', 'GSM', 'Barn', 'Total', 'Hay, Barn, Pasture', 'Class 1-4 Land Portion - With Imports', 'Class 1-4 Land Portion - No Imports', 'headperheci', 'headperhecni', 'Yield(T/ha) - With Imports', 'Yield(T/ha) - Without Imports'], axis = 1) #delete reference date column

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
head_livestock['LIVE'].loc[head_livestock['LIVE']== 'Beef cows'] = 'Beef'
head_livestock['LIVE'].loc[head_livestock['LIVE']== 'Lambs'] = 'Lamb'
head_livestock['LIVE'].loc[head_livestock['LIVE']== 'Grower and finishing pigs'] = 'Pork'
head_livestock['LIVE'].loc[head_livestock['LIVE']== 'Turkeys'] = 'Turkey'
head_livestock['LIVE'].loc[head_livestock['LIVE']== 'Broilers, roasters and Cornish'] = 'Chicken'
head_livestock['LIVE'].loc[head_livestock['LIVE']== 'Dairy cows'] = 'Milk'
head_livestock['LIVE'].loc[head_livestock['LIVE']== 'Laying hens, 19 weeks and over, that produce table eggs'] = 'Eggs'

livestock = pd.merge(left=hec_per_tonne, right = head_livestock, left_on=['Commodity'], right_on =['LIVE'], how = 'inner')
livestock = livestock.drop(['LIVE'], axis =1)
livestock['SWBC yield'] = livestock['headpercommodity - imports']*livestock['Value']
livestock = livestock.drop(['headpercommodity - imports', 'headpercommodity - no imports', 'Value'], axis = 1)
mycy = cy.drop(['Unnamed: 0', 'hectares', 'tonnes', 'value'], axis = 1)
mycy.columns = ['Commodity', 'SWBC yield']
myframes = [livestock, mycy]
newnew = pd.concat(myframes)

#FUZZY STRING MATCHING
fn_copy = np.copy(fn['commodity'])
cy_copy = np.copy(newnew['Commodity'])
fuzzmatch = np.copy(fn_copy)
for i in range(len(fn_copy)):
    match = process.extractOne(fn_copy[i], cy_copy, score_cutoff = 90)
    if match is None:
        fuzzmatch[i] = match
    else:
        fuzzmatch[i] = match[0]
print(fuzzmatch)

fn['commodity'] = fuzzmatch
fn = fn.groupby('commodity', as_index=False).sum() 
cropsr = pd.merge(left=fn, right = newnew, left_on=['commodity'], right_on =['Commodity'], how = 'inner')
cropsr = cropsr.drop([ 'Unnamed: 0', 'kg/person', 'servings/person', 'reference', 'waste', 'conversion', 'tonnes', 'Commodity'], axis = 1) #delete reference date column
cropsr['self reliance'] = (cropsr['SWBC yield']/cropsr['food need'])



















