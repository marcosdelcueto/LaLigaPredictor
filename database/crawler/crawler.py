#!/usr/bin/env python3.6
# Marcos del Cueto
import re
import sys
import requests
import unidecode
import pandas as pd
from bs4 import BeautifulSoup
from difflib import SequenceMatcher


#########################################
##### START CUSTOMIZABLE PARAMETERS #####
start_index = 29246
end_index   = 29340
csv_file_name = 'test_dataframe.csv'
base_url = 'https://www.bdfutbol.com/en/p/p.php?id='
base_url_player_bdfutbol = "https://www.bdfutbol.com/en/j/j"
base_url_sofifa_search = 'https://sofifa.com/players?keyword='
base_url_sofifa_player = 'https://sofifa.com/player/'
special_cases = [['Takashi Inui',[205114]],['Lee Kang In',[243780]],['Takefusa Kubo',[237681]],['Francisco de Borja Fernandez Fernandez',[110787]],['Junior Osmar Ignacio Alonso Mujica',[220337]],['Gustavo Adrian Ramos Vasquez',[176619]],['Esteban Felix Granero Molina',[178085]],['Pablo Guido Larrea Gambara',[235971]],['Gaku Shibasaki',[232883]],['Enzo Alan Zidane Fernandez',[211234]],['Alex Pachon Parraga',[246760]],['Victor Campuzano Bonilla',[246949]],['Emerson Aparecido Leite de Souza',[247204]],['Papakouli Diop ',[178250]],['Jose Carlos Sanchez Gonzalez',[240919]],['Loic Alex Teliere Hubert Remy',[179527]],['Ivan Villar Martinez',[222572]],['Rachid Ait-Atmane',[225120]],['Papakouli Diop',[178250]],['Martin Aguirregabiria Padilla',[241827]],['Markel Areitio Cedrun',[235990]],['Mikel Carro Fandino',[247806]],['Antolin Alcaraz Viveros',[138949]],['Angel de la Calzada Ramos',[231750]],['Dario Poveda Romera',[236940]],['Steve Aldo One',[228975]],['Javier Lopez Abadias',[230875]],['Jaime Seoane Valenciano',[247793]],['Waldo Rubio Marin',[231414]],['Enrique Cebria Alcover',[212488]],['Ruben Sanchez Perez-Cejuela',[236995]],['Robert Mazan',[227936]],['Gustavo Enrique Giordano Amaro Assuncao da Silva',[248386]],['Diego Caballo Alonso',[244466]],['Diego Barrios Perez',[236384]],['Manuel Alejandro Garcia Sanchez',[172287]],['Aly Malle',[237294]],['Antonio Moya Vega',[241588]],['Eugeni Valderrama Domenech',[209695]],['Merveil Valthy Streeker Ndockyt',[242792]],['Zourdine Mouhemed Thior',[248398]],['Timothee Kolodziejczak',[190034]],['Eric Curbelo de la Fe',[237442]],['Martin Hongla',[236556]],['Daniel Raba Antolin',[241463]],['Maksym Anatoliyovych Koval',[206412]],['Juan Carlos Lazaro Cervera',[235978]],['Paulino de la Fuente Gomez',[248710]],['Alex Collado Gutierrez',[242999]],['Andres Pascual Santoja',[234152]],['David Carmona Sierra',[234151]],['Pervis Josue Estupinan Tenorio',[237942]],['Jaime Sierra Mateos',[243036]],['Lorenzo Jesus Moron Garcia',[242348]],['Manuel Sanchez de la Pena',[252327]],['Carles Perez Sayol',[240654]],['Roberto Olabe del Arco',[238225]],['Mohammed Zakaria Boulahia',[238291]],['Mathieu Flamini',[156722]],['Imoh Ezekiel',[208022]],['Andoni Zubiaurre Dorronsoro',[243304]],['Pablo Fernandez Blanco',[238344]],['Ignacio Vidal Miralles',[238305]],['Gabriel Salazar Rojo',[242799]],['Manuel Morlanes Arino',[241856]],['Jhon Steven Mondragon Dosman',[225505]],['Hugo Duro Perales',[243032]],['Jose Carlos Lazo Romero',[229631]],['Francisco Barbosa Vieites',[243587]],['Carlos Isaac Munoz Obejero',[243080]]]
time_labels_up_to = 21
###### END CUSTOMIZABLE PARAMETERS ######
#########################################


