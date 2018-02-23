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

cy.loc[cy['crop']== 'Cherries, sweet', 'crop'] = 'Cherries'
cy.loc[cy['crop']== 'Sweet corn', 'crop'] = 'Corn'
cy.loc[cy['crop']== 'Shallots and green onions', 'crop'] = 'Shallots and onions'
cy.loc[cy['crop']== 'Peaches (fresh and clingstone)', 'crop'] = 'Peaches'
cy.loc[cy['crop']== 'Green peas', 'crop'] = 'Peas'
cy.loc[cy['crop']== 'Plums and prunes', 'crop'] = 'Plums'
cy.loc[cy['crop']== 'Total wheat', 'crop'] = 'Wheat'
fn.loc[fn['commodity']== 'Apple sauce', 'commodity'] = 'Apples sauce'
fn.loc[fn['commodity']== 'Pineapples canned', 'commodity'] = 'Pineapple canned'
fn.loc[fn['commodity']== 'Pineapples fresh', 'commodity'] = 'Pineapple fresh'
fn.loc[fn['commodity']== 'Corn flour and meal', 'commodity'] = 'C0rnflour and meal'
fn.loc[fn['commodity']== 'Beef and veal, boneless weight', 'commodity'] = 'Beef'
fn.loc[fn['commodity']== 'Eggs (15)', 'commodity'] = 'Eggs'
fn.loc[fn['commodity']== 'Mutton and lamb, boneless weight', 'commodity'] = 'Lamb'
fn.loc[fn['commodity']== 'Pork, boneless weight', 'commodity'] = 'Pork'
fn.loc[fn['commodity']== 'Turkey, boneless weight', 'commodity'] = 'Turkey'


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
head_livestock.loc[head_livestock['LIVE']== 'Beef cows', 'LIVE'] = 'Beef'
head_livestock.loc[head_livestock['LIVE']== 'Lambs', 'LIVE'] = 'Lamb'
head_livestock.loc[head_livestock['LIVE']== 'Grower and finishing pigs', 'LIVE'] = 'Pork'
head_livestock.loc[head_livestock['LIVE']== 'Turkeys', 'LIVE'] = 'Turkey'
head_livestock.loc[head_livestock['LIVE']== 'Broilers, roasters and Cornish', 'LIVE'] = 'Chicken'
head_livestock.loc[head_livestock['LIVE']== 'Dairy cows', 'LIVE'] = 'Milk'
head_livestock.loc[head_livestock['LIVE']== 'Laying hens, 19 weeks and over, that produce table eggs', 'LIVE'] = 'Eggs'

livestock = pd.merge(left=hec_per_tonne, right = head_livestock, left_on=['Commodity'], right_on =['LIVE'], how = 'inner')
livestock = livestock.drop(['LIVE'], axis =1)
livestock['SWBC yield'] = livestock['headpercommodity - imports']*livestock['Value']
livestock = livestock.drop(['headpercommodity - imports', 'headpercommodity - no imports', 'Value'], axis = 1)
mycy = cy.drop(['Unnamed: 0', 'date', 'hectares', 'tonnes', 'tonnes_per_hec', 'SWBC hectares planted'], axis = 1)
mycy.columns = ['Commodity','SWBC yield']
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
cropsr = cropsr.drop([ 'Unnamed: 0', 'kg/person', 'servings/person', 'reference', 'waste', 'conversion', 'Commodity'], axis = 1) #delete reference date column
cropsr.columns = ['commodity', 'season', 'percent of group', 'balanced rec(kg)', 'balanced rec (t)', 'incwaste', 'Food Need (t/per)', 'Food Need (t)', 'diet and seasonality constraint', 'SWBC yield (t)']
cropsr['self reliance'] = cropsr['Food Need (t)']
for i in range(len(cropsr['Food Need (t)'])):
    mymin = min(cropsr['diet and seasonality constraint'][i], cropsr['SWBC yield (t)'][i])
    cropsr['self reliance'][i] = (mymin /cropsr['Food Need (t)'][i])*100
    #print(mymin)

mymet = (cropsr['Food Need (t)']*(cropsr['self reliance']/100))
totalsr = sum(mymet/cropsr['Food Need (t)'])
print(totalsr)














