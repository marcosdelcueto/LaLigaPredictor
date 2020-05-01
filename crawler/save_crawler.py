#!/usr/bin/env python3.6
# Marcos del Cueto
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

data = []
base_url = 'https://www.bdfutbol.com/en/p/p.php?id='
# Loop over all indeces
for id_index in range(29720,29721):
    # Assign corresponding season
    if id_index >= 25600 and id_index <= 25979:
        Season = 2009
    elif id_index >= 26000 and id_index <= 26379:
        Season = 2010
    elif id_index >= 26643 and id_index <= 27022:
        Season = 2011
    elif id_index >= 27023 and id_index <= 27402:
        Season = 2012
    elif id_index >= 27403 and id_index <= 27782:
        Season = 2013
    elif id_index >= 27783 and id_index <= 28162:
        Season = 2014
    elif id_index >= 28200 and id_index <= 28579:
        Season = 2015
    elif id_index >= 28580 and id_index <= 28959:
        Season = 2016
    elif id_index >= 28960 and id_index <= 29339:
        Season = 2017
    elif id_index >= 29340 and id_index <= 29719:
        Season = 2018
    elif id_index >= 29720 and id_index <= 29909:
        Season = 2019
    else:
        continue
    # Parse html with BeautifulSoup
    url = base_url + str(id_index)
    #print('#########')
    #print('TEST url:',url)
    res = requests.get(url)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    text = soup.find_all(text=True)
    # Loop over each line to extract data
    counter=0
    counter_holder = -1000
    for line in text:
        if line.rstrip():
            place_holder = re.findall(r"Round+",line)
            #print(line)
            # Use the string 'round' as a place holder to look for data
            if place_holder: 
                counter_holder = counter
                Round = line.split()[4]
                Date = line.split()[6]
            if counter > counter_holder and counter_holder > 0:
                # ignore info about when players scored
                if line.strip()[-1] == "'" or line.strip()[-1] == ")":
                    continue
            # Get TeamHome
            if counter > counter_holder and counter <= counter_holder+1:
                TeamHome = line
            # Get Result
            if counter > counter_holder+1 and counter <= counter_holder+2:
                Result = line.split()[0] + line.split()[1] + line.split()[2]
            # Get TeamAway
            if counter > counter_holder+2 and counter <= counter_holder+3:
                TeamAway = line
            # Get Stadium
            if counter > counter_holder+3 and counter <= counter_holder+4:
                Stadium = line.strip()
            # Get Referee
            if counter > counter_holder+4 and counter <= counter_holder+5:
                Referee = line.strip()
            # Get Players
            if counter > counter_holder+7 and counter_holder > 0:
                test = line.strip()
                # stop looking for players after string 'Manager' is found
                if test == 'Manager': break
                # skip line with 'Substitutes' string
                if test == 'Substitutes': continue
                # if possible, transform string to int
                try:
                    test = int(test)
                except:
                    pass
                #print(test,type(test))
                if type(test) == str:
                    player_name = test
                    player_complete_name = re.findall(rf"{player_name}</a>",str(soup))
                    print(player_name, player_complete_name)
                    print(str(soup))
                    #print(soup)
                    #print(text)
                    #####################
                    #base_url = 'https://sofifa.com/players?keyword='
                    #url = base_url + str(player_name)
                    #res = requests.get(url)
                    #html_page = res.content
                    #soup = BeautifulSoup(html_page, 'html.parser')
                    ##text = soup.find_all(text=True)
                    ##print(soup)
                    #for line2 in soup:
                        ##print(line2)
                        #player_id = re.findall(r"href=\"/player/[0-9]+",str(line2))
                        #player_id = re.findall(r"[0-9]+",str(player_id))
                        #if player_id: 
                            #player_sofifa_id = player_id
                    #if len(player_sofifa_id) == 1: 
                        #print(player_name,player_sofifa_id)
                    #elif len(player_sofifa_id) > 1: 
                        #print('####################################################################')
                        #print('ERROR: More than 1 possible ID when looking in sofifa for:', player_name)
                        #print('####################################################################')
                    #elif len(player_sofifa_id) < 1:
                        #print('####################################################################')
                        #print('ERROR: No ID found when looking in sofifa for:', player_name)
                        #print('####################################################################')
                    #break ### this is just for testing 1 players
                    #####################



            counter = counter + 1
    data_row = [Season,Round,Date,TeamHome,Result,TeamAway,Stadium,Referee]
    data.append(data_row)

df = pd.DataFrame(data,columns=['Season','Round','Date','TeamHome','Result','TeamAway','Stadium','Referee'])

#print(df.to_string())

df.to_csv (r'test_dataframe.csv', index = False, header=True)