###########################
### START main function ###
def main():
    # Initialize list with final results
    data = []
    # Loop over all indeces
    for id_index in range(start_index,end_index):
        # Print new id_index
        print('#######################')
        print('New match. Index:', id_index)
        print('#######################')
        # Calculate Season
        Season = get_Season(id_index)
        # Get general info from bdfutbol
        counter=0
        Round, Date, TeamHome, Result, TeamAway, Stadium, Referee, player_name, soup, counter = get_general_info_bdfutbol(id_index,counter) 
        # Get complete player name from bdfutbol
        player_name_complete = get_bdfutbol_complete_name(player_name,soup)
        # Get players info from sofifa
        player_rating, player_potential, counter = get_player_sofifa_info(counter,Season,Round,player_name_complete,player_name,special_cases,time_labels_up_to)
        # Create dataframe with data
        df = create_dataframe(player_name,player_rating,player_potential,data,Season,Round,Date,TeamHome,Result,TeamAway,Stadium,Referee)
        # Print dataframe into csv file
        df.to_csv (csv_file_name, index = False, header=True)
#### END main function ####
###########################

############################################
### START function to get id from sofifa ###
def get_id(medium_name,time_label):
    medium_name= medium_name.strip()
    url = base_url_sofifa_search + str(medium_name) + "&r=" + str(time_label) + "&set=true"
    #print('TEST search in sofifa url:',url)
    res = requests.get(url)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    for line in soup:
        exact_name = re.findall(rf"<a class=.+{medium_name}\" href=\"/player/[0-9]+",str(line))
        if exact_name: 
            id_by_exact_name = re.findall(r"[0-9]+",str(exact_name))
        player_id = re.findall(r"href=\"/player/[0-9]+",str(line))
        player_id = re.findall(r"[0-9]+",str(player_id))
        if player_id:
            player_sofifa_id = player_id
            if len(player_sofifa_id)>1 and exact_name:
                if id_by_exact_name[0] in player_sofifa_id:
                    player_sofifa_id = []
                    player_sofifa_id.append(id_by_exact_name[0])
                    #print('# warning # More than 1 ID found. Was able to solve it:',medium_name,id_by_exact_name[0],'--',TeamHome,'-',TeamAway,'--',url)
            return player_sofifa_id,url
    return None,None
#### END function to get id from sofifa ####
############################################

