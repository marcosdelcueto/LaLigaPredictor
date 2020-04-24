#!/usr/bin/env python3.6
# Marcos del Cueto
import re
import numpy as np
import pandas as pd
import statistics
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

### START CUSTOMIZABLE PARAMETERS ###
Samples = 100               # Number of times NLP is run: use large numbers (e.g. 100) to average over random_state
threshold = 0.6             # When final averaged predictions are given: assign N/A if probability is under threshold value
nodes_list = [(120,120)]    # Each tuple contains number of nodes per hidden layer. More than one layer will try them in turn
#### END CUSTOMIZABLE PARAMETERS ####

########################
### Start function main
def main():
    # Read data
    df_results = pd.read_csv('data.csv')
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
    # Transform time from HH:MM to HH (float)
    df_results['TimeHour']=df_results['Time'].astype(str).str[0:2].astype(float)
    df_results['TimeMinute']=df_results['Time'].astype(str).str[3:5].astype(float)/60
    df_results['Time']=df_results['TimeHour']+df_results['TimeMinute']
    # Get one hot encoding of columns TeamHome, TeamAway and Referee
    one_hot_TeamHome = pd.get_dummies(df_results['TeamHome'],prefix='TeamHome',sparse=True)
    one_hot_TeamAway = pd.get_dummies(df_results['TeamAway'],prefix='TeamAway',sparse=True)
    one_hot_Referee  = pd.get_dummies(df_results['Referee'], prefix='Referee', sparse=True)
    # Join the encoded dfs to main df
    df_results = df_results.join(one_hot_TeamHome)
    df_results = df_results.join(one_hot_TeamAway)
    df_results = df_results.join(one_hot_Referee)
    # Drop unnecessary columns
    df_results = df_results.drop('Result',axis = 1)
    df_results = df_results.drop('Spectators',axis = 1)
    df_results = df_results.drop('TimeHour',axis = 1)
    df_results = df_results.drop('TimeMinute',axis = 1)
    df_results = df_results.drop('Date',axis = 1)
    df_results = df_results.drop('Stadium',axis = 1)
    df_results = df_results.drop('YellowCards',axis = 1)
    df_results = df_results.drop('RedCards',axis = 1)
    df_results = df_results.drop('GoalsHome',axis = 1)
    df_results = df_results.drop('GoalsAway',axis = 1)
    df_results = df_results.drop('TeamHome',axis = 1)
    df_results = df_results.drop('TeamAway',axis = 1)
    df_results = df_results.drop('Referee',axis = 1)
    # Assign X and y
    X = df_results.drop('ResultHome',axis = 1)
    y = df_results[['ResultHome']]
    # Call MLP function
    MLP(X,y)
### End function main
########################

########################
### Start function MLP
def MLP(X,y):
    # Scale Season and MatchDay
    #scaler = StandardScaler().fit(X[['Season','MatchDay']])
    scaler = MinMaxScaler().fit(X[['Season','MatchDay','Time']])
    X[['Season','MatchDay','Time']]=scaler.transform(X[['Season','MatchDay','Time']])
    X = X.drop('Time',axis = 1)
    #print('SCALED X:')
    #print(X)
    #print('y:')
    #print(y)
    print('##############')
    
    X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=10,shuffle=False)
    print('NEW X_test:')
    print(X_test)
    print('NEW y_test:')
    print(y_test)
    
    # Start ML
    for nodes in nodes_list:
        accu_per_node=[]
        result_1 = [[] for j in range(len(y_test))] # TeamHome wins
        result_0 = [[] for j in range(len(y_test))] # TeamHome loses
        result_X = [[] for j in range(len(y_test))] # Draw
        for j in range(Samples):
            clf = MLPClassifier(hidden_layer_sizes=(nodes), max_iter=10000, alpha=1e-4, solver='adam',  random_state=None,tol=0.0001)
            clf.fit(X_train, y_train.values.ravel())
            y_pred = clf.predict(X_test)
            #print('j, y_pred:', j, y_pred)
            print('Progress %.1f%s' %(j*100/Samples, '%'))
            for i in range(len(y_pred)):
                if y_pred[i] ==  1: result_1[i].append(1)
                if y_pred[i] == -1: result_0[i].append(1)
                if y_pred[i] ==  0: result_X[i].append(1)
            accu=accuracy_score(y_test, y_pred)
            accu_per_node.append(accu)
        for i in range(len(y_pred)):
            best = 'N/A'
            if sum(result_1[i]) >= sum(result_X[i]) and sum(result_1[i]) >= sum(result_0[i]) and sum(result_1[i])/Samples >= threshold: best = '1'
            if sum(result_X[i]) >= sum(result_1[i]) and sum(result_X[i]) >= sum(result_0[i]) and sum(result_X[i])/Samples >= threshold: best = 'X'
            if sum(result_0[i]) >= sum(result_X[i]) and sum(result_0[i]) >= sum(result_1[i]) and sum(result_0[i])/Samples >= threshold: best = '0'
            print('BET: Match %i. Final: %s ## 1: %.2f. X: %.2f. 0: %.2f' %(i,best,sum(result_1[i])/Samples,sum(result_X[i])/Samples,sum(result_0[i])/Samples))
        print('Nodes: %s. Mean: %.3f. Median: %.3f. Stdev: %.3f' % (str(nodes),statistics.mean(accu_per_node),statistics.median(accu_per_node),statistics.stdev(accu_per_node)))
### End function MLP
########################

########################
### Start function get_ResultHome
def get_ResultHome(row):
    # Function to assign victory value wrt local team
    # transform results from (GoalsHome -- GoalsAway) to {1,0,-1}
    if row['GoalsHome']   < row['GoalsAway']:
        val = -1
    elif row['GoalsHome'] > row['GoalsAway']:
        val = 1
    else:
        val = 0
    return val
### End function get_ResultHome
########################

########################
### Start function short_TeamNames
def short_TeamNames(row,column):
    # Function to remove acronyms and brackets
    # remove F.C., S. D., R. C. D., (x) and similar from name, as well as trailing spaces
    result = re.sub(r'.?[\.]','',row[column]).strip()
    result = re.sub(r'.?[\(.*\)]','',result).strip()
    return result
### End function short_TeamNames
########################
################################################################
main()
