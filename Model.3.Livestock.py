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
#feedreqs.index = feedreqs['Livestock Type']
#feedreqs = feedreqs.drop(['Livestock Type'], axis =1)
feedreqs = feedreqs.transpose()
feedreqs.columns = feedreqs.iloc[0]
feedreqs = feedreqs.reindex(feedreqs.index.drop('Livestock Type'))

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
years = np.array([2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011])
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
c_meal = oilandmeal.Value.ix[2011, 'Meal produced', 'Canola (rapeseed)', 'Value']
canolamealyield = ((c_meal/c_seed)*final_yields['yields used'].ix['Canola'])    #CHECK THIS SHIT!!!
    
soybeanmealyield = 2.005 #2002-2011 average meal/hectare seeded [(from 'Yields - Historic, Crops_2015.07.20.xlsx' 'Soybeans' workbook
pastureyield = 4.2 #Average SC, SL, PR - 4 tonnes DM/Ha (Wallapak says just use this one)
yieldadditions = pd.DataFrame({'BC yield': ['0', '0', '0'], 'Canada yield': ['0', '0', '0'], 'yields used': [canolamealyield, soybeanmealyield, pastureyield]}, index=['Canola Meal', 'Soybean Meal', 'Pasture'])
final_yields = final_yields.append(yieldadditions)

as_list = final_yields.index.tolist()
idx1 = as_list.index('Wheat, all')
idx2 = as_list.index('Corn for grain')
idx3 = as_list.index('Peas, dry')
idx4 = as_list.index('Tame hay')
idx5 = as_list.index('Corn, fodder') #SILAGE = 'Corn, fodder'
as_list[idx1] = 'Wheat'
as_list[idx2] = 'Grain Corn'
as_list[idx3] = 'Dry Peas'
as_list[idx4] = 'Hay'
as_list[idx5] = 'Silage'
final_yields.index = as_list

##2 - Feed Reqs * Feed Crop Yield = Land Req Per Animal
feedreqs = feedreqs.join(final_yields['yields used'])    
feedreqs = feedreqs.transpose()
landreqperanimal = pd.DataFrame.copy(feedreqs)
commodity = (landreqperanimal.columns.values)
for i in range(len(commodity)):
    landreqperanimal[commodity[i]] = (landreqperanimal[commodity[i]].astype(float))/final_yields['yields used'].loc[commodity[i]]
landreqperanimal = landreqperanimal.drop('yields used', axis =0)
landreqperanimal['GSM'] = landreqperanimal['Wheat'] + landreqperanimal['Oats'] + landreqperanimal['Barley'] + landreqperanimal['Grain Corn'] + landreqperanimal['Dry Peas'] + landreqperanimal['Soybean Meal'] + landreqperanimal['Canola Meal'] + landreqperanimal['Silage'] 

# Land Req/Aninal * Commodity/Animal = Land Req/Commodity
meatperanimal = pd.read_csv('meat_per_animal.csv', header = 0, index_col = 'Meat')
milkeggsperanimal = pd.read_csv('milk&eggs_per_animal.csv', header = 0, index_col = 'Unit')
barnarea = pd.read_csv('barnarea.csv', header = 0, index_col = 'Livestock Type')
hec_per_tonne = pd.read_csv('areapercommodity.csv', header = 0, index_col = 'Commodity')      

#Milk and Eggs
milk_prodarea_p = landreqperanimal.Pasture.ix['Dairy cows']
milk_rearingarea_p = (landreqperanimal.Pasture.ix['Dairy calves <1 yr'] + (1.2*landreqperanimal.Pasture.ix['Dairy Heifers > 1 yr']))
hec_per_tonne.Pasture.ix['Milk'] = ((milk_prodarea_p + (milk_rearingarea_p/milkeggsperanimal.Dairy.ix['N years of commodity production'])) /milkeggsperanimal.Dairy.ix['Tonnes/commodity/animal/year']) 

milk_prodarea_h = landreqperanimal.Hay.ix['Dairy cows']
milk_rearingarea_h = (landreqperanimal.Hay.ix['Dairy calves <1 yr'] + (1.2*landreqperanimal.Hay.ix['Dairy Heifers > 1 yr']))
hec_per_tonne.Hay.ix['Milk'] = ((milk_prodarea_h + (milk_rearingarea_h/milkeggsperanimal.Dairy.ix['N years of commodity production'])) /milkeggsperanimal.Dairy.ix['Tonnes/commodity/animal/year']) 