#############################
### START sofifa_function ###
def sofifa_function(p,time_label,counter_player,player_name,special_cases):
    player_sofifa_id = None
    final_url = None
    # Special cases
    if unidecode.unidecode(p) == 'Jacobus Antonius Peter Johannes Cillessen': p='Jasper Cillessen'
    for i in range(len(special_cases)):
        if unidecode.unidecode(p) == special_cases[i][0]: player_sofifa_id = special_cases[i][1]
    # Calculate id using long name
    if player_sofifa_id == None:
        medium_name = p
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    if player_sofifa_id == None: player_sofifa_id, final_url = get_id(unidecode.unidecode(medium_name),time_label)
    ##################################
    # Manually fix discrepancies on sofifa and bdfutbol
    if player_sofifa_id == None and unidecode.unidecode(p)=='Miguel Alfonso Herrero Javaloyas': 
        medium_name = 'Miguel Angel Herrero Javaloyas'
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    elif player_sofifa_id == None and unidecode.unidecode(p)=='Luis Alberto Suarez Diaz': 
        medium_name = 'Luis Suarez'
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    elif player_sofifa_id == None and unidecode.unidecode(p)=='Idrissu Baba Mohammed': 
        medium_name = 'Iddrisu Baba'
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    elif player_sofifa_id == None and unidecode.unidecode(p)=='Djene Dakonam Ortega': 
        medium_name = 'Dakonam Djene'
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    elif player_sofifa_id == None and unidecode.unidecode(p)=='Alhassane Bangoura': 
        medium_name = 'Lassane Bangoura'
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    elif player_sofifa_id == None and unidecode.unidecode(p)=='Osvaldo Nicolas Fabian Gaitan': 
        medium_name = 'Nicolas Gaitan'
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    elif player_sofifa_id == None and unidecode.unidecode(p)=='Carlos Gurpegui Nausia': 
        medium_name = 'Carlos Gurpegi'
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    elif player_sofifa_id == None and unidecode.unidecode(p)=='Francisco Jesus Lopez de la Manzanara Delgado': 
        medium_name = 'Fran Manzanara'
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    elif player_sofifa_id == None and unidecode.unidecode(p)=='Aderlan Leandro de Jesus Santos': 
        medium_name = 'Aderllan Santos'
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    elif player_sofifa_id == None and unidecode.unidecode(p)=='Angel Martin Correa Martinez': 
        medium_name = 'Angel Correa'
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    elif player_sofifa_id == None and unidecode.unidecode(p)=='Youssef El-Arabi': 
        medium_name = 'Youssef El Arabi'
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    elif player_sofifa_id == None and unidecode.unidecode(p)=='Sergio Mendiguchia Iglesias': 
        medium_name = 'Sergio Mendi'
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    elif player_sofifa_id == None and unidecode.unidecode(p)=='Alberto Martin-Romo Garcia-Adamez': 
        medium_name = 'Alberto Martin'
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    elif player_sofifa_id == None and unidecode.unidecode(p)=='Fabio Alexandre da Silva Coentrao': 
        medium_name = 'Fabio Coentrao'
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    elif player_sofifa_id == None and unidecode.unidecode(p)=='Diogo Jose Rosario Gomes Figueiras': 
        medium_name = 'Diogo Figueiras'
        player_sofifa_id, final_url = get_id(medium_name,time_label)
    ##################################
    # If no ID has been found when searching long name in sofifa, try removing last word of long name
    if player_sofifa_id == None or len(player_sofifa_id) > 1:
        if len(p.split()) > 1:
            new_name=[]
            for i in p.split():
                new_name.append(i)
            new_name = new_name[0:-1]
            medium_name=''
            for i in new_name:
                medium_name = medium_name + ' ' + i
            player_sofifa_id, final_url = get_id(medium_name,time_label)
            if player_sofifa_id == None or len(player_sofifa_id) > 1: player_sofifa_id, final_url = get_id(unidecode.unidecode(medium_name),time_label)
    #################################
    # If no ID has been found when searching long name in sofifa, try removing 2nd word from long name
    if player_sofifa_id == None or len(player_sofifa_id) > 1:
        if len(p.split()) > 2:
            new_name=[]
            for i in p.split():
                new_name.append(i)
            new_name2 = new_name[0:1] + new_name[2:]
            medium_name=''
            for i in new_name2:
                medium_name = medium_name + ' ' + i
            player_sofifa_id, final_url = get_id(medium_name,time_label)
            if player_sofifa_id == None or len(player_sofifa_id) > 1: player_sofifa_id, final_url = get_id(unidecode.unidecode(medium_name),time_label)
    ################################        
    # If no ID has been found when searching long name in sofifa, use only first three names
    if player_sofifa_id == None or len(player_sofifa_id) > 1:
        if len(p.split()) > 4:
            new_name=[]
            for i in p.split():
                new_name.append(i)
            new_name2 = new_name[0:3]
            medium_name=''
            for i in new_name2:
                medium_name = medium_name + ' ' + i
            player_sofifa_id, final_url = get_id(medium_name,time_label)
            if player_sofifa_id == None or len(player_sofifa_id) > 1: player_sofifa_id, final_url = get_id(unidecode.unidecode(medium_name),time_label)
    ################################        
    # If no ID has been found when searching long name in sofifa, try using just 2 first words
    if player_sofifa_id == None or len(player_sofifa_id) > 1:
        if len(p.split()) > 2:
            new_name=[]
            for i in p.split():
                new_name.append(i)
            new_name2 = new_name[0:2]
            medium_name=''
            for i in new_name2:
                medium_name = medium_name + ' ' + i
            player_sofifa_id, final_url = get_id(medium_name,time_label)
            if player_sofifa_id == None or len(player_sofifa_id) > 1: player_sofifa_id, final_url = get_id(unidecode.unidecode(medium_name),time_label)
    ################################        
    # If no ID has been found when searching long name in sofifa, try using just 1 or 3 words
    if player_sofifa_id == None or len(player_sofifa_id) > 1:
        if len(p.split()) > 3 and p.split()[2] not in ['do','de','di','da','del']:
            new_name=[]
            for i in p.split():
                new_name.append(i)
            new_name2 = new_name[0:1] + new_name[2:3]
            medium_name=''
            for i in new_name2:
                medium_name = medium_name + ' ' + i
            player_sofifa_id, final_url = get_id(medium_name,time_label)
            if player_sofifa_id == None or len(player_sofifa_id) > 1: player_sofifa_id, final_url = get_id(unidecode.unidecode(medium_name),time_label)
    ################################        
    # If no ID has been found when searching long name in sofifa, drop first word
    if player_sofifa_id == None or len(player_sofifa_id) > 1:
        if len(p.split()) > 2:
            new_name=[]
            for i in p.split():
                new_name.append(i)
            new_name2 = new_name[1:]
            medium_name=''
            for i in new_name2:
                medium_name = medium_name + ' ' + i
            player_sofifa_id, final_url = get_id(medium_name,time_label)
            if player_sofifa_id == None or len(player_sofifa_id) > 1: player_sofifa_id, final_url = get_id(unidecode.unidecode(medium_name),time_label)
    ################################        
    # If no ID has been found when searching long name in sofifa, drop first or last name
    if player_sofifa_id == None or len(player_sofifa_id) > 1:
        if len(p.split()) > 3:
            new_name=[]
            for i in p.split():
                new_name.append(i)
            new_name2 = new_name[1:-1]
            medium_name=''
            for i in new_name2:
                medium_name = medium_name + ' ' + i
            player_sofifa_id, final_url = get_id(medium_name,time_label)
            if player_sofifa_id == None or len(player_sofifa_id) > 1: player_sofifa_id, final_url = get_id(unidecode.unidecode(medium_name),time_label)
    ################################        
    # If no ID has been found when searching long name in sofifa, try with short name
    if player_sofifa_id == None or len(player_sofifa_id) > 1:
        player_sofifa_id, final_url = get_id(player_name[counter_player],time_label)
        player_sofifa_id, final_url = get_id(unidecode.unidecode(player_name[counter_player]),time_label)
    ################################        
    return player_sofifa_id, final_url, p
