#!/usr/bin/env python3.6
# Marcos del Cueto
import re
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

### Parameters ###
#nodes=5
#predict=[2018,1,"Leganes","Alaves","Munuera Montero"]
##################



def get_ResultHome(row):
    # transform results from (GoalsHome -- GoalsAway) to {1,0,-1}
    if row['GoalsHome']   < row['GoalsAway']:
        val = -1
    elif row['GoalsHome'] > row['GoalsAway']:
        val = 1
    else:
        val = 0
    return val

def short_TeamNames(row,column):
    # remove F.C., S. D., R. C. D., (x) and similar from name, as well as trailing spaces
    result = re.sub(r'.?[\.]','',row[column]).strip()
    result = re.sub(r'.?[\(.*\)]','',result).strip()
    return result

# Read data
df_results = pd.read_csv('results.csv')
# From X-Y result, transform to {1,0,-1}
df_results['GoalsHome']=df_results['Result'].astype(str).str[0]
df_results['GoalsAway']=df_results['Result'].astype(str).str[4]
df_results['ResultHome']=df_results.apply(get_ResultHome,axis=1)
# Make data uniform: remove special characters and acronyms
for column in ['Stadium','Referee','TeamHome','TeamAway']:
    df_results[column]=df_results[column].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
for column in [['TeamHome'],['TeamAway']]:
    args=column
    df_results[column]=df_results.apply(short_TeamNames,args=args,axis=1)
# Print initial data frame
print('Result:')
#print(df_results[['Season','MatchDay','Time','Stadium','Referee','TeamHome','TeamAway','ResultHome']])
#print(df_results[['Season','MatchDay','Time','Stadium','Referee','TeamHome','TeamAway','ResultHome']].to_string())
print(df_results.to_string())

# Drop unnecessary columns
df_results = df_results.drop('Result',axis = 1)
df_results = df_results.drop('Spectators',axis = 1)
df_results = df_results.drop('Time',axis = 1)
df_results = df_results.drop('Date',axis = 1)
df_results = df_results.drop('YellowCards',axis = 1)
df_results = df_results.drop('RedCards',axis = 1)
df_results = df_results.drop('GoalsHome',axis = 1)
df_results = df_results.drop('GoalsAway',axis = 1)
# Get one hot encoding of columns B
one_hot_TeamHome = pd.get_dummies(df_results['TeamHome'],prefix='TeamHome',sparse=True)
one_hot_TeamAway = pd.get_dummies(df_results['TeamAway'],prefix='TeamAway',sparse=True)
one_hot_Stadium  = pd.get_dummies(df_results['Stadium'], prefix='Stadium', sparse=True)
one_hot_Referee  = pd.get_dummies(df_results['Referee'], prefix='Referee', sparse=True)
# Join the encoded dfs
df_results = df_results.join(one_hot_TeamHome)
df_results = df_results.join(one_hot_TeamAway)
df_results = df_results.join(one_hot_Stadium)
df_results = df_results.join(one_hot_Referee)
print('--- df2 ---')
print(df_results.info())
print(df_results.to_string())




#df_results = pd.DataFrame({'TeamHome'})
#df_results=pd.get_dummies(df_results,prefix=['TeamHome': []])
#print(df_results)




# Dictionary
#dict_teams   = {"Alaves" : 1 ,"Athletic" : 2 ,"Atletico" : 3 ,"Barcelona" : 4 ,"Betis" : 5 ,"Celta" : 6 ,"Deportivo" : 7 ,"Eibar" : 8 ,"Espannol" : 9 ,"Getafe" : 10 ,"Girona" : 11 ,"LasPalmas" : 12 ,"Leganes" : 13 ,"Levante" : 14 ,"Malaga" : 15 ,"RealMadrid" : 16 ,"RealSociedad" : 17 ,"Sevilla" : 18 ,"Valencia" : 19 ,"Villarreal" : 20}
#dict_referee = {"Munuera Montero":1,"Gil Manzano":2,"Mateu Lahoz":3,"Munuera Montero":4,"Hernandez Hernandez":5,"Melero Lopez":6,"Trujillo Suarez":7,"Gonzalez Gonzalez":8,"Alvarez Izquierdo":9,"Medie Jimenez":10}

#df_results['TeamHome']=df_results['TeamHome'].map(dict_teams)
#df_results['TeamAway']=df_results['TeamAway'].map(dict_teams)
#df_results['Referee']=df_results['Referee'].map(dict_referee)


#X=df_results[['Season','MatchDay','TeamHome','TeamAway','Referee']]
#y=df_results['ResultHome']
#print('X:')
#print(X)
#scaler = StandardScaler()
#scaler.fit(X)
#X=scaler.transform(X)
#print('SCALED X:')
#print(X)
#print('y:')
#print(y)


#print('Predict:')
#print('Season:', predict[0], '. MatchDay:', predict[1], '. TeamHome:', predict[2], '. TeamAway:', predict[3], '. Referee:', predict[4])

#for i in range(10):
    #clf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(nodes,nodes))
    #fit_data=clf.fit(X, y)
    #predict2=pd.DataFrame(predict,columns=['predict'])
    #predict2['predict']=predict2['predict'].map(dict_teams).fillna(predict2['predict'])
    #predict2['predict']=predict2['predict'].map(dict_referee).fillna(predict2['predict'])
    #predict2=predict2.T
    #predict2=predict2.rename(columns={0:"Season", 1:"MatchDay", 2:"TeamHome", 3:"TeamAway", 4:"Referee"})
    #predict2=scaler.transform(predict2)
    #result=clf.predict(predict2)
    #result2=clf.predict_proba(predict2)
    #print('ResultsHome:', result2)
    #print('ResultsHome:', result)