milk_prodarea_gsm = landreqperanimal.GSM.ix['Dairy cows']
milk_rearingarea_gsm = (landreqperanimal.GSM.ix['Dairy calves <1 yr'] + (1.2*landreqperanimal.GSM.ix['Dairy Heifers > 1 yr']))
hec_per_tonne.GSM.ix['Milk'] = ((milk_prodarea_gsm + (milk_rearingarea_gsm/milkeggsperanimal.Dairy.ix['N years of commodity production'])) /milkeggsperanimal.Dairy.ix['Tonnes/commodity/animal/year']) 

eggs_prodarea_gsm = landreqperanimal.GSM.ix['Layers ']
eggs_rearingarea_gsm = ((landreqperanimal.GSM.ix['Layers '] * milkeggsperanimal.Eggs.ix['Rearing period']) /milkeggsperanimal.Eggs.ix['N years of commodity production'])
hec_per_tonne.GSM.ix['Eggs'] = ((eggs_prodarea_gsm + (eggs_rearingarea_gsm/milkeggsperanimal.Eggs.ix['N years of commodity production'])) /milkeggsperanimal.Eggs.ix['Tonnes/commodity/animal/year']) 

#MEAT
beef_rearingarea_p = (((landreqperanimal.Pasture.ix['Slaughter calves']*meatperanimal.Beef.ix['noffspring'])+landreqperanimal.Pasture.ix['Beef cows '])/meatperanimal.Beef.ix['noffspring'])
beef_only_p = ((landreqperanimal.Pasture.ix['Steers & Heifer Slaughter']/12)*4)
hec_per_tonne.Pasture.ix['Beef'] = ((beef_rearingarea_p + beef_only_p + (meatperanimal.Beef.ix['Fr']*(beef_rearingarea_p+beef_only_p))) / (meatperanimal.Beef.ix['Wo'] +(meatperanimal.Beef.ix['Fr']*meatperanimal.Beef.ix['Wb'])))

beef_rearingarea_h = (((landreqperanimal.Hay.ix['Slaughter calves']*meatperanimal.Beef.ix['noffspring'])+landreqperanimal.Hay.ix['Beef cows '])/meatperanimal.Beef.ix['noffspring'])
beef_only_h = ((landreqperanimal.Hay.ix['Steers & Heifer Slaughter']/12)*4)
hec_per_tonne.Hay.ix['Beef'] = ((beef_rearingarea_h + beef_only_h + (meatperanimal.Beef.ix['Fr']*(beef_rearingarea_p+beef_only_h))) / (meatperanimal.Beef.ix['Wo'] +(meatperanimal.Beef.ix['Fr']*meatperanimal.Beef.ix['Wb'])))

beef_rearingarea_gsm = (((landreqperanimal.GSM.ix['Slaughter calves']*meatperanimal.Beef.ix['noffspring'])+landreqperanimal.GSM.ix['Beef cows '])/meatperanimal.Beef.ix['noffspring'])
beef_only_gsm = ((landreqperanimal.GSM.ix['Steers & Heifer Slaughter']/12)*4)
hec_per_tonne.GSM.ix['Beef'] = ((beef_rearingarea_gsm + beef_only_gsm + (meatperanimal.Beef.ix['Fr']*(beef_rearingarea_gsm+beef_only_gsm))) / (meatperanimal.Beef.ix['Wo'] +(meatperanimal.Beef.ix['Fr']*meatperanimal.Beef.ix['Wb'])))

lamb_rearingarea_p = (((landreqperanimal.Pasture.ix['Slaughter lambs']*meatperanimal.Lamb.ix['noffspring'])+landreqperanimal.Pasture.ix['Rams & Ewes'])/meatperanimal.Lamb.ix['noffspring'])
hec_per_tonne.Pasture.ix['Lamb'] = ((lamb_rearingarea_p + (meatperanimal.Lamb.ix['Fr']*lamb_rearingarea_p)) / (meatperanimal.Lamb.ix['Wo'] +(meatperanimal.Lamb.ix['Fr']*meatperanimal.Lamb.ix['Wb'])))

lamb_rearingarea_h = (((landreqperanimal.Hay.ix['Slaughter lambs']*meatperanimal.Lamb.ix['noffspring'])+landreqperanimal.Hay.ix['Rams & Ewes'])/meatperanimal.Lamb.ix['noffspring'])
hec_per_tonne.Hay.ix['Lamb'] = ((lamb_rearingarea_h + (meatperanimal.Lamb.ix['Fr']*lamb_rearingarea_h)) / (meatperanimal.Lamb.ix['Wo'] +(meatperanimal.Lamb.ix['Fr']*meatperanimal.Lamb.ix['Wb'])))