#### END sofifa_function ####
#############################

###############################
### START Create time label ###
def create_time_label(Season,Round,Increment):
    fifa_year = int(str(Season)[-2:]) + 1
    time_stamp = int(Round)+int(Increment)
    if time_stamp < 10:
        time_stamp = '000' + str(time_stamp)
    else:
        time_stamp = '00' + str(time_stamp)
    time_label = str(fifa_year) + str(time_stamp)
    return time_label
#### END Create time label ####
###############################

########################
### START get_Season ###
def get_Season(id_index):
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
        print('ERROR: index out of range:', id_index)
        sys.exit()
    return Season
#### END get_Season ####
########################

#######################################
### START get_general_info_bdfutbol ###
def get_general_info_bdfutbol(id_index,counter):
    # Parse bdfutbol html with BeautifulSoup
    url = base_url + str(id_index)
    res = requests.get(url)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    text = soup.find_all(text=True)
    # Loop over each line to extract data
    counter_holder = -1000
    player_name = []
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
            # Get short names Players
            if counter > counter_holder+7 and counter_holder > 0:
                test = line.strip()
                # stop looking for players after string 'Manager' is found
                if test == 'Manager': break
                # skip line with 'Substitutes' string
                if test == 'Substitutes': continue
                # if possible, transform string to int, to ignore integers
                try:
                    test = int(test)
                except:
                    pass
                is_this_int_with_extra_time = re.findall(r".+\+.+",str(test))
                #if is_this_int_with_extra_time: print('I FOUND INT AT EXTRA TIME', test)
                #print(test,type(test))
                if type(test) == str and not is_this_int_with_extra_time:
                    player_name.append(test)
            counter = counter + 1
    return Round, Date, TeamHome, Result, TeamAway, Stadium, Referee, player_name, soup, counter
