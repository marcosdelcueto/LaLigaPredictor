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
csv_output_name = 'database_final_expanded.csv'
last_N_matches = 5

def main():
    df = pd.read_csv(csv_file_name)
    
    print(df)
 
    all_teams_home = df['TeamHome'].unique()
    all_teams_away = df['TeamAway'].unique()

    print('All teams home:')
    print(all_teams_home)
    print('All teams away:')
    print(all_teams_away)

    # add code to check if all_teams_home has same contents as all_teams_away

    for team in all_teams_home:
    #for team in ['Betis']:
        team_home_df = df.loc[df['TeamHome'] == team]
        team_away_df = df.loc[df['TeamAway'] == team]
        team_home_index = list(team_home_df.index)
        team_away_index = list(team_away_df.index)
        team_total_index = team_home_index + team_away_index
        team_total_index = sorted(team_total_index)
        print(team)
        print('Home:', team_home_index)
        print('Away:', team_away_index)
        print('Total:', team_total_index)
        print('###############')

        # Calculate points for last N matches played at home
        prev_home = [[] for i in range(len(team_home_index))]
        prev_points_home = []
        # for each match played home
        for i in range(len(team_home_index)):
            points = 0
            # ignore first N matches
            if i <= (last_N_matches-1): prev_points_home.append(0)
            # get points for last N matches
            if i > (last_N_matches-1):
                # loop from 1 to N, assigning points for home team
                for j in range(1,(last_N_matches+1)):
                    prev_home[i].append(team_home_index[i-j])
                    result_match = df.iloc[team_home_index[i-j]][5]
                    goals_home = result_match[0]
                    goals_away = result_match[2]
                    if int(goals_home) > int(goals_away):
                        points = points + 3
                    elif int(goals_home) < int(goals_away):
                        points = points + 0
                    else:
                        points = points + 1
                # get final points for each match
                prev_points_home.append(points)
            df.at[team_home_index[i],'TeamHomeRecentPointsHome'] = prev_points_home[i]
        #print('prev_home:',prev_home)
        #print('prev_points_home:',prev_points_home)
        #print('###############')

        # Calculate points for last N matches played away
        prev_away = [[] for i in range(len(team_away_index))]
        prev_points_away = []
        # for each match played away
        for i in range(len(team_away_index)):
            #print(i)
            points = 0
            # ignore first N matches
            if i <= (last_N_matches-1): prev_points_away.append(0)
            # get points for last N matches
            if i > (last_N_matches-1):
                # loop from 1 to N, assigning points for away team
                for j in range(1,(last_N_matches+1)):
                    prev_away[i].append(team_away_index[i-j])
                    result_match = df.iloc[team_away_index[i-j]][5]
                    #print(result_match)
                    goals_home = result_match[0]
                    goals_away = result_match[2]
                    if int(goals_away) > int(goals_home):
                        points = points + 3
                    elif int(goals_away) < int(goals_home):
                        points = points + 0
                    else:
                        points = points + 1
                    #print('Points:', points)
                # get final points for each match
                prev_points_away.append(points)
            df.at[team_away_index[i],'TeamAwayRecentPointsAway'] = prev_points_away[i]
        #print('prev_away:',prev_away)
        #print('prev_points_away:',prev_points_away)
        #print('###############')

        # Calculate points for last N matches played anywhere
        prev_total = [[] for i in range(len(team_total_index))]
        prev_points_total = []
        # for each match played anywhere
        for i in range(len(team_total_index)):
            #print(i)
            points = 0
            # ignore first N matches
            if i <= (last_N_matches-1): prev_points_total.append(0)
            # get points for last N matches
            if i > (last_N_matches-1):
                # loop from 1 to N, assigning points for team
                for j in range(1,(last_N_matches+1)):
                    prev_total[i].append(team_total_index[i-j])
                    result_match = df.iloc[team_total_index[i-j]][5]
                    #print(result_match)
                    goals_home = result_match[0]
                    goals_away = result_match[2]
                    if int(goals_home) > int(goals_away):
                        if team_total_index[i-j] in team_home_index: points = points + 3
                        if team_total_index[i-j] in team_away_index: points = points + 0
                    elif int(goals_home) < int(goals_away):
                        if team_total_index[i-j] in team_home_index: points = points + 0
                        if team_total_index[i-j] in team_away_index: points = points + 3
                    else:
                        points = points + 1
                    #print('Points:', points)
                # get final points for each match
                prev_points_total.append(points)
            if team_total_index[i] in team_home_index: df.at[team_total_index[i],'TeamHomeRecentPoints'] = prev_points_total[i]
            if team_total_index[i] in team_away_index: df.at[team_total_index[i],'TeamAwayRecentPoints'] = prev_points_total[i]
        #print('prev_total:',prev_total)
        #print('prev_points_total:',prev_points_total)
        #print('###############')

    df.to_csv (csv_output_name, index = False, header=True)



########################
### Start function get_Month
def test_func(row):
    val = row['TeamHome'].strip()

    if val == 'Betis': 
        print(val)
    return val
### End function get_Month
########################

main()