lamb_rearingarea_gsm = (((landreqperanimal.GSM.ix['Slaughter lambs']*meatperanimal.Lamb.ix['noffspring'])+landreqperanimal.GSM.ix['Rams & Ewes'])/meatperanimal.Lamb.ix['noffspring'])
hec_per_tonne.GSM.ix['Lamb'] = ((lamb_rearingarea_gsm + (meatperanimal.Lamb.ix['Fr']*lamb_rearingarea_gsm)) / (meatperanimal.Lamb.ix['Wo'] +(meatperanimal.Lamb.ix['Fr']*meatperanimal.Lamb.ix['Wb'])))

pork_rearingarea_gsm = (((landreqperanimal.GSM.ix['Feeder Pigs']*meatperanimal.Pork.ix['noffspring'])+landreqperanimal.GSM.ix['Sows & Bred Gilts'])/meatperanimal.Pork.ix['noffspring'])
hec_per_tonne.GSM.ix['Pork'] = ((pork_rearingarea_gsm + (meatperanimal.Pork.ix['Fr']*pork_rearingarea_gsm)) / (meatperanimal.Pork.ix['Wo'] +(meatperanimal.Pork.ix['Fr']*meatperanimal.Pork.ix['Wb'])))

turkey_rearingarea_gsm = (((landreqperanimal.GSM.ix['Turkeys']*meatperanimal.Turkey.ix['noffspring'])+landreqperanimal.GSM.ix['Turkeys'])/meatperanimal.Turkey.ix['noffspring'])
hec_per_tonne.GSM.ix['Turkey'] = ((turkey_rearingarea_gsm + (meatperanimal.Turkey.ix['Fr']*turkey_rearingarea_gsm)) / (meatperanimal.Turkey.ix['Wo'] +(meatperanimal.Turkey.ix['Fr']*meatperanimal.Turkey.ix['Wb'])))

chicken_rearingarea_gsm = (((landreqperanimal.GSM.ix['Broilers']*meatperanimal.Chicken.ix['noffspring'])+landreqperanimal.GSM.ix['Broilers'])/meatperanimal.Chicken.ix['noffspring'])
hec_per_tonne.GSM.ix['Chicken'] = ((chicken_rearingarea_gsm + (meatperanimal.Chicken.ix['Fr']*chicken_rearingarea_gsm)) / (meatperanimal.Chicken.ix['Wo'] +(meatperanimal.Chicken.ix['Fr']*meatperanimal.Chicken.ix['Wb'])))
print(landreqperanimal.GSM.ix['Broilers'])
print(hec_per_tonne.GSM.ix['Chicken'])
print(chicken_rearingarea_gsm)
print((meatperanimal.Chicken.ix['Wo'] +(meatperanimal.Chicken.ix['Fr']*meatperanimal.Chicken.ix['Wb'])))
print(meatperanimal.Chicken.ix['noffspring'])
#CHICKEN GSM VALUE IS .67 instead of .87!!!!!!!!!!!!! all other values are correct


#BARN AREA
beef_rearingarea_barn = (((barnarea.ba.ix['Beef - offspring']*meatperanimal.Beef.ix['noffspring'])+barnarea.ba.ix['Beef - breeder'])/meatperanimal.Beef.ix['noffspring'])
beef_only_barn = (barnarea.ba.ix['Beef - offspring'])
hec_per_tonne.Barn.ix['Beef'] = ((beef_rearingarea_barn + beef_only_barn + (meatperanimal.Beef.ix['Fr']*(beef_rearingarea_barn+beef_only_barn))) / (meatperanimal.Beef.ix['Wo'] +(meatperanimal.Beef.ix['Fr']*meatperanimal.Beef.ix['Wb'])))

lamb_rearingarea_barn = (((barnarea.ba.ix['Lamb - offspring']*meatperanimal.Lamb.ix['noffspring'])+barnarea.ba.ix['Lamb - breeder'])/meatperanimal.Lamb.ix['noffspring'])
hec_per_tonne.Barn.ix['Lamb'] = ((lamb_rearingarea_barn + (meatperanimal.Lamb.ix['Fr']*lamb_rearingarea_barn)) / (meatperanimal.Lamb.ix['Wo'] +(meatperanimal.Lamb.ix['Fr']*meatperanimal.Lamb.ix['Wb'])))