#### END get_general_info_bdfutbol ####
###############################

########################################
### START get_bdfutbol_complete_name ###
def get_bdfutbol_complete_name(player_name,soup):
    # Get bdfutbol ID from each player
    player_id_bdfutbol = []
    player_name_complete = []
    for p in range(len(player_name)):
        for line in soup:
            player_bdfutbol_id = re.findall(rf"<a href=\"../j/j[0-9]+.html\">{player_name[p]}</a>",str(line))
            #print('### test ###:',p, player_name[p], player_bdfutbol_id)
            player_bdfutbol_id = re.findall(r"[0-9]+",str(player_bdfutbol_id))
            if player_bdfutbol_id: 
                player_id_bdfutbol.append(player_bdfutbol_id[0])
                break
    # For each player
    for p in range(len(player_name)):
        url_player_bdfutbol = base_url_player_bdfutbol + str(player_id_bdfutbol[p]) + ".html"
        res = requests.get(url_player_bdfutbol)
        html_page = res.content
        soup = BeautifulSoup(html_page, 'html.parser')
        text = soup.find_all(text=True)
        # for each line in the bdfutbol page of the player
        for line in text:
            if line.rstrip():
                player_complete_name = re.findall(rf"{player_name[p]}, .+ - Footballer",str(line))
                player_complete_name = re.findall(r",.+-",str(player_complete_name))
                # if we get the complete name of the player:
                if player_complete_name: 
                    player_name_complete.append(player_complete_name[0][2:-2])
        # if no 'short name, long name' format is provided, use short name as long one
        if p == len(player_name_complete):
            player_name_complete.append(player_name[p])
    #print(player_name_complete)
    return player_name_complete
#### END get_bdfutbol_complete_name ####
########################################

