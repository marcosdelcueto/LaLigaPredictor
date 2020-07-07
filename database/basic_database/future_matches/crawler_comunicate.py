#!/usr/bin/env python3.6
# Marcos del Cueto
import re
import sys
import requests
import unidecode
import pandas as pd
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

from bs4.element import Comment
import urllib.request


#########################################
##### START CUSTOMIZABLE PARAMETERS #####
Season = 2019
Round = 35
list_of_match_no = [0,1,2,3,4,5,6,7,8,9] # indeces within a round go from 0 to 9 (10 matches in total)
#list_of_TeamHome = ['Betis','Getafe','Villarreal','Barcelona','Eibar','Valladolid','Osasuna','Alavés','Real Madrid']
#list_of_TeamAway = ['Granada','Espanyol','Mallorca','Leganés','Athletic Club','Celta de Vigo','Atlético de Madrid','Real Sociedad','Valencia']
#list_of_TeamHome = ['Athletic Club','Atlético de Madrid','Celta de Vigo','Espanyol','Getafe','Granada','Mallorca','Real Sociedad','Sevilla','Valencia']
#list_of_TeamAway = ['Betis','Valladolid','Alavés','Levante','Eibar','Villarreal','Leganés','Real Madrid','Barcelona','Osasuna']
#list_of_TeamHome = ['Barcelona','Alavés','Eibar','Leganés','Levante','Betis','Real Madrid','Real Sociedad','Valladolid','Villarreal']
#list_of_TeamAway = ['Athletic Club','Osasuna','Valencia','Granada','Atlético de Madrid','Espanyol','Mallorca','Celta de Vigo','Getafe','Sevilla']
#list_of_TeamHome = ['Athletic Club','Atlético de Madrid','Celta de Vigo','Espanyol','Getafe','Granada','Levante','Osasuna','Sevilla','Villarreal']
#list_of_TeamAway = ['Mallorca','Alavés','Barcelona','Real Madrid','Real Sociedad','Eibar','Betis','Leganés','Valladolid','Valencia']
#list_of_TeamHome = ['Barcelona','Alavés','Eibar','Leganés','Mallorca','Betis','Real Madrid','Real Sociedad','Valladolid','Valencia']
#list_of_TeamAway = ['Atlético de Madrid','Granada','Osasuna','Sevilla','Celta de Vigo','Villarreal','Getafe','Espanyol','Levante','Athletic Club']
#list_of_TeamHome = ['Athletic Club','Atlético de Madrid','Celta de Vigo','Espanyol','Granada','Levante','Osasuna','Valladolid','Sevilla','Villarreal']
#list_of_TeamAway = ['Real Madrid','Mallorca','Betis','Leganés','Valencia','Real Sociedad','Getafe','Alavés','Eibar','Barcelona']
list_of_TeamHome = ['Athletic Club','Barcelona','Celta de Vigo','Eibar','Getafe','Mallorca','Betis','Real Madrid','Real Sociedad','Valencia']
list_of_TeamAway = ['Sevilla','Espanyol','Atlético de Madrid','Leganés','Villarreal','Levante','Osasuna','Alavés','Granada','Valladolid']


csv_file_name = 'test_dataframe.csv'
base_url = 'https://www.comuniate.com/alineaciones'
base_url_sofifa_search = 'https://sofifa.com/players?keyword='
###### END CUSTOMIZABLE PARAMETERS ######
#########################################

