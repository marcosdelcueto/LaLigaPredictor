#!/usr/bin/env python3.6
# Marcos del Cueto
import re
import numpy as np
import pandas as pd
import statistics
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

##### START FUNCTIONS #####
# Function to assign victory value wrt local team
def get_ResultHome(row):
    # transform results from (GoalsHome -- GoalsAway) to {1,0,-1}
    if row['GoalsHome']   < row['GoalsAway']:
        val = -1
    elif row['GoalsHome'] > row['GoalsAway']:
        val = 1
    else:
        val = 0
    return val
# Function to remove acronyms and brackets
def short_TeamNames(row,column):
    # remove F.C., S. D., R. C. D., (x) and similar from name, as well as trailing spaces
    result = re.sub(r'.?[\.]','',row[column]).strip()
    result = re.sub(r'.?[\(.*\)]','',result).strip()
    return result
###### END FUNCTIONS ######
# Read data
df_results = pd.read_csv('train.csv')
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
#print('Result:')
#print(df_results[['Season','MatchDay','TeamHome','TeamAway','ResultHome','Referee']].to_string())


# Get one hot encoding of columns B
one_hot_TeamHome = pd.get_dummies(df_results['TeamHome'],prefix='TeamHome',sparse=True)
one_hot_TeamAway = pd.get_dummies(df_results['TeamAway'],prefix='TeamAway',sparse=True)
#one_hot_Stadium  = pd.get_dummies(df_results['Stadium'], prefix='Stadium', sparse=True)
one_hot_Referee  = pd.get_dummies(df_results['Referee'], prefix='Referee', sparse=True)
# Join the encoded dfs
df_results = df_results.join(one_hot_TeamHome)
df_results = df_results.join(one_hot_TeamAway)
#df_results = df_results.join(one_hot_Stadium)
df_results = df_results.join(one_hot_Referee)
# Drop unnecessary columns
df_results = df_results.drop('Result',axis = 1)
df_results = df_results.drop('Spectators',axis = 1)
df_results = df_results.drop('Time',axis = 1)
df_results = df_results.drop('Date',axis = 1)
df_results = df_results.drop('Stadium',axis = 1)
df_results = df_results.drop('YellowCards',axis = 1)
df_results = df_results.drop('RedCards',axis = 1)
df_results = df_results.drop('GoalsHome',axis = 1)
df_results = df_results.drop('GoalsAway',axis = 1)
df_results = df_results.drop('TeamHome',axis = 1)
df_results = df_results.drop('TeamAway',axis = 1)
df_results = df_results.drop('Referee',axis = 1)
# Print df info after one hot encoding
#print('--- df2 ---')
#print(df_results.info())

# Assign X_train and y_train
X_train = df_results.drop('ResultHome',axis = 1)
y_train = df_results[['ResultHome']]
#print('### X_train: ###')
#print(X_train)
#print('### y_train: ###')
#print(y_train)
print('#############')
########################
# Get test data
# Read data
df_test = pd.read_csv('test.csv')
# From X-Y result, transform to {1,0,-1}
df_test['GoalsHome']=df_test['Result'].astype(str).str[0]
df_test['GoalsAway']=df_test['Result'].astype(str).str[4]
df_test['ResultHome']=df_test.apply(get_ResultHome,axis=1)
# Make data uniform: remove special characters and acronyms
for column in ['Stadium','Referee','TeamHome','TeamAway']:
    df_test[column]=df_test[column].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
for column in [['TeamHome'],['TeamAway']]:
    args=column
    df_test[column]=df_test.apply(short_TeamNames,args=args,axis=1)
# Print initial data frame
#print('Test data:')
#print(df_test[['Season','MatchDay','TeamHome','TeamAway','ResultHome','Referee']].to_string())

print('#### df_test_final ####')
df_test_final = pd.DataFrame(data=None, columns=df_results.columns, index=df_results.index)

Ntest = df_test.shape[0] 
print('number of test samples:',df_test.shape[0]) # measure number of rows and use if for next loop