######################################
#### START get_player_sofifa_info ####
def get_player_sofifa_info(counter,Season,Round,player_name_complete,player_name,special_cases,time_labels_up_to):
    player_rating = []
    player_potential = []
    # For each player, look in sofifa and get player info (try to get id both for regular name, and unicode-friendly one)
    counter_player=0
    for p in player_name_complete:
        player_sofifa_id = None
        if unidecode.unidecode(p) == 'Giovanni Jesus Navarro Sole': # special case where player is actually in another league: 2B
            player_sofifa_id = [225473]
            print('### WARNING --- I am really player', p)
            print('### WARNING --- I am going to use mock id:', player_sofifa_id)
        # Look in sofifa for different dates
        for t in range(int((time_labels_up_to-3)/2),time_labels_up_to+1):
            if player_sofifa_id == None:
                time_label = create_time_label(Season,Round,t)
                player_sofifa_id, final_url, p = sofifa_function(p,time_label,counter_player,player_name,special_cases)
        for t in range(int((time_labels_up_to-3)/2)):
            if player_sofifa_id == None:
                time_label = create_time_label(Season,Round,t)
                player_sofifa_id, final_url, p = sofifa_function(p,time_label,counter_player,player_name,special_cases)
        # Print error message if no ID was found
        if player_sofifa_id == None:
            print('####################################################################')
            print('ERROR: No ID found when looking in sofifa for:', p)
            print('ERROR: No ID found when looking in sofifa for:', player_name[counter_player])
            print('####################################################################')
            sys.exit()
        # Print error message if more than one ID was found
        if len(player_sofifa_id) > 1:
            print('####################################################################')
            print('ERROR: More than 1 possible ID when looking in sofifa for:', p)
            print('####################################################################')
            sys.exit()
        counter_player = counter_player+1
        # Once we have one unique ID, get data from that player at corresponding time
        url = base_url_sofifa_player + str(player_sofifa_id[0]) + "/" + str(time_label)
        res = requests.get(url)
        html_page = res.content
        soup = BeautifulSoup(html_page, 'html.parser')
        text = soup.find_all(text=True)
        counter_line=0
        counter_placeholder=-100
        look_for_sofifa_data = False
        for line in text:
            if line.rstrip():
                found_this =re.findall(r"^Calculator",str(line))
                if found_this: look_for_sofifa_data = True
                if look_for_sofifa_data == True:
                    name_sofifa = re.findall(r".+\(ID\:.+",str(line))
                    name_sofifa = re.findall(r".+?(?=\(ID\:)",str(name_sofifa))
                    name_sofifa = unidecode.unidecode(str(name_sofifa))
                    name_sofifa = re.findall(r"[a-zA-Z\- ]{2,}",str(name_sofifa))
                    if name_sofifa: 
                        #if SequenceMatcher(a=unidecode.unidecode(p),b=name_sofifa[0].strip()).ratio() < 0.59:
                        #print('TEST special names:', [i[0] for i in special_cases])
                        if SequenceMatcher(a=unidecode.unidecode(p),b=name_sofifa[0].strip()).ratio() < 0.59 and unidecode.unidecode(p) not in [i[0] for i in special_cases]:

                            print('### WARNING ### Player:', p, '---', name_sofifa[0], player_sofifa_id, final_url, SequenceMatcher(a=unidecode.unidecode(p),b=name_sofifa[0].strip()).ratio())
                    player_lbs = re.findall(r"lbs$",str(line))
                    if player_lbs: counter_placeholder=counter
                    counter = counter+1
                    if counter == counter_placeholder+2: rating = line
                    if counter == counter_placeholder+4:
                        try:
                            int(line)
                            potential = line
                        except:
                            potential = None
                            pass
                    if counter == counter_placeholder+5 and potential == None:
                        try:
                            int(line)
                            potential = line
                        except:
                            pass
                    if counter > counter_placeholder+5 and counter_placeholder > 0: break
        player_rating.append(int(rating))
        player_potential.append(int(potential))
    return player_rating, player_potential, counter
##### END get_player_sofifa_info #####
######################################

##############################
### START create_dataframe ###
def create_dataframe(player_name,player_rating,player_potential,data,Season,Round,Date,TeamHome,Result,TeamAway,Stadium,Referee):
    # Initialize lists
    PlayersHome = []
    PlayersAway = []
    ratingHome = []
    ratingAway = []
    potentialHome = []
    potentialAway = []
    # Create lists for home team players
    PlayersHome.append(player_name[0:11])           # starting players
    PlayersHome.append(player_name[22:29])          # substitutes
    ratingHome.append(player_rating[0:11])          # starting players
    ratingHome.append(player_rating[22:29])         # substitutes
    potentialHome.append(player_potential[0:11])    # starting players
    potentialHome.append(player_potential[22:29])   # substitutes
    # Create lists for away team players
    PlayersAway.append(player_name[11:22])          # starting players
    PlayersAway.append(player_name[29:36])          # substitutes
    ratingAway.append(player_rating[11:22])         # starting players
    ratingAway.append(player_rating[29:36])         # substitutes
    potentialAway.append(player_potential[11:22])   # starting players
    potentialAway.append(player_potential[29:36])   # substitutes
    # Put all lists into another list and append to previous data
    data_row = [Season,Round,Date,TeamHome,Result,TeamAway,Stadium,Referee,PlayersHome,ratingHome,potentialHome,PlayersAway,ratingAway,potentialAway]
    data.append(data_row)
    # Transform list into a data frame
    df = pd.DataFrame(data,columns=['Season','Round','Date','TeamHome','Result','TeamAway','Stadium','Referee','PlayersHome','RatingHome','PotentialHome','PlayersAway','RatingAway','PotentialAway'])
    # print data frame into csv file
    #df.to_csv (r'test_dataframe.csv', index = False, header=True)
    #df.to_csv (csv_file_name, index = False, header=True)
    return df
#### END create_dataframe ####
##############################

# Run main function
main()