def main():
    data = []
    for i in range(len(list_of_match_no)):
        # Transform team names to sofifa format
        match_no = list_of_match_no[i]
        TeamHome = list_of_TeamHome[i]
        TeamAway = list_of_TeamAway[i]
        sofifa_TeamHome = TeamHome
        sofifa_TeamAway = TeamAway
        if TeamHome == 'Betis': sofifa_TeamHome = 'Real Betis'
        if TeamAway == 'Betis': sofifa_TeamAway = 'Real Betis'
        if TeamHome == 'Granada': sofifa_TeamHome = 'Granada CF'
        if TeamAway == 'Granada': sofifa_TeamAway = 'Granada CF'
        if TeamHome == 'Levante': sofifa_TeamHome = 'Levante UD'
        if TeamAway == 'Levante': sofifa_TeamAway = 'Levante UD'
        if TeamHome == 'Sevilla': sofifa_TeamHome = 'Sevilla FC'
        if TeamAway == 'Sevilla': sofifa_TeamAway = 'Sevilla FC'
        if TeamHome == 'Getafe': sofifa_TeamHome = 'Getafe CF'
        if TeamAway == 'Getafe': sofifa_TeamAway = 'Getafe CF'
        if TeamHome == 'Espanyol': sofifa_TeamHome = 'RCD Espanyol'
        if TeamAway == 'Espanyol': sofifa_TeamAway = 'RCD Espanyol'
        if TeamHome == 'Villarreal': sofifa_TeamHome = 'Villarreal CF'
        if TeamAway == 'Villarreal': sofifa_TeamAway = 'Villarreal CF'
        if TeamHome == 'Mallorca': sofifa_TeamHome = 'RCD Mallorca'
        if TeamAway == 'Mallorca': sofifa_TeamAway = 'RCD Mallorca'
        if TeamHome == 'Barcelona': sofifa_TeamHome = 'FC Barcelona'
        if TeamAway == 'Barcelona': sofifa_TeamAway = 'FC Barcelona'
        if TeamHome == 'Leganés': sofifa_TeamHome = 'CD Leganés'
        if TeamAway == 'Leganés': sofifa_TeamAway = 'CD Leganés'
        if TeamHome == 'Eibar': sofifa_TeamHome = 'SD Eibar'
        if TeamAway == 'Eibar': sofifa_TeamAway = 'SD Eibar'
        if TeamHome == 'Athletic Club': sofifa_TeamHome = 'Athletic Club de Bilbao'
        if TeamAway == 'Athletic Club': sofifa_TeamAway = 'Athletic Club de Bilbao'
        if TeamHome == 'Valladolid': sofifa_TeamHome = 'Real Valladolid CF'
        if TeamAway == 'Valladolid': sofifa_TeamAway = 'Real Valladolid CF'
        if TeamHome == 'Celta de Vigo': sofifa_TeamHome = 'RC Celta'
        if TeamAway == 'Celta de Vigo': sofifa_TeamAway = 'RC Celta'
        if TeamHome == 'Osasuna': sofifa_TeamHome = 'CA Osasuna'
        if TeamAway == 'Osasuna': sofifa_TeamAway = 'CA Osasuna'
        if TeamHome == 'Atlético de Madrid': sofifa_TeamHome = 'Atlético Madrid'
        if TeamAway == 'Atlético de Madrid': sofifa_TeamAway = 'Atlético Madrid'
        if TeamHome == 'Alavés': sofifa_TeamHome = 'Deportivo Alavés'
        if TeamAway == 'Alavés': sofifa_TeamAway = 'Deportivo Alavés'
        if TeamHome == 'Valencia': sofifa_TeamHome = 'Valencia CF'
        if TeamAway == 'Valencia': sofifa_TeamAway = 'Valencia CF'
        
        url = base_url + "/" + str(match_no) + "/" + str(Round) + "/"
        print('#######################')
        print('New Match:', TeamHome, '-', TeamAway)
        print(url)
    
        html = urllib.request.urlopen(url).read()
        final_text = text_from_html(html)
        #print('TEST final text:')
        #print(final_text)
        long_date = re.findall(r'Fecha del partido:(.*?)   ', final_text)
        if long_date:
            long_date = long_date[0].strip().split('-')
            Date = long_date[0] + "/2020"
            Time = long_date[1]
        else:
            Date = ''
            Time = ''
        
        r = re.findall(r'Posible Alineación(.*?)Jugadores lesionados', final_text)
        Referee=""
        Stadium=""
        Result = '0-0'
        counter=0
        playershome=[]
        PlayersHome=[]
        ratingshome=[]
        RatingHome=[]
        potentialshome=[]
        PotentialHome=[]
        playersaway=[]
        PlayersAway=[]
        ratingsaway=[]
        RatingAway=[]
        potentialsaway=[]
        PotentialAway=[]
        for text in r:
            words = text.split('   ')
            #print('TEST words:', words)
            for w in words:
                w = w.strip()
                if w and w != '' and not w.isdecimal():
                    new_w = re.sub("( [0-9]+|J[0-9]+)", " ", w).strip()
                    new_w = unidecode.unidecode(new_w)
                    if counter != 0 and counter != 12:
                        if new_w == 'Loren Moron': new_w = 'Lorenzo Moron'
                        if new_w == 'Emerson de Souza': new_w = 'Emerson'
                        if new_w == 'Antonio Puertas': new_w = 'Puertas'
                        if new_w == 'Yan Eteki': new_w = 'Eteki'
                        if new_w == 'Samu Chukwueze': new_w = 'Samuel Chukwueze'
                        if new_w == 'Cucho Hernandez': new_w = 'Hernandez'
                        if new_w == 'Idrissu Baba': new_w = 'Iddrisu Baba'
                        if new_w == 'Jose Angel Cote': new_w = 'Cote'
                        if new_w == 'Fede San Emeterio': new_w = 'Emeterio'
                        if new_w == 'Nacho Martinez': new_w = 'Nacho'
                        if new_w == 'David Garcia Zub.': new_w = 'David Garcia'
                        if new_w == 'Jose Gimenez': new_w = 'Gimenez'
                        if new_w == 'Fede Valverde': new_w = 'Valverde'
                        if new_w == 'Maxi Gomez': new_w = 'Gomez'
                        if new_w == 'Vinicius Junior': new_w = 'Vinicius jr'
                        if new_w == 'Michel Herrero': new_w = 'Herrero'
                        if new_w == 'Ferreira Carrasco': new_w = 'Carrasco'
                        if new_w == 'Jacobo Gonzalez': new_w = 'jacobo&r=200024&set=true'
                        if new_w == 'Rober Pier': new_w = 'Pier'
                        if new_w == 'Abdallahi': new_w = 'Manu Garcia'
                        medium_name = new_w
                        #print('TEST name:',medium_name)
                        player_sofifa_id, final_team, player_rating, player_potential = get_id(medium_name)
                        counter2=0
                        for team in final_team:
                            if counter > 0 and counter < 12 and team[0] == sofifa_TeamHome:
                                print('Player:', medium_name, '-- Sofifa info -- ID:',player_sofifa_id[counter2],'. Team:',final_team[counter2][0],'. Rating:',player_rating[counter2],'. Potential:',player_potential[counter2])
                                playershome.append(medium_name)
                                ratingshome.append(int(player_rating[counter2]))
                                potentialshome.append(int(player_potential[counter2]))
                            elif counter > 12 and counter < 24 and team[0] == sofifa_TeamAway:
                                print('Player:', medium_name, '-- Sofifa info -- ID:',player_sofifa_id[counter2],'. Team:',final_team[counter2][0],'. Rating:',player_rating[counter2],'. Potential:',player_potential[counter2])
                                playersaway.append(medium_name)
                                ratingsaway.append(int(player_rating[counter2]))
                                potentialsaway.append(int(player_potential[counter2]))
                            counter2 = counter2+1

                    counter=counter+1
        print('#######################')
        PlayersHome.append(playershome)
        PlayersAway.append(playersaway)
        RatingHome.append(ratingshome)
        RatingAway.append(ratingsaway)
        PotentialHome.append(potentialshome)
        PotentialAway.append(potentialsaway)
        # Transform to data frame
        data_row = [Season,Round,Date,Time,TeamHome,Result,TeamAway,Referee,Stadium,PlayersHome,RatingHome,PotentialHome,PlayersAway,RatingAway,PotentialAway]
        data.append(data_row)
        
        df = pd.DataFrame(data,columns=['Season','Round','Date','Time','TeamHome','Result','TeamAway','Referee','Stadium','PlayersHome','RatingHome','PotentialHome','PlayersAway','RatingAway','PotentialAway'])
        #print(df)
        df.to_csv (csv_file_name, index = False, header=True)


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