pork_rearingarea_barn = (((barnarea.ba.ix['Pig - offspring']*meatperanimal.Pork.ix['noffspring'])+barnarea.ba.ix['Pig - breeder'])/meatperanimal.Pork.ix['noffspring'])
hec_per_tonne.Barn.ix['Pork'] = (((pork_rearingarea_barn + (meatperanimal.Pork.ix['Fr']*pork_rearingarea_barn)) / (meatperanimal.Pork.ix['Wo'] +(meatperanimal.Pork.ix['Fr']*meatperanimal.Pork.ix['Wb']))) * meatperanimal.Pork.ix['Lifespan of animal'])

turkey_rearingarea_barn = (((barnarea.ba.ix['Turkey']*meatperanimal.Turkey.ix['noffspring'])+barnarea.ba.ix['Turkey'])/meatperanimal.Turkey.ix['noffspring'])
hec_per_tonne.Barn.ix['Turkey'] = (((turkey_rearingarea_barn + (meatperanimal.Turkey.ix['Fr']*turkey_rearingarea_barn)) / (meatperanimal.Turkey.ix['Wo'] +(meatperanimal.Turkey.ix['Fr']*meatperanimal.Turkey.ix['Wb']))) * meatperanimal.Turkey.ix['Lifespan of animal'])

chicken_rearingarea_barn = (((barnarea.ba.ix['Broiler']*meatperanimal.Chicken.ix['noffspring'])+barnarea.ba.ix['Broiler'])/meatperanimal.Chicken.ix['noffspring'])
hec_per_tonne.Barn.ix['Chicken'] = (((chicken_rearingarea_barn + (meatperanimal.Chicken.ix['Fr']*chicken_rearingarea_barn)) / (meatperanimal.Chicken.ix['Wo'] +(meatperanimal.Chicken.ix['Fr']*meatperanimal.Chicken.ix['Wb']))) * meatperanimal.Chicken.ix['Lifespan of animal'])
#CHICKEN BARN VALUE IS .00032 instead of .00041!!!!!!!!!!!!! all other values are correct

hec_per_tonne.Barn.ix['Milk'] = (((barnarea.ba.ix['Dairy cow']/milkeggsperanimal.Dairy.ix['N years of commodity production']) + barnarea.ba.ix['Dairy cow']) / milkeggsperanimal.Dairy.ix['Tonnes/commodity/animal/year'])

hec_per_tonne.Barn.ix['Eggs'] = ((barnarea.ba.ix['Layer']+((barnarea.ba.ix['Layer']*milkeggsperanimal.Eggs.ix['Rearing period'])/milkeggsperanimal.Eggs.ix['N years of commodity production']))/milkeggsperanimal.Eggs.ix['Tonnes/commodity/animal/year'])



hec_per_tonne['Total'] = hec_per_tonne['Pasture'] + hec_per_tonne['Hay'] + hec_per_tonne['GSM'] + hec_per_tonne['Barn']
hec_per_tonne['Hay, Barn, Pasture'] = hec_per_tonne['Pasture'] + hec_per_tonne['Hay'] + hec_per_tonne['Barn']
hec_per_tonne['Class 1-4 Land Portion - No Imports'] = ((hec_per_tonne['GSM'] + hec_per_tonne['Hay'])/ hec_per_tonne['Total'])
hec_per_tonne['Class 1-4 Land Portion - With Imports'] = (hec_per_tonne['Hay']/ (hec_per_tonne['Hay']+hec_per_tonne['Pasture']+hec_per_tonne['Barn']))
hec_per_tonne['Yield(T/ha) - With Imports'] = (1/(hec_per_tonne['Pasture'] + hec_per_tonne['Hay'] + hec_per_tonne['Barn']))
hec_per_tonne['Yield(T/ha) - Without Imports'] = (1/(hec_per_tonne['Total']))

meatperanimal.ix['Yt'] = (meatperanimal.ix['Wo']+(meatperanimal.ix['Fr']*meatperanimal.ix['Wb']))