for row in range(df_test.shape[0]):
    for col in df_test_final.columns:
        df_test_final[col].values[row] = 0
    df_test_final['Season'][row]=df_test['Season'][row]
    df_test_final['MatchDay'][row]=df_test['MatchDay'][row]
    df_test_final['ResultHome'][row]=df_test['ResultHome'][row]
    TeamHomeColumnName = 'TeamHome_' + df_test['TeamHome'][row]
    TeamAwayColumnName = 'TeamAway_' + df_test['TeamAway'][row]
    RefereeColumnName  = 'Referee_' + df_test['Referee'][row]
    #print('#############')
    #print(TeamHomeColumnName)
    #print(TeamAwayColumnName)
    #print(RefereeColumnName)
    df_test_final[TeamHomeColumnName][row]=1
    df_test_final[TeamAwayColumnName][row]=1
    df_test_final[RefereeColumnName][row]=1
df_test_final.dropna(inplace=True)
#print(df_test_final)


# Assign X_test and y_test
X_test = df_test_final.drop('ResultHome',axis = 1)
y_test = df_test_final[['ResultHome']]
#print('### X_test: ###')
#print(X_test)
#print('### y_test: ###')
#print(y_test)




# Scale Season and MatchDay
scaler = StandardScaler().fit(X_train[['Season','MatchDay']])
X_train[['Season','MatchDay']]=scaler.transform(X_train[['Season','MatchDay']])
X_test[['Season','MatchDay']]=scaler.transform(X_test[['Season','MatchDay']])
print('SCALED X_train:')
#print(X_train.to_string())
print(X_train)
print('y_train:')
print(y_train)
print('##############')
print('SCALED X_test:')
print(X_test)
print('y_test:')
print(y_test)


X_train, X_test, y_train, y_test = train_test_split(X_train,y_train, test_size=10,shuffle=False)
#X_test, X_train, y_test, y_train = train_test_split(X_train,y_train, test_size=10,shuffle=False)
print('NEW X_test:', X_test)
print(type(X_test))
print('NEW y_test:', y_test)
print(type(y_test))
#print('y_pred:', y_pred)
#print(type(y_pred))
# Start ML
Samples = 100
nodes_list=[]
for i in [20,40,60,100,120,140,160,180,200]:
    nodes_list.append(i)
for nodes in nodes_list:
    accu_per_node=[]
    result_1 = [[] for j in range(len(y_test))] # TeamHome wins
    result_0 = [[] for j in range(len(y_test))] # TeamHome loses
    result_X = [[] for j in range(len(y_test))] # Draw
    for j in range(Samples):
        #clf = MLPClassifier(hidden_layer_sizes=(10,10), max_iter=5000, alpha=1e-3, solver='sgd', verbose=10,  random_state=19)
        clf = MLPClassifier(hidden_layer_sizes=(nodes,nodes), max_iter=10000, alpha=1e-3, solver='lbfgs',  random_state=None,tol=0.0001)
        clf.fit(X_train, y_train.values.ravel())
        y_pred = clf.predict(X_test)
        print('y_pred:', y_pred)
        for i in range(len(y_pred)):
            if y_pred[i] ==  1: result_1[i].append(1)
            if y_pred[i] == -1: result_0[i].append(1)
            if y_pred[i] ==  0: result_X[i].append(1)
        accu=accuracy_score(y_test, y_pred)
        accu_per_node.append(accu)
        #print('Nodes: %i. Accuracy score: %.4f' % (nodes,accu))
    #print('result1:', result_1)
    #print('result0:', result_0)
    #print('resultX:', result_X)
    for i in range(len(y_pred)):
        print('BET: Match %i. 1: %.2f. X: %.2f. 0: %.2f' %(i,sum(result_1[i])/Samples,sum(result_X[i])/Samples,sum(result_0[i])/Samples))
    print('Nodes: %i. Mean: %.3f. Median: %.3f. Stdev: %.3f' % (nodes,statistics.mean(accu_per_node),statistics.median(accu_per_node),statistics.stdev(accu_per_node)))




#nodes=20
#mlp = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(nodes,nodes))
#fit_data=mlp.fit(X_train,y_train)

#print("Training set score: %f" % mlp.score(X_train, y_train))
#print("Test set score: %f" % mlp.score(X_test, y_test))



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