### START function to get id from sofifa ###
def get_id(medium_name):
    #print('CALL TO get_id')
    medium_name= medium_name.strip()
    url = base_url_sofifa_search + str(medium_name)
    #print('TEST search in sofifa url:',url)
    res = requests.get(url)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    my_teams = []
    player_id = None
    for line in soup:
        #exact_name = re.findall(rf"<a class=.+{medium_name}\" href=\"/player/[0-9]+",str(line))
        #print(line)
        #if exact_name: 
            #id_by_exact_name = re.findall(r"[0-9]+",str(exact_name))
        look_for_this = re.findall(r"href=\"/player/[0-9]+",str(line))
        if look_for_this:
            player_id = re.findall(r"[0-9]+",str(look_for_this))
            player_scores = re.findall(r'<span class=\"bp3-tag p p-(.*?)\">', str(line))
            player_rating = player_scores[0::2]
            player_potential = player_scores[1::2]
            #print('TEST all:', player_scores)
            #print('TEST rating:', player_rating)
            #print('TEST potential:', player_potential)
#r = re.findall(r'Posible Alineación(.*?)Jugadores lesionados', final_text)
        my_team = re.findall(r"<a href=\"/team/.+",str(line))
        for text in my_team:
            #print('TEST:',text)
            my_team2 = re.findall(r'>(.+?)</a>',str(text))
            #print('TEST2:',my_team2)
            my_teams.append(my_team2)
    #if player_id: print('TEST player_id',player_id)
    #if my_teams: print('TEST2 my_teams', my_teams)
    if player_id == None:

        print('ERROR - No information of player %s could be found in sofifa' %(medium_name))
        sys.exit()
    return player_id, my_teams, player_rating, player_potential
#### END function to get id from sofifa ####
############################################

main()