#print(meatperanimal['Beef'])
hec_per_tonne['headperheci'] = (hec_per_tonne['Yield(T/ha) - With Imports'])
hec_per_tonne.headperheci.ix['Beef'] = (1/((hec_per_tonne.headperheci.ix['Beef'])*(meatperanimal.Beef.ix['Yt'])))
hec_per_tonne.headperheci.ix['Lamb'] = (1/((hec_per_tonne.headperheci.ix['Lamb'])*(meatperanimal.Lamb.ix['Yt'])))
hec_per_tonne.headperheci.ix['Pork'] = (1/((hec_per_tonne.headperheci.ix['Pork'])*(meatperanimal.Pork.ix['Yt'])))
hec_per_tonne.headperheci.ix['Turkey'] = (1/((hec_per_tonne.headperheci.ix['Turkey'])*(meatperanimal.Turkey.ix['Yt'])))
hec_per_tonne.headperheci.ix['Chicken'] = (1/((hec_per_tonne.headperheci.ix['Chicken'])*(meatperanimal.Chicken.ix['Yt'])))
hec_per_tonne.headperheci.ix['Milk'] = (1/((hec_per_tonne.headperheci.ix['Milk'])*(milkeggsperanimal.Dairy.ix['Tonnes/commodity/animal/year'])))
hec_per_tonne.headperheci.ix['Eggs'] = (1/((hec_per_tonne.headperheci.ix['Eggs'])*(milkeggsperanimal.Eggs.ix['Tonnes/commodity/animal/year'])))


hec_per_tonne['headperhecni'] = (hec_per_tonne['Yield(T/ha) - Without Imports'])
hec_per_tonne.headperhecni.ix['Beef'] = (1/((hec_per_tonne.headperhecni.ix['Beef'])*(meatperanimal.Beef.ix['Yt'])))
hec_per_tonne.headperhecni.ix['Lamb'] = (1/((hec_per_tonne.headperhecni.ix['Lamb'])*(meatperanimal.Lamb.ix['Yt'])))
hec_per_tonne.headperhecni.ix['Pork'] = (1/((hec_per_tonne.headperhecni.ix['Pork'])*(meatperanimal.Pork.ix['Yt'])))
hec_per_tonne.headperhecni.ix['Turkey'] = (1/((hec_per_tonne.headperhecni.ix['Turkey'])*(meatperanimal.Turkey.ix['Yt'])))
hec_per_tonne.headperhecni.ix['Chicken'] = (1/((hec_per_tonne.headperhecni.ix['Chicken'])*(meatperanimal.Chicken.ix['Yt'])))
hec_per_tonne.headperhecni.ix['Milk'] = (1/((hec_per_tonne.headperhecni.ix['Milk'])*(milkeggsperanimal.Dairy.ix['Tonnes/commodity/animal/year'])))
hec_per_tonne.headperhecni.ix['Eggs'] = (1/((hec_per_tonne.headperhecni.ix['Eggs'])*(milkeggsperanimal.Eggs.ix['Tonnes/commodity/animal/year'])))

hec_per_tonne['headpercommodity - imports'] = ((1/hec_per_tonne['Yield(T/ha) - With Imports'])*hec_per_tonne['headperheci'])
hec_per_tonne['headpercommodity - no imports'] = ((1/hec_per_tonne['Yield(T/ha) - Without Imports'])*hec_per_tonne['headperhecni'])
#ERROR - NO DIFFERENCE BETWEEN IMPORTS AND NO IMPORTS RESULTS
hec_per_tonne.to_csv('livestockhecpertonne.csv')



#hec_per_tonne.headperhec.ix['Beef'] = (1/((hec_per_tonne.headperhec.ix['Beef'])*(meatperanimal.Beef.ix['Yt'])))
#
#
#
#

#
#
#
#
#
#
#
#
#
#hec_per_tonne['head/hec - Without Imports'] = (1/(hec_per_tonne['Pasture'] + hec_per_tonne['Hay'] + hec_per_tonne['Barn']))
#hec_per_tonne.to_csv('livestockhecpertonne.csv')






#             #MEAT   
#        
#feedlist = ['GrainHaySilage', 'Pasture', 'Hay']
#
#for feed in feedlist:        
#    beef_offspring_p = landreqperanimal.feed.ix['Slaughter calves']
#    beef_breeder_p = landreqperanimal.feed.ix['Beef cows']
#    beef_offspring_area_p = ((((beef_offspring_p*meatperanimal.noffspring.ix['Beef']) + beef_breeder_p)/meatperanimal.noffspring.ix['Beef']) + ((beef_offspring_p/12)*4))
#    beef_area = (beef_offspring_area_p)+(meatperanimal.Fr.ix['Beef']*beef_offspring_area_p) / (meatperanimal.Wo.ix['Beef'] + (meatperanimal.Fr.ix['Beef'] * meatperanimal.Wb.ix['Beef']))
#    hec_per_tonne.feed.ix['Beef'] = beef_area
#
#
#commodities_list = ['beef', 'lamb', 'pork', 'turkey', 'chicken', 'milk', 'eggs']
#for i in range(len(commodities_list)):
#    barnarea
#
##REVIEW
#    #MAKE UNTIS  CLEAR
#    #MAKE SURE that all the yields are actually what they are supposed to be
#


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

