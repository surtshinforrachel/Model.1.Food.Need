#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 12:58:52 2017

@author: JFM3
"""
#check location of working directory
import os
cwd = os.getcwd()
print(cwd)
import pandas as pd
import numpy as np

#AVAILABILITY DATA CLEANING
avail = pd.read_csv('cansim0020011.csv', header = 0)
avail = avail.drop(['Geography', 'Food categories'], axis = 1) #delete first three columns
avail.columns = ['commodity', 'kg/person'] #name first column header 'commodity' and name second column header 'kg/person'
avail.ix[:, 1] = avail.ix[:, 1].apply(pd.to_numeric, errors = 'coerce') #turn everything in values column into a numeric. if it won't do it coerce it into an NaN
avail = avail.dropna(axis=0, how='any')  #if value is NA, delete that row
avail['commodity'] = avail['commodity'].astype(str) #turn all commodities to strings
ommit_list = [ "Sugar refined", "Maple sugar", "Honey", "Dry", "Tea", "Coffee", "Cocoa", "Ale", "Distilled", "Wines", "Soft", "Bottled", "Cider", "whey", "Sweetened", "Milkshake", "cream", "Sherbert", "Ice milk", "drink", "stewing", "Chicken, boneless weight", "Stewing hen, boneless weight", "Beef and veal", "Other fresh berries", "musk", "Other fresh melons", "Watermelons", "Wintermelons", "Quinces", "Fruits not specified", "Oranges fresh", "Lemons fresh", "Grapefruits fresh", "Limes fresh", "Mandarins fresh", "Other citrus fresh", "Chinese cabbage", "Other edible roots fresh", "leguminous", "Olives fresh", "Potatoes chips", "Potatoes total", "Potatoes white fresh and processed", "Vegetables not specified", 'Guavas']
avail = avail[~avail['commodity'].str.contains('|'.join(ommit_list))] #remove every row for which column 1 contains strings from caitlyn's list
insufficient_data = ['Tree nuts', 'Melons total fresh', 'Kiwis', 'Nectarines', 'Artichokes', 'Eggplant', 'Kohlrabi', 'Garlic', 'Leeks', 'Okra', 'Parsley', 'Parsnips', 'Rappini']
avail = avail[~avail['commodity'].str.contains('|'.join(insufficient_data))] #remove every row for which column 1 contains strings from the commodities without sufficent units data
#print(avail)

#POPULATION DATA CLEANING
pop = pd.read_csv('cansim0510062.2016.csv', header = 0)
pop = pop.drop(['Ref_Date'], axis = 1) #delete date column
#pop = pop.pivot(columns = 'GEO', values = 'value') #pivot table so that it is indexed by age group and columns correspond to region      index = 'AGE'
#age_order = ['0 to 4 years', '5 to 9 years', '10 to 14 years', '15 to 19 years', '20 to 24 years', '25 to 29 years', '30 to 34 years', '35 to 39 years', '40 to 44 years', '45 to 49 years', '50 to 54 years', '55 to 59 years', '60 to 64 years', '65 to 69 years', '70 to 74 years', '75 to 79 years', '80 to 84 years', '85 to 89 years', '90 years and over']
#pop = pop.reindex(age_order) #indexing by age messes with the order of the age brackets so we have to farmer style them back into order.
pop.columns = ['geo', 'sex', 'age', 'value']

# extract int from every cell in 'age' column
pop_group = np.array(pop['age'])
for i in range(len(pop['age'])):
    pop_group[i] = int((pop['age'][i]).split()[0])
    #pop['age'][i] = pop_group[i]     
#print(pop_group)                   #SETTING WITH COPY WARNING -MUST RESOLVE!
#print(pop.groupby(['geo', 'sex', 'age_group']).sum())

#DIETARY RECOMMENDATION CLEANING
rec = pd.read_csv('diet.csv', header = 0)
rec = rec.pivot(index = 'Age', columns = 'Food Group', values = 'Servings/Year')
rec.columns = ['Fats&Oils','Fruit&Veg', 'Grains', 'Meat&Alt', 'Milk&Alt']
#UNITS TABLE
units = pd.read_csv('units.csv', header = 0)

#RENAME ROWS THAT WILL BE COMBINED
avail.loc[avail['commodity']== 'Breakfast food','commodity'] = 'Oatmeal and rolled oats'
avail.loc[(avail['commodity']== 'Beef, boneless weight') | (avail['commodity']== 'Veal, boneless weight') ,'commodity'] = 'Beef and veal, boneless weight'
avail.loc[(avail['commodity']== 'Broccoli frozen (5)') | (avail['commodity']== 'Cauliflower frozen') ,'commodity'] = 'Broccoli & Cauliflower frozen'
avail.loc[(avail['commodity']== 'Baked and canned beans') | (avail['commodity']== 'Lima beans frozen') ,'commodity'] = 'Baked and canned beans and lima beans'
#COMBINE ROWS WITH THE SAME 'commodity' NAME
avail_new = avail.groupby('commodity', as_index=False).sum() 

#MERGE avail AND units TABLES 
#merged_left = pd.merge(left=survey_sub,right=species_sub, how='left', left_on='species_id', right_on='species_id')
big_table = pd.merge(left=avail_new, right=units, left_on='commodity', right_on='Food Name (CANSIM Adjusted for waste)') #took out , how='outer' for inner join showing only matched rows
big_table.columns = ['commodity', 'kg/person', 'name', 'group', 'serving', 'reference', 'waste', 'conversion', 'season' ] #name first column header 'commodity' and name second column header 'value'
big_table['servings/person'] = (big_table['kg/person']*1000) / (big_table['reference'])
big_table = big_table[['commodity', 'kg/person', 'servings/person', 'name', 'group', 'serving', 'reference', 'waste', 'conversion', 'season']]

#RESULTS TABLE
total_pop = sum(pop['value'])
quantity_foods = (np.array(avail['kg/person'])) * (total_pop)

#PERCENT OF GROUP THAT EACH COMMODITY IS
groups = np.array(big_table['group'])
for i in range(len(groups)):
    grp = (groups[i])
    group_sum = sum(big_table[big_table['group']== grp ]['kg/person'])
    percent_of_group = np.array(big_table['kg/person'])/ (group_sum)
    #print(percent_of_group)
sum(percent_of_group)

# CREATE DIETARY REC FOR EVERY AGE GIVEN IN THE POPULATION DATA
pop['Fruit&Veg'] = np.array(pop['sex'])
pop['Grains'] = np.array(pop['sex'])
pop['Milk&Alt'] = np.array(pop['sex'])
pop['Meat&Alt'] = np.array(pop['sex'])
pop['Fats&Oils'] = np.array(pop['sex'])

for i in range(len(pop_group)):
    if pop_group[i] < 2:
        pop.loc[[i], 'Fruit&Veg'] = 0
        pop.loc[[i], 'Grains'] = 0
        pop.loc[[i], 'Milk&Alt'] = 0
        pop.loc[[i], 'Meat&Alt'] = 0
        pop.loc[[i], 'Fats&Oils'] = 0
    if (pop_group[i] >= 2) & (pop_group[i] <=3):
        pop.loc[[i], 'Fruit&Veg'] = int(rec.loc['2 to 3', 'Fruit&Veg'])
        pop.loc[[i], 'Grains'] = int(rec.loc['2 to 3', 'Grains'])
        pop.loc[[i], 'Milk&Alt'] = int(rec.loc['2 to 3', 'Milk&Alt'])
        pop.loc[[i], 'Meat&Alt'] = int(rec.loc['2 to 3', 'Meat&Alt'])
        pop.loc[[i], 'Fats&Oils'] = int(rec.loc['2 to 3', 'Fats&Oils'])
    if (pop_group[i] >= 4) & (pop_group[i] <=8):
        pop.loc[[i], 'Fruit&Veg'] = int(rec.loc['4 to 8 ', 'Fruit&Veg'])
        pop.loc[[i], 'Grains'] = int(rec.loc['4 to 8 ', 'Grains'])
        pop.loc[[i], 'Milk&Alt'] = int(rec.loc['4 to 8 ', 'Milk&Alt'])
        pop.loc[[i], 'Meat&Alt'] = int(rec.loc['4 to 8 ', 'Meat&Alt'])
        pop.loc[[i], 'Fats&Oils'] = int(rec.loc['4 to 8 ', 'Fats&Oils'])
    if (pop_group[i] >= 9) & (pop_group[i] <=13):
        pop.loc[[i], 'Fruit&Veg'] = int(rec.loc['9 to 13', 'Fruit&Veg'])
        pop.loc[[i], 'Grains'] = int(rec.loc['9 to 13', 'Grains'])
        pop.loc[[i], 'Milk&Alt'] = int(rec.loc['9 to 13', 'Milk&Alt'])
        pop.loc[[i], 'Meat&Alt'] = int(rec.loc['9 to 13', 'Meat&Alt'])
        pop.loc[[i], 'Fats&Oils'] = int(rec.loc['9 to 13', 'Fats&Oils'])
    if (pop_group[i] >= 14) & (pop_group[i] <=18) & (pop['sex'][i] == 'Females'):
        pop.loc[[i], 'Fruit&Veg'] = int(rec.loc['Female (14-18)', 'Fruit&Veg'])
        pop.loc[[i], 'Grains'] = int(rec.loc['Female (14-18)', 'Grains'])
        pop.loc[[i], 'Milk&Alt'] = int(rec.loc['Female (14-18)', 'Milk&Alt'])
        pop.loc[[i], 'Meat&Alt'] = int(rec.loc['Female (14-18)', 'Meat&Alt'])
        pop.loc[[i], 'Fats&Oils'] = int(rec.loc['Female (14-18)', 'Fats&Oils'])
    if (pop_group[i] >= 14) & (pop_group[i] <=18) & (pop['sex'][i] == 'Males'):
        pop.loc[[i], 'Fruit&Veg'] = int(rec.loc['Male (14-18)', 'Fruit&Veg'])
        pop.loc[[i], 'Grains'] = int(rec.loc['Male (14-18)', 'Grains'])
        pop.loc[[i], 'Milk&Alt'] = int(rec.loc['Male (14-18)', 'Milk&Alt'])
        pop.loc[[i], 'Meat&Alt'] = int(rec.loc['Male (14-18)', 'Meat&Alt'])
        pop.loc[[i], 'Fats&Oils'] = int(rec.loc['Male (14-18)', 'Fats&Oils'])
    if (pop_group[i] >= 19) & (pop_group[i] <=50) & (pop['sex'][i] == 'Females'):
        pop.loc[[i], 'Fruit&Veg'] = int(rec.loc['Females (19-50)', 'Fruit&Veg'])
        pop.loc[[i], 'Grains'] = int(rec.loc['Females (19-50)', 'Grains'])
        pop.loc[[i], 'Milk&Alt'] = int(rec.loc['Females (19-50)', 'Milk&Alt'])
        pop.loc[[i], 'Meat&Alt'] = int(rec.loc['Females (19-50)', 'Meat&Alt'])
        pop.loc[[i], 'Fats&Oils'] = int(rec.loc['Females (19-50)', 'Fats&Oils'])
    if (pop_group[i] >= 19) & (pop_group[i] <=50) & (pop['sex'][i] == 'Males'):
        pop.loc[[i], 'Fruit&Veg'] = int(rec.loc['Males (19-50)', 'Fruit&Veg'])
        pop.loc[[i], 'Grains'] = int(rec.loc['Males (19-50)', 'Grains'])
        pop.loc[[i], 'Milk&Alt'] = int(rec.loc['Males (19-50)', 'Milk&Alt'])
        pop.loc[[i], 'Meat&Alt'] = int(rec.loc['Males (19-50)', 'Meat&Alt'])
        pop.loc[[i], 'Fats&Oils'] = int(rec.loc['Males (19-50)', 'Fats&Oils'])
    if (pop_group[i] >= 51) & (pop['sex'][i] == 'Females'):
        pop.loc[[i], 'Fruit&Veg'] = int(rec.loc['Females (51+)', 'Fruit&Veg'])
        pop.loc[[i], 'Grains'] = int(rec.loc['Females (51+)', 'Grains'])
        pop.loc[[i], 'Milk&Alt'] = int(rec.loc['Females (51+)', 'Milk&Alt'])
        pop.loc[[i], 'Meat&Alt'] = int(rec.loc['Females (51+)', 'Meat&Alt'])
        pop.loc[[i], 'Fats&Oils'] = int(rec.loc['Females (51+)', 'Fats&Oils'])
    if (pop_group[i] >= 51) & (pop['sex'][i] == 'Males'):
        pop.loc[[i], 'Fruit&Veg'] = int(rec.loc['Males (51+)', 'Fruit&Veg'])
        pop.loc[[i], 'Grains'] = int(rec.loc['Males (51+)', 'Grains'])
        pop.loc[[i], 'Milk&Alt'] = int(rec.loc['Males (51+)', 'Milk&Alt'])
        pop.loc[[i], 'Meat&Alt'] = int(rec.loc['Males (51+)', 'Meat&Alt'])
        pop.loc[[i], 'Fats&Oils'] = int(rec.loc['Males (51+)', 'Fats&Oils'])

#FIND RECOMMENDATION FOR AVERAGE PERSON IN SWBC IN SERVINGS - IS TAKING THE AVERAGE RECOMMENDATION QUANTITATIVELY SOUND IN THIS CASE?
allrecs = np.zeros(shape=(5,1))
allrecs[0] = sum((np.array(pop['value'])) * (np.array(pop['Fats&Oils'])))/(total_pop)
allrecs[1] = sum((np.array(pop['value'])) * (np.array(pop['Fruit&Veg'])))/(total_pop)
allrecs[2] = sum((np.array(pop['value'])) * (np.array(pop['Grains'])))/(total_pop)
allrecs[3] = sum((np.array(pop['value'])) * (np.array(pop['Meat&Alt'])))/(total_pop)
allrecs[4] = sum((np.array(pop['value'])) * (np.array(pop['Milk&Alt'])))/(total_pop)

#SUM servings/person BY GROUP, GIVING A TOTAL NUMBER OF AVAILABLE SERVINGS OF FOOD PER PERSON PER FOOD GROUP
big_table_groups = big_table.groupby('group', as_index=False).sum() 
avail_by_group = np.array(big_table_groups['servings/person']) 

percent_food_group_rec_met = np.array(big_table_groups['servings/person'])
for i in range(len(big_table_groups['servings/person'])):
    percent_food_group_rec_met[i] = ((allrecs[i]/avail_by_group[i]))
percent_food_group_rec_met = pd.DataFrame({'group': big_table_groups['group'],'percent':percent_food_group_rec_met}) #ADD THE FOOD GROUP LABEL TO THE percent_food_group_rec_met

#TO BALANCE AVAILABILITY WITH FOOD NEED WE MUST ONLY USE THE PERCENT_FOOD_GROUP_REC_MET >1. DOING IT MANUALLY HERE... WOULD BE BEST TO AUTOMATE
#recperfood IS THE AMOUNT OF SERVINGS OF THE FOOD NEEDED FOR AVERAGE INDIVIDUAL IN THE RECOMMENDED DIET
recperfood = np.array(big_table['kg/person'])
for i in range(len(big_table['kg/person'])):
    if (big_table['group'][i] == 'Fats and Oils'):
        recperfood[i] = 1 * (big_table['kg/person'][i])   
    if (big_table['group'][i] == 'Fruit & Vegetables'):
        recperfood[i] = (percent_food_group_rec_met['percent'][1]) * (big_table['kg/person'][i])      
    if (big_table['group'][i] == 'Grains'):
        recperfood[i] = 1 * (big_table['kg/person'][i])
    if (big_table['group'][i] == 'Meat & Alts'):
        recperfood[i] = (percent_food_group_rec_met['percent'][3]) * (big_table['kg/person'][i])        
    if (big_table['group'][i] == 'Milk & Alts'):
        recperfood[i] = (percent_food_group_rec_met['percent'][4]) * (big_table['kg/person'][i])           
print(recperfood)

tonnesfood = np.array(recperfood)
for i in range(len(recperfood)):
    tonnesfood[i] = (recperfood[i]) * 1000
    
incwaste = np.multiply(tonnesfood, np.array(big_table['waste']))
foodneed = np.multiply(incwaste, np.array(big_table['conversion']))