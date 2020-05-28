#!/usr/bin/env python3.6
# Marcos del Cueto
import re
import sys
import numpy as np
import pandas as pd
import statistics
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix


csv_file_name = 'database_final.csv'

########################
### Start function get_Month
def get_Month(row):
    month = 0
    #print('test month:', row['Month'].strip(), type (row['Month']))
    if row['Month'].strip() == 'enero':     
        month = 1
    elif row['Month'].strip() == 'febrero':   
        month = 2
    elif row['Month'].strip() == 'marzo':     
        month = 3
    elif row['Month'].strip() == 'abril':     
        month = 4
    elif row['Month'].strip() == 'mayo':      
        month = 5
    elif row['Month'].strip() == 'junio':     
        month = 6
    elif row['Month'].strip() == 'julio':     
        month = 7
    elif row['Month'].strip() == 'agosto':    
        month = 8
    elif row['Month'].strip() == 'septiembre': 
        month = 9
    elif row['Month'].strip() == 'octubre':   
        month = 10
    elif row['Month'].strip() == 'noviembre': 
        month = 11
    elif row['Month'].strip() == 'diciembre': 
        month = 12
    else:
        print('ERROR: not month found')
        sys.exit()
    return month
### End function get_ResultHome
########################

########################
### Start function get_Year
def get_Year(row):
    if row['NewMonth'] <= 7:
        year = row['Season'] + 1
    else:
        year = row['Season']
    return year
### End function get_Year
########################

########################
### Start function get_NewDate
def get_NewDate(row):
    if int(row['Day']) < 10:
        if int(row['NewMonth']) < 10:
            new_date = '0' + str(row['Day'].strip()) + '/' + '0' + str(row['NewMonth']) + '/' + str(row['Year'])
        else:
            new_date = '0' + str(row['Day'].strip()) + '/' + str(row['NewMonth']) + '/' + str(row['Year'])
    else: 
        if int(row['NewMonth']) < 10:
            new_date = str(row['Day'].strip()) + '/' + '0' + str(row['NewMonth']) + '/' + str(row['Year'])
        else:
            new_date = str(row['Day'].strip()) + '/' + str(row['NewMonth']) + '/' + str(row['Year'])
    return new_date
### End function get_NewDate
########################

df_laliga = pd.read_csv('database_laliga.csv')
df_sofifa = pd.read_csv('database_sofifa.csv')
# Transform date from laliga format to more standard sofifa format
df_laliga['Day'] = df_laliga['Date'].str.extract(r'(.*de)').astype(str)
df_laliga['Day'] = df_laliga['Day'].astype(str).str[:-2]
df_laliga['Month'] = df_laliga['Date'].str.extract(r'(de.*)').astype(str)
df_laliga['Month'] = df_laliga['Month'].astype(str).str[3:]
df_laliga['NewMonth'] = df_laliga.apply(get_Month,axis=1)
df_laliga['Year'] = df_laliga.apply(get_Year,axis=1)
df_laliga['NewDate'] = df_laliga.apply(get_NewDate,axis=1)
print(df_laliga[['Date','Day','Month','NewMonth','Year','NewDate']].tail(20))

# Transform Result from laliga to sofifa format
#df_laliga['Result'] = df_laliga['Result'].astype(str).str[0] + df_laliga['Result'].astype(str).str[2] + df_laliga['Result'].astype(str).str[4]
df_laliga['Result'] = df_laliga['Result'].astype(str)
df_laliga['Result'] = df_laliga['Result'].str.replace(' ', '')
#df.columns = df.columns.str.replace(' ', '')
#data_frame_trimmed = data_frame.apply(lambda x: x.str.strip() if x.dtype == "object" else x)



N_laliga = df_laliga.shape[0]
N_sofifa = df_sofifa.shape[0]

print('Number of entries: laliga and sofifa',N_laliga,N_sofifa)


#for n in range(N_sofifa):
    #print(df_sofifa.iloc[[n],[0,1,2,3,4,5]].to_string(header=False))
    #print(df_laliga.iloc[[n],[0,1,16,2,3,4]].to_string(header=False))
    #print('################')

