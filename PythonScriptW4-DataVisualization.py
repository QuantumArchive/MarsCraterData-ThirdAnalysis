# -*- coding: utf-8 -*-
"""
Created on Tue May 17 20:53:48 2016

@author: Chris
"""
import pandas
import numpy
import seaborn
import matplotlib.pyplot as plt
from IPython.display import display
#%matplotlib inline

#bug fix for display formats to avoid run time errors
pandas.set_option('display.float_format', lambda x:'%f'%x)

#Set Pandas to show all columns in DataFrame
pandas.set_option('display.max_columns', None)
#Set Pandas to show all rows in DataFrame
pandas.set_option('display.max_rows', None)

#data here will act as the data frame containing the Mars crater data
data = pandas.read_csv('D:\\Coursera\\marscrater_pds.csv', low_memory=False)

#convert the latitude and diameter columns to numeric and ejecta morphology is categorical
data['LATITUDE_CIRCLE_IMAGE'] = data['LATITUDE_CIRCLE_IMAGE'].convert_objects(convert_numeric=True)
data['DIAM_CIRCLE_IMAGE'] = data['DIAM_CIRCLE_IMAGE'].convert_objects(convert_numeric=True)
data['MORPHOLOGY_EJECTA_1'] = data['MORPHOLOGY_EJECTA_1'].astype('category')
#Any crater with no designated morphology will be replaced with NaN
data['MORPHOLOGY_EJECTA_1'] = data['MORPHOLOGY_EJECTA_1'].replace(' ',numpy.NaN)

print('This plot shows the distribution of craters based on latitude.')
plotc1 = seaborn.distplot(data['LATITUDE_CIRCLE_IMAGE'],kde=False)
plt.xlabel('Latitude (degrees)')
plt.title('Distribution of Mars Craters by Latitude')

print('This plot shows the distribution of craters based on diameter.')
plotc2 = seaborn.distplot(data['DIAM_CIRCLE_IMAGE'],kde=False)
plt.xlabel('Diameter (km)')
plt.title('Distribution of Mars Craters by Diameter')

print('The diameter data from Mars crater data shows quite a bit of right skew and it makes the plot \
difficult to see. So we will look at the description data and maybe see where we can filter some of \
data out')
    
craterdiamdesc = data['DIAM_CIRCLE_IMAGE'].describe()
print(craterdiamdesc)

print('Because the description shows quite a high standard deviation, one may assume some very big outliers. We will \
use cut to try and see if we can get better granularity of this.')

data['CRATER_DIAM_BIN'] = pandas.cut(data['DIAM_CIRCLE_IMAGE'],[0,5,10,15,20,25,30,35,40,45,50,55,60,1170])

plotc2bin = seaborn.countplot(x='CRATER_DIAM_BIN',data=data)
plt.xlabel('Crater Diameter Bin (km)')
plt.title('Histogram of Mars Craters by Diameter')
plt.xticks(rotation='vertical')

print('This table will be used to filter out craters with diameters greater than 40 km.')
data2 = data[(data['DIAM_CIRCLE_IMAGE'] <= 40)].copy()

print('This plot shows the distribution of craters based on diameter when reducing it craters with a diameter of 40 or less.')
plotc2v2 = seaborn.distplot(data2['DIAM_CIRCLE_IMAGE'],kde=False)
plt.xlabel('Diameter (km)')
plt.title('Distribution of Mars Craters by Diameter')

print('Some crater morphology contains multiple categories that the morphology may fall under. For this study \
we want to limit the data to craters with well defined morphology, i.e. have only one category they fall under.')

#Creating this function to help identify craters with morphology that only fit into one category (i.e. does not have / in the name)
#if the crater morphology fits more then 1 type, we return a 1 else we return a 0
def identifysingletype(cratertype):
    if '/' in cratertype:
        return 1
    else:
        return 0
        
print("We will label and filter out craters that fall in more then one category of morphology in our filtered table data2 \
as well as exclude any craters that don't fall into a specific category.")
data2 = data2.dropna(subset=['MORPHOLOGY_EJECTA_1'])
data2['MORPH_CATEGORY_1'] = data2['MORPHOLOGY_EJECTA_1'].apply(lambda x: identifysingletype(x))
data3 = data2[(data2['MORPH_CATEGORY_1']==0)]

print('Finally we will exclude any craters which have fewer then 10 of a specific single morphology.')
#note there seems to be something odd that carries over from pandas to seaborn so that even though I filter out
#certain rows in the dataframe, they still appear as variables with 0 value in the plot, so this is a workaround
ejectamorphbin = data3.groupby('MORPHOLOGY_EJECTA_1').size()
ejectamorphbin = ejectamorphbin[ejectamorphbin > 10]
summarytable = pandas.DataFrame({'COUNT':ejectamorphbin}).reset_index()
labels = numpy.array(summarytable['MORPHOLOGY_EJECTA_1'])
counts = numpy.array(summarytable['COUNT'])
orderedarray = ['Rd', 'SLEPS', 'SLERS', 'SLEPC', 'SLERC', 'DLERS', 'DLEPS', 'MLERS',
       'DLEPC', 'DLERC', 'SLEPCPd', 'SLEPSPd', 'SLEPd', 'MLEPS', 'SLERSPd']

#print('This plot shows the distribution of crater morphology.')
plotc3 = seaborn.barplot(x=labels,y=counts,order=orderedarray)
plt.xlabel('Crater Morphology Type')
plt.title('Mars Crater Morphology Distribution')
plt.xticks(rotation='vertical')

print('Let us now look at data with only the top 3 morphology types present')

#slice out the rows with just the morphology we want
morphofinterest = ['Rd', 'SLEPS', 'SLERS']
data3['MORPH_OF_INTEREST'] = data3['MORPHOLOGY_EJECTA_1'].apply(lambda x: x in morphofinterest)
data3 = data3.loc[data3['MORPH_OF_INTEREST']==True]

#create a new dataframe with the slice
latitude = numpy.array(data3['LATITUDE_CIRCLE_IMAGE'])
diameter = numpy.array(data3['DIAM_CIRCLE_IMAGE'])
morphology = numpy.array(data3['MORPHOLOGY_EJECTA_1'])
data4 = pandas.DataFrame({'LATITUDE_CIRCLE_IMAGE':latitude,'DIAM_CIRCLE_IMAGE':diameter,'MORPHOLOGY_EJECTA_1':morphology})

#plot out the distribution between crater diameter and latitude for the three types
seaborn.lmplot(x='LATITUDE_CIRCLE_IMAGE',y='DIAM_CIRCLE_IMAGE',data=data4,hue='MORPHOLOGY_EJECTA_1',fit_reg=False)
plt.title('Correlation Between Crater Latitude and Diameter')
plt.xlabel('Crater Latitude (Degrees)')
plt.ylabel('Crater Diameter (km)')

print('We will bin the latitudes into 7 discrete bins of 30 degrees.')
data4['LATITUDE_BIN'] = pandas.cut(data4['LATITUDE_CIRCLE_IMAGE'],[-90,-60,-30,0,30,60,90])

seaborn.factorplot(x='LATITUDE_BIN',y='DIAM_CIRCLE_IMAGE',hue='MORPHOLOGY_EJECTA_1',data=data4)
plt.xlabel('Latitude by Bin (Degrees)')
plt.ylabel('Crater Diameter (km)')
plt.title('Distribution of Martian Crater Diameter by Latitude')
plt.xticks(rotation='vertical')