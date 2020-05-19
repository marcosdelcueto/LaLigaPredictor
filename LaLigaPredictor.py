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
NLPtimes = 10              # Number of times NLP is run: use large numbers (e.g. 100) to average over random_state
threshold = 0.6             # When final averaged predictions are given: assign N/A if probability is under threshold value
nodes_list = [(120,120)]    # Each tuple contains number of nodes per hidden layer. More than one layer will try them in turn
predict_samples = 10        # Number of samples at the end of data.csv that are predicted
#### END CUSTOMIZABLE PARAMETERS ####

################################################################
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
    # Create list with teams that play in the matches whose outcome we will try to predict
    list_TeamHome = df_results['TeamHome'].values.tolist()[-predict_samples:]
    list_TeamAway = df_results['TeamAway'].values.tolist()[-predict_samples:]
    # Drop unnecessary columns
    lists_columns_to_drop = ['Result','Spectators','TimeHour','TimeMinute','Date','Stadium','YellowCards','RedCards','GoalsHome','GoalsAway','TeamHome','TeamAway','Referee']
    df_results  = drop_columns(df_results,lists_columns_to_drop)
    # Assign descriptors X and target y
    X = df_results.drop('ResultHome',axis = 1)
    y = df_results[['ResultHome']]
    # Call MLP function
    MLP(X,y,list_TeamHome,list_TeamAway)
### End function main
########################

########################
### Start function drop_columns
def drop_columns(df_results,list_columns_to_drop):
    for i in list_columns_to_drop:
        df_results = df_results.drop(i,axis = 1)
    return df_results
### End function drop_columns
########################

########################
### Start function MLP
def MLP(X,y,list_TeamHome,list_TeamAway):
    # Scale Season and Round
    #scaler = StandardScaler().fit(X[['Season','Round']])
    scaler = MinMaxScaler().fit(X[['Season','Round','Time']])
    X[['Season','Round','Time']]=scaler.transform(X[['Season','Round','Time']])
    X = X.drop('Time',axis = 1)
    #print('SCALED X:')
    #print(X)
    #print('y:')
    #print(y)
    print('##################')
    print('## Input values ##')
    print('##################')
    print('NLPtimes:',NLPtimes)
    print('threshold:',threshold)
    print('nodes_list:',nodes_list)
    print('predict_samples:',predict_samples)
    print('##################')
    X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=predict_samples,shuffle=False)
    #print('## Descriptors of matches to predict:')
    #print(X_test)
    new_list_results = []
    list_result = y_test['ResultHome'].values.tolist()
    print('###########################################')
    print('## %i matches outcomes will be predicted ##' %(len(list_result)))
    print('## Real results of these matches         ##')
    print('###########################################')
    for i in range(len(list_result)):
        if list_result[i] ==  1: new_list_results.append(1)
        if list_result[i] ==  0: new_list_results.append('X')
        if list_result[i] == -1: new_list_results.append(2)
        #print(list_TeamHome[i],'---',list_TeamAway[i],':',new_list_results[i])
        print('%20s %3s %20s %2s %1s' %(list_TeamHome[i],'---',list_TeamAway[i],': ',new_list_results[i]))
    #print(new_list_results)
    #print(y_test)
    #print(list_result)
    
    # Start ML
    for nodes in nodes_list:
        print('##########################################################')
        print('## Starting MLP training -- It may take several minutes ##')
        print('##########################################################')
        print('Progress  %.1f%s' %(0.0, '%'))
        progress_count = 1
        accu_per_node=[]
        result_1 = [[] for j in range(len(y_test))] # TeamHome wins
        result_2 = [[] for j in range(len(y_test))] # TeamHome loses
        result_X = [[] for j in range(len(y_test))] # Draw
        for j in range(NLPtimes):
            clf = MLPClassifier(hidden_layer_sizes=(nodes), max_iter=10000, alpha=1e-4, solver='adam',  random_state=None,tol=0.0001)
            clf.fit(X_train, y_train.values.ravel())
            y_pred = clf.predict(X_test)
            #print('j, y_pred:', j, y_pred)
            prog = (j+1)*100/NLPtimes
            if prog >= 10*progress_count:
                print('Progress %.1f%s' %(prog, '%'))
                progress_count = progress_count + 1
            for i in range(len(y_pred)):
                if y_pred[i] ==  1: result_1[i].append(1)
                if y_pred[i] == -1: result_2[i].append(1)
                if y_pred[i] ==  0: result_X[i].append(1)
            accu=accuracy_score(y_test, y_pred)
            accu_per_node.append(accu)
        #print('Nodes: %s. Mean: %.3f. Median: %.3f. Stdev: %.3f' % (str(nodes),statistics.mean(accu_per_node),statistics.median(accu_per_node),statistics.stdev(accu_per_node)))
        #print('')
        print('##################')
        print('###### Bets ######')
        print('##################')
        correct_bets    = 0
        incorrect_bets = 0
        for i in range(len(y_pred)):
            best = 'N/A'
            if sum(result_1[i]) >= sum(result_X[i]) and sum(result_1[i]) >= sum(result_2[i]) and sum(result_1[i])/NLPtimes >= threshold: best = '1'
            if sum(result_X[i]) >= sum(result_1[i]) and sum(result_X[i]) >= sum(result_2[i]) and sum(result_X[i])/NLPtimes >= threshold: best = 'X'
            if sum(result_2[i]) >= sum(result_X[i]) and sum(result_2[i]) >= sum(result_1[i]) and sum(result_2[i])/NLPtimes >= threshold: best = '2'
            #print('TEST best:', best, type(best))
            #print('TEST list_result[i]:', list_result[i], type(list_result[i]))
            if best == '1':
                if list_result[i] == 1:
                    #print('I am correct', best)
                    correct_bets = correct_bets + 1
                else:
                    #print('I am incorrect', best)
                    incorrect_bets = incorrect_bets + 1
            if best == 'X':
                if list_result[i] == 0:
                    #print('I am correct', best)
                    correct_bets = correct_bets + 1
                else:
                    #print('I am incorrect', best)
                    incorrect_bets = incorrect_bets + 1
            if best == '2':
                if list_result[i] == -1:
                    #print('I am correct', best)
                    correct_bets = correct_bets + 1
                else:
                    #print('I am incorrect', best)
                    incorrect_bets = incorrect_bets + 1
            #print('Bet: %s. %s -- %s. %s (1: %.2f. X: %.2f. 2: %.2f)' %(best,list_TeamHome[i],list_TeamAway[i],'\t',sum(result_1[i])/NLPtimes,sum(result_X[i])/NLPtimes,sum(result_2[i])/NLPtimes))
            print('%4s %5s %20s %3s %20s  (1: %.2f. X: %.2f. 2: %.2f)' %('Bet:',best,list_TeamHome[i],'---',list_TeamAway[i],sum(result_1[i])/NLPtimes,sum(result_X[i])/NLPtimes,sum(result_2[i])/NLPtimes))
        #print('#################')
        print('#############################################')
        print('### Analytics with betting threshold %.2f ###' %(threshold))
        print('#############################################')
        print('# Correct bets:', correct_bets)
        print('# Incorrect bets:', incorrect_bets)
        print('# Bet accuracy: %.0f'  %(100*correct_bets/(correct_bets+incorrect_bets)))
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