# Update column types:
#df_laliga['Date'] = pd.to_datetime(df_laliga['NewDate'])
#df_sofifa['Date'] = pd.to_datetime(df_sofifa['Date'])
df_laliga['Date'] = df_laliga['NewDate'].astype('string').str.strip()
df_sofifa['Date'] = df_sofifa['Date'].astype('string').str.strip()
df_laliga['TeamHome'] = df_laliga['TeamHome'].astype('string').str.strip()
df_sofifa['TeamHome'] = df_sofifa['TeamHome'].astype('string').str.strip()
df_laliga['Result'] = df_laliga['Result'].astype('string').str.strip()
df_sofifa['Result'] = df_sofifa['Result'].astype('string').str.strip()
df_laliga['TeamAway'] = df_laliga['TeamAway'].astype('string').str.strip()
df_sofifa['TeamAway'] = df_sofifa['TeamAway'].astype('string').str.strip()


print('Type df_laliga',df_laliga.dtypes)
print('Type df_sofifa',df_sofifa.dtypes)


counter = 0
for n in range(N_sofifa):
    print('Match:', n)
    for m in range(N_laliga):
        #if df_sofifa.iloc[[n],[0]] == df_laliga.iloc[[m],[0]] and df_sofifa.iloc[[n],[1]] == df_laliga.iloc[[m],[1]] and df_sofifa.iloc[[n],[2]] == df_laliga.iloc[[m],[16]] and df_sofifa.iloc[[n],[3]] == df_laliga.iloc[[m],[2]] and df_sofifa.iloc[[n],[4]] == df_laliga.iloc[[m],[3]] and df_sofifa.iloc[[n],[5]] == df_laliga.iloc[[m],[4]]:
        d1 = pd.DataFrame(df_sofifa.iloc[[n],[0,1,2,3,4,5]])
        d2 = pd.DataFrame(df_laliga.iloc[[m],[0,1,6,2,3,4]])
        is_same = np.array_equal(d1.values,d2.values)
        #print(df_sofifa.iloc[[n],[0,1,2,3,4,5]])
        #print(df_laliga.iloc[[m],[0,1,6,2,3,4]])
        #print(is_same)
        #print('#############')
        #if n ==50:
            #print('new m', m)
            #print(df_sofifa.iloc[[n],[0,1,2,3,4,5]].to_string(header=False))
            #print(df_laliga.iloc[[m],[0,1,6,2,3,4]].to_string(header=False))
        if is_same == True:
            print('new m', m)
            print(df_sofifa.iloc[[n],[0,1,2,3,4,5]].to_string(header=False))
            print(df_laliga.iloc[[m],[0,1,6,2,3,4]].to_string(header=False))
            #new_dataset = df_sofifa[['Season','Round','Date','TeamHome','Result','TeamAway','Referee','Stadium','PlayersHome','RatingHome','PotentialHome','PlayersAway','RatingAway','PotentialAway']].copy(deep=True)
            #new_dataset['Time'] = df_laliga.iloc['Time']
            if n==0:
                df_new = df_sofifa.iloc[[n],[0,1,2,3,4,5,6,7,8,9,10,11,12,13]]
                df_new['Time'] = df_laliga.iloc[[m],[7]]
                new_dataset = df_sofifa.iloc[[n],[0,1,2,3,4,5,6,7,8,9,10,11,12,13]]
                new_dataset['Time'] = df_laliga.iloc[[m],[7]]
            else:
                #df_new = df_sofifa.iloc[[n],[0,1,2,3,4,5,6,7,8,9,10,11,12,13]]
                df_new = df_sofifa.iloc[[n],[0,1,2,3,4,5,6,7,8,9,10,11,12,13]]
                new_dataset = new_dataset.append(df_new,ignore_index = True)
                #new_dataset.at[n,'Time'] = df_laliga.iloc[[m],[7]]
                #print('time:', df_laliga.iloc[[m],[7]])
                #print('time:', df_laliga.iat[m,7])
                new_dataset.iloc[n,3] = df_laliga.iat[m,7]
            new_dataset = new_dataset[['Season','Round','Date','Time','TeamHome','Result','TeamAway','Referee','Stadium','PlayersHome','RatingHome','PotentialHome','PlayersAway','RatingAway','PotentialAway']]
            #print(new_dataset)
            new_dataset.to_csv (csv_file_name, index = False, header=True)
            #print(new_dataset.to_string())
            #print(is_same)
            #print('#############')
            break


        if m == N_laliga-1:
            print('ERROR: could not find match for', df_sofifa.iloc[[n],[0,1,2,3,4,5]], ' in database_sofifa.csv')
            sys.exit()
